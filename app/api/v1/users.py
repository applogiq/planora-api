from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_

from app.core.auth import (
    get_current_active_user,
    require_admin, require_user_manage
)
from app.db.base import get_db
from app.models import User, Role, UserRole, UserProfile
from app.schemas.user import (
    User as UserSchema, UserCreate, UserUpdate, UserWithRoles,
    UserListResponse, UserProfile as UserProfileSchema,
    UserProfileCreate, UserProfileUpdate
)
from app.core.security import get_password_hash
import uuid

router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_user_manage),
    db: Session = Depends(get_db)
) -> Any:
    """List users in the tenant"""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.outerjoin(UserProfile).filter(
            or_(
                User.email.ilike(f"%{search}%"),
                UserProfile.first_name.ilike(f"%{search}%"),
                UserProfile.last_name.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    users = query.offset(offset).limit(per_page).options(
        joinedload(User.profile)
    ).all()
    
    pages = (total + per_page - 1) // per_page
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.post("", response_model=UserSchema)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_user_manage),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        and_(
            User.email == user_data.email,
            User.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = User(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password) if user_data.password else None,
        sso_subject=user_data.sso_subject,
        is_active=user_data.is_active
    )
    
    db.add(user)
    db.flush()
    
    # Create user profile if provided
    if user_data.profile:
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            **user_data.profile.model_dump()
        )
        db.add(profile)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user details"""
    
    # Users can view their own profile, or admins can view any user
    if user_id != str(current_user.id):
        # Check if current user has permission to view other users
        from app.core.auth import require_user_manage
        require_user_manage(current_user, db)
    
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
    ).options(
        joinedload(User.profile),
        joinedload(User.user_roles).joinedload(UserRole.role)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user roles and permissions
    roles = [ur.role.name for ur in user.user_roles]
    
    # Get user permissions through roles
    permissions = []
    for user_role in user.user_roles:
        role_perms = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role_perms:
            for rp in role_perms.role_permissions:
                permissions.append(rp.permission.key)
    
    user_dict = {
        **user.__dict__,
        'roles': roles,
        'permissions': list(set(permissions))
    }
    
    return UserWithRoles(**user_dict)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user"""
    
    # Users can update their own profile, or admins can update any user
    if user_id != str(current_user.id):
        from app.core.auth import require_user_manage
        require_user_manage(current_user, db)
    
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_data.model_dump(exclude_unset=True, exclude={'profile'})
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Update profile if provided
    if user_data.profile:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            profile_data = user_data.profile.model_dump(exclude_unset=True)
            for field, value in profile_data.items():
                setattr(profile, field, value)
        else:
            # Create new profile
            profile = UserProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                **user_data.profile.model_dump()
            )
            db.add(profile)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_user_manage),
    db: Session = Depends(get_db)
) -> Any:
    """Delete user"""
    
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.put("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_user_manage),
    db: Session = Depends(get_db)
) -> Any:
    """Activate a user"""
    
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": "User activated successfully"}


@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_user_manage),
    db: Session = Depends(get_db)
) -> Any:
    """Deactivate a user"""
    
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}


# User Profile endpoints
@router.get("/{user_id}/profile", response_model=UserProfileSchema)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user profile"""
    
    # Users can view their own profile, or admins can view any profile
    if user_id != str(current_user.id):
        from app.core.auth import require_user_manage
        require_user_manage(current_user, db)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile


@router.put("/{user_id}/profile", response_model=UserProfileSchema)
async def update_user_profile(
    user_id: str,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update user profile"""
    
    # Users can update their own profile, or admins can update any profile
    if user_id != str(current_user.id):
        from app.core.auth import require_user_manage
        require_user_manage(current_user, db)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # Create new profile
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user_id,
            **profile_data.model_dump()
        )
        db.add(profile)
    else:
        # Update existing profile
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile

