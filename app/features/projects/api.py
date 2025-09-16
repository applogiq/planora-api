from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.tasks.crud import crud_task
from app.features.audit_logs.crud import crud_audit_log
# from app.crud import crud_project, crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.projects.schemas import Project as ProjectSchema, ProjectCreate, ProjectUpdate
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[ProjectSchema])
def read_projects(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in name, description, customer"),
    status: Optional[str] = Query(default=None, description="Filter by project status"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    team_lead_id: Optional[str] = Query(default=None, description="Filter by team lead"),
    customer: Optional[str] = Query(default=None, description="Filter by customer"),
    tag: Optional[str] = Query(default=None, description="Filter by tag"),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """
    Get projects with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, name, status, priority, progress, start_date, end_date, budget, created_at

    **Search:** Searches in project name, description, and customer fields.

    **Filters:**
    - status: Filter by project status (Active, On Hold, Completed, Planning)
    - priority: Filter by priority (Low, Medium, High, Critical)
    - team_lead_id: Filter by team lead user ID
    - customer: Filter by customer name (partial match)
    - tag: Filter by specific tag
    """
    projects, total = crud_project.get_projects_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        status=status,
        priority=priority,
        team_lead_id=team_lead_id,
        customer=customer,
        tag=tag
    )

    return PaginatedResponse.create(
        items=projects,
        total=total,
        page=page,
        per_page=per_page
    )

@router.post("/", response_model=ProjectSchema)
def create_project(
    *,
    request: Request,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    project = crud_project.create(db, obj_in=project_in)

    # Log project creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Project",
        details=f"Created new project: {project.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return project

@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    *,
    request: Request,
    db: Session = Depends(get_db),
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.require_permissions(["project:write"]))
) -> Any:
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system",
        )
    project = crud_project.update(db, db_obj=project, obj_in=project_in)

    # Log project update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Project",
        details=f"Updated project: {project.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return project

@router.get("/{project_id}", response_model=ProjectSchema)
def read_project(
    *,
    db: Session = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system",
        )
    return project

@router.delete("/{project_id}", response_model=ProjectSchema)
def delete_project(
    *,
    request: Request,
    db: Session = Depends(get_db),
    project_id: str,
    current_user: User = Depends(deps.require_permissions(["project:delete"]))
) -> Any:
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system",
        )

    project = crud_project.remove(db, id=project_id)

    # Log project deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Project",
        details=f"Deleted project: {project.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return project

@router.get("/status/{status}", response_model=List[ProjectSchema])
def read_projects_by_status(
    *,
    db: Session = Depends(get_db),
    status: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    projects = crud_project.get_by_status(db, status=status)
    return projects

@router.get("/active/list", response_model=List[ProjectSchema])
def read_active_projects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    projects = crud_project.get_active_projects(db)
    return projects

@router.get("/lead/{team_lead_id}", response_model=List[ProjectSchema])
def read_projects_by_team_lead(
    *,
    db: Session = Depends(get_db),
    team_lead_id: str,
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    projects = crud_project.get_by_team_lead(db, team_lead_id=team_lead_id)
    return projects

@router.get("/stats/overview")
def get_project_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    all_projects = crud_project.get_multi(db, limit=1000)

    stats = {
        "total_projects": len(all_projects),
        "active_projects": len([p for p in all_projects if p.status == "Active"]),
        "completed_projects": len([p for p in all_projects if p.status == "Completed"]),
        "on_hold_projects": len([p for p in all_projects if p.status == "On Hold"]),
        "planning_projects": len([p for p in all_projects if p.status == "Planning"]),
        "total_budget": sum([p.budget or 0 for p in all_projects]),
        "total_spent": sum([p.spent or 0 for p in all_projects]),
        "avg_progress": sum([p.progress or 0 for p in all_projects]) / len(all_projects) if all_projects else 0
    }

    return stats

@router.get("/priorities/list")
def get_project_priorities(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    return {
        "priorities": ["Low", "Medium", "High", "Critical"]
    }

@router.get("/statuses/list")
def get_project_statuses(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    return {
        "statuses": ["Planning", "Active", "On Hold", "Completed"]
    }