from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.users.crud import crud_user
from app.features.projects.crud import crud_project
from app.features.epics.crud import crud_epic
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.epics.schemas import (
    Epic as EpicSchema,
    EpicCreate,
    EpicUpdate,
    EpicStats,
    EpicSummary
)
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

def populate_epic_names(db: Session, epic):
    """Helper function to populate epic names from foreign keys"""
    if epic.project_id:
        project = crud_project.get(db, id=epic.project_id)
        if project:
            epic.project_name = project.name

    if epic.assignee_id:
        assignee = crud_user.get(db, id=epic.assignee_id)
        if assignee:
            epic.assignee_name = assignee.name

    return epic

@router.get("/", response_model=PaginatedResponse[EpicSchema])
def read_epics(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in title, description, business value"),
    status: Optional[str] = Query(default=None, description="Filter by epic status"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    project_id: Optional[str] = Query(default=None, description="Filter by project ID"),
    assignee_id: Optional[str] = Query(default=None, description="Filter by assignee"),
    label: Optional[str] = Query(default=None, description="Filter by label"),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """
    Get epics with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, title, priority, status, due_date, total_story_points, completed_story_points, created_at

    **Search:** Searches in epic title, description, and business value fields.

    **Filters:**
    - status: Filter by epic status (To Do, In Progress, Review, Done, Cancelled)
    - priority: Filter by priority (Low, Medium, High, Critical, Urgent)
    - project_id: Filter by project ID
    - assignee_id: Filter by assignee user ID
    - label: Filter by specific label
    """
    epics, total = crud_epic.get_epics_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        status=status,
        priority=priority,
        project_id=project_id,
        assignee_id=assignee_id,
        label=label
    )

    # Add computed fields
    for epic in epics:
        populate_epic_names(db, epic)

        # Calculate completion percentage
        if epic.total_story_points > 0:
            epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)
        else:
            epic.completion_percentage = 0.0

    return PaginatedResponse.create(
        items=epics,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=EpicSchema)
