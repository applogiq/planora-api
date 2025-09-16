from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogBase(BaseModel):
    user_id: Optional[str] = None
    user_name: str
    action: str
    resource: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogInDB(AuditLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLog(AuditLogInDB):
    pass