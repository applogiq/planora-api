from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.features.users.schemas import User

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

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    spent: Optional[float] = None
    customer: Optional[str] = None
    customer_id: Optional[str] = None
    priority: Optional[str] = None
    team_lead_id: Optional[str] = None
    team_members: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Project(ProjectInDB):
    team_lead: Optional["User"] = None

    model_config = ConfigDict(from_attributes=True)

# Import the User schema to resolve forward reference
from app.features.users.schemas import User
Project.model_rebuild()