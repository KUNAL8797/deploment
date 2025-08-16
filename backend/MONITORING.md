# Monitoring and Health Checks Guide

## Health Check Endpoints

### 1. Basic Health Check - `/health`

**Purpose**: Quick health check for load balancers and basic monitoring
**Response Time**: < 100ms
**Usage**: Frequent monitoring (every 30 seconds)

```bash
curl https://your-backend.onrender.com/health
```

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T12:00:00.000000",
  "service": "AI Innovation Idea Incubator",
  "version": "1.0.0",
  "environment": "production",
  "database": "healthy"
}
```

### 2. Detailed Health Check - `/health/detailed`

**Purpose**: Comprehensive health check with detailed metrics
**Response Time**: < 2 seconds
**Usage**: Periodic monitoring (every 5 minutes)

```bash
curl https://your-backend.onrender.com/health/detailed
```

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T12:00:00.000000",
  "service": "AI Innovation Idea Incubator",
  "version": "1.0.0",
  "environment": "production",
  "check_duration_ms": 45.67,
  "uptime": {
    "uptime_seconds": 3600.0,
    "uptime_human": "1:00:00",
    "started_at": "2025-01-16T11:00:00.000000"
  },
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12.34,
      "last_check": "2025-01-16T12:00:00.000000",
      "error": null
    },
    "gemini_api": {
      "status": "configured",
      "last_check": "2025-01-16T12:00:00.000000",
      "error": null,
      "api_key_length": 39
    },
    "redis": {
      "status": "not_configured",
      "last_check": "2025-01-16T12:00:00.000000",
      "error": "Redis not configured"
    }
  },
  "system": {
    "cpu": {
      "usage_percent": 15.2,
      "count": 2
    },
    "memory": {
      "total_mb": 512.0,
      "available_mb": 256.0,
      "used_percent": 50.0
    },
    "disk": {
      "total_gb": 10.0,
      "free_gb": 7.5,
      "used_percent": 25.0
    }
  }
}
```

### 3. Service Status - `/status`

**Purpose**: Simple status check without dependencies
**Response Time**: < 10ms
**Usage**: Basic availability monitoring

```bash
curl https://your-backend.onrender.com/status
```

**Response**:

```json
{
  "status": "running",
  "service": "AI Innovation Idea Incubator",
  "version": "1.0.0",
  "timestamp": "2025-01-16T12:00:00.000000"
}
```

## Metrics Endpoint

### Application Metrics - `/metrics`

**Purpose**: Application performance and usage metrics
**Usage**: Performance monitoring and analytics

```bash
curl https://your-backend.onrender.com/metrics
```

**Response**:

```json
{
  "service": "AI Innovation Idea Incubator",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-01-16T12:00:00.000000",
  "uptime": {
    "uptime_seconds": 3600.0,
    "uptime_human": "1:00:00",
    "started_at": "2025-01-16T11:00:00.000000"
  },
  "application": {
    "requests": {
      "total": 1500,
      "errors": 25,
      "error_rate": 1.67,
      "requests_per_second": 0.42
    },
    "response_times": {
      "average_ms": 125.5,
      "max_ms": 2500.0,
      "min_ms": 15.2
    },
    "uptime_seconds": 3600.0
  }
}
```

## Health Check Status Codes

### HTTP Status Codes

- **200 OK**: Service is healthy
- **503 Service Unavailable**: Service is unhealthy
- **500 Internal Server Error**: Health check failed

### Health Status Values

- **healthy**: All critical services are working
- **unhealthy**: One or more critical services are failing
- **degraded**: Non-critical services are failing (future use)

## Monitoring Setup

### 1. Render Built-in Monitoring

Render provides built-in monitoring:

- **Service Health**: Automatic health checks
- **Logs**: Real-time log streaming
- **Metrics**: CPU, memory, and network usage
- **Alerts**: Email notifications for issues

### 2. External Monitoring Services

#### UptimeRobot (Free)

```bash
# Monitor endpoints
https://your-backend.onrender.com/health
https://your-backend.onrender.com/status
```

**Configuration**:

- Check interval: 5 minutes
- Timeout: 30 seconds
- Alert contacts: Email, SMS, Slack

#### Pingdom

```bash
# HTTP check
URL: https://your-backend.onrender.com/health
Expected: "healthy"
Interval: 1 minute
```

### 3. Custom Monitoring Scripts

#### Simple Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Simple health monitoring

BACKEND_URL="https://your-backend.onrender.com"
WEBHOOK_URL="your-slack-webhook-url"

# Check health
HEALTH=$(curl -s "$BACKEND_URL/health" | jq -r '.status')

