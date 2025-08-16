"""
Health check and monitoring utilities
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import text
from ..database import SessionLocal
from ..config import settings

logger = logging.getLogger(__name__)

# Global variables for tracking
_start_time = time.time()
_health_checks = {
    "database": {"status": "unknown", "last_check": None, "error": None},
    "gemini_api": {"status": "unknown", "last_check": None, "error": None},
    "redis": {"status": "unknown", "last_check": None, "error": None},
}


class HealthChecker:
    """Comprehensive health checking system"""
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            db = SessionLocal()
            
            # Test basic connectivity
            db.execute(text("SELECT 1"))
            
            # Test table access
            db.execute(text("SELECT COUNT(*) FROM users LIMIT 1"))
            
            # Test write capability (if needed)
            # db.execute(text("CREATE TEMP TABLE health_test (id INTEGER)"))
            # db.execute(text("DROP TABLE health_test"))
            
            db.close()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "last_check": datetime.utcnow().isoformat(),
                "error": None
            }
            
            _health_checks["database"] = result
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Database health check failed: {error_msg}")
            
            result = {
                "status": "unhealthy",
                "response_time_ms": None,
                "last_check": datetime.utcnow().isoformat(),
                "error": error_msg
            }
            
            _health_checks["database"] = result
            return result
    
    @staticmethod
    def check_gemini_api() -> Dict[str, Any]:
        """Check Gemini API configuration and connectivity"""
        try:
            if not settings.gemini_api_key:
                result = {
                    "status": "not_configured",
                    "last_check": datetime.utcnow().isoformat(),
                    "error": "API key not configured"
                }
            else:
                # Basic configuration check
                result = {
                    "status": "configured",
                    "last_check": datetime.utcnow().isoformat(),
                    "error": None,
                    "api_key_length": len(settings.gemini_api_key)
                }
            
            _health_checks["gemini_api"] = result
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API health check failed: {error_msg}")
            
            result = {
                "status": "error",
                "last_check": datetime.utcnow().isoformat(),
                "error": error_msg
            }
            
            _health_checks["gemini_api"] = result
            return result
    
    @staticmethod
    def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity (if configured)"""
        try:
            if not hasattr(settings, 'redis_url') or not settings.redis_url:
                return {
                    "status": "not_configured",
                    "last_check": datetime.utcnow().isoformat(),
                    "error": "Redis not configured"
                }
            
            # If Redis is configured, you would test connectivity here
            # For now, just return configured status
            result = {
                "status": "configured",
                "last_check": datetime.utcnow().isoformat(),
                "error": None
            }
            
            _health_checks["redis"] = result
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Redis health check failed: {error_msg}")
            
            result = {
                "status": "error",
                "last_check": datetime.utcnow().isoformat(),
                "error": error_msg
            }
            
            _health_checks["redis"] = result
            return result
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "available_mb": round(memory.available / 1024 / 1024, 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                }
            }
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_uptime() -> Dict[str, Any]:
        """Get application uptime"""
        uptime_seconds = time.time() - _start_time
        uptime_delta = timedelta(seconds=uptime_seconds)
        
        return {
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_human": str(uptime_delta),
            "started_at": datetime.fromtimestamp(_start_time).isoformat()
        }
    
    @classmethod
    def comprehensive_health_check(cls) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        # Run all health checks
        db_health = cls.check_database()
        gemini_health = cls.check_gemini_api()
        redis_health = cls.check_redis()
        system_metrics = cls.get_system_metrics()
        uptime_info = cls.get_uptime()
        
        # Determine overall status
        critical_services = [db_health]
        overall_healthy = all(check["status"] == "healthy" for check in critical_services)
        
        check_duration = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "check_duration_ms": round(check_duration, 2),
            "uptime": uptime_info,
            "checks": {
                "database": db_health,
                "gemini_api": gemini_health,
                "redis": redis_health
            },
            "system": system_metrics
        }
    
    @classmethod
    def quick_health_check(cls) -> Dict[str, Any]:
        """Quick health check for frequent monitoring"""
        try:
            # Quick database check
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_healthy = True
        except Exception:
            db_healthy = False
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "database": "healthy" if db_healthy else "unhealthy"
        }


class MetricsCollector:
    """Application metrics collection"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.start_time = time.time()
    
    def record_request(self, response_time: float, status_code: int):
        """Record request metrics"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if status_code >= 400:
            self.error_count += 1
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        uptime = time.time() - self.start_time
        
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            max_response_time = max(self.response_times)
            min_response_time = min(self.response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        return {
            "requests": {
                "total": self.request_count,
                "errors": self.error_count,
                "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
                "requests_per_second": self.request_count / uptime if uptime > 0 else 0
            },
            "response_times": {
                "average_ms": round(avg_response_time * 1000, 2),
                "max_ms": round(max_response_time * 1000, 2),
                "min_ms": round(min_response_time * 1000, 2)
            },
            "uptime_seconds": round(uptime, 2)
        }


# Global metrics collector
metrics_collector = MetricsCollector()