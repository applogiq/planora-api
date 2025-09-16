from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core import deps
from app.core.pagination import PaginationParams, PaginatedResponse
from app.features.users.crud import crud_user
from app.features.audit_logs.crud import crud_audit_log
from app.db.database import get_db
from app.features.users.models import User
from app.features.users.schemas import User as UserSchema, UserCreate, UserUpdate
from app.features.users.user_summary import UserSummary
from app.features.audit_logs.schemas import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(default=None, description="Search in name and email"),
    role_name: Optional[str] = Query(default=None, description="Filter by role name"),
    role_id: Optional[str] = Query(default=None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    department: Optional[str] = Query(default=None, description="Filter by department"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get users with advanced filtering, pagination, and sorting

    **Supported sort fields:** id, name, email, created_at, updated_at, department, is_active

    **Search:** Searches in user name and email fields. Supports partial matches and split name search.

    **Filters:**
    - role_name: Filter by role name (case-insensitive)
    - role_id: Filter by specific role ID
    - is_active: Filter by active status (true/false)
    - department: Filter by department (case-insensitive, partial match)
    """
    users, total = crud_user.get_users_with_filters(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        role_name=role_name,
        role_id=role_id,
        is_active=is_active,
        department=department
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/summary", response_model=UserSummary)
def get_user_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get user summary statistics including:
    - Total users count
    - Active/inactive users count
    - Total roles count
    - Count of users by role (Admin, Project Manager, Developer, Client, etc.)
    """
    summary_data = crud_user.get_user_summary(db)
    return UserSummary(**summary_data)

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create(db, obj_in=user_in)

    # Log user creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="User",
        details=f"Created new user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(deps.require_permissions(["user:write"]))
) -> Any:
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud_user.update(db, db_obj=user, obj_in=user_in)

    # Log user update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="User",
        details=f"Updated user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return user

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_id: str,
    current_user: User = Depends(deps.require_permissions(["user:delete"]))
) -> Any:
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves",
        )

    user = crud_user.remove(db, id=user_id)

    # Log user deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="User",
        details=f"Deleted user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return user

@router.get("/role/{role_name}", response_model=PaginatedResponse[UserSchema])
def read_users_by_role(
    *,
    db: Session = Depends(get_db),
    role_name: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """Get users by role name with pagination and sorting"""
    users, total = crud_user.get_users_by_role(
        db=db,
        role_name=role_name,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/summary", response_model=UserSummary)
def get_user_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """
    Get user summary statistics including:
    - Total users count
    - Active/inactive users count
    - Total roles count
    - Count of users by role (Admin, Project Manager, Developer, Client, etc.)
    """
    summary_data = crud_user.get_user_summary(db)
    return UserSummary(**summary_data)

@router.get("/active/list", response_model=PaginatedResponse[UserSchema])
def read_active_users(
    *,
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    """Get active users with pagination and sorting"""
    users, total = crud_user.get_active_users(
        db=db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse.create(
        items=users,
        total=total,
        page=page,
        per_page=per_page
    )