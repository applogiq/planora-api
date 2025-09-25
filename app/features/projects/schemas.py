from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, TYPE_CHECKING, Union
from datetime import datetime, date

if TYPE_CHECKING:
    from app.features.users.schemas import User

class TeamMemberDetail(BaseModel):
    """Detailed team member information for project responses"""
    id: str
    name: str
    department: Optional[str] = None
    role_id: str
    role_name: Optional[str] = None
    user_profile: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectMembersResponse(BaseModel):
    """Response model for project members endpoint"""
    project_id: str
    project_name: str
    team_lead: Optional[TeamMemberDetail] = None
    team_members: List[TeamMemberDetail] = []

    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str
    progress: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    spent: float = 0.0
    customer: Optional[str] = None
    customer_id: Optional[str] = None
    priority: Optional[str] = None
    team_lead_id: Optional[str] = None
    team_members: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    methodology: Optional[str] = None
    project_type: Optional[str] = None

class ProjectCreate(ProjectBase):
    name: str = Field(..., description="Project name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field(..., description="Project status (Planning, Active, On Hold, Completed, Cancelled)")
    project_type: str = Field(..., description="Type of project (Software Development, Mobile Development, etc.)")
    color: Optional[str] = Field("#6C757D", description="Project color code (hex format)", pattern="^#[0-9A-Fa-f]{6}$")
    team_lead_id: Optional[str] = Field(None, description="ID of the team lead user")
    team_members: Optional[List[str]] = Field(default_factory=list, description="List of team member user IDs")
    customer: Optional[str] = Field(None, description="Customer name")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    start_date: Optional[Union[datetime, date, str]] = Field(None, description="Project start date (YYYY-MM-DD or ISO datetime)")
    end_date: Optional[Union[datetime, date, str]] = Field(None, description="Project end date (YYYY-MM-DD or ISO datetime)")
    priority: Optional[str] = Field("Medium", description="Project priority (Low, Medium, High, Critical, Urgent)")
    methodology: Optional[str] = Field("Scrum", description="Project methodology (Scrum, Kanban, Waterfall)")
    budget: Optional[float] = Field(None, description="Project budget", ge=0)
    tags: Optional[List[str]] = Field(default_factory=list, description="Project tags")

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

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    start_date: Optional[Union[datetime, date, str]] = None
    end_date: Optional[Union[datetime, date, str]] = None
    budget: Optional[float] = None
    spent: Optional[float] = None
    customer: Optional[str] = None
    customer_id: Optional[str] = None
    priority: Optional[str] = None
    team_lead_id: Optional[str] = None
    team_members: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    methodology: Optional[str] = None
    project_type: Optional[str] = None

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

class ProjectInDB(ProjectBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Project(ProjectInDB):
    team_lead_detail: Optional[TeamMemberDetail] = None
    team_members_detail: Optional[List[TeamMemberDetail]] = None

    model_config = ConfigDict(from_attributes=True)

# Import the User schema to resolve forward reference
from app.features.users.schemas import User
Project.model_rebuild()