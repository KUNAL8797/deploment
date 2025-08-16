"""
Enhanced logging configuration for production deployment
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any
import json
from ..config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'client_ip'):
            log_entry['client_ip'] = record.client_ip
        
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add stack trace if present
        if record.stack_info:
            log_entry['stack_trace'] = record.stack_info
        
        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        if not sys.stdout.isatty():
            # No colors for non-terminal output
            return super().format(record)
        
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        return super().format(record)


def setup_logging():
    """Configure logging for the application"""
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.is_production:
        # JSON formatter for production
        console_formatter = JSONFormatter()
    else:
        # Colored formatter for development
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler for errors (if in production)
    if settings.is_production:
        try:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            # Error file handler
            error_handler = logging.handlers.RotatingFileHandler(
                'logs/error.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(error_handler)
            
            # Application file handler
            app_handler = logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=50*1024*1024,  # 50MB
                backupCount=3
            )
            app_handler.setLevel(logging.INFO)
            app_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(app_handler)
            
        except Exception as e:
            # If file logging fails, log to console
            root_logger.error(f"Failed to setup file logging: {e}")
    
    # Configure specific loggers
    configure_loggers()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {settings.log_level}, Environment: {settings.environment}")


def configure_loggers():
    """Configure specific loggers"""
    
    # Reduce noise from third-party libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)
    
    # SQLAlchemy logging
    if settings.is_production:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # HTTP client logging
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    # Application loggers
    logging.getLogger('app').setLevel(logging.INFO)
    logging.getLogger('app.auth').setLevel(logging.INFO)
    logging.getLogger('app.security').setLevel(logging.INFO)
    logging.getLogger('app.monitoring').setLevel(logging.INFO)


class RequestLogger:
    """Request logging utility"""
    
    @staticmethod
    def log_request(
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        client_ip: str = None,
        user_id: str = None,
        request_id: str = None
    ):
        """Log HTTP request"""
        logger = logging.getLogger('app.requests')
        
        extra = {
            'method': method,
            'endpoint': path,
            'status_code': status_code,
            'response_time': round(response_time * 1000, 2),  # Convert to ms
        }
        
        if client_ip:
            extra['client_ip'] = client_ip
        
        if user_id:
            extra['user_id'] = user_id
        
        if request_id:
            extra['request_id'] = request_id
        
        # Determine log level based on status code
        if status_code >= 500:
            logger.error(f"{method} {path} - {status_code} ({extra['response_time']}ms)", extra=extra)
        elif status_code >= 400:
            logger.warning(f"{method} {path} - {status_code} ({extra['response_time']}ms)", extra=extra)
        else:
            logger.info(f"{method} {path} - {status_code} ({extra['response_time']}ms)", extra=extra)
    
    @staticmethod
    def log_auth_attempt(
        username: str,
        success: bool,
        client_ip: str = None,
        reason: str = None
    ):
        """Log authentication attempt"""
        logger = logging.getLogger('app.auth')
        
        extra = {
            'username': username,
            'auth_success': success,
        }
        
        if client_ip:
            extra['client_ip'] = client_ip
        
        if reason:
            extra['reason'] = reason
        
        if success:
            logger.info(f"Successful login for user: {username}", extra=extra)
        else:
            logger.warning(f"Failed login attempt for user: {username} - {reason}", extra=extra)
    
    @staticmethod
    def log_security_event(
        event_type: str,
        description: str,
        client_ip: str = None,
        user_id: str = None,
        severity: str = "medium"
    ):
        """Log security event"""
        logger = logging.getLogger('app.security')
        
        extra = {
            'event_type': event_type,
            'severity': severity,
        }
        
        if client_ip:
            extra['client_ip'] = client_ip
        
        if user_id:
            extra['user_id'] = user_id
        
        # Determine log level based on severity
        if severity == "critical":
            logger.critical(f"Security event: {event_type} - {description}", extra=extra)
        elif severity == "high":
            logger.error(f"Security event: {event_type} - {description}", extra=extra)
        elif severity == "medium":
            logger.warning(f"Security event: {event_type} - {description}", extra=extra)
        else:
            logger.info(f"Security event: {event_type} - {description}", extra=extra)


class ErrorLogger:
    """Error logging utility"""
    
    @staticmethod
    def log_exception(
        exception: Exception,
        context: Dict[str, Any] = None,
        user_id: str = None,
        request_id: str = None
    ):
        """Log exception with context"""
        logger = logging.getLogger('app.errors')
        
        extra = {
            'exception_type': type(exception).__name__,
        }
        
        if context:
            extra.update(context)
        
        if user_id:
            extra['user_id'] = user_id
        
        if request_id:
            extra['request_id'] = request_id
        
        logger.error(f"Exception occurred: {str(exception)}", exc_info=True, extra=extra)
    
    @staticmethod
    def log_database_error(
        operation: str,
        error: Exception,
        table: str = None,
        user_id: str = None
    ):
        """Log database error"""
        logger = logging.getLogger('app.database')
        
        extra = {
            'operation': operation,
            'error_type': type(error).__name__,
        }
        
        if table:
            extra['table'] = table
        
        if user_id:
            extra['user_id'] = user_id
        
        logger.error(f"Database error during {operation}: {str(error)}", exc_info=True, extra=extra)
    
    @staticmethod
    def log_api_error(
        service: str,
        error: Exception,
        endpoint: str = None,
        user_id: str = None
    ):
        """Log external API error"""
        logger = logging.getLogger('app.external_api')
        
        extra = {
            'service': service,
            'error_type': type(error).__name__,
        }
        
        if endpoint:
            extra['endpoint'] = endpoint
        
        if user_id:
            extra['user_id'] = user_id
        
        logger.error(f"External API error ({service}): {str(error)}", exc_info=True, extra=extra)


# Initialize logging when module is imported
setup_logging()