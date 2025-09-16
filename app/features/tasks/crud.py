from typing import List, Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.tasks.models import Task
from app.features.users.models import User
from app.features.projects.models import Project
from app.features.tasks.schemas import TaskCreate, TaskUpdate
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

    def get(self, db: Session, id: Any) -> Optional[Task]:
        return db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.project)
        ).filter(Task.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        return db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.project)
        ).offset(skip).limit(limit).all()

    def get_tasks_with_filters(
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
        assignee_id: Optional[str] = None,
        project_id: Optional[str] = None,
        sprint: Optional[str] = None,
        label: Optional[str] = None
    ) -> tuple[List[Task], int]:
        """
        Get tasks with advanced filtering, pagination, and sorting
        """
        query = db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.project)
        )

        # Apply filters
        filters = []

        # Search filter (title and description)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(Task.title).contains(search_term),
                func.lower(Task.description).contains(search_term)
            ]
            filters.append(or_(*search_filters))

        # Status filter
        if status:
            filters.append(func.lower(Task.status) == status.lower())

        # Priority filter
        if priority:
            filters.append(func.lower(Task.priority) == priority.lower())

        # Assignee filter
        if assignee_id:
            filters.append(Task.assignee_id == assignee_id)

        # Project filter
        if project_id:
            filters.append(Task.project_id == project_id)

        # Sprint filter
        if sprint:
            filters.append(func.lower(Task.sprint) == sprint.lower())

        # Label filter
        if label:
            filters.append(Task.labels.any(label.lower()))

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
            model_class=Task
        )

    def get_tasks_by_status(
        self,
        db: Session,
        status: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Task], int]:
        """Get tasks by status with pagination"""
        return self.get_tasks_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status
        )

    def get_tasks_by_assignee(
        self,
        db: Session,
        assignee_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Task], int]:
        """Get tasks by assignee with pagination"""
        return self.get_tasks_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            assignee_id=assignee_id
        )

crud_task = CRUDTask(Task)

# Export for backward compatibility
__all__ = ["crud_task", "CRUDTask"]