from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Union, TYPE_CHECKING
from datetime import datetime, date

if TYPE_CHECKING:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project

class SprintBase(BaseModel):
    name: str
    status: str  # Planning, Active, Completed, Cancelled
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    goal: Optional[str] = None
    total_points: int = 0
    completed_points: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    velocity: float = 0.0
    project_id: Optional[str] = None
    scrum_master_id: Optional[str] = None
    team_size: int = 0
    burndown_trend: Optional[str] = None  # On Track, Behind, Ahead, At Risk

class SprintCreate(SprintBase):
    name: str = Field(..., description="Sprint name", min_length=1, max_length=255)
    status: str = Field(..., description="Sprint status (Planning, Active, Completed, Cancelled)")
    start_date: Optional[Union[datetime, date, str]] = Field(None, description="Sprint start date (YYYY-MM-DD or ISO datetime)")
    end_date: Optional[Union[datetime, date, str]] = Field(None, description="Sprint end date (YYYY-MM-DD or ISO datetime)")
    goal: Optional[str] = Field(None, description="Sprint goal description")
    project_id: str = Field(..., description="Project ID this sprint belongs to")
    scrum_master_id: Optional[str] = Field(None, description="ID of the scrum master user")
    team_size: int = Field(default=0, description="Number of team members", ge=0)
    burndown_trend: Optional[str] = Field(default="On Track", description="Burndown trend (On Track, Behind, Ahead, At Risk)")

    @field_validator('start_date', 'end_date', mode='before')
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

class SprintUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Sprint name")
    status: Optional[str] = Field(None, description="Sprint status")
    start_date: Optional[Union[datetime, date, str]] = Field(None, description="Sprint start date")
    end_date: Optional[Union[datetime, date, str]] = Field(None, description="Sprint end date")
    goal: Optional[str] = Field(None, description="Sprint goal")
    total_points: Optional[int] = Field(None, description="Total story points", ge=0)
    completed_points: Optional[int] = Field(None, description="Completed story points", ge=0)
    total_tasks: Optional[int] = Field(None, description="Total number of tasks", ge=0)
    completed_tasks: Optional[int] = Field(None, description="Completed number of tasks", ge=0)
    velocity: Optional[float] = Field(None, description="Sprint velocity", ge=0)
    scrum_master_id: Optional[str] = Field(None, description="Scrum master ID")
    team_size: Optional[int] = Field(None, description="Team size", ge=0)
    burndown_trend: Optional[str] = Field(None, description="Burndown trend")

    @field_validator('start_date', 'end_date', mode='before')
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

class SprintInDB(SprintBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Sprint(SprintInDB):
    # Computed fields for API response
    project_name: Optional[str] = None
    scrum_master_name: Optional[str] = None

    # Relationships
    project: Optional["Project"] = None
    scrum_master: Optional["User"] = None

    model_config = ConfigDict(from_attributes=True)

class SprintStats(BaseModel):
    """Sprint statistics and metrics"""
    total_sprints: int = 0
    active_sprints: int = 0
    completed_sprints: int = 0
    planning_sprints: int = 0
    cancelled_sprints: int = 0
    average_velocity: float = 0.0
    average_completion_rate: float = 0.0
    total_story_points: int = 0
    completed_story_points: int = 0

class SprintSummary(BaseModel):
    """Summary view of sprint for lists"""
    id: str
    name: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_points: int = 0
    completed_points: int = 0
    completion_percentage: float = 0.0
    project_id: str
    project_name: Optional[str] = None
    scrum_master_name: Optional[str] = None
    burndown_trend: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Import schemas to resolve forward references
try:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project
    Sprint.model_rebuild()
except ImportError:
    pass  # Handle circular import during initial setup