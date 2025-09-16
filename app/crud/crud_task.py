from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
import uuid

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_by_status(self, db: Session, *, status: str) -> List[Task]:
        return db.query(Task).filter(Task.status == status).all()

    def get_by_assignee(self, db: Session, *, assignee_id: str) -> List[Task]:
        return db.query(Task).filter(Task.assignee_id == assignee_id).all()

    def get_by_project(self, db: Session, *, project_id: str) -> List[Task]:
        return db.query(Task).filter(Task.project_id == project_id).all()

    def get_by_sprint(self, db: Session, *, sprint: str) -> List[Task]:
        return db.query(Task).filter(Task.sprint == sprint).all()

    def create(self, db: Session, *, obj_in: TaskCreate) -> Task:
        db_obj = Task(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_task = CRUDTask(Task)