def create_epic(
    *,
    request: Request,
    db: Session = Depends(get_db),
    epic_in: EpicCreate,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    """
    Create a new epic with validation.

    **Required fields:**
    - title: Epic title
    - priority: Epic priority (Low, Medium, High, Critical, Urgent)
    - status: Epic status (To Do, In Progress, Review, Done, Cancelled)
    - project_id: ID of the project this epic belongs to

    **Optional fields:**
    - description: Epic description
    - assignee_id: ID of the assignee user
    - due_date: Epic due date (YYYY-MM-DD or ISO datetime)
    - total_story_points: Total story points
    - completed_story_points: Completed story points
    - total_tasks: Total number of tasks
    - completed_tasks: Completed number of tasks
    - labels: Epic labels/tags
    - business_value: Business value description
    """

    # Validate project exists
    project = crud_project.get(db, id=epic_in.project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {epic_in.project_id} not found"
        )

    # Validate assignee exists if provided
    if epic_in.assignee_id:
        assignee = crud_user.get(db, id=epic_in.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=404,
                detail=f"Assignee with ID {epic_in.assignee_id} not found"
            )

    # Validate story points
    if epic_in.completed_story_points > epic_in.total_story_points:
        raise HTTPException(
            status_code=400,
            detail="Completed story points cannot exceed total story points"
        )

    # Validate tasks
    if epic_in.completed_tasks > epic_in.total_tasks:
        raise HTTPException(
            status_code=400,
            detail="Completed tasks cannot exceed total tasks"
        )

    epic = crud_epic.create(db, obj_in=epic_in)

    # Log epic creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Epic",
        details=f"Created new epic: {epic.title} for project {project.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Add computed fields
    epic = crud_epic.get(db, id=epic.id)
    populate_epic_names(db, epic)

    # Calculate completion percentage
    if epic.total_story_points > 0:
        epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epic

@router.put("/{epic_id}", response_model=EpicSchema)
def update_epic(
    *,
    request: Request,
    db: Session = Depends(get_db),
    epic_id: str,
    epic_in: EpicUpdate,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    """
    Update an existing epic with validation.

    **Supported updates:**
    - Basic info: title, description, priority, status
    - Assignment: assignee_id
    - Timing: due_date
    - Metrics: total_story_points, completed_story_points, total_tasks, completed_tasks
    - Organization: labels, business_value
    """
    epic = crud_epic.get(db, id=epic_id)
    if not epic:
        raise HTTPException(
            status_code=404,
            detail="The epic with this id does not exist in the system",
        )

    # Validate assignee exists if provided
    if epic_in.assignee_id:
        assignee = crud_user.get(db, id=epic_in.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=404,
                detail=f"Assignee with ID {epic_in.assignee_id} not found"
            )

    # Validate story points
    total_points = epic_in.total_story_points if epic_in.total_story_points is not None else epic.total_story_points
    completed_points = epic_in.completed_story_points if epic_in.completed_story_points is not None else epic.completed_story_points

    if completed_points > total_points:
        raise HTTPException(
            status_code=400,
            detail="Completed story points cannot exceed total story points"
        )

    # Validate tasks
    total_tasks = epic_in.total_tasks if epic_in.total_tasks is not None else epic.total_tasks
    completed_tasks = epic_in.completed_tasks if epic_in.completed_tasks is not None else epic.completed_tasks

    if completed_tasks > total_tasks:
        raise HTTPException(
            status_code=400,
            detail="Completed tasks cannot exceed total tasks"
        )

    epic = crud_epic.update(db, db_obj=epic, obj_in=epic_in)

    # Log epic update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Epic",
        details=f"Updated epic: {epic.title} (ID: {epic.id})",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Add computed fields
    epic = crud_epic.get(db, id=epic.id)
    populate_epic_names(db, epic)

    # Calculate completion percentage
    if epic.total_story_points > 0:
        epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epic

@router.get("/{epic_id}", response_model=EpicSchema)
def read_epic(
    *,
    db: Session = Depends(get_db),
    epic_id: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get a specific epic by ID"""
    epic = crud_epic.get(db, id=epic_id)
    if not epic:
        raise HTTPException(
            status_code=404,
            detail="The epic with this id does not exist in the system",
        )

    # Add computed fields
    populate_epic_names(db, epic)

    # Calculate completion percentage
    if epic.total_story_points > 0:
        epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epic

@router.delete("/{epic_id}", response_model=EpicSchema)
def delete_epic(
    *,
    request: Request,
    db: Session = Depends(get_db),
    epic_id: str,
    current_user: User = Depends(deps.require_permissions(["project:delete"]))
) -> Any:
    """Delete an epic"""
    epic = crud_epic.get(db, id=epic_id)
    if not epic:
        raise HTTPException(
            status_code=404,
            detail="The epic with this id does not exist in the system",
        )

    epic = crud_epic.remove(db, id=epic_id)

    # Log epic deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Epic",
        details=f"Deleted epic: {epic.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return epic

@router.get("/status/{status}", response_model=List[EpicSchema])
def read_epics_by_status(
    *,
    db: Session = Depends(get_db),
    status: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get epics by status"""
    epics = crud_epic.get_by_status(db, status=status)

    # Add computed fields
    for epic in epics:
        populate_epic_names(db, epic)

        if epic.total_story_points > 0:
            epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epics

@router.get("/project/{project_id}", response_model=PaginatedResponse[EpicSchema])
def read_epics_by_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get epics for a specific project"""
    # Validate project exists
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {project_id} not found"
        )

    epics, total = crud_epic.get_project_epics(
        db=db,
        project_id=project_id,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Add computed fields
    for epic in epics:
        populate_epic_names(db, epic)

        if epic.total_story_points > 0:
            epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return PaginatedResponse.create(
        items=epics,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/assignee/{assignee_id}", response_model=List[EpicSchema])
def read_epics_by_assignee(
    *,
    db: Session = Depends(get_db),
    assignee_id: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get epics assigned to a specific user"""
    epics = crud_epic.get_by_assignee(db, assignee_id=assignee_id)

    # Add computed fields
    for epic in epics:
        populate_epic_names(db, epic)

        if epic.total_story_points > 0:
            epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epics

@router.get("/priority/{priority}", response_model=List[EpicSchema])
def read_epics_by_priority(
    *,
    db: Session = Depends(get_db),
    priority: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get epics by priority"""
    epics = crud_epic.get_by_priority(db, priority=priority)

    # Add computed fields
    for epic in epics:
        populate_epic_names(db, epic)

        if epic.total_story_points > 0:
            epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epics

@router.get("/active/list", response_model=List[EpicSchema])
def read_active_epics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get all active epics (To Do, In Progress, Review)"""
    epics = crud_epic.get_active_epics(db)

    # Add computed fields
    for epic in epics:
        populate_epic_names(db, epic)

        if epic.total_story_points > 0:
            epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epics

@router.post("/{epic_id}/update-metrics", response_model=EpicSchema)
def update_epic_metrics(
    *,
    request: Request,
    db: Session = Depends(get_db),
    epic_id: str,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    """Update epic metrics based on associated tasks"""
    epic = crud_epic.update_epic_metrics(db, epic_id=epic_id)
    if not epic:
        raise HTTPException(
            status_code=404,
            detail="The epic with this id does not exist in the system",
        )

    # Log metric update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Epic",
        details=f"Updated metrics for epic: {epic.title}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Add computed fields
    populate_epic_names(db, epic)

    if epic.total_story_points > 0:
        epic.completion_percentage = round((epic.completed_story_points / epic.total_story_points) * 100, 2)

    return epic

@router.get("/stats/overview", response_model=EpicStats)
def get_epic_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get epic statistics and metrics"""
    return crud_epic.get_epic_stats(db)

@router.get("/statuses/list")
def get_epic_statuses(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get available epic statuses"""
    return {
        "statuses": ["To Do", "In Progress", "Review", "Done", "Cancelled"]
    }

@router.get("/priorities/list")
def get_epic_priorities(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get available epic priorities"""
    return {
        "priorities": ["Low", "Medium", "High", "Critical", "Urgent"]
    }