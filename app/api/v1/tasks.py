from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_, desc
import uuid
import json

from app.core.auth import (
    get_current_active_user, ProjectPermissionChecker,
    require_task_create, require_task_update, require_task_delete
)
from app.db.base import get_db
from app.models import (
    User, Project, Task, Comment, Attachment, Label, TaskLabel,
    CustomField, TaskCustomField, TaskHistory, Sprint, TaskLink
)
from app.schemas.task import (
    Task as TaskSchema, TaskCreate, TaskUpdate, TaskWithDetails,
    TaskListResponse, Comment as CommentSchema, CommentCreate, CommentUpdate,
    Attachment as AttachmentSchema, Label as LabelSchema, LabelCreate, LabelUpdate,
    CustomField as CustomFieldSchema, CustomFieldCreate, CustomFieldUpdate,
    TaskHistoryEntry, TaskLink as TaskLinkSchema, TaskLinkCreate
)

router = APIRouter()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    project_id: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    sprint_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    label_ids: Optional[List[str]] = Query(None),
    sort_by: str = Query("updated_at", description="Sort by: created_at, updated_at, priority, due_date"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List tasks with filtering and pagination"""
    
    query = db.query(Task).filter(Task.tenant_id == current_user.tenant_id)
    
    # Apply filters
    if project_id:
        # Check project access
        project_access = db.query(Project).join(
            Project.members
        ).filter(
            and_(
                Project.id == project_id,
                Project.tenant_id == current_user.tenant_id,
                Project.members.any(user_id=current_user.id)
            )
        ).first()
        
        if not project_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to this project"
            )
        
        query = query.filter(Task.project_id == project_id)
    else:
        # Only show tasks from projects user has access to
        from app.models import ProjectMember
        accessible_projects = db.query(Project.id).join(ProjectMember).filter(
            and_(
                Project.tenant_id == current_user.tenant_id,
                ProjectMember.user_id == current_user.id
            )
        ).subquery()
        query = query.filter(Task.project_id.in_(accessible_projects))
    
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    
    if sprint_id:
        query = query.filter(Task.sprint_id == sprint_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    if type:
        query = query.filter(Task.type == type)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if search:
        query = query.filter(
            or_(
                Task.title.ilike(f"%{search}%"),
                Task.key.ilike(f"%{search}%"),
                Task.description_md.ilike(f"%{search}%")
            )
        )
    
    if label_ids:
        query = query.join(TaskLabel).filter(TaskLabel.label_id.in_(label_ids))
    
    # Apply sorting
    if hasattr(Task, sort_by):
        order_col = getattr(Task, sort_by)
        if sort_order == "desc":
            order_col = desc(order_col)
        query = query.order_by(order_col)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    tasks = query.offset(offset).limit(per_page).options(
        joinedload(Task.project),
        joinedload(Task.assignee),
        joinedload(Task.reporter),
        joinedload(Task.sprint)
    ).all()
    
    pages = (total + per_page - 1) // per_page
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.post("", response_model=TaskSchema)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_task_create),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new task"""
    
    # Verify project access
    project = db.query(Project).join(
        Project.members
    ).filter(
        and_(
            Project.id == task_data.project_id,
            Project.tenant_id == current_user.tenant_id,
            Project.members.any(user_id=current_user.id)
        )
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this project"
        )
    
    # Generate task key
    task_count = db.query(func.count(Task.id)).filter(
        Task.project_id == task_data.project_id
    ).scalar() or 0
    task_key = f"{project.key}-{task_count + 1}"
    
    # Verify parent task exists (if provided)
    if task_data.parent_task_id:
        parent_task = db.query(Task).filter(
            and_(
                Task.id == task_data.parent_task_id,
                Task.project_id == task_data.project_id
            )
        ).first()
        if not parent_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent task not found"
            )
    
    # Verify assignee exists (if provided)
    if task_data.assignee_id:
        assignee = db.query(User).filter(
            and_(
                User.id == task_data.assignee_id,
                User.tenant_id == current_user.tenant_id,
                User.is_active == True
            )
        ).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee not found"
            )
    
    # Create task
    task_dict = task_data.model_dump(exclude={'labels', 'custom_fields'})
    task = Task(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        key=task_key,
        reporter_id=current_user.id,
        **task_dict
    )
    
    db.add(task)
    db.flush()
    
    # Add labels
    if task_data.labels:
        for label_id in task_data.labels:
            task_label = TaskLabel(task_id=task.id, label_id=label_id)
            db.add(task_label)
    
    # Add custom field values
    if task_data.custom_fields:
        for field_id, value in task_data.custom_fields.items():
            custom_field_value = TaskCustomField(
                task_id=task.id,
                field_id=field_id,
                value_json=json.dumps(value) if value is not None else None
            )
            db.add(custom_field_value)
    
    # Create history entry
    history = TaskHistory(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        task_id=task.id,
        actor_user_id=current_user.id,
        changes=json.dumps({"action": "created", "data": task_dict})
    )
    db.add(history)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.get("/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get task details"""
    
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id
        )
    ).options(
        joinedload(Task.project),
        joinedload(Task.assignee),
        joinedload(Task.reporter),
        joinedload(Task.sprint),
        joinedload(Task.parent_task),
        joinedload(Task.subtasks),
        joinedload(Task.comments).joinedload(Comment.author),
        joinedload(Task.attachments).joinedload(Attachment.uploader),
        joinedload(Task.task_labels).joinedload(TaskLabel.label),
        joinedload(Task.custom_field_values).joinedload(TaskCustomField.field),
        joinedload(Task.outgoing_links),
        joinedload(Task.incoming_links)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check project access
    from app.models import ProjectMember
    project_access = db.query(ProjectMember).filter(
        and_(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id
        )
    ).first()
    
    if not project_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this task"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(require_task_update),
    db: Session = Depends(get_db)
) -> Any:
    """Update task"""
    
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check project access
    from app.models import ProjectMember
    project_access = db.query(ProjectMember).filter(
        and_(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id
        )
    ).first()
    
    if not project_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this task"
        )
    
    # Store original values for history
    original_values = {
        field: getattr(task, field) for field in task_data.model_dump(exclude_unset=True).keys()
        if hasattr(task, field)
    }
    
    # Update task (with optimistic concurrency control)
    update_data = task_data.model_dump(exclude_unset=True, exclude={'labels', 'custom_fields'})
    
    if update_data:
        # Increment version for OCC
        current_version = task.version
        
        for field, value in update_data.items():
            setattr(task, field, value)
        task.version = current_version + 1
        
        # Check if update succeeded (OCC)
        rows_updated = db.query(Task).filter(
            and_(Task.id == task_id, Task.version == current_version)
        ).update({**update_data, 'version': current_version + 1})
        
        if rows_updated == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task was modified by another user. Please refresh and try again."
            )
    
    # Update labels
    if task_data.labels is not None:
        # Remove existing labels
        db.query(TaskLabel).filter(TaskLabel.task_id == task_id).delete()
        
        # Add new labels
        for label_id in task_data.labels:
            task_label = TaskLabel(task_id=task_id, label_id=label_id)
            db.add(task_label)
    
    # Update custom fields
    if task_data.custom_fields is not None:
        # Remove existing custom field values
        db.query(TaskCustomField).filter(TaskCustomField.task_id == task_id).delete()
        
        # Add new custom field values
        for field_id, value in task_data.custom_fields.items():
            custom_field_value = TaskCustomField(
                task_id=task_id,
                field_id=field_id,
                value_json=json.dumps(value) if value is not None else None
            )
            db.add(custom_field_value)
    
    # Create history entry
    changes = {
        "action": "updated",
        "changes": {
            field: {"from": original_values.get(field), "to": value}
            for field, value in update_data.items()
        }
    }
    
    history = TaskHistory(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        task_id=task_id,
        actor_user_id=current_user.id,
        changes=json.dumps(changes)
    )
    db.add(history)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(require_task_delete),
    db: Session = Depends(get_db)
) -> Any:
    """Delete task"""
    
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check project access
    from app.models import ProjectMember
    project_access = db.query(ProjectMember).filter(
        and_(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id
        )
    ).first()
    
    if not project_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this task"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


