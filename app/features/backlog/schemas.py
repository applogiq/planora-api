from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project
    from app.features.epics.schemas import Epic

class BacklogBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str  # User Story, Bug, Epic, Task, etc.
    priority: str  # Low, Medium, High, Critical
    status: str  # Ready, In Progress, Review, Done, etc.
    epic_id: Optional[str] = None
    epic_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    story_points: Optional[int] = None
    business_value: Optional[str] = None  # High, Medium, Low
    effort: Optional[str] = None  # High, Medium, Low
    labels: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None

class BacklogCreate(BacklogBase):
    pass

class BacklogUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    epic_id: Optional[str] = None
    epic_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    story_points: Optional[int] = None
    business_value: Optional[str] = None
    effort: Optional[str] = None
    labels: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None

class BacklogInDB(BacklogBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Backlog(BacklogInDB):
    epic: Optional["Epic"] = None
    project: Optional["Project"] = None
    assignee: Optional["User"] = None
    reporter: Optional["User"] = None

    model_config = ConfigDict(from_attributes=True)

# Import the related schemas to resolve forward references
from app.features.users.schemas import User
from app.features.projects.schemas import Project
from app.features.epics.schemas import Epic
Backlog.model_rebuild()