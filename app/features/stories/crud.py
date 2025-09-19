from typing import List, Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.stories.models import Story
from app.features.users.models import User
from app.features.projects.models import Project
from app.features.stories.schemas import StoryCreate, StoryUpdate
import uuid

class CRUDStory(CRUDBase[Story, StoryCreate, StoryUpdate]):
    def get_by_status(self, db: Session, *, status: str) -> List[Story]:
        return db.query(Story).filter(Story.status == status).all()

    def get_by_assignee(self, db: Session, *, assignee_id: str) -> List[Story]:
        return db.query(Story).filter(Story.assignee_id == assignee_id).all()

    def get_by_project(self, db: Session, *, project_id: str) -> List[Story]:
        return db.query(Story).filter(Story.project_id == project_id).all()

    def get_by_type(self, db: Session, *, story_type: str) -> List[Story]:
        return db.query(Story).filter(Story.type == story_type).all()

    def create(self, db: Session, *, obj_in: StoryCreate) -> Story:
        db_obj = Story(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: Any) -> Optional[Story]:
        return db.query(Story).options(
            joinedload(Story.assignee),
            joinedload(Story.reporter),
            joinedload(Story.project)
        ).filter(Story.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Story]:
        return db.query(Story).options(
            joinedload(Story.assignee),
            joinedload(Story.reporter),
            joinedload(Story.project)
        ).offset(skip).limit(limit).all()

    def get_stories_with_filters(
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
        story_type: Optional[str] = None,
        assignee_id: Optional[str] = None,
        project_id: Optional[str] = None,
        epic_id: Optional[str] = None,
        label: Optional[str] = None
    ) -> tuple[List[Story], int]:
        """
        Get stories with advanced filtering, pagination, and sorting
        """
        query = db.query(Story).options(
            joinedload(Story.assignee),
            joinedload(Story.reporter),
            joinedload(Story.project)
        )

        # Apply filters
        filters = []

        # Search filter (title and description)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(Story.title).contains(search_term),
                func.lower(Story.description).contains(search_term)
            ]
            filters.append(or_(*search_filters))

        # Status filter
        if status:
            filters.append(func.lower(Story.status) == status.lower())

        # Priority filter
        if priority:
            filters.append(func.lower(Story.priority) == priority.lower())

        # Type filter
        if story_type:
            filters.append(func.lower(Story.type) == story_type.lower())

        # Assignee filter
        if assignee_id:
            filters.append(Story.assignee_id == assignee_id)

        # Project filter
        if project_id:
            filters.append(Story.project_id == project_id)

        # Epic filter
        if epic_id:
            filters.append(Story.epic_id == epic_id)

        # Label filter
        if label:
            filters.append(Story.labels.any(label.lower()))

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
            model_class=Story
        )

    def get_stories_by_status(
        self,
        db: Session,
        status: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Story], int]:
        """Get stories by status with pagination"""
        return self.get_stories_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status
        )

    def get_stories_by_assignee(
        self,
        db: Session,
        assignee_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Story], int]:
        """Get stories by assignee with pagination"""
        return self.get_stories_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            assignee_id=assignee_id
        )

    def get_stories_by_type(
        self,
        db: Session,
        story_type: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Story], int]:
        """Get stories by type with pagination"""
        return self.get_stories_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            story_type=story_type
        )

crud_story = CRUDStory(Story)

# Export for backward compatibility
__all__ = ["crud_story", "CRUDStory"]