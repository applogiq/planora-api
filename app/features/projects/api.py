from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginatedResponse
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.stories.crud import crud_story
from app.features.audit_logs.crud import crud_audit_log
# from app.crud import crud_project, crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.projects.schemas import Project as ProjectSchema, ProjectCreate, ProjectUpdate, TeamMemberDetail, ProjectMembersResponse
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

def enrich_project_with_team_details(db: Session, project) -> ProjectSchema:
    """Enrich project with full team member and team lead details"""
    project_dict = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "progress": project.progress,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "budget": project.budget,
        "spent": project.spent,
        "customer": project.customer,
        "customer_id": project.customer_id,
        "priority": project.priority,
        "team_lead_id": project.team_lead_id,
        "team_members": project.team_members,
        "tags": project.tags,
        "color": project.color,
        "methodology": project.methodology,
        "project_type": project.project_type,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }

    # Enrich team lead details
    team_lead_detail = None
    if project.team_lead_id:
        team_lead = crud_user.get(db, id=project.team_lead_id)
        if team_lead:
            team_lead_detail = TeamMemberDetail(
                id=team_lead.id,
                name=team_lead.name,
                department=team_lead.department,
                role_id=team_lead.role_id,
                role_name=team_lead.role.name if team_lead.role else None,
                user_profile=team_lead.user_profile
            )

    # Enrich team members details
    team_members_detail = []
    if project.team_members:
        for member_id in project.team_members:
            member = crud_user.get(db, id=member_id)
            if member:
                member_detail = TeamMemberDetail(
                    id=member.id,
                    name=member.name,
                    department=member.department,
                    role_id=member.role_id,
                    role_name=member.role.name if member.role else None,
                    user_profile=member.user_profile
                )
                team_members_detail.append(member_detail)

    project_dict["team_lead_detail"] = team_lead_detail
    project_dict["team_members_detail"] = team_members_detail

    return ProjectSchema(**project_dict)

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
    methodology: Optional[str] = Query(default=None, description="Filter by methodology"),
    project_type: Optional[str] = Query(default=None, description="Filter by project type"),
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
    - methodology: Filter by project methodology (Scrum, Kanban, Waterfall)
    - project_type: Filter by project type (Software Development, Research, Marketing, etc.)
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
        tag=tag,
        methodology=methodology,
        project_type=project_type
    )

    # Enrich projects with team member details
    enriched_projects = [enrich_project_with_team_details(db, project) for project in projects]

    return PaginatedResponse.create(
        items=enriched_projects,
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
    """
    Create a new project with all required and optional fields.

    **Required fields:**
    - name: Project name
    - status: Project status (Planning, Active, On Hold, Completed, Cancelled)
    - project_type: Type of project (Software Development, Mobile Development, etc.)

    **Optional fields:**
    - description: Project description
    - team_lead_id: ID of the team lead user
    - team_members: List of team member user IDs
    - customer: Customer name
    - customer_id: Customer ID
    - start_date: Project start date
    - end_date: Project end date
    - budget: Project budget
    - priority: Project priority (Low, Medium, High, Critical, Urgent)
    - methodology: Project methodology (Scrum, Kanban, Waterfall)
    - color: Project color code (hex format)
    - tags: Project tags
    """

    # Validate team lead exists if provided
    if project_in.team_lead_id:
        team_lead = crud_user.get(db, id=project_in.team_lead_id)
        if not team_lead:
            raise HTTPException(
                status_code=404,
                detail=f"Team lead with ID {project_in.team_lead_id} not found"
            )

    # Validate team members exist if provided
    if project_in.team_members:
        for member_id in project_in.team_members:
            member = crud_user.get(db, id=member_id)
            if not member:
                raise HTTPException(
                    status_code=404,
                    detail=f"Team member with ID {member_id} not found"
                )

    # Validate end_date is after start_date if both are provided
    if project_in.start_date and project_in.end_date:
        if project_in.end_date <= project_in.start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )

    project = crud_project.create(db, obj_in=project_in)

    # Log project creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Project",
        details=f"Created new project: {project.name} (Type: {project.project_type}, Status: {project.status})",
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
    """
    Update an existing project with validation for all fields.

    **Supported updates:**
    - Basic info: name, description, status, progress
    - Dates: start_date, end_date (accepts YYYY-MM-DD or ISO datetime format)
    - Financial: budget, spent
    - Team: team_lead_id, team_members (validates user existence)
    - Customer: customer, customer_id
    - Project details: priority, methodology, project_type, color, tags
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="The project with this id does not exist in the system",
        )

    # Validate team lead exists if provided
    if project_in.team_lead_id:
        team_lead = crud_user.get(db, id=project_in.team_lead_id)
        if not team_lead:
            raise HTTPException(
                status_code=404,
                detail=f"Team lead with ID {project_in.team_lead_id} not found"
            )

    # Validate team members exist if provided
    if project_in.team_members:
        for member_id in project_in.team_members:
            member = crud_user.get(db, id=member_id)
            if not member:
                raise HTTPException(
                    status_code=404,
                    detail=f"Team member with ID {member_id} not found"
                )

    # Validate end_date is after start_date if both are provided
    start_date = project_in.start_date if project_in.start_date is not None else project.start_date
    end_date = project_in.end_date if project_in.end_date is not None else project.end_date

    if start_date and end_date:
        if end_date <= start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )

    project = crud_project.update(db, db_obj=project, obj_in=project_in)

    # Log project update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Project",
        details=f"Updated project: {project.name} (ID: {project.id})",
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
    return enrich_project_with_team_details(db, project)

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
    return [enrich_project_with_team_details(db, project) for project in projects]

@router.get("/active/list", response_model=List[ProjectSchema])
def read_active_projects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    projects = crud_project.get_active_projects(db)
    return [enrich_project_with_team_details(db, project) for project in projects]

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

@router.get("/methodologies/list")
def get_project_methodologies(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    return {
        "methodologies": ["Scrum", "Kanban", "Waterfall"]
    }

@router.get("/types/list")
def get_project_types(
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    return {
        "project_types": [
            "Software Development",
            "Web Development",
            "Mobile Development",
            "AI/ML Development",
            "Blockchain Development",
            "IoT Development",
            "VR/AR Development",
            "API Development",
            "Data Analytics",
            "Infrastructure",
            "Enterprise Software",
            "Education Technology",
            "Health Technology",
            "Marketing Technology",
            "Media Technology",
            "Operations Technology",
            "Research",
            "Design",
            "Testing",
            "Maintenance"
        ]
    }

@router.get("/users/team-leads")
def get_available_team_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get users who can be assigned as team leads (Admin, Project Manager roles)"""
    team_leads = crud_user.get_users_by_roles(db, roles=["role_admin", "role_project_manager"])
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None
        }
        for user in team_leads
    ]

