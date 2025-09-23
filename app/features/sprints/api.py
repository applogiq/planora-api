from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.users.crud import crud_user
from app.features.projects.crud import crud_project
from app.features.sprints.crud import crud_sprint
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.sprints.schemas import (
    Sprint as SprintSchema,
    SprintCreate,
    SprintUpdate,
    SprintStats,
    SprintSummary
)
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[SprintSchema])
def read_sprints(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in name, goal"),
    status: Optional[str] = Query(default=None, description="Filter by sprint status"),
    project_id: Optional[str] = Query(default=None, description="Filter by project ID"),
    scrum_master_id: Optional[str] = Query(default=None, description="Filter by scrum master"),
    burndown_trend: Optional[str] = Query(default=None, description="Filter by burndown trend"),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """
    Get sprints with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, name, status, start_date, end_date, total_points, completed_points, velocity, created_at

    **Search:** Searches in sprint name and goal fields.

    **Filters:**
    - status: Filter by sprint status (Planning, Active, Completed, Cancelled)
    - project_id: Filter by project ID
    - scrum_master_id: Filter by scrum master user ID
    - burndown_trend: Filter by burndown trend (On Track, Behind, Ahead, At Risk)
    """
    sprints, total = crud_sprint.get_sprints_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        status=status,
        project_id=project_id,
        scrum_master_id=scrum_master_id,
        burndown_trend=burndown_trend
    )

    # Add computed fields
    for sprint in sprints:
        if hasattr(sprint, 'project') and sprint.project:
            sprint.project_name = sprint.project.name
        elif sprint.project_id:
            # Get project name directly if relationship is not available
            project = crud_project.get(db, id=sprint.project_id)
            if project:
                sprint.project_name = project.name

        if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
            sprint.scrum_master_name = sprint.scrum_master.name
        elif sprint.scrum_master_id:
            # Get scrum master name directly if relationship is not available
            scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
            if scrum_master:
                sprint.scrum_master_name = scrum_master.name

    return PaginatedResponse.create(
        items=sprints,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=SprintSchema)
def create_sprint(
    *,
    request: Request,
    db: Session = Depends(get_db),
    sprint_in: SprintCreate,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    """
    Create a new sprint with validation.

    **Required fields:**
    - name: Sprint name
    - status: Sprint status (Planning, Active, Completed, Cancelled)
    - project_id: ID of the project this sprint belongs to

    **Optional fields:**
    - start_date: Sprint start date (YYYY-MM-DD or ISO datetime)
    - end_date: Sprint end date (YYYY-MM-DD or ISO datetime)
    - goal: Sprint goal description
    - scrum_master_id: ID of the scrum master user
    - team_size: Number of team members
    - burndown_trend: Burndown trend status
    """

    # Validate project exists
    project = crud_project.get(db, id=sprint_in.project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {sprint_in.project_id} not found"
        )

    # Validate scrum master exists if provided
    if sprint_in.scrum_master_id:
        scrum_master = crud_user.get(db, id=sprint_in.scrum_master_id)
        if not scrum_master:
            raise HTTPException(
                status_code=404,
                detail=f"Scrum master with ID {sprint_in.scrum_master_id} not found"
            )

    # Validate end_date is after start_date if both are provided
    if sprint_in.start_date and sprint_in.end_date:
        if sprint_in.end_date <= sprint_in.start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )

    sprint = crud_sprint.create(db, obj_in=sprint_in)

    # Log sprint creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Sprint",
        details=f"Created new sprint: {sprint.name} for project {project.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Add computed fields
    sprint = crud_sprint.get(db, id=sprint.id)
    if hasattr(sprint, 'project') and sprint.project:
        sprint.project_name = sprint.project.name
    elif sprint.project_id:
        # Get project name directly if relationship is not available
        project = crud_project.get(db, id=sprint.project_id)
        if project:
            sprint.project_name = project.name

    if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
        sprint.scrum_master_name = sprint.scrum_master.name
    elif sprint.scrum_master_id:
        # Get scrum master name directly if relationship is not available
        scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
        if scrum_master:
            sprint.scrum_master_name = scrum_master.name

    return sprint

