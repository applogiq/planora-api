from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None


class UserLogin(BaseModel):
    email: Optional[str] = None  # Changed from EmailStr to allow username-like emails
    username: Optional[str] = None  # Allow username as alternative to email
    password: str
    
    @model_validator(mode='after')
    def validate_login_identifier(self):
        if not self.email and not self.username:
            raise ValueError('Either email or username must be provided')
        # Allow empty strings to be treated as None
        if self.email == "":
            self.email = None
        if self.username == "":
            self.username = None
        if not self.email and not self.username:
            raise ValueError('Either email or username must be provided')
        return self
    
    @property
    def login_identifier(self) -> str:
        """Return email or username for authentication"""
        return self.email or self.username


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tenant_name: Optional[str] = None  # For new tenant creation


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# API Token schemas
class APITokenCreate(BaseModel):
    name: str
    scopes: List[str] = []
    expires_in_days: Optional[int] = None


class APITokenResponse(BaseModel):
    id: str
    name: str
    token: str  # Only returned on creation
    scopes: List[str]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APITokenInfo(BaseModel):
    id: str
    name: str
    scopes: List[str]
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Role and Permission schemas
class PermissionBase(BaseModel):
    key: str
    description: Optional[str] = None


class Permission(PermissionBase):
    id: str
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None


class Role(RoleBase):
    id: str
    tenant_id: str
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True


# User role assignment
class UserRoleAssignment(BaseModel):
    user_id: str
    role_ids: List[str]


# SSO Configuration
class SSOProviderConfig(BaseModel):
    provider_type: str  # 'oidc' or 'saml'
    provider_name: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    discovery_url: Optional[str] = None
    issuer: Optional[str] = None
    redirect_uri: Optional[str] = None
    # SAML specific
    metadata_url: Optional[str] = None
    entity_id: Optional[str] = None


class SSOProvider(BaseModel):
    id: str
    tenant_id: str
    provider_type: str
    provider_name: str
    is_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True