@router.get("/users/team-members")
def get_available_team_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """Get all active users who can be assigned as team members"""
    team_members = crud_user.get_active_users(db)
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "department": user.department,
            "skills": user.skills or []
        }
        for user in team_members
    ]

@router.get("/members/{project_id}", response_model=ProjectMembersResponse)
def get_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["project:read"]))
) -> Any:
    """
    Get team member and team lead details for a specific project.

    Returns:
    - project_id: ID of the project
    - project_name: Name of the project
    - team_lead: Details of the team lead (id, name, role)
    - team_members: List of team member details (id, name, role)
    """
    # Get the project
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get team lead details
    team_lead_detail = None
    if project.team_lead_id:
        team_lead = crud_user.get(db, id=project.team_lead_id)
        if team_lead:
            team_lead_detail = TeamMemberDetail(
                id=team_lead.id,
                name=team_lead.name,
                department=team_lead.department,
                role_id=team_lead.role_id,
                role_name=team_lead.role.name if team_lead.role else None,
                user_profile=team_lead.user_profile
            )

    # Get team members details
    team_members_detail = []
    if project.team_members:
        for member_id in project.team_members:
            member = crud_user.get(db, id=member_id)
            if member:
                member_detail = TeamMemberDetail(
                    id=member.id,
                    name=member.name,
                    department=member.department,
                    role_id=member.role_id,
                    role_name=member.role.name if member.role else None,
                    user_profile=member.user_profile
                )
                team_members_detail.append(member_detail)

    return ProjectMembersResponse(
        project_id=project.id,
        project_name=project.name,
        team_lead=team_lead_detail,
        team_members=team_members_detail
    )