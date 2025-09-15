from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.auth import get_current_active_user, get_current_user
from app.core.config import settings
from app.db.base import get_db
from app.models import User, UserProfile, Role, UserRole
from app.schemas.auth import (
    Token, UserLogin, UserRegister, RefreshToken, 
    PasswordReset, PasswordResetConfirm, ChangePassword,
    APITokenCreate, APITokenResponse, APITokenInfo
)
from app.schemas.user import User as UserSchema
import uuid

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """JSON login endpoint, get an access token for future requests"""
    if not user_credentials.email and not user_credentials.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or username is required"
        )
    
    user = authenticate_user(db, user_credentials.login_identifier, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }



@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token"""
    payload = security.verify_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    new_refresh_token = security.create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user (without tenant)
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            password_hash=security.get_password_hash(user_data.password),
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Create user profile
        if user_data.first_name or user_data.last_name:
            profile = UserProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            db.add(profile)
        
        # Assign default admin role to user
        admin_role = db.query(Role).filter(Role.name == "Admin").first()

        if not admin_role:
            # Create admin role
            admin_role = Role(
                id=uuid.uuid4(),
                name="Admin",
                description="Administrator role with full access"
            )
            db.add(admin_role)
            db.flush()

        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        db.add(user_role)
        
        db.commit()
        db.refresh(user)
        
        # Manually load the profile to avoid lazy loading issues
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        
        # Convert to schema-compatible format
        user_data = {
            'id': str(user.id),
            'email': user.email,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'profile': None
        }
        
        if profile:
            user_data['profile'] = {
                'id': str(profile.id),
                'user_id': str(profile.user_id),
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'avatar_url': profile.avatar_url,
                'bio': profile.bio,
                'timezone': profile.timezone
            }
        
        return UserSchema(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user"""
    # Load the profile to avoid lazy loading issues
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    # Convert to schema-compatible format
    user_data = {
        'id': str(current_user.id),
        'email': current_user.email,
        'is_active': current_user.is_active,
        'created_at': current_user.created_at,
        'profile': None
    }
    
    if profile:
        user_data['profile'] = {
            'id': str(profile.id),
            'user_id': str(profile.user_id),
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'avatar_url': profile.avatar_url,
            'bio': profile.bio,
            'timezone': profile.timezone
        }
    
    return UserSchema(**user_data)


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Change user password"""
    if not security.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.password_hash = security.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/api-tokens", response_model=APITokenResponse)
async def create_api_token(
    token_data: APITokenCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new API token"""
    from app.models import APIToken
    from datetime import datetime, timedelta
    
    token, token_hash = security.generate_api_token()
    
    api_token = APIToken(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=token_data.name,
        token_hash=token_hash,
        scopes=token_data.scopes,
        expires_at=datetime.utcnow() + timedelta(days=token_data.expires_in_days) if token_data.expires_in_days else None
    )
    
    db.add(api_token)
    db.commit()
    db.refresh(api_token)
    
    # Return token only once
    return APITokenResponse(
        id=str(api_token.id),
        name=api_token.name,
        token=token,
        scopes=api_token.scopes,
        expires_at=api_token.expires_at,
        created_at=api_token.created_at
    )


@router.get("/api-tokens", response_model=list[APITokenInfo])
async def list_api_tokens(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List user's API tokens"""
    from app.models import APIToken
    
    tokens = db.query(APIToken).filter(APIToken.user_id == current_user.id).all()
    return tokens


@router.delete("/api-tokens/{token_id}")
async def delete_api_token(
    token_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete an API token"""
    from app.models import APIToken
    
    token = db.query(APIToken).filter(
        APIToken.id == token_id,
        APIToken.user_id == current_user.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    db.delete(token)
    db.commit()
    
    return {"message": "Token deleted successfully"}


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user