if [ "$HEALTH" != "healthy" ]; then
    # Send alert
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚨 Backend health check failed: '$HEALTH'"}' \
        "$WEBHOOK_URL"
fi
```

#### Python Monitoring Script

```python
#!/usr/bin/env python3
import requests
import time
import logging
from datetime import datetime

def check_health(url):
    try:
        response = requests.get(f"{url}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'healthy'
        return False
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return False

def monitor_service():
    backend_url = "https://your-backend.onrender.com"

    while True:
        if not check_health(backend_url):
            logging.error(f"Service unhealthy at {datetime.now()}")
            # Send alert here

        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor_service()
```

## Alerting Configuration

### 1. Render Alerts

Configure in Render dashboard:

- **Service Down**: When service stops responding
- **High CPU**: When CPU usage > 80%
- **High Memory**: When memory usage > 90%
- **Deploy Failures**: When deployments fail

### 2. Custom Alerts

#### Slack Integration

```python
import requests

def send_slack_alert(message):
    webhook_url = "your-slack-webhook-url"
    payload = {"text": f"🚨 {message}"}
    requests.post(webhook_url, json=payload)

# Usage
send_slack_alert("Backend service is unhealthy")
```

#### Email Alerts

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = "alerts@yourdomain.com"
    msg['To'] = "admin@yourdomain.com"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("your-email", "your-password")
    server.send_message(msg)
    server.quit()
```

## Performance Monitoring

### 1. Response Time Monitoring

Monitor these metrics:

- **Average Response Time**: Should be < 200ms
- **95th Percentile**: Should be < 500ms
- **Maximum Response Time**: Should be < 2000ms

### 2. Error Rate Monitoring

Track error rates:

- **Overall Error Rate**: Should be < 1%
- **Authentication Errors**: Monitor for attacks
- **Database Errors**: Monitor for connectivity issues

### 3. Resource Usage Monitoring

Monitor system resources:

- **CPU Usage**: Should be < 70% average
- **Memory Usage**: Should be < 80%
- **Disk Usage**: Should be < 90%

## Log Monitoring

### 1. Application Logs

Monitor for:

- Error patterns
- Security events
- Performance issues
- Unusual activity

### 2. Log Aggregation

Use log aggregation services:

- **Render Logs**: Built-in log streaming
- **Papertrail**: Log aggregation and search
- **Loggly**: Log management and analysis

### 3. Log Alerts

Set up alerts for:

- High error rates
- Security events
- Performance degradation
- Service failures

## Monitoring Dashboard

### 1. Grafana Dashboard

Create dashboards for:

- Service health status
- Response time trends
- Error rate trends
- Resource usage
- Request volume

### 2. Custom Dashboard

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Service Monitor</title>
    <script>
      async function checkHealth() {
        try {
          const response = await fetch("/health");
          const data = await response.json();
          document.getElementById("status").textContent = data.status;
          document.getElementById("status").className = data.status;
        } catch (error) {
          document.getElementById("status").textContent = "error";
          document.getElementById("status").className = "error";
        }
      }

      setInterval(checkHealth, 30000); // Check every 30 seconds
      checkHealth(); // Initial check
    </script>
    <style>
      .healthy {
        color: green;
      }
      .unhealthy {
        color: red;
      }
      .error {
        color: orange;
      }
    </style>
  </head>
  <body>
    <h1>Service Status</h1>
    <p>Status: <span id="status">checking...</span></p>
  </body>
</html>
```

## Troubleshooting

### Common Issues

**Health Check Timeouts**

- Increase timeout values
- Check database connectivity
- Monitor system resources

**False Positive Alerts**

- Adjust alert thresholds
- Add alert delays
- Implement alert suppression

**Missing Metrics**

- Check middleware configuration
- Verify endpoint accessibility
- Review log outputs

### Debugging Commands

```bash
# Test health endpoints
curl -v https://your-backend.onrender.com/health
curl -v https://your-backend.onrender.com/health/detailed
curl -v https://your-backend.onrender.com/metrics

# Check response times
time curl https://your-backend.onrender.com/health

# Monitor continuously
watch -n 30 'curl -s https://your-backend.onrender.com/health | jq .status'
```

## Best Practices

### 1. Health Check Design

- Keep basic health checks fast (< 100ms)
- Test critical dependencies only
- Return appropriate HTTP status codes
- Include meaningful error messages

### 2. Monitoring Strategy

- Use multiple monitoring services
- Set up redundant alerts
- Monitor both technical and business metrics
- Regular review and updates

### 3. Alert Management

- Avoid alert fatigue
- Use appropriate alert levels
- Include actionable information
- Test alert mechanisms regularly
