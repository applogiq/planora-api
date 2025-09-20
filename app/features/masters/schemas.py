from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectMethodologyBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class ProjectMethodologyResponse(ProjectMethodologyBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class ProjectTypeResponse(ProjectTypeBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectStatusBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class ProjectStatusResponse(ProjectStatusBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PriorityBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    level: int
    is_active: bool = True
    sort_order: int = 0

class PriorityResponse(PriorityBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class DepartmentResponse(DepartmentBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectMastersResponse(BaseModel):
    methodologies: List[ProjectMethodologyResponse]
    types: List[ProjectTypeResponse]
    statuses: List[ProjectStatusResponse]
    priorities: List[PriorityResponse]