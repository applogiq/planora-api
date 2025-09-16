from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.user import User
    from app.schemas.project import Project

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[str] = None
    project_id: Optional[str] = None
    sprint: Optional[str] = None
    labels: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    story_points: Optional[int] = None
    comments_count: int = 0
    attachments_count: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    project_id: Optional[str] = None
    sprint: Optional[str] = None
    labels: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    story_points: Optional[int] = None
    comments_count: Optional[int] = None
    attachments_count: Optional[int] = None

class TaskInDB(TaskBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Task(TaskInDB):
    assignee: Optional["User"] = None
    project: Optional["Project"] = None

    model_config = ConfigDict(from_attributes=True)

# Import the related schemas to resolve forward references
from app.schemas.user import User
from app.schemas.project import Project
Task.model_rebuild()