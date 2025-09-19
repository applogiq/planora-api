from typing import List, Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.backlog.models import Backlog
from app.features.users.models import User
from app.features.projects.models import Project
from app.features.epics.models import Epic
from app.features.backlog.schemas import BacklogCreate, BacklogUpdate
import uuid

class CRUDBacklog(CRUDBase[Backlog, BacklogCreate, BacklogUpdate]):
    def get_by_status(self, db: Session, *, status: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.status == status).all()

    def get_by_type(self, db: Session, *, type: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.type == type).all()

    def get_by_priority(self, db: Session, *, priority: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.priority == priority).all()

    def get_by_assignee(self, db: Session, *, assignee_id: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.assignee_id == assignee_id).all()

    def get_by_reporter(self, db: Session, *, reporter_id: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.reporter_id == reporter_id).all()

    def get_by_project(self, db: Session, *, project_id: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.project_id == project_id).all()

    def get_by_epic(self, db: Session, *, epic_id: str) -> List[Backlog]:
        return db.query(Backlog).filter(Backlog.epic_id == epic_id).all()

    def create(self, db: Session, *, obj_in: BacklogCreate) -> Backlog:
        db_obj = Backlog(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: Any) -> Optional[Backlog]:
        return db.query(Backlog).options(
            joinedload(Backlog.epic),
            joinedload(Backlog.project),
            joinedload(Backlog.assignee),
            joinedload(Backlog.reporter)
        ).filter(Backlog.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Backlog]:
        return db.query(Backlog).options(
            joinedload(Backlog.epic),
            joinedload(Backlog.project),
            joinedload(Backlog.assignee),
            joinedload(Backlog.reporter)
        ).offset(skip).limit(limit).all()

    def get_backlog_items_with_filters(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        search: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        reporter_id: Optional[str] = None,
        project_id: Optional[str] = None,
        epic_id: Optional[str] = None,
        business_value: Optional[str] = None,
        effort: Optional[str] = None,
        label: Optional[str] = None
    ) -> tuple[List[Backlog], int]:
        """
        Get backlog items with advanced filtering, pagination, and sorting
        """
        query = db.query(Backlog).options(
            joinedload(Backlog.epic),
            joinedload(Backlog.project),
            joinedload(Backlog.assignee),
            joinedload(Backlog.reporter)
        )

        # Apply filters
        filters = []

        # Search filter (title and description)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(Backlog.title).contains(search_term),
                func.lower(Backlog.description).contains(search_term)
            ]
            filters.append(or_(*search_filters))

        # Status filter
        if status:
            filters.append(func.lower(Backlog.status) == status.lower())

        # Type filter
        if type:
            filters.append(func.lower(Backlog.type) == type.lower())

        # Priority filter
        if priority:
            filters.append(func.lower(Backlog.priority) == priority.lower())

        # Assignee filter
        if assignee_id:
            filters.append(Backlog.assignee_id == assignee_id)

        # Reporter filter
        if reporter_id:
            filters.append(Backlog.reporter_id == reporter_id)

        # Project filter
        if project_id:
            filters.append(Backlog.project_id == project_id)

        # Epic filter
        if epic_id:
            filters.append(Backlog.epic_id == epic_id)

        # Business value filter
        if business_value:
            filters.append(func.lower(Backlog.business_value) == business_value.lower())

        # Effort filter
        if effort:
            filters.append(func.lower(Backlog.effort) == effort.lower())

        # Label filter
        if label:
            filters.append(Backlog.labels.any(label.lower()))

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
            model_class=Backlog
        )

    def get_backlog_items_by_status(
        self,
        db: Session,
        status: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Backlog], int]:
        """Get backlog items by status with pagination"""
        return self.get_backlog_items_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status
        )

    def get_backlog_items_by_assignee(
        self,
        db: Session,
        assignee_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Backlog], int]:
        """Get backlog items by assignee with pagination"""
        return self.get_backlog_items_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            assignee_id=assignee_id
        )

    def get_backlog_items_by_project(
        self,
        db: Session,
        project_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Backlog], int]:
        """Get backlog items by project with pagination"""
        return self.get_backlog_items_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            project_id=project_id
        )

    def get_backlog_items_by_epic(
        self,
        db: Session,
        epic_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Backlog], int]:
        """Get backlog items by epic with pagination"""
        return self.get_backlog_items_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            epic_id=epic_id
        )

crud_backlog = CRUDBacklog(Backlog)

# Export for backward compatibility
__all__ = ["crud_backlog", "CRUDBacklog"]