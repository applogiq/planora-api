from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_user, crud_audit_log
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.schemas.audit_log import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users

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

@router.get("/role/{role_name}", response_model=List[UserSchema])
def read_users_by_role(
    *,
    db: Session = Depends(get_db),
    role_name: str,
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    # This would need to be implemented in CRUD to join with roles table
    # For now, returning all users
    users = crud_user.get_multi(db)
    return [user for user in users if user.role and user.role.name == role_name]

@router.get("/active/list", response_model=List[UserSchema])
def read_active_users(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["user:read"]))
) -> Any:
    users = crud_user.get_multi(db)
    return [user for user in users if user.is_active]