from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    id: str
    user_id: str
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: Optional[str] = None
    sso_subject: Optional[str] = None
    profile: Optional[UserProfileCreate] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    profile: Optional[UserProfileUpdate] = None


class UserInDB(UserBase):
    id: str
    tenant_id: str
    password_hash: Optional[str] = None
    sso_subject: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class User(UserBase):
    id: str
    tenant_id: str
    created_at: datetime
    profile: Optional[UserProfile] = None
    
    class Config:
        from_attributes = True


class UserWithRoles(User):
    roles: List[str] = []
    permissions: List[str] = []


class UserListResponse(BaseModel):
    users: List[User]
    total: int
    page: int
    per_page: int
    pages: int

