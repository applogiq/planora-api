from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_

from app.core.auth import (
    get_current_active_user,
    require_project_manage, ProjectPermissionChecker
)
from app.db.base import get_db
from app.models import User, Project, ProjectMember, Task
from app.schemas.project import (
    Project as ProjectSchema, ProjectCreate, ProjectUpdate,
    ProjectWithMembers, ProjectWithStats, ProjectListResponse,
    ProjectMember as ProjectMemberSchema, ProjectMemberCreate, ProjectMemberUpdate
)
import uuid

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List projects with optional filtering"""
    
    query = db.query(Project).filter(Project.tenant_id == current_user.tenant_id)
    
    # Filter by user's project membership
    query = query.join(ProjectMember).filter(ProjectMember.user_id == current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.key.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
        )
    
    if status:
        query = query.filter(Project.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    projects = query.offset(offset).limit(per_page).options(
        joinedload(Project.owner),
        joinedload(Project.members).joinedload(ProjectMember.user)
    ).all()
    
    # Add statistics
    projects_with_stats = []
    for project in projects:
        task_stats = db.query(
            func.count(Task.id).label('total'),
            func.sum(func.case((Task.status.in_(['done', 'completed']), 1), else_=0)).label('completed'),
            func.sum(func.case((Task.status.notin_(['done', 'completed']), 1), else_=0)).label('active')
        ).filter(Task.project_id == project.id).first()
        
        member_count = db.query(func.count(ProjectMember.user_id)).filter(
            ProjectMember.project_id == project.id
        ).scalar()
        
        project_dict = {
            **project.__dict__,
            'task_count': task_stats.total or 0,
            'completed_task_count': task_stats.completed or 0,
            'active_task_count': task_stats.active or 0,
            'member_count': member_count or 0
        }
        projects_with_stats.append(ProjectWithStats(**project_dict))
    
    pages = (total + per_page - 1) // per_page
    
    return ProjectListResponse(
        projects=projects_with_stats,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.post("", response_model=ProjectSchema)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_project_manage),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new project"""
    
    # Check if project key is unique within tenant
    existing_project = db.query(Project).filter(
        and_(
            Project.tenant_id == current_user.tenant_id,
            Project.key == project_data.key
        )
    ).first()
    
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with key '{project_data.key}' already exists"
        )
    
    # Create project
    project = Project(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        owner_user_id=project_data.owner_user_id or current_user.id,
        **project_data.model_dump(exclude={'owner_user_id'})
    )
    
    db.add(project)
    db.flush()
    
    # Add creator as project owner
    project_member = ProjectMember(
        project_id=project.id,
        user_id=project.owner_user_id,
        role="Owner"
    )
    db.add(project_member)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.get("/{project_id}", response_model=ProjectWithMembers)
async def get_project(
    project_id: str,
    current_user: User = Depends(ProjectPermissionChecker()),
    db: Session = Depends(get_db)
) -> Any:
    """Get project details"""
    
    project = db.query(Project).filter(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    ).options(
        joinedload(Project.owner),
        joinedload(Project.members).joinedload(ProjectMember.user)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(ProjectPermissionChecker("PM")),
    db: Session = Depends(get_db)
) -> Any:
    """Update project"""
    
    project = db.query(Project).filter(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if new key is unique (if provided)
    if project_data.key and project_data.key != project.key:
        existing_project = db.query(Project).filter(
            and_(
                Project.tenant_id == current_user.tenant_id,
                Project.key == project_data.key,
                Project.id != project_id
            )
        ).first()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with key '{project_data.key}' already exists"
            )
    
    # Update project
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(ProjectPermissionChecker("Owner")),
    db: Session = Depends(get_db)
) -> Any:
    """Delete project"""
    
    project = db.query(Project).filter(
        and_(
            Project.id == project_id,
            Project.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}


# Project Members endpoints
@router.get("/{project_id}/members", response_model=List[ProjectMemberSchema])
async def list_project_members(
    project_id: str,
    current_user: User = Depends(ProjectPermissionChecker()),
    db: Session = Depends(get_db)
) -> Any:
    """List project members"""
    
    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).options(joinedload(ProjectMember.user)).all()
    
    return members


@router.post("/{project_id}/members", response_model=ProjectMemberSchema)
async def add_project_member(
    project_id: str,
    member_data: ProjectMemberCreate,
    current_user: User = Depends(ProjectPermissionChecker("PM")),
    db: Session = Depends(get_db)
) -> Any:
    """Add member to project"""
    
    # Check if user exists and is in same tenant
    user = db.query(User).filter(
        and_(
            User.id == member_data.user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_active == True
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a member
    existing_member = db.query(ProjectMember).filter(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_data.user_id
        )
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a project member"
        )
    
    # Add member
    member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return member


@router.put("/{project_id}/members/{user_id}", response_model=ProjectMemberSchema)
async def update_project_member(
    project_id: str,
    user_id: str,
    member_data: ProjectMemberUpdate,
    current_user: User = Depends(ProjectPermissionChecker("PM")),
    db: Session = Depends(get_db)
) -> Any:
    """Update project member role"""
    
    member = db.query(ProjectMember).filter(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )
    
    # Update member
    if member_data.role:
        member.role = member_data.role
    
    db.commit()
    db.refresh(member)
    
    return member


@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(
    project_id: str,
    user_id: str,
    current_user: User = Depends(ProjectPermissionChecker("PM")),
    db: Session = Depends(get_db)
) -> Any:
    """Remove member from project"""
    
    member = db.query(ProjectMember).filter(
        and_(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found"
        )
    
    # Don't allow removing the project owner
    if member.role == "Owner":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove project owner"
        )
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed from project"}