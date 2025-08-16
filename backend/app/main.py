from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from .routers import auth, ideas
from .database import engine, Base
from .config import settings
from .middleware.security import (
    rate_limit_middleware,
    security_logging_middleware,
    SecurityHeaders,
    validate_cors_origins
)
from .monitoring.health import metrics_collector
from .utils.logging import RequestLogger
from .utils.error_handlers import setup_error_handlers

# Load environment variables
load_dotenv()

# Import logging configuration (this sets up logging automatically)
from .utils import logging as app_logging

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
    AI-powered platform for refining and scoring business ideas using Gemini 2.5 Pro.
    
    ## Features
    - JWT Authentication with role-based access
    - Complete CRUD operations for innovation ideas
    - Text, enum, boolean, and calculated fields
    - Advanced filtering, pagination, and search
    - AI-powered idea refinement and feasibility scoring
    """,
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Security middleware for production
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.onrender.com", "localhost", "127.0.0.1"]
    )

# Metrics and logging middleware
@app.middleware("http")
async def metrics_and_logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.headers.get("X-Real-IP", "")
    if not client_ip and request.client:
        client_ip = request.client.host
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    metrics_collector.record_request(process_time, response.status_code)
    
    # Log request
    RequestLogger.log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        response_time=process_time,
        client_ip=client_ip
    )
    
    # Add response time header
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    
    return response

# Security middleware (order matters - add before CORS)
if settings.is_production:
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(security_logging_middleware)

# CORS configuration with validation
# Include the deployed frontend URL
cors_origins = settings.cors_origins + ["https://deployment-6p8p-git-main-kunals-projects-6bb44ad3.vercel.app"]
validated_origins = validate_cors_origins(cors_origins)
logger.info(f"CORS origins configured: {validated_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=validated_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Apply security headers in production
    if settings.is_production:
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Force HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = SecurityHeaders.get_csp_policy(settings.environment)
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = SecurityHeaders.get_permissions_policy()
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Cache control for sensitive endpoints
        if request.url.path.startswith("/auth") or request.url.path.startswith("/users"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
    
    return response

# Set up error handlers
setup_error_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(ideas.router, prefix="/ideas", tags=["ideas"])

@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs" if not settings.is_production else "Documentation disabled in production"
    }

@app.get("/health")
async def health_check():
    """Quick health check for load balancers and monitoring"""
    from .monitoring.health import HealthChecker
    
    health_data = HealthChecker.quick_health_check()
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return JSONResponse(content=health_data, status_code=status_code)

@app.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive health check with detailed metrics"""
    from .monitoring.health import HealthChecker
    
    health_data = HealthChecker.comprehensive_health_check()
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return JSONResponse(content=health_data, status_code=status_code)

@app.get("/metrics")
async def get_metrics():
    """Application metrics endpoint"""
    from .monitoring.health import metrics_collector, HealthChecker
    
    # Get basic metrics
    app_metrics = metrics_collector.get_metrics()
    uptime_info = HealthChecker.get_uptime()
    
    metrics_data = {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": uptime_info,
        "application": app_metrics
    }
    
    # Add system metrics in development
    if not settings.is_production:
        system_metrics = HealthChecker.get_system_metrics()
        metrics_data["system"] = system_metrics
    
    return metrics_data

@app.get("/status")
async def service_status():
    """Simple status endpoint for basic monitoring"""
    return {
        "status": "running",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }
