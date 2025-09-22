from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.epics.models import Epic
from app.features.projects.models import Project
from app.features.users.models import User
from app.features.stories.models import Story
from app.features.epics.schemas import EpicCreate, EpicUpdate, EpicStats
import uuid

class CRUDEpic(CRUDBase[Epic, EpicCreate, EpicUpdate]):
    def create(self, db: Session, *, obj_in: EpicCreate) -> Epic:
        db_obj = Epic(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: Any) -> Optional[Epic]:
        return db.query(Epic).filter(Epic.id == id).first()  # Temporarily disabled joinedload

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Epic]:
        return db.query(Epic).offset(skip).limit(limit).all()  # Temporarily disabled joinedload

    def get_by_project(self, db: Session, *, project_id: str) -> List[Epic]:
        return db.query(Epic).filter(Epic.project_id == project_id).all()

    def get_by_status(self, db: Session, *, status: str) -> List[Epic]:
        return db.query(Epic).filter(Epic.status == status).all()

    def get_by_priority(self, db: Session, *, priority: str) -> List[Epic]:
        return db.query(Epic).filter(Epic.priority == priority).all()

    def get_by_assignee(self, db: Session, *, assignee_id: str) -> List[Epic]:
        return db.query(Epic).filter(Epic.assignee_id == assignee_id).all()

    def get_active_epics(self, db: Session) -> List[Epic]:
        return db.query(Epic).filter(Epic.status.in_(["To Do", "In Progress", "Review"])).all()

    def get_epics_with_filters(
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
        project_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        label: Optional[str] = None
    ) -> tuple[List[Epic], int]:
        """
        Get epics with advanced filtering, pagination, and sorting
        """
        query = db.query(Epic)

        # Apply filters
        filters = []

        # Search filter (title, description, business_value)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(Epic.title).contains(search_term),
                func.lower(Epic.description).contains(search_term),
                func.lower(Epic.business_value).contains(search_term)
            ]
            filters.append(or_(*search_filters))

        # Status filter
        if status:
            filters.append(func.lower(Epic.status) == status.lower())

        # Priority filter
        if priority:
            filters.append(func.lower(Epic.priority) == priority.lower())

        # Project filter
        if project_id:
            filters.append(Epic.project_id == project_id)

        # Assignee filter
        if assignee_id:
            filters.append(Epic.assignee_id == assignee_id)

        # Label filter
        if label:
            filters.append(Epic.labels.any(label.lower()))

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
            model_class=Epic
        )

    def update_epic_metrics(self, db: Session, *, epic_id: str) -> Optional[Epic]:
        """Update epic metrics based on associated stories"""
        epic = self.get(db, id=epic_id)
        if not epic:
            return None

        # Get stories for this epic
        stories = db.query(Story).filter(Story.epic_id == epic_id).all()

        # Calculate metrics
        total_stories = len(stories)
        completed_stories = len([t for t in stories if t.status == 'done'])
        total_story_points = sum([t.story_points or 0 for t in stories])
        completed_story_points = sum([t.story_points or 0 for t in stories if t.status == 'done'])

        # Update epic
        update_data = {
            "total_stories": total_stories,
            "completed_stories": completed_stories,
            "total_story_points": total_story_points,
            "completed_story_points": completed_story_points
        }

        return self.update(db, db_obj=epic, obj_in=update_data)

    def get_epic_stats(self, db: Session) -> EpicStats:
        """Get epic statistics"""
        all_epics = self.get_multi(db, limit=1000)

        total_epics = len(all_epics)
        todo_epics = len([e for e in all_epics if e.status == "To Do"])
        in_progress_epics = len([e for e in all_epics if e.status == "In Progress"])
        review_epics = len([e for e in all_epics if e.status == "Review"])
        done_epics = len([e for e in all_epics if e.status == "Done"])
        cancelled_epics = len([e for e in all_epics if e.status == "Cancelled"])
        high_priority_epics = len([e for e in all_epics if e.priority in ["High", "Critical", "Urgent"]])

        # Calculate totals and averages
        total_story_points = sum([e.total_story_points for e in all_epics])
        completed_story_points = sum([e.completed_story_points for e in all_epics])

        avg_completion_rate = 0.0
        if total_epics > 0:
            completion_rates = []
            for epic in all_epics:
                if epic.total_story_points > 0:
                    completion_rate = (epic.completed_story_points / epic.total_story_points) * 100
                    completion_rates.append(completion_rate)

            if completion_rates:
                avg_completion_rate = sum(completion_rates) / len(completion_rates)

        return EpicStats(
            total_epics=total_epics,
            todo_epics=todo_epics,
            in_progress_epics=in_progress_epics,
            review_epics=review_epics,
            done_epics=done_epics,
            cancelled_epics=cancelled_epics,
            total_story_points=total_story_points,
            completed_story_points=completed_story_points,
            average_completion_rate=round(avg_completion_rate, 2),
            high_priority_epics=high_priority_epics
        )

    def get_project_epics(
        self,
        db: Session,
        project_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Epic], int]:
        """Get epics for a specific project with pagination"""
        return self.get_epics_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            project_id=project_id
        )

    def get_assignee_epics(
        self,
        db: Session,
        assignee_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Epic], int]:
        """Get epics for a specific assignee with pagination"""
        return self.get_epics_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            assignee_id=assignee_id
        )

    def get_epics_by_status(
        self,
        db: Session,
        status: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Epic], int]:
        """Get epics by status with pagination"""
        return self.get_epics_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            status=status
        )

crud_epic = CRUDEpic(Epic)

# Export for backward compatibility
__all__ = ["crud_epic", "CRUDEpic"]