@router.put("/{sprint_id}", response_model=SprintSchema)
def update_sprint(
    *,
    request: Request,
    db: Session = Depends(get_db),
    sprint_id: str,
    sprint_in: SprintUpdate,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    """
    Update an existing sprint with validation.

    **Supported updates:**
    - Basic info: name, status, goal
    - Dates: start_date, end_date (accepts YYYY-MM-DD or ISO datetime format)
    - Metrics: total_points, completed_points, total_tasks, completed_tasks, velocity
    - Team: scrum_master_id, team_size
    - Status: burndown_trend
    """
    sprint = crud_sprint.get(db, id=sprint_id)
    if not sprint:
        raise HTTPException(
            status_code=404,
            detail="The sprint with this id does not exist in the system",
        )

    # Validate scrum master exists if provided
    if sprint_in.scrum_master_id:
        scrum_master = crud_user.get(db, id=sprint_in.scrum_master_id)
        if not scrum_master:
            raise HTTPException(
                status_code=404,
                detail=f"Scrum master with ID {sprint_in.scrum_master_id} not found"
            )

    # Validate end_date is after start_date if both are provided
    start_date = sprint_in.start_date if sprint_in.start_date is not None else sprint.start_date
    end_date = sprint_in.end_date if sprint_in.end_date is not None else sprint.end_date

    if start_date and end_date:
        if end_date <= start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )

    sprint = crud_sprint.update(db, db_obj=sprint, obj_in=sprint_in)

    # Log sprint update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Sprint",
        details=f"Updated sprint: {sprint.name} (ID: {sprint.id})",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Add computed fields
    sprint = crud_sprint.get(db, id=sprint.id)
    if hasattr(sprint, 'project') and sprint.project:
        sprint.project_name = sprint.project.name
    elif sprint.project_id:
        # Get project name directly if relationship is not available
        project = crud_project.get(db, id=sprint.project_id)
        if project:
            sprint.project_name = project.name
    if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
        sprint.scrum_master_name = sprint.scrum_master.name
    elif sprint.scrum_master_id:
        # Get scrum master name directly if relationship is not available
        scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
        if scrum_master:
            sprint.scrum_master_name = scrum_master.name

    return sprint

