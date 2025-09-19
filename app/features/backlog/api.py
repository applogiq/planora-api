from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.epics.crud import crud_epic
from app.features.backlog.crud import crud_backlog
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.backlog.schemas import Backlog as BacklogSchema, BacklogCreate, BacklogUpdate
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[BacklogSchema])
def read_backlog_items(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in title and description"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    type: Optional[str] = Query(default=None, description="Filter by type"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    assignee_id: Optional[str] = Query(default=None, description="Filter by assignee"),
    reporter_id: Optional[str] = Query(default=None, description="Filter by reporter"),
    project_id: Optional[str] = Query(default=None, description="Filter by project"),
    epic_id: Optional[str] = Query(default=None, description="Filter by epic"),
    business_value: Optional[str] = Query(default=None, description="Filter by business value"),
    effort: Optional[str] = Query(default=None, description="Filter by effort"),
    label: Optional[str] = Query(default=None, description="Filter by label"),
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    """
    Get backlog items with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, title, type, status, priority, story_points, created_at, updated_at

    **Search:** Searches in backlog item title and description fields.

    **Filters:**
    - status: Filter by status (Ready, In Progress, Review, Done, etc.)
    - type: Filter by type (User Story, Bug, Epic, Task, etc.)
    - priority: Filter by priority (Low, Medium, High, Critical)
    - assignee_id: Filter by assignee user ID
    - reporter_id: Filter by reporter user ID
    - project_id: Filter by project ID
    - epic_id: Filter by epic ID
    - business_value: Filter by business value (High, Medium, Low)
    - effort: Filter by effort (High, Medium, Low)
    - label: Filter by specific label
    """
    backlog_items, total = crud_backlog.get_backlog_items_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        status=status,
        type=type,
        priority=priority,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        project_id=project_id,
        epic_id=epic_id,
        business_value=business_value,
        effort=effort,
        label=label
    )

    return PaginatedResponse.create(
        items=backlog_items,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=BacklogSchema)
def create_backlog_item(
    *,
    request: Request,
    db: Session = Depends(get_db),
    backlog_in: BacklogCreate,
    current_user: User = Depends(deps.require_permissions(["backlog:write"]))
) -> Any:
    backlog_item = crud_backlog.create(db, obj_in=backlog_in)

    # Log backlog item creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Backlog",
        details=f"Created new backlog item: {backlog_item.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return backlog_item

@router.put("/{backlog_id}", response_model=BacklogSchema)
def update_backlog_item(
    *,
    request: Request,
    db: Session = Depends(get_db),
    backlog_id: str,
    backlog_in: BacklogUpdate,
    current_user: User = Depends(deps.require_permissions(["backlog:write"]))
) -> Any:
    backlog_item = crud_backlog.get(db, id=backlog_id)
    if not backlog_item:
        raise HTTPException(
            status_code=404,
            detail="The backlog item with this id does not exist in the system",
        )

    old_status = backlog_item.status
    backlog_item = crud_backlog.update(db, db_obj=backlog_item, obj_in=backlog_in)

    # Log backlog item update with status change details
    details = f"Updated backlog item: {backlog_item.title}"
    if backlog_in.status and old_status != backlog_in.status:
        details += f" (Status changed from '{old_status}' to '{backlog_in.status}')"

    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Backlog",
        details=details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return backlog_item

