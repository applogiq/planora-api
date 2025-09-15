from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from app.schemas.user import User


class ProjectMemberBase(BaseModel):
    role: str = Field(..., description="Role in project: Owner, PM, Member, Viewer")


class ProjectMemberCreate(ProjectMemberBase):
    user_id: str


class ProjectMemberUpdate(BaseModel):
    role: Optional[str] = None


class ProjectMember(ProjectMemberBase):
    project_id: str
    user_id: str
    joined_at: datetime
    user: Optional[User] = None
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    key: str = Field(..., min_length=2, max_length=10, description="Short project code (e.g., 'MKT')")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="active", description="Project status")
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    owner_user_id: Optional[str] = None  # If not provided, use current user


class ProjectUpdate(BaseModel):
    key: Optional[str] = Field(None, min_length=2, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    owner_user_id: Optional[str] = None


class Project(ProjectBase):
    id: str
    tenant_id: str
    owner_user_id: Optional[str] = None
    created_at: datetime
    owner: Optional[User] = None
    
    class Config:
        from_attributes = True


class ProjectWithMembers(Project):
    members: List[ProjectMember] = []


class ProjectWithStats(Project):
    task_count: int = 0
    active_task_count: int = 0
    completed_task_count: int = 0
    member_count: int = 0


class ProjectListResponse(BaseModel):
    projects: List[ProjectWithStats]
    total: int
    page: int
    per_page: int
    pages: int