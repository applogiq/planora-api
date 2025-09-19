from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str  # story, task, bug
    priority: str
    status: str
    epic_id: Optional[str] = None
    epic_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    story_points: Optional[int] = 0
    business_value: Optional[str] = None
    effort: Optional[str] = None
    labels: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    epic_id: Optional[str] = None
    epic_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    story_points: Optional[int] = None
    business_value: Optional[str] = None
    effort: Optional[str] = None
    labels: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None

class StoryInDB(StoryBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Story(StoryInDB):
    assignee: Optional["User"] = None
    reporter: Optional["User"] = None
    project: Optional["Project"] = None

    model_config = ConfigDict(from_attributes=True)

# Import the related schemas to resolve forward references
from app.features.users.schemas import User
from app.features.projects.schemas import Project
Story.model_rebuild()