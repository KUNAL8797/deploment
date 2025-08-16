"""
Security middleware for production deployment
"""

import time
import logging
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self, client_ip: str) -> int:
        """Get time when rate limit resets"""
        client_requests = self.requests[client_ip]
        if client_requests:
            return int(client_requests[0] + self.window_seconds)
        return int(time.time())


# Global rate limiter instances
general_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 requests per minute
auth_limiter = RateLimiter(max_requests=10, window_seconds=60)      # 10 auth requests per minute
api_limiter = RateLimiter(max_requests=200, window_seconds=60)      # 200 API requests per minute


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (common in production)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = get_client_ip(request)
    path = request.url.path
    
    # Choose appropriate rate limiter based on endpoint
    if path.startswith("/auth"):
        limiter = auth_limiter
        limit_type = "authentication"
    elif path.startswith("/docs") or path.startswith("/redoc"):
        # No rate limiting for docs in development
        return await call_next(request)
    else:
        limiter = general_limiter
        limit_type = "general"
    
    # Check rate limit
    if not limiter.is_allowed(client_ip):
        reset_time = limiter.get_reset_time(client_ip)
        
        logger.warning(f"Rate limit exceeded for {client_ip} on {path} ({limit_type})")
        
        return JSONResponse(
            status_code=429,
            content={
                "detail": f"Rate limit exceeded for {limit_type} requests",
                "retry_after": reset_time - int(time.time())
            },
            headers={
                "Retry-After": str(reset_time - int(time.time())),
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Window": str(limiter.window_seconds),
                "X-RateLimit-Reset": str(reset_time)
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers to successful responses
    remaining = limiter.max_requests - len(limiter.requests[client_ip])
    reset_time = limiter.get_reset_time(client_ip)
    
    response.headers["X-RateLimit-Limit"] = str(limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    
    return response


async def security_logging_middleware(request: Request, call_next):
    """Security event logging middleware"""
    start_time = time.time()
    client_ip = get_client_ip(request)
    
    # Log security-relevant requests
    if any(path in request.url.path for path in ["/auth", "/users", "/admin"]):
        logger.info(f"Security request: {client_ip} {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log failed authentication attempts
    if request.url.path.startswith("/auth") and response.status_code >= 400:
        logger.warning(f"Failed auth attempt: {client_ip} {request.method} {request.url.path} - {response.status_code}")
    
    # Log slow requests (potential DoS)
    request_time = time.time() - start_time
    if request_time > 5.0:  # 5 seconds
        logger.warning(f"Slow request: {client_ip} {request.method} {request.url.path} - {request_time:.2f}s")
    
    return response


class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_csp_policy(environment: str = "production") -> str:
        """Get Content Security Policy based on environment"""
        if environment == "development":
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss: https:; "
            )
        else:
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://generativelanguage.googleapis.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
    
    @staticmethod
    def get_permissions_policy() -> str:
        """Get Permissions Policy header"""
        return (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=(), "
            "fullscreen=(self), "
            "sync-xhr=()"
        )


def validate_cors_origins(origins: list) -> list:
    """Validate and sanitize CORS origins"""
    valid_origins = []
    
    for origin in origins:
        # Remove trailing slashes
        origin = origin.rstrip('/')
        
        # Validate format
        if origin.startswith(('http://', 'https://')):
            valid_origins.append(origin)
        elif origin == "localhost" or origin.startswith("localhost:"):
            valid_origins.append(f"http://{origin}")
        else:
            logger.warning(f"Invalid CORS origin format: {origin}")
    
    return valid_origins