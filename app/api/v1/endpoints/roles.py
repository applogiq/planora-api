from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core import deps
from app.crud import crud_role, crud_audit_log
from app.db.database import get_db
from app.models.user import User
from app.schemas.role import Role as RoleSchema, RoleCreate, RoleUpdate
from app.schemas.audit_log import AuditLogCreate

router = APIRouter()

@router.get("/", response_model=List[RoleSchema])
def read_roles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_permissions(["role:read"]))
) -> Any:
    roles = crud_role.get_multi(db, skip=skip, limit=limit)
    return roles

@router.post("/", response_model=RoleSchema)
def create_role(
    *,
    request: Request,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    current_user: User = Depends(deps.require_permissions(["role:write"]))
) -> Any:
    role = crud_role.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="The role with this name already exists in the system.",
        )
    role = crud_role.create(db, obj_in=role_in)

    # Log role creation
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="CREATE",
        resource="Role",
        details=f"Created new role: {role.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return role

@router.put("/{role_id}", response_model=RoleSchema)
def update_role(
    *,
    request: Request,
    db: Session = Depends(get_db),
    role_id: str,
    role_in: RoleUpdate,
    current_user: User = Depends(deps.require_permissions(["role:write"]))
) -> Any:
    role = crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="The role with this id does not exist in the system",
        )
    role = crud_role.update(db, db_obj=role, obj_in=role_in)

    # Log role update
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="UPDATE",
        resource="Role",
        details=f"Updated role: {role.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return role

@router.get("/{role_id}", response_model=RoleSchema)
def read_role(
    *,
    db: Session = Depends(get_db),
    role_id: str,
    current_user: User = Depends(deps.require_permissions(["role:read"]))
) -> Any:
    role = crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="The role with this id does not exist in the system",
        )
    return role

@router.delete("/{role_id}", response_model=RoleSchema)
def delete_role(
    *,
    request: Request,
    db: Session = Depends(get_db),
    role_id: str,
    current_user: User = Depends(deps.require_permissions(["role:write"]))
) -> Any:
    role = crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="The role with this id does not exist in the system",
        )

    # Check if role is in use
    if hasattr(role, 'users') and role.users:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete role that is assigned to users",
        )

    role = crud_role.remove(db, id=role_id)

    # Log role deletion
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="DELETE",
        resource="Role",
        details=f"Deleted role: {role.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return role

@router.get("/active/list", response_model=List[RoleSchema])
def read_active_roles(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permissions(["role:read"]))
) -> Any:
    roles = crud_role.get_active_roles(db)
    return roles

@router.get("/permissions/list")
def get_available_permissions(
    current_user: User = Depends(deps.require_permissions(["role:read"]))
) -> Any:
    return {
        "permissions": [
            "user:read", "user:write", "user:delete",
            "role:read", "role:write",
            "project:read", "project:write", "project:delete",
            "task:read", "task:write", "task:delete",
            "team:read", "team:write",
            "report:read", "report:write",
            "customer:read", "customer:write",
            "settings:read", "settings:write",
            "audit:read",
            "*"  # Super admin permission
        ]
    }