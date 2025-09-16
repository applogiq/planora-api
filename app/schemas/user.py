from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

class UserInDB(UserBase):
    id: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass