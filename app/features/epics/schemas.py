from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Union, TYPE_CHECKING
from datetime import datetime, date

if TYPE_CHECKING:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project

class EpicBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str  # Low, Medium, High, Critical, Urgent
    status: str  # To Do, In Progress, Review, Done, Cancelled
    project_id: str
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    total_story_points: int = 0
    completed_story_points: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    labels: Optional[List[str]] = None
    business_value: Optional[str] = None

class EpicCreate(EpicBase):
    title: str = Field(..., description="Epic title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Epic description")
    priority: str = Field(..., description="Epic priority (Low, Medium, High, Critical, Urgent)")
    status: str = Field(..., description="Epic status (To Do, In Progress, Review, Done, Cancelled)")
    project_id: str = Field(..., description="Project ID this epic belongs to")
    assignee_id: Optional[str] = Field(None, description="ID of the assignee user")
    due_date: Optional[Union[datetime, date, str]] = Field(None, description="Epic due date (YYYY-MM-DD or ISO datetime)")
    total_story_points: int = Field(default=0, description="Total story points", ge=0)
    completed_story_points: int = Field(default=0, description="Completed story points", ge=0)
    total_tasks: int = Field(default=0, description="Total number of tasks", ge=0)
    completed_tasks: int = Field(default=0, description="Completed number of tasks", ge=0)
    labels: Optional[List[str]] = Field(default_factory=list, description="Epic labels/tags")
    business_value: Optional[str] = Field(None, description="Business value description")

    @field_validator('due_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Try parsing as date first (YYYY-MM-DD)
                if len(v) == 10 and v.count('-') == 2:
                    parsed_date = datetime.strptime(v, '%Y-%m-%d')
                    return parsed_date
                # Try parsing as ISO datetime
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return v
        return v

class EpicUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Epic title")
    description: Optional[str] = Field(None, description="Epic description")
    priority: Optional[str] = Field(None, description="Epic priority")
    status: Optional[str] = Field(None, description="Epic status")
    assignee_id: Optional[str] = Field(None, description="Assignee ID")
    due_date: Optional[Union[datetime, date, str]] = Field(None, description="Epic due date")
    total_story_points: Optional[int] = Field(None, description="Total story points", ge=0)
    completed_story_points: Optional[int] = Field(None, description="Completed story points", ge=0)
    total_tasks: Optional[int] = Field(None, description="Total number of tasks", ge=0)
    completed_tasks: Optional[int] = Field(None, description="Completed number of tasks", ge=0)
    labels: Optional[List[str]] = Field(None, description="Epic labels")
    business_value: Optional[str] = Field(None, description="Business value")

    @field_validator('due_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Try parsing as date first (YYYY-MM-DD)
                if len(v) == 10 and v.count('-') == 2:
                    parsed_date = datetime.strptime(v, '%Y-%m-%d')
                    return parsed_date
                # Try parsing as ISO datetime
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return v
        return v

class EpicInDB(EpicBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Epic(EpicInDB):
    # Computed fields for API response
    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    completion_percentage: float = 0.0

    # Relationships
    project: Optional["Project"] = None
    assignee: Optional["User"] = None

    model_config = ConfigDict(from_attributes=True)

class EpicStats(BaseModel):
    """Epic statistics and metrics"""
    total_epics: int = 0
    todo_epics: int = 0
    in_progress_epics: int = 0
    review_epics: int = 0
    done_epics: int = 0
    cancelled_epics: int = 0
    total_story_points: int = 0
    completed_story_points: int = 0
    average_completion_rate: float = 0.0
    high_priority_epics: int = 0

class EpicSummary(BaseModel):
    """Summary view of epic for lists"""
    id: str
    title: str
    status: str
    priority: str
    due_date: Optional[datetime] = None
    total_story_points: int = 0
    completed_story_points: int = 0
    completion_percentage: float = 0.0
    project_id: str
    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    labels: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

# Import schemas to resolve forward references
try:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project
    Epic.model_rebuild()
except ImportError:
    pass  # Handle circular import during initial setup