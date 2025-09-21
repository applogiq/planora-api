from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.features.roles.schemas import Role

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role_id: str
    user_profile: Optional[str] = None
    is_active: bool = True
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role_id: Optional[str] = None
    user_profile: Optional[str] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    role: Optional["Role"] = None

    model_config = ConfigDict(from_attributes=True)

# Import the Role schema to resolve the forward reference
from app.features.roles.schemas import Role
User.model_rebuild()