@router.get("/{sprint_id}", response_model=SprintSchema)
def read_sprint(
    *,
    db: Session = Depends(get_db),
    sprint_id: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get a specific sprint by ID"""
    sprint = crud_sprint.get(db, id=sprint_id)
    if not sprint:
        raise HTTPException(
            status_code=404,
            detail="The sprint with this id does not exist in the system",
        )

    # Add computed fields
    if hasattr(sprint, 'project') and sprint.project:
        sprint.project_name = sprint.project.name
    elif sprint.project_id:
        # Get project name directly if relationship is not available
        project = crud_project.get(db, id=sprint.project_id)
        if project:
            sprint.project_name = project.name
    if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
        sprint.scrum_master_name = sprint.scrum_master.name
    elif sprint.scrum_master_id:
        # Get scrum master name directly if relationship is not available
        scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
        if scrum_master:
            sprint.scrum_master_name = scrum_master.name

    return sprint

@router.delete("/{sprint_id}", response_model=SprintSchema)
def delete_sprint(
    *,
    request: Request,
    db: Session = Depends(get_db),
    sprint_id: str,
    current_user: User = Depends(deps.require_permissions(["project:delete"]))
) -> Any:
    """Delete a sprint"""
    sprint = crud_sprint.get(db, id=sprint_id)
    if not sprint:
        raise HTTPException(
            status_code=404,
            detail="The sprint with this id does not exist in the system",
        )

    sprint = crud_sprint.remove(db, id=sprint_id)

    # Log sprint deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Sprint",
        details=f"Deleted sprint: {sprint.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return sprint

@router.get("/status/{status}", response_model=List[SprintSchema])
def read_sprints_by_status(
    *,
    db: Session = Depends(get_db),
    status: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get sprints by status"""
    sprints = crud_sprint.get_by_status(db, status=status)

    # Add computed fields
    for sprint in sprints:
        if hasattr(sprint, 'project') and sprint.project:
            sprint.project_name = sprint.project.name
        elif sprint.project_id:
            # Get project name directly if relationship is not available
            project = crud_project.get(db, id=sprint.project_id)
            if project:
                sprint.project_name = project.name
        if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
            sprint.scrum_master_name = sprint.scrum_master.name
        elif sprint.scrum_master_id:
            # Get scrum master name directly if relationship is not available
            scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
            if scrum_master:
                sprint.scrum_master_name = scrum_master.name

    return sprints

@router.get("/project/{project_id}", response_model=PaginatedResponse[SprintSchema])
def read_sprints_by_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get sprints for a specific project"""
    # Validate project exists
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {project_id} not found"
        )

    sprints, total = crud_sprint.get_project_sprints(
        db=db,
        project_id=project_id,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Add computed fields
    for sprint in sprints:
        if hasattr(sprint, 'project') and sprint.project:
            sprint.project_name = sprint.project.name
        elif sprint.project_id:
            # Get project name directly if relationship is not available
            project = crud_project.get(db, id=sprint.project_id)
            if project:
                sprint.project_name = project.name
        if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
            sprint.scrum_master_name = sprint.scrum_master.name
        elif sprint.scrum_master_id:
            # Get scrum master name directly if relationship is not available
            scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
            if scrum_master:
                sprint.scrum_master_name = scrum_master.name

    return PaginatedResponse.create(
        items=sprints,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/active/list", response_model=List[SprintSchema])
def read_active_sprints(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get all active sprints"""
    sprints = crud_sprint.get_active_sprints(db)

    # Add computed fields
    for sprint in sprints:
        if hasattr(sprint, 'project') and sprint.project:
            sprint.project_name = sprint.project.name
        elif sprint.project_id:
            # Get project name directly if relationship is not available
            project = crud_project.get(db, id=sprint.project_id)
            if project:
                sprint.project_name = project.name
        if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
            sprint.scrum_master_name = sprint.scrum_master.name
        elif sprint.scrum_master_id:
            # Get scrum master name directly if relationship is not available
            scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
            if scrum_master:
                sprint.scrum_master_name = scrum_master.name

    return sprints

@router.get("/scrum-master/{scrum_master_id}", response_model=List[SprintSchema])
def read_sprints_by_scrum_master(
    *,
    db: Session = Depends(get_db),
    scrum_master_id: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get sprints managed by a specific scrum master"""
    sprints = crud_sprint.get_by_scrum_master(db, scrum_master_id=scrum_master_id)

    # Add computed fields
    for sprint in sprints:
        if hasattr(sprint, 'project') and sprint.project:
            sprint.project_name = sprint.project.name
        elif sprint.project_id:
            # Get project name directly if relationship is not available
            project = crud_project.get(db, id=sprint.project_id)
            if project:
                sprint.project_name = project.name
        if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
            sprint.scrum_master_name = sprint.scrum_master.name
        elif sprint.scrum_master_id:
            # Get scrum master name directly if relationship is not available
            scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
            if scrum_master:
                sprint.scrum_master_name = scrum_master.name

    return sprints

@router.post("/{sprint_id}/update-metrics", response_model=SprintSchema)
def update_sprint_metrics(
    *,
    request: Request,
    db: Session = Depends(get_db),
    sprint_id: str,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    """Update sprint metrics based on associated tasks"""
    sprint = crud_sprint.update_sprint_metrics(db, sprint_id=sprint_id)
    if not sprint:
        raise HTTPException(
            status_code=404,
            detail="The sprint with this id does not exist in the system",
        )

    # Log metric update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Sprint",
        details=f"Updated metrics for sprint: {sprint.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Add computed fields
    if hasattr(sprint, 'project') and sprint.project:
        sprint.project_name = sprint.project.name
    elif sprint.project_id:
        # Get project name directly if relationship is not available
        project = crud_project.get(db, id=sprint.project_id)
        if project:
            sprint.project_name = project.name
    if hasattr(sprint, 'scrum_master') and sprint.scrum_master:
        sprint.scrum_master_name = sprint.scrum_master.name
    elif sprint.scrum_master_id:
        # Get scrum master name directly if relationship is not available
        scrum_master = crud_user.get(db, id=sprint.scrum_master_id)
        if scrum_master:
            sprint.scrum_master_name = scrum_master.name

    return sprint

@router.get("/stats/overview", response_model=SprintStats)
def get_sprint_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get sprint statistics and metrics"""
    return crud_sprint.get_sprint_stats(db)

@router.get("/statuses/list")
def get_sprint_statuses(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get available sprint statuses"""
    return {
        "statuses": ["Planning", "Active", "Completed", "Cancelled"]
    }

@router.get("/burndown-trends/list")
def get_burndown_trends(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get available burndown trend options"""
    return {
        "burndown_trends": ["On Track", "Behind", "Ahead", "At Risk"]
    }