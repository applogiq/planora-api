from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class PlanoraException(Exception):
    """Base exception for Planora"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(PlanoraException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class NotFoundError(PlanoraException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class PermissionDeniedError(PlanoraException):
    """Permission denied exception"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ConflictError(PlanoraException):
    """Resource conflict exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitError(PlanoraException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


async def planora_exception_handler(request: Request, exc: PlanoraException) -> JSONResponse:
    """Handle Planora custom exceptions"""
    logger.error(f"Planora Exception: {exc.message}", exc_info=exc)
    
    content = {
        "error": {
            "message": exc.message,
            "type": exc.__class__.__name__,
            "details": exc.details
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    content = {
        "error": {
            "message": exc.detail,
            "type": "HTTPException",
            "status_code": exc.status_code
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    logger.warning(f"Validation Exception: {exc.errors()}")
    
    content = {
        "error": {
            "message": "Validation error",
            "type": "ValidationError",
            "details": {
                "validation_errors": exc.errors()
            }
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=exc)
    
    content = {
        "error": {
            "message": "Internal server error",
            "type": "InternalServerError",
            "details": {}
        }
    }
    
    # Don't expose internal error details in production
    from app.core.config import settings
    if settings.DEBUG:
        content["error"]["details"]["debug_info"] = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )