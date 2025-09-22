from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime, date

class TaskCommentSchema(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[datetime] = None

class TaskAttachmentSchema(BaseModel):
    id: str
    filename: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    uploaded_at: Optional[datetime] = None

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    project_id: str
    assignee_id: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: float = 0.0
    tags: Optional[List[str]] = []
    subtasks: Optional[List[Any]] = []
    comments: Optional[List[TaskCommentSchema]] = []
    attachments: Optional[List[TaskAttachmentSchema]] = []
    is_active: bool = True

    @field_validator('start_date', 'due_date', mode='before')
    @classmethod
    def validate_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v.date()
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    project_id: Optional[str] = None
    assignee_id: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress: Optional[float] = None
    tags: Optional[List[str]] = None
    subtasks: Optional[List[Any]] = None
    comments: Optional[List[TaskCommentSchema]] = None
    attachments: Optional[List[TaskAttachmentSchema]] = None
    is_active: Optional[bool] = None

    @field_validator('start_date', 'due_date', mode='before')
    @classmethod
    def validate_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v.date()
        return v

class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True