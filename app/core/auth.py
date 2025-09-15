from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.base import get_db
from app.core.security import verify_token, verify_api_token
from app.models import User, Role, Permission, UserRole, RolePermission, APIToken

security = HTTPBearer()


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token or API token"""
    token = credentials.credentials
    
    # Try JWT token first
    payload = verify_token(token)
    if payload and payload.get("type") != "refresh":
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
            if user:
                return user
    
    # Try API token
    api_token = db.query(APIToken).filter(
        APIToken.is_active == True,
        APIToken.expires_at > db.func.now() if APIToken.expires_at is not None else True
    ).first()
    
    if api_token and verify_api_token(token, api_token.token_hash):
        # Update last used
        api_token.last_used_at = db.func.now()
        db.commit()
        
        user = db.query(User).filter(User.id == api_token.user_id, User.is_active == True).first()
        if user:
            return user
    
    raise AuthenticationError()


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




class PermissionChecker:
    """Dependency class for checking permissions"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check if user has required permissions"""
        if not self.required_permissions:
            return current_user
        
        # Get user permissions
        user_permissions = self._get_user_permissions(current_user.id, db)
        
        # Check if user has all required permissions
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise AuthorizationError(f"Missing permission: {permission}")
        
        return current_user
    
    def _get_user_permissions(self, user_id: str, db: Session) -> List[str]:
        """Get all permissions for a user"""
        permissions = db.query(Permission.key).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            Role, RolePermission.role_id == Role.id
        ).join(
            UserRole, Role.id == UserRole.role_id
        ).filter(
            UserRole.user_id == user_id
        ).all()
        
        return [p.key for p in permissions]


class RoleChecker:
    """Dependency class for checking roles"""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check if user has required roles"""
        if not self.required_roles:
            return current_user
        
        # Get user roles
        user_roles = db.query(Role.name).join(
            UserRole, Role.id == UserRole.role_id
        ).filter(
            UserRole.user_id == current_user.id
        ).all()
        
        user_role_names = [r.name for r in user_roles]
        
        # Check if user has any of the required roles
        if not any(role in user_role_names for role in self.required_roles):
            raise AuthorizationError(f"Missing required role. Required: {self.required_roles}")
        
        return current_user


class ProjectPermissionChecker:
    """Dependency class for checking project-specific permissions"""
    
    def __init__(self, required_role: str = None):
        self.required_role = required_role
    
    def __call__(
        self,
        project_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check if user has access to specific project"""
        from app.models import ProjectMember
        
        # Check if user is project member
        membership = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id
            )
        ).first()
        
        if not membership:
            raise AuthorizationError("No access to this project")
        
        # Check role if specified
        if self.required_role and membership.role != self.required_role:
            # Allow Owner and Admin to access everything
            if membership.role not in ["Owner", "Admin"]:
                raise AuthorizationError(f"Insufficient project permissions. Required: {self.required_role}")
        
        return current_user


# Common permission dependencies
require_admin = PermissionChecker(["admin.manage"])
require_project_manage = PermissionChecker(["project.manage"])
require_task_create = PermissionChecker(["task.create"])
require_task_update = PermissionChecker(["task.update"])
require_task_delete = PermissionChecker(["task.delete"])
require_user_manage = PermissionChecker(["user.manage"])
require_report_view = PermissionChecker(["report.view"])
require_report_manage = PermissionChecker(["report.manage"])

# Common role dependencies
require_admin_role = RoleChecker(["Admin", "Owner"])
require_pm_role = RoleChecker(["Admin", "Owner", "PM"])


async def get_tenant_context(request: Request) -> Optional[str]:
    """Extract tenant context from request headers or subdomain"""
    # Try header first (for API calls)
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id
    
    # Try subdomain (for web interface)
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        # Look up tenant by subdomain (would need a subdomain field in Tenant model)
        # For now, return None to use user's tenant
    
    return None