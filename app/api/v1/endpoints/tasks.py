from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_task, crud_audit_log
from app.db.database import get_db
from app.models.user import User
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.schemas.audit_log import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by task status"),
    assignee_id: Optional[str] = Query(None, description="Filter by assignee"),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    sprint: Optional[str] = Query(None, description="Filter by sprint"),
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    if status:
        tasks = crud_task.get_by_status(db, status=status)
    elif assignee_id:
        tasks = crud_task.get_by_assignee(db, assignee_id=assignee_id)
    elif project_id:
        tasks = crud_task.get_by_project(db, project_id=project_id)
    elif sprint:
        tasks = crud_task.get_by_sprint(db, sprint=sprint)
    else:
        tasks = crud_task.get_multi(db, skip=skip, limit=limit)
    return tasks

@router.post("/", response_model=TaskSchema)
def create_task(
    *,
    request: Request,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.require_permissions(["task:write"]))
) -> Any:
    task = crud_task.create(db, obj_in=task_in)

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

@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    *,
    request: Request,
    db: Session = Depends(get_db),
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.require_permissions(["task:write"]))
) -> Any:
    task = crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="The task with this id does not exist in the system",
        )

    old_status = task.status
    task = crud_task.update(db, db_obj=task, obj_in=task_in)

    # Log task update with status change details
    details = f"Updated task: {task.title}"
    if task_in.status and old_status != task_in.status:
        details += f" (Status changed from '{old_status}' to '{task_in.status}')"

    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Task",
        details=details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return task

@router.get("/{task_id}", response_model=TaskSchema)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: str,
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    task = crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="The task with this id does not exist in the system",
        )
    return task

@router.delete("/{task_id}", response_model=TaskSchema)
def delete_task(
    *,
    request: Request,
    db: Session = Depends(get_db),
    task_id: str,
    current_user: User = Depends(deps.require_permissions(["task:delete"]))
) -> Any:
    task = crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="The task with this id does not exist in the system",
        )

    task = crud_task.remove(db, id=task_id)

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

@router.get("/status/{status}", response_model=List[TaskSchema])
def read_tasks_by_status(
    *,
    db: Session = Depends(get_db),
    status: str,
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    tasks = crud_task.get_by_status(db, status=status)
    return tasks

@router.get("/assignee/{assignee_id}", response_model=List[TaskSchema])
def read_tasks_by_assignee(
    *,
    db: Session = Depends(get_db),
    assignee_id: str,
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    tasks = crud_task.get_by_assignee(db, assignee_id=assignee_id)
    return tasks

@router.get("/project/{project_id}", response_model=List[TaskSchema])
def read_tasks_by_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    tasks = crud_task.get_by_project(db, project_id=project_id)
    return tasks

@router.get("/sprint/{sprint}", response_model=List[TaskSchema])
def read_tasks_by_sprint(
    *,
    db: Session = Depends(get_db),
    sprint: str,
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    tasks = crud_task.get_by_sprint(db, sprint=sprint)
    return tasks

@router.get("/board/kanban")
def get_kanban_board(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    if project_id:
        all_tasks = crud_task.get_by_project(db, project_id=project_id)
    else:
        all_tasks = crud_task.get_multi(db, limit=1000)

    board = {
        "backlog": [task for task in all_tasks if task.status == "backlog"],
        "todo": [task for task in all_tasks if task.status == "todo"],
        "in_progress": [task for task in all_tasks if task.status == "in-progress"],
        "review": [task for task in all_tasks if task.status == "review"],
        "done": [task for task in all_tasks if task.status == "done"]
    }

    return board

@router.get("/stats/overview")
def get_task_stats(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    if project_id:
        all_tasks = crud_task.get_by_project(db, project_id=project_id)
    else:
        all_tasks = crud_task.get_multi(db, limit=1000)

    stats = {
        "total_tasks": len(all_tasks),
        "backlog": len([t for t in all_tasks if t.status == "backlog"]),
        "todo": len([t for t in all_tasks if t.status == "todo"]),
        "in_progress": len([t for t in all_tasks if t.status == "in-progress"]),
        "review": len([t for t in all_tasks if t.status == "review"]),
        "done": len([t for t in all_tasks if t.status == "done"]),
        "total_story_points": sum([t.story_points or 0 for t in all_tasks]),
        "completed_story_points": sum([t.story_points or 0 for t in all_tasks if t.status == "done"]),
        "high_priority_tasks": len([t for t in all_tasks if t.priority in ["high", "critical"]]),
        "overdue_tasks": 0  # Would need date comparison logic
    }

    return stats

@router.get("/priorities/list")
def get_task_priorities(
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    return {
        "priorities": ["low", "medium", "high", "critical"]
    }

@router.get("/statuses/list")
def get_task_statuses(
    current_user: User = Depends(deps.require_permissions(["task:read"]))
) -> Any:
    return {
        "statuses": ["backlog", "todo", "in-progress", "review", "done"]
    }