from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

if TYPE_CHECKING:
    from app.features.users.schemas import User
    from app.features.projects.schemas import Project

class SubtaskSchema(BaseModel):
    task_name: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: str
    due_date: Optional[date] = None

class CommentSchema(BaseModel):
    id: str
    author_id: str
    author_name: str
    content: str
    created_at: datetime

class CommentCreateSchema(BaseModel):
    id: str
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None

class AttachedFileSchema(BaseModel):
    id: str
    filename: str
    file_path: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime

class AttachedFileCreateSchema(BaseModel):
    id: str
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None

class ActivitySchema(BaseModel):
    id: str
    user_id: str
    user_name: str
    action: str
    description: str
    timestamp: datetime

class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None
    story_type: str  # story, task, bug
    priority: str
    status: str
    epic_id: Optional[str] = None
    epic_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    story_points: Optional[int] = 0
    business_value: Optional[str] = None
    effort: Optional[str] = None
    labels: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None

    # New fields for complete task management
    subtasks: Optional[List[SubtaskSchema]] = None
    comments: Optional[List[CommentSchema]] = None
    attached_files: Optional[List[AttachedFileSchema]] = None
    progress: Optional[int] = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tags: Optional[List[str]] = None
    activity: Optional[List[ActivitySchema]] = None

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def validate_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v.date()
        return v

class StoryCreate(StoryBase):
    comments: Optional[List[CommentCreateSchema]] = None
    attached_files: Optional[List[AttachedFileCreateSchema]] = None

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    story_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    epic_id: Optional[str] = None
    epic_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    sprint_id: Optional[str] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    story_points: Optional[int] = None
    business_value: Optional[str] = None
    effort: Optional[str] = None
    labels: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None

    # New fields for complete task management
    subtasks: Optional[List[SubtaskSchema]] = None
    comments: Optional[List[CommentCreateSchema]] = None
    attached_files: Optional[List[AttachedFileCreateSchema]] = None
    progress: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tags: Optional[List[str]] = None
    activity: Optional[List[ActivitySchema]] = None

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def validate_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            return v.date()
        return v

class StoryInDB(StoryBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Story(StoryInDB):
    assignee: Optional["User"] = None
    reporter: Optional["User"] = None
    project: Optional["Project"] = None

    model_config = ConfigDict(from_attributes=True)

# Import the related schemas to resolve forward references
from app.features.users.schemas import User
from app.features.projects.schemas import Project
Story.model_rebuild()