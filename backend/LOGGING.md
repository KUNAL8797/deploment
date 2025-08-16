# Logging and Error Handling Guide

## Logging Configuration

### 1. Log Levels

The application supports standard Python logging levels:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause system failure

### 2. Environment-Based Configuration

#### Development Environment

- **Format**: Colored console output with timestamps
- **Level**: DEBUG (configurable via LOG_LEVEL)
- **Output**: Console only
- **Features**: Full stack traces, detailed error messages

#### Production Environment

- **Format**: Structured JSON logging
- **Level**: INFO (configurable via LOG_LEVEL)
- **Output**: Console + rotating log files
- **Features**: Structured data, log rotation, security-focused

### 3. Log Formats

#### Development Format

```
2025-01-16 12:00:00 - app.auth - INFO - User login successful: testuser
2025-01-16 12:00:01 - app.requests - WARNING - POST /auth/login - 401 (125.5ms)
```

#### Production Format (JSON)

```json
{
  "timestamp": "2025-01-16T12:00:00.000000",
  "level": "INFO",
  "logger": "app.auth",
  "message": "User login successful: testuser",
  "module": "auth",
  "function": "login_user",
  "line": 45,
  "user_id": "123",
  "client_ip": "192.168.1.1",
  "endpoint": "/auth/login",
  "method": "POST"
}
```

## Log Categories

### 1. Request Logs

**Logger**: `app.requests`
**Purpose**: HTTP request/response logging

```python
# Automatic logging via middleware
# Logs: method, path, status_code, response_time, client_ip
```

**Example Output**:

```json
{
  "timestamp": "2025-01-16T12:00:00.000000",
  "level": "INFO",
  "logger": "app.requests",
  "message": "POST /auth/login - 200 (125.5ms)",
  "method": "POST",
  "endpoint": "/auth/login",
  "status_code": 200,
  "response_time": 125.5,
  "client_ip": "192.168.1.1"
}
```

### 2. Authentication Logs

**Logger**: `app.auth`
**Purpose**: Authentication and authorization events

```python
from app.utils.logging import RequestLogger

# Log successful login
RequestLogger.log_auth_attempt(
    username="testuser",
    success=True,
    client_ip="192.168.1.1"
)

# Log failed login
RequestLogger.log_auth_attempt(
    username="testuser",
    success=False,
    client_ip="192.168.1.1",
    reason="Invalid password"
)
```

### 3. Security Logs

**Logger**: `app.security`
**Purpose**: Security-related events

```python
from app.utils.logging import RequestLogger

# Log security event
RequestLogger.log_security_event(
    event_type="rate_limit_exceeded",
    description="User exceeded login rate limit",
    client_ip="192.168.1.1",
    severity="medium"
)
```

**Severity Levels**:

- **critical**: Immediate action required
- **high**: Urgent attention needed
- **medium**: Should be investigated
- **low**: Informational

### 4. Error Logs

**Logger**: `app.errors`
**Purpose**: Application errors and exceptions

```python
from app.utils.logging import ErrorLogger

# Log general exception
try:
    # Some operation
    pass
except Exception as e:
    ErrorLogger.log_exception(
        exception=e,
        context={"operation": "user_creation"},
        user_id="123"
    )

# Log database error
ErrorLogger.log_database_error(
    operation="user_query",
    error=e,
    table="users",
    user_id="123"
)

# Log external API error
ErrorLogger.log_api_error(
    service="gemini_ai",
    error=e,
    endpoint="/generate",
    user_id="123"
)
```

### 5. Database Logs

**Logger**: `app.database`
**Purpose**: Database operations and errors

### 6. External API Logs

**Logger**: `app.external_api`
**Purpose**: External service interactions

## Error Handling

### 1. Custom Error Classes

#### APIError (Base Class)

```python
from app.utils.error_handlers import APIError

raise APIError(
    message="Operation failed",
    status_code=500,
    error_code="OPERATION_FAILED",
    details={"operation": "user_creation"}
)
```

#### Specific Error Types

```python
from app.utils.error_handlers import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ExternalServiceError
)

# Validation error
raise ValidationError(
    message="Invalid input data",
    details={"field": "email", "issue": "invalid format"}
)

# Authentication error
raise AuthenticationError("Invalid credentials")

# Authorization error
raise AuthorizationError("Insufficient permissions")

# Not found error
raise NotFoundError("User")

# Conflict error
raise ConflictError("Username already exists")

# Rate limit error
raise RateLimitError("Too many requests", retry_after=60)

# External service error
raise ExternalServiceError("gemini_ai", "Service unavailable")
```

### 2. Error Response Format

