from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
import uuid

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_by_status(self, db: Session, *, status: str) -> List[Project]:
        return db.query(Project).filter(Project.status == status).all()

    def get_by_team_lead(self, db: Session, *, team_lead_id: str) -> List[Project]:
        return db.query(Project).filter(Project.team_lead_id == team_lead_id).all()

    def get_active_projects(self, db: Session) -> List[Project]:
        return db.query(Project).filter(Project.status == "Active").all()

    def create(self, db: Session, *, obj_in: ProjectCreate) -> Project:
        db_obj = Project(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_project = CRUDProject(Project)