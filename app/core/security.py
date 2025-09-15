from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import hashlib

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token generation
ALGORITHM = settings.ALGORITHM


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create access token with expiration"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create refresh token with longer expiration"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_token() -> tuple[str, str]:
    """Generate a new API token and its hash"""
    # Generate a random token
    token = secrets.token_urlsafe(32)
    
    # Create hash for storage
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    return token, token_hash


def verify_api_token(token: str, stored_hash: str) -> bool:
    """Verify an API token against its stored hash"""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return secrets.compare_digest(token_hash, stored_hash)


def generate_webhook_secret() -> str:
    """Generate a webhook secret"""
    return secrets.token_urlsafe(32)


def generate_shared_link_token() -> str:
    """Generate a shared link token"""
    return secrets.token_urlsafe(16)