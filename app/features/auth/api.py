from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import deps
from app.core import security
from app.core.config import settings
from app.features.users.crud import crud_user
from app.features.roles.crud import crud_role
from app.features.projects.crud import crud_project
from app.features.tasks.crud import crud_task
from app.features.audit_logs.crud import crud_audit_log
# from app.crud import crud_user, crud_audit_log
from app.db.database import get_db
from app.features.auth.schemas import Token, LoginData
from app.features.audit_logs.schemas import AuditLogCreate
from app.features.users.schemas import User as UserSchema
from app.features.users.models import User

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    login_data: LoginData,
    db: Session = Depends(get_db)
) -> Any:
    user = crud_user.authenticate(
        db, email=login_data.email, password=login_data.password
    )
    if not user:
        # Log failed login attempt
        audit_log = AuditLogCreate(
            user_name=login_data.email,
            action="LOGIN_FAILED",
            resource="Authentication",
            details="Failed login attempt - incorrect credentials",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            status="failure"
        )
        crud_audit_log.create(db=db, obj_in=audit_log)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(user.id)

    # Log successful login
    audit_log = AuditLogCreate(
        user_id=user.id,
        user_name=user.name,
        action="LOGIN",
        resource="Authentication",
        details="Successful login from web interface",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    # Update last login
    user.last_login = audit_log.timestamp if hasattr(audit_log, 'timestamp') else None
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Any:
    user_id = security.verify_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = crud_user.get(db, id=user_id)
    if not user or not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    new_refresh_token = security.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    # Log logout
    audit_log = AuditLogCreate(
        user_id=current_user.id,
        user_name=current_user.name,
        action="LOGOUT",
        resource="Authentication",
        details="User logged out",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    crud_audit_log.create(db=db, obj_in=audit_log)

    return {"message": "Successfully logged out"}