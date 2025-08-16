"""
Enhanced error handling for production deployment
"""

import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from ..config import settings
from .logging import ErrorLogger

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"API_ERROR_{status_code}"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(APIError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(APIError):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(APIError):
    """Resource not found error"""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            error_code="NOT_FOUND_ERROR"
        )


class ConflictError(APIError):
    """Resource conflict error"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR"
        )


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after}
        )


class ExternalServiceError(APIError):
    """External service error"""
    
    def __init__(self, service: str, message: str = None):
        message = message or f"External service '{service}' is unavailable"
        super().__init__(
            message=message,
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> JSONResponse:
    """Create standardized error response"""
    
    error_response = {
        "error": {
            "message": message,
            "code": error_code or f"HTTP_{status_code}",
            "status_code": status_code,
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    if not settings.is_production:
        error_response["error"]["timestamp"] = logger.handlers[0].formatter.formatTime(
            logging.LogRecord("", 0, "", 0, "", (), None)
        )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors"""
    client_ip = get_client_ip(request)
    
    # Log the error
    logger.error(
        f"API Error: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "client_ip": client_ip,
            "endpoint": str(request.url.path),
            "method": request.method,
            "details": exc.details
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    client_ip = get_client_ip(request)
    
    # Log the error
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "client_ip": client_ip,
            "endpoint": str(request.url.path),
            "method": request.method
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}"
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    client_ip = get_client_ip(request)
    
    # Extract validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log the error
    logger.warning(
        f"Validation Error: {len(validation_errors)} validation errors",
        extra={
            "client_ip": client_ip,
            "endpoint": str(request.url.path),
            "method": request.method,
            "validation_errors": validation_errors
        }
    )
    
    return create_error_response(
        status_code=422,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": validation_errors}
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors"""
    client_ip = get_client_ip(request)
    
    # Log the database error
    ErrorLogger.log_database_error(
        operation=f"{request.method} {request.url.path}",
        error=exc
    )
    
    if settings.is_production:
        # Don't expose database details in production
        message = "Database operation failed"
        details = None
    else:
        message = f"Database error: {str(exc)}"
        details = {"error_type": type(exc).__name__}
    
    return create_error_response(
        status_code=500,
        message=message,
        error_code="DATABASE_ERROR",
        details=details
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    client_ip = get_client_ip(request)
    
    # Log the exception
    ErrorLogger.log_exception(
        exception=exc,
        context={
            "endpoint": str(request.url.path),
            "method": request.method,
            "client_ip": client_ip
        }
    )
    
    if settings.is_production:
        # Don't expose internal details in production
        message = "Internal server error"
        details = None
    else:
        message = f"Internal error: {str(exc)}"
        details = {
            "error_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    
    return create_error_response(
        status_code=500,
        message=message,
        error_code="INTERNAL_ERROR",
        details=details
    )


def setup_error_handlers(app):
    """Set up all error handlers for the FastAPI app"""
    
    # Custom API errors
    app.add_exception_handler(APIError, api_error_handler)
    
    # HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Database errors
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    # General exceptions (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured")


# Context manager for error handling
class ErrorContext:
    """Context manager for handling errors with additional context"""
    
    def __init__(self, operation: str, user_id: str = None, **context):
        self.operation = operation
        self.user_id = user_id
        self.context = context
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            ErrorLogger.log_exception(
                exception=exc_val,
                context={
                    "operation": self.operation,
                    **self.context
                },
                user_id=self.user_id
            )
        return False  # Don't suppress the exception


# Decorator for error handling
def handle_errors(operation: str = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except APIError:
                # Re-raise API errors as they're already handled
                raise
            except Exception as e:
                # Log and convert to API error
                ErrorLogger.log_exception(
                    exception=e,
                    context={"operation": operation or func.__name__}
                )
                
                if settings.is_production:
                    raise APIError("Operation failed")
                else:
                    raise APIError(f"Operation failed: {str(e)}")
        
        return wrapper
    return decorator