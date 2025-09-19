from typing import List, Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.core.pagination import paginate_query
from app.shared.crud import CRUDBase
from app.features.sprints.models import Sprint
from app.features.projects.models import Project
from app.features.users.models import User
from app.features.tasks.models import Task
from app.features.sprints.schemas import SprintCreate, SprintUpdate, SprintStats
import uuid

class CRUDSprint(CRUDBase[Sprint, SprintCreate, SprintUpdate]):
    def create(self, db: Session, *, obj_in: SprintCreate) -> Sprint:
        db_obj = Sprint(
            id=str(uuid.uuid4()),
            **obj_in.dict()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: Any) -> Optional[Sprint]:
        return db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        ).filter(Sprint.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Sprint]:
        return db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        ).offset(skip).limit(limit).all()

    def get_by_project(self, db: Session, *, project_id: str) -> List[Sprint]:
        return db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        ).filter(Sprint.project_id == project_id).all()

    def get_by_status(self, db: Session, *, status: str) -> List[Sprint]:
        return db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        ).filter(Sprint.status == status).all()

    def get_active_sprints(self, db: Session) -> List[Sprint]:
        return db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        ).filter(Sprint.status == "Active").all()

    def get_by_scrum_master(self, db: Session, *, scrum_master_id: str) -> List[Sprint]:
        return db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        ).filter(Sprint.scrum_master_id == scrum_master_id).all()

    def get_sprints_with_filters(
        self,
        db: Session,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        search: Optional[str] = None,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
        scrum_master_id: Optional[str] = None,
        burndown_trend: Optional[str] = None
    ) -> tuple[List[Sprint], int]:
        """
        Get sprints with advanced filtering, pagination, and sorting
        """
        query = db.query(Sprint).options(
            joinedload(Sprint.project),
            joinedload(Sprint.scrum_master)
        )

        # Apply filters
        filters = []

        # Search filter (name, goal)
        if search:
            search_term = f"%{search.lower()}%"
            search_filters = [
                func.lower(Sprint.name).contains(search_term),
                func.lower(Sprint.goal).contains(search_term)
            ]
            filters.append(or_(*search_filters))

        # Status filter
        if status:
            filters.append(func.lower(Sprint.status) == status.lower())

        # Project filter
        if project_id:
            filters.append(Sprint.project_id == project_id)

        # Scrum master filter
        if scrum_master_id:
            filters.append(Sprint.scrum_master_id == scrum_master_id)

        # Burndown trend filter
        if burndown_trend:
            filters.append(func.lower(Sprint.burndown_trend) == burndown_trend.lower())

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
            model_class=Sprint
        )

    def update_sprint_metrics(self, db: Session, *, sprint_id: str) -> Optional[Sprint]:
        """Update sprint metrics based on associated tasks"""
        sprint = self.get(db, id=sprint_id)
        if not sprint:
            return None

        # Get tasks for this sprint
        tasks = db.query(Task).filter(Task.sprint_id == sprint_id).all()

        # Calculate metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'done'])
        total_points = sum([t.story_points or 0 for t in tasks])
        completed_points = sum([t.story_points or 0 for t in tasks if t.status == 'done'])

        # Calculate velocity (completed points per day if sprint is active)
        velocity = 0.0
        if sprint.start_date and sprint.status == "Active":
            from datetime import datetime
            days_elapsed = (datetime.now() - sprint.start_date).days
            if days_elapsed > 0:
                velocity = completed_points / days_elapsed

        # Update sprint
        update_data = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "total_points": total_points,
            "completed_points": completed_points,
            "velocity": velocity
        }

        return self.update(db, db_obj=sprint, obj_in=update_data)

    def get_sprint_stats(self, db: Session) -> SprintStats:
        """Get sprint statistics"""
        all_sprints = self.get_multi(db, limit=1000)

        total_sprints = len(all_sprints)
        active_sprints = len([s for s in all_sprints if s.status == "Active"])
        completed_sprints = len([s for s in all_sprints if s.status == "Completed"])
        planning_sprints = len([s for s in all_sprints if s.status == "Planning"])
        cancelled_sprints = len([s for s in all_sprints if s.status == "Cancelled"])

        # Calculate averages
        avg_velocity = 0.0
        avg_completion_rate = 0.0
        total_story_points = 0
        completed_story_points = 0

        if total_sprints > 0:
            velocities = [s.velocity for s in all_sprints if s.velocity > 0]
            if velocities:
                avg_velocity = sum(velocities) / len(velocities)

            completion_rates = []
            for sprint in all_sprints:
                if sprint.total_points > 0:
                    completion_rate = (sprint.completed_points / sprint.total_points) * 100
                    completion_rates.append(completion_rate)
                total_story_points += sprint.total_points
                completed_story_points += sprint.completed_points

            if completion_rates:
                avg_completion_rate = sum(completion_rates) / len(completion_rates)

        return SprintStats(
            total_sprints=total_sprints,
            active_sprints=active_sprints,
            completed_sprints=completed_sprints,
            planning_sprints=planning_sprints,
            cancelled_sprints=cancelled_sprints,
            average_velocity=round(avg_velocity, 2),
            average_completion_rate=round(avg_completion_rate, 2),
            total_story_points=total_story_points,
            completed_story_points=completed_story_points
        )

    def get_project_sprints(
        self,
        db: Session,
        project_id: str,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Sprint], int]:
        """Get sprints for a specific project with pagination"""
        return self.get_sprints_with_filters(
            db=db,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            project_id=project_id
        )

crud_sprint = CRUDSprint(Sprint)

# Export for backward compatibility
__all__ = ["crud_sprint", "CRUDSprint"]