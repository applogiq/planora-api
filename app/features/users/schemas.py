from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.features.roles.schemas import Role

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role_id: str
    avatar: Optional[str] = None
    is_active: bool = True
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    avatar_url: Optional[str] = Field(None, description="External URL for profile picture")

    @validator('avatar_url')
    def validate_avatar_url(cls, v):
        if v is not None:
            from urllib.parse import urlparse
            parsed = urlparse(v)
            if not parsed.scheme in ['http', 'https']:
                raise ValueError('Avatar URL must start with http:// or https://')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role_id: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = Field(None, description="External URL for profile picture")

    @validator('avatar_url')
    def validate_avatar_url(cls, v):
        if v is not None:
            from urllib.parse import urlparse
            parsed = urlparse(v)
            if not parsed.scheme in ['http', 'https']:
                raise ValueError('Avatar URL must start with http:// or https://')
        return v

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