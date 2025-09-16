from typing import List, Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.projects.models import Project
from app.features.users.models import User
from app.features.projects.schemas import ProjectCreate, ProjectUpdate
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

    def get(self, db: Session, id: Any) -> Optional[Project]:
        return db.query(Project).options(joinedload(Project.team_lead)).filter(Project.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        return db.query(Project).options(joinedload(Project.team_lead)).offset(skip).limit(limit).all()

    def get_projects_with_filters(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        team_lead_id: Optional[str] = None,
        customer: Optional[str] = None,
        tag: Optional[str] = None
    ) -> tuple[List[Project], int]:
        """
        Get projects with advanced filtering, pagination, and sorting
        """
        query = db.query(Project).options(joinedload(Project.team_lead))

        # Apply filters
        filters = []

        # Search filter (name, description, customer)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(Project.name).contains(search_term),
                func.lower(Project.description).contains(search_term),
                func.lower(Project.customer).contains(search_term)
            ]
            filters.append(or_(*search_filters))

        # Status filter
        if status:
            filters.append(func.lower(Project.status) == status.lower())

        # Priority filter
        if priority:
            filters.append(func.lower(Project.priority) == priority.lower())

        # Team lead filter
        if team_lead_id:
            filters.append(Project.team_lead_id == team_lead_id)

        # Customer filter
        if customer:
            filters.append(func.lower(Project.customer).contains(customer.lower()))

        # Tag filter
        if tag:
            filters.append(Project.tags.any(tag.lower()))

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Apply pagination and sorting
        return paginate_query(
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            model_class=Project
        )

    def get_projects_by_status(
        self,
        db: Session,
        status: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Project], int]:
        """Get projects by status with pagination"""
        return self.get_projects_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status
        )

crud_project = CRUDProject(Project)

# Export for backward compatibility
__all__ = ["crud_project", "CRUDProject"]