@router.get("/{backlog_id}", response_model=BacklogSchema)
def read_backlog_item(
    *,
    db: Session = Depends(get_db),
    backlog_id: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_item = crud_backlog.get(db, id=backlog_id)
    if not backlog_item:
        raise HTTPException(
            status_code=404,
            detail="The backlog item with this id does not exist in the system",
        )
    return backlog_item

@router.delete("/{backlog_id}", response_model=BacklogSchema)
def delete_backlog_item(
    *,
    request: Request,
    db: Session = Depends(get_db),
    backlog_id: str,
    current_user: User = Depends(deps.require_permissions(["backlog:delete"]))
) -> Any:
    backlog_item = crud_backlog.get(db, id=backlog_id)
    if not backlog_item:
        raise HTTPException(
            status_code=404,
            detail="The backlog item with this id does not exist in the system",
        )

    backlog_item = crud_backlog.remove(db, id=backlog_id)

    # Log backlog item deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Backlog",
        details=f"Deleted backlog item: {backlog_item.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return backlog_item

@router.get("/status/{status}", response_model=List[BacklogSchema])
def read_backlog_items_by_status(
    *,
    db: Session = Depends(get_db),
    status: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_status(db, status=status)
    return backlog_items

@router.get("/type/{type}", response_model=List[BacklogSchema])
def read_backlog_items_by_type(
    *,
    db: Session = Depends(get_db),
    type: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_type(db, type=type)
    return backlog_items

@router.get("/priority/{priority}", response_model=List[BacklogSchema])
def read_backlog_items_by_priority(
    *,
    db: Session = Depends(get_db),
    priority: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_priority(db, priority=priority)
    return backlog_items

@router.get("/assignee/{assignee_id}", response_model=List[BacklogSchema])
def read_backlog_items_by_assignee(
    *,
    db: Session = Depends(get_db),
    assignee_id: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_assignee(db, assignee_id=assignee_id)
    return backlog_items

@router.get("/reporter/{reporter_id}", response_model=List[BacklogSchema])
def read_backlog_items_by_reporter(
    *,
    db: Session = Depends(get_db),
    reporter_id: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_reporter(db, reporter_id=reporter_id)
    return backlog_items

@router.get("/project/{project_id}", response_model=List[BacklogSchema])
def read_backlog_items_by_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_project(db, project_id=project_id)
    return backlog_items

@router.get("/epic/{epic_id}", response_model=List[BacklogSchema])
def read_backlog_items_by_epic(
    *,
    db: Session = Depends(get_db),
    epic_id: str,
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    backlog_items = crud_backlog.get_by_epic(db, epic_id=epic_id)
    return backlog_items

@router.get("/board/kanban")
def get_backlog_kanban_board(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    epic_id: Optional[str] = Query(None, description="Filter by epic"),
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    if project_id:
        all_items = crud_backlog.get_by_project(db, project_id=project_id)
    elif epic_id:
        all_items = crud_backlog.get_by_epic(db, epic_id=epic_id)
    else:
        all_items = crud_backlog.get_multi(db, limit=1000)

    board = {
        "ready": [item for item in all_items if item.status.lower() == "ready"],
        "in_progress": [item for item in all_items if item.status.lower() == "in progress"],
        "review": [item for item in all_items if item.status.lower() == "review"],
        "done": [item for item in all_items if item.status.lower() == "done"]
    }

    return board

@router.get("/stats/overview")
def get_backlog_stats(
    db: Session = Depends(get_db),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    epic_id: Optional[str] = Query(None, description="Filter by epic"),
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    if project_id:
        all_items = crud_backlog.get_by_project(db, project_id=project_id)
    elif epic_id:
        all_items = crud_backlog.get_by_epic(db, epic_id=epic_id)
    else:
        all_items = crud_backlog.get_multi(db, limit=1000)

    stats = {
        "total_items": len(all_items),
        "ready": len([i for i in all_items if i.status.lower() == "ready"]),
        "in_progress": len([i for i in all_items if i.status.lower() == "in progress"]),
        "review": len([i for i in all_items if i.status.lower() == "review"]),
        "done": len([i for i in all_items if i.status.lower() == "done"]),
        "total_story_points": sum([i.story_points or 0 for i in all_items]),
        "completed_story_points": sum([i.story_points or 0 for i in all_items if i.status.lower() == "done"]),
        "high_priority_items": len([i for i in all_items if i.priority.lower() in ["high", "critical"]]),
        "user_stories": len([i for i in all_items if i.type.lower() == "user story"]),
        "bugs": len([i for i in all_items if i.type.lower() == "bug"]),
        "epics": len([i for i in all_items if i.type.lower() == "epic"]),
        "tasks": len([i for i in all_items if i.type.lower() == "task"]),
        "high_business_value": len([i for i in all_items if i.business_value and i.business_value.lower() == "high"])
    }

    return stats

@router.get("/types/list")
def get_backlog_types(
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    return {
        "types": ["User Story", "Bug", "Epic", "Task", "Feature", "Enhancement", "Spike"]
    }

@router.get("/priorities/list")
def get_backlog_priorities(
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    return {
        "priorities": ["Low", "Medium", "High", "Critical"]
    }

@router.get("/statuses/list")
def get_backlog_statuses(
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    return {
        "statuses": ["Ready", "In Progress", "Review", "Done", "Blocked", "On Hold"]
    }

@router.get("/business-values/list")
def get_business_values(
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    return {
        "business_values": ["High", "Medium", "Low"]
    }

@router.get("/efforts/list")
def get_effort_levels(
    current_user: User = Depends(deps.require_permissions(["backlog:read"]))
) -> Any:
    return {
        "efforts": ["High", "Medium", "Low"]
    }