from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ContactBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    title: Optional[str] = None

class AddressBase(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None

class CustomerBase(BaseModel):
    name: str
    industry: Optional[str] = None
    contact: ContactBase
    website: Optional[str] = None
    address: Optional[AddressBase] = None
    status: Optional[str] = "Active"
    join_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    total_revenue: Optional[float] = 0.0
    project_ids: Optional[List[str]] = []
    priority: Optional[str] = "Medium"
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    contact: Optional[ContactBase] = None
    website: Optional[str] = None
    address: Optional[AddressBase] = None
    status: Optional[str] = None
    join_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    total_revenue: Optional[float] = None
    project_ids: Optional[List[str]] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

class CustomerFilter(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    min_revenue: Optional[float] = None
    max_revenue: Optional[float] = None
    project_id: Optional[str] = None