from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.stories.crud import crud_story
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.tasks.schemas import TaskResponse, TaskCreate, TaskUpdate
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[TaskResponse])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of tasks to return"),
    project_id: Optional[str] = Query(default=None, description="Filter by project ID"),
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    """
    Retrieve tasks (stories with type='task') with optional project filtering
    """
    if project_id:
        tasks = crud_story.get_by_project_and_type(db=db, project_id=project_id, story_type="task", skip=skip, limit=limit)
    else:
        tasks = crud_story.get_by_type(db=db, story_type="task", skip=skip, limit=limit)

    total = len(tasks)  # For simplicity, not implementing proper count query

    return PaginatedResponse.create(
        items=tasks,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )

@router.post("/", response_model=TaskResponse)
def create_task(
    *,
    request: Request,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.require_permissions(["story:write"]))
) -> Any:
    """
    Create new task (creates a story with type='task')
    """
    # Convert task data to story data
    from app.features.stories.schemas import StoryCreate, CommentCreateSchema, AttachedFileCreateSchema

    # Transform comments from task format to story format
    transformed_comments = []
    if task_in.comments:
        for comment in task_in.comments:
            comment_data = comment.dict() if hasattr(comment, 'dict') else comment
            transformed_comment = CommentCreateSchema(
                id=comment_data.get('id', ''),
                author_id=comment_data.get('user_id'),
                author_name=comment_data.get('user_name'),
                content=comment_data.get('text'),
                created_at=comment_data.get('created_at')
            )
            transformed_comments.append(transformed_comment)

    # Transform attachments from task format to story format
    transformed_attachments = []
    if task_in.attachments:
        for attachment in task_in.attachments:
            attachment_data = attachment.dict() if hasattr(attachment, 'dict') else attachment
            transformed_attachment = AttachedFileCreateSchema(
                id=attachment_data.get('id', ''),
                filename=attachment_data.get('filename'),
                file_path=attachment_data.get('url'),  # Map url to file_path
                file_size=attachment_data.get('size'),
                uploaded_by=current_user.id,  # Set current user as uploader
                uploaded_at=attachment_data.get('uploaded_at')
            )
            transformed_attachments.append(transformed_attachment)

    story_data = StoryCreate(
        title=task_in.title,
        description=task_in.description or "",
        type="task",  # Set type as task
        priority=task_in.priority,
        status=task_in.status,
        project_id=task_in.project_id,
        assignee_id=task_in.assignee_id,
        start_date=task_in.start_date,
        end_date=task_in.due_date,  # Map due_date to end_date
        progress=int(task_in.progress),  # Convert float to int
        subtasks=task_in.subtasks,
        comments=transformed_comments,
        attached_files=transformed_attachments,
        tags=task_in.tags,
        activity=[]  # Initialize empty activity
    )

    task = crud_story.create(db=db, obj_in=story_data)

    # Log task creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Task",
        details=f"Created new task: {task.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return task

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: str,
    current_user: User = Depends(deps.require_permissions(["story:read"]))
) -> Any:
    """
    Get task by ID (gets story with type='task')
    """
    task = crud_story.get(db=db, id=task_id)
    if not task or task.type != "task":
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    *,
    request: Request,
    db: Session = Depends(get_db),
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.require_permissions(["story:write"]))
) -> Any:
    """
    Update task (updates story with type='task')
    """
    task = crud_story.get(db=db, id=task_id)
    if not task or task.type != "task":
        raise HTTPException(status_code=404, detail="Task not found")

    # Convert task update data to story update data
    from app.features.stories.schemas import StoryUpdate, CommentCreateSchema, AttachedFileCreateSchema

    story_update_data = {}
    if task_in.title is not None:
        story_update_data["title"] = task_in.title
    if task_in.description is not None:
        story_update_data["description"] = task_in.description
    if task_in.priority is not None:
        story_update_data["priority"] = task_in.priority
    if task_in.status is not None:
        story_update_data["status"] = task_in.status
    if task_in.assignee_id is not None:
        story_update_data["assignee_id"] = task_in.assignee_id
    if task_in.start_date is not None:
        story_update_data["start_date"] = task_in.start_date
    if task_in.due_date is not None:
        story_update_data["end_date"] = task_in.due_date
    if task_in.progress is not None:
        story_update_data["progress"] = int(task_in.progress)
    if task_in.subtasks is not None:
        story_update_data["subtasks"] = task_in.subtasks
    if task_in.comments is not None:
        # Transform comments from task format to story format
        transformed_comments = []
        for comment in task_in.comments:
            comment_data = comment.dict() if hasattr(comment, 'dict') else comment
            transformed_comment = CommentCreateSchema(
                id=comment_data.get('id', ''),
                author_id=comment_data.get('user_id'),
                author_name=comment_data.get('user_name'),
                content=comment_data.get('text'),
                created_at=comment_data.get('created_at')
            )
            transformed_comments.append(transformed_comment)
        story_update_data["comments"] = transformed_comments
    if task_in.attachments is not None:
        # Transform attachments from task format to story format
        transformed_attachments = []
        for attachment in task_in.attachments:
            attachment_data = attachment.dict() if hasattr(attachment, 'dict') else attachment
            transformed_attachment = AttachedFileCreateSchema(
                id=attachment_data.get('id', ''),
                filename=attachment_data.get('filename'),
                file_path=attachment_data.get('url'),  # Map url to file_path
                file_size=attachment_data.get('size'),
                uploaded_by=current_user.id,  # Set current user as uploader
                uploaded_at=attachment_data.get('uploaded_at')
            )
            transformed_attachments.append(transformed_attachment)
        story_update_data["attached_files"] = transformed_attachments
    if task_in.tags is not None:
        story_update_data["tags"] = task_in.tags

    story_update = StoryUpdate(**story_update_data)
    task = crud_story.update(db=db, db_obj=task, obj_in=story_update)

    # Log task update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Task",
        details=f"Updated task: {task.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return task

@router.delete("/{task_id}", response_model=TaskResponse)
def delete_task(
    *,
    request: Request,
    db: Session = Depends(get_db),
    task_id: str,
    current_user: User = Depends(deps.require_permissions(["story:delete"]))
) -> Any:
    """
    Delete task (deletes story with type='task')
    """
    task = crud_story.get(db=db, id=task_id)
    if not task or task.type != "task":
        raise HTTPException(status_code=404, detail="Task not found")

    task = crud_story.remove(db=db, id=task_id)

    # Log task deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Task",
        details=f"Deleted task: {task.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return task