# Comments endpoints
@router.get("/{task_id}/comments", response_model=List[CommentSchema])
async def list_task_comments(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List task comments"""
    
    # Verify task access
    task = await get_task(task_id, current_user, db)
    
    comments = db.query(Comment).filter(
        Comment.task_id == task_id
    ).options(joinedload(Comment.author)).order_by(Comment.created_at).all()
    
    return comments


@router.post("/{task_id}/comments", response_model=CommentSchema)
async def create_comment(
    task_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a comment on a task"""
    
    # Verify task access
    task = await get_task(task_id, current_user, db)
    
    comment = Comment(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        task_id=task_id,
        author_user_id=current_user.id,
        body_md=comment_data.body_md
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@router.put("/{task_id}/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
    task_id: str,
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a comment"""
    
    comment = db.query(Comment).filter(
        and_(
            Comment.id == comment_id,
            Comment.task_id == task_id,
            Comment.author_user_id == current_user.id
        )
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or no permission to edit"
        )
    
    if comment_data.body_md:
        comment.body_md = comment_data.body_md
        comment.updated_at = func.now()
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/{task_id}/comments/{comment_id}")
async def delete_comment(
    task_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a comment"""
    
    comment = db.query(Comment).filter(
        and_(
            Comment.id == comment_id,
            Comment.task_id == task_id,
            Comment.author_user_id == current_user.id
        )
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or no permission to delete"
        )
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}


# Task history endpoint
@router.get("/{task_id}/history", response_model=List[TaskHistoryEntry])
async def get_task_history(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get task history"""
    
    # Verify task access
    task = await get_task(task_id, current_user, db)
    
    history = db.query(TaskHistory).filter(
        TaskHistory.task_id == task_id
    ).options(joinedload(TaskHistory.actor)).order_by(
        desc(TaskHistory.changed_at)
    ).all()
    
    return history


# Task links endpoints
@router.get("/{task_id}/links", response_model=List[TaskLinkSchema])
async def list_task_links(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List task links"""
    
    # Verify task access
    task = await get_task(task_id, current_user, db)
    
    outgoing_links = db.query(TaskLink).filter(
        TaskLink.from_task_id == task_id
    ).options(joinedload(TaskLink.to_task)).all()
    
    incoming_links = db.query(TaskLink).filter(
        TaskLink.to_task_id == task_id
    ).options(joinedload(TaskLink.from_task)).all()
    
    return outgoing_links + incoming_links


@router.post("/{task_id}/links", response_model=TaskLinkSchema)
async def create_task_link(
    task_id: str,
    link_data: TaskLinkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a task link"""
    
    # Verify both tasks exist and user has access
    from_task = await get_task(task_id, current_user, db)
    to_task = await get_task(link_data.to_task_id, current_user, db)
    
    # Check if link already exists
    existing_link = db.query(TaskLink).filter(
        and_(
            TaskLink.from_task_id == task_id,
            TaskLink.to_task_id == link_data.to_task_id,
            TaskLink.link_type == link_data.link_type
        )
    ).first()
    
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link already exists"
        )
    
    task_link = TaskLink(
        from_task_id=task_id,
        to_task_id=link_data.to_task_id,
        link_type=link_data.link_type
    )
    
    db.add(task_link)
    db.commit()
    db.refresh(task_link)
    
    return task_link


@router.delete("/{task_id}/links/{to_task_id}/{link_type}")
async def delete_task_link(
    task_id: str,
    to_task_id: str,
    link_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a task link"""
    
    task_link = db.query(TaskLink).filter(
        and_(
            TaskLink.from_task_id == task_id,
            TaskLink.to_task_id == to_task_id,
            TaskLink.link_type == link_type
        )
    ).first()
    
    if not task_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task link not found"
        )
    
    db.delete(task_link)
    db.commit()
    
    return {"message": "Task link deleted successfully"}