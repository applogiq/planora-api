from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

from app.schemas.user import User
from app.schemas.project import Project


class TaskLinkBase(BaseModel):
    link_type: str = Field(..., description="Link type: blocks, is_blocked_by, relates")


class TaskLinkCreate(TaskLinkBase):
    to_task_id: str


class TaskLink(TaskLinkBase):
    from_task_id: str
    to_task_id: str
    to_task: Optional["Task"] = None
    
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    body_md: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    body_md: Optional[str] = Field(None, min_length=1)


class Comment(CommentBase):
    id: str
    task_id: str
    author_user_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: Optional[User] = None
    
    class Config:
        from_attributes = True


class AttachmentBase(BaseModel):
    original_filename: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None


class Attachment(AttachmentBase):
    id: str
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    uploader_user_id: Optional[str] = None
    object_key: str
    av_status: str = "pending"
    created_at: datetime
    uploader: Optional[User] = None
    
    class Config:
        from_attributes = True


class LabelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color_hex: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class LabelCreate(LabelBase):
    pass


class LabelUpdate(LabelBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color_hex: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class Label(LabelBase):
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


class CustomFieldBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., description="Field type: text, number, select, user, date")
    config_json: Optional[str] = None


class CustomFieldCreate(CustomFieldBase):
    pass


class CustomFieldUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = None
    config_json: Optional[str] = None


class CustomField(CustomFieldBase):
    id: str
    tenant_id: str
    
    class Config:
        from_attributes = True


class TaskCustomFieldValue(BaseModel):
    field_id: str
    value_json: Optional[str] = None
    field: Optional[CustomField] = None
    
    class Config:
        from_attributes = True


class SprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    goal: Optional[str] = None


class SprintCreate(SprintBase):
    project_id: str


class SprintUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    goal: Optional[str] = None
    state: Optional[str] = None


class Sprint(SprintBase):
    id: str
    tenant_id: str
    project_id: str
    state: str = "planned"
    
    class Config:
        from_attributes = True


class BoardColumnBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    wip_limit: Optional[int] = Field(None, ge=0)
    position: int = Field(default=0, ge=0)


class BoardColumnCreate(BoardColumnBase):
    pass


class BoardColumnUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    wip_limit: Optional[int] = Field(None, ge=0)
    position: Optional[int] = Field(None, ge=0)


class BoardColumn(BoardColumnBase):
    id: str
    board_id: str
    
    class Config:
        from_attributes = True


class BoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class BoardCreate(BoardBase):
    project_id: str


class BoardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class Board(BoardBase):
    id: str
    tenant_id: str
    project_id: str
    columns: List[BoardColumn] = []
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description_md: Optional[str] = None
    type: str = Field(default="task", description="Task type: task, bug, epic, subtask")
    status: str = Field(..., description="Task status")
    priority: str = Field(default="medium", description="Priority: low, medium, high, critical")
    story_points: Optional[Decimal] = Field(None, ge=0, le=999.99)
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    project_id: str
    parent_task_id: Optional[str] = None
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    labels: List[str] = []  # Label IDs
    custom_fields: Dict[str, Any] = {}  # Field ID -> Value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description_md: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    sprint_id: Optional[str] = None
    story_points: Optional[Decimal] = Field(None, ge=0, le=999.99)
    due_date: Optional[date] = None
    labels: Optional[List[str]] = None  # Label IDs
    custom_fields: Optional[Dict[str, Any]] = None  # Field ID -> Value


class Task(TaskBase):
    id: str
    tenant_id: str
    project_id: str
    parent_task_id: Optional[str] = None
    sprint_id: Optional[str] = None
    key: str
    assignee_id: Optional[str] = None
    reporter_id: Optional[str] = None
    version: int = 1
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    project: Optional[Project] = None
    parent_task: Optional["Task"] = None
    assignee: Optional[User] = None
    reporter: Optional[User] = None
    sprint: Optional[Sprint] = None
    
    class Config:
        from_attributes = True


class TaskWithDetails(Task):
    subtasks: List[Task] = []
    comments: List[Comment] = []
    attachments: List[Attachment] = []
    labels: List[Label] = []
    custom_field_values: List[TaskCustomFieldValue] = []
    outgoing_links: List[TaskLink] = []
    incoming_links: List[TaskLink] = []


class TaskListResponse(BaseModel):
    tasks: List[Task]
    total: int
    page: int
    per_page: int
    pages: int


class TaskHistoryEntry(BaseModel):
    id: str
    task_id: str
    actor_user_id: Optional[str] = None
    changed_at: datetime
    changes: Optional[str] = None
    actor: Optional[User] = None
    
    class Config:
        from_attributes = True


# Forward reference resolution
TaskLink.model_rebuild()
Task.model_rebuild()