All errors return a standardized JSON response:

```json
{
  "error": {
    "message": "Validation error",
    "code": "VALIDATION_ERROR",
    "status_code": 422,
    "details": {
      "validation_errors": [
        {
          "field": "email",
          "message": "field required",
          "type": "value_error.missing"
        }
      ]
    },
    "request_id": "req_123456789"
  }
}
```

### 3. Error Handler Configuration

Error handlers are automatically configured in `main.py`:

```python
from app.utils.error_handlers import setup_error_handlers

# Set up all error handlers
setup_error_handlers(app)
```

**Handled Error Types**:

- Custom API errors
- HTTP exceptions
- Request validation errors
- Database errors
- General exceptions

### 4. Error Context Management

Use the `ErrorContext` context manager for operations that need error tracking:

```python
from app.utils.error_handlers import ErrorContext

async def create_user(user_data):
    with ErrorContext("user_creation", user_id=None, **user_data):
        # User creation logic
        user = User(**user_data)
        db.add(user)
        db.commit()
        return user
```

### 5. Error Handling Decorator

Use the `handle_errors` decorator for automatic error handling:

```python
from app.utils.error_handlers import handle_errors

@handle_errors("user_creation")
async def create_user(user_data):
    # User creation logic
    return user
```

## Log File Management

### 1. Log File Locations (Production)

```
logs/
├── app.log          # General application logs
├── app.log.1        # Rotated log file
├── app.log.2        # Rotated log file
├── error.log        # Error-only logs
├── error.log.1      # Rotated error log
└── error.log.2      # Rotated error log
```

### 2. Log Rotation

- **Application Logs**: 50MB max size, 3 backup files
- **Error Logs**: 10MB max size, 5 backup files
- **Automatic Rotation**: When size limit is reached

### 3. Log Retention

- **Development**: Logs are not persisted
- **Production**: Logs are kept for the rotation period
- **External Logging**: Consider using external log aggregation services

## Monitoring and Alerting

### 1. Log-Based Monitoring

Monitor logs for:

- High error rates
- Authentication failures
- Security events
- Performance issues
- External service failures

### 2. Log Aggregation

Recommended log aggregation services:

- **Papertrail**: Simple log aggregation
- **Loggly**: Advanced log analysis
- **ELK Stack**: Self-hosted solution
- **Datadog**: Comprehensive monitoring

### 3. Alert Configuration

Set up alerts for:

- Error rate > 5%
- Authentication failure rate > 10%
- Critical security events
- External service failures
- Database connection issues

## Best Practices

### 1. Logging Best Practices

- **Use appropriate log levels**
- **Include relevant context**
- **Don't log sensitive information**
- **Use structured logging in production**
- **Log both successes and failures**

### 2. Error Handling Best Practices

- **Use specific error types**
- **Provide meaningful error messages**
- **Include relevant context**
- **Don't expose internal details in production**
- **Log all errors for debugging**

### 3. Security Considerations

- **Never log passwords or tokens**
- **Sanitize user input in logs**
- **Use log levels to control information exposure**
- **Monitor logs for security events**
- **Implement log access controls**

## Configuration

### 1. Environment Variables

```bash
# Log level configuration
LOG_LEVEL=INFO

# Environment (affects log format)
ENVIRONMENT=production
```

### 2. Logger Configuration

```python
# Configure specific loggers
logging.getLogger('app.auth').setLevel(logging.INFO)
logging.getLogger('app.security').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
```

### 3. Custom Logger Usage

```python
import logging

# Get logger for your module
logger = logging.getLogger(__name__)

# Log messages
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")

# Log with extra context
logger.info(
    "User action completed",
    extra={
        "user_id": "123",
        "action": "profile_update",
        "client_ip": "192.168.1.1"
    }
)
```

## Troubleshooting

### 1. Common Issues

**Logs Not Appearing**

- Check log level configuration
- Verify logger names
- Check file permissions (production)

**JSON Format Issues**

- Verify environment is set to production
- Check for logging configuration conflicts

**Performance Impact**

- Reduce log level in production
- Use asynchronous logging for high-volume applications
- Monitor log file sizes

### 2. Debugging Commands

```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# View JSON logs with jq
tail -f logs/app.log | jq .

# Monitor specific logger
grep "app.auth" logs/app.log
```

### 3. Log Analysis

```bash
# Count error types
grep "ERROR" logs/app.log | jq -r '.error_code' | sort | uniq -c

# Monitor response times
grep "app.requests" logs/app.log | jq -r '.response_time' | sort -n

# Track authentication failures
grep "app.auth" logs/app.log | jq 'select(.auth_success == false)'
```
