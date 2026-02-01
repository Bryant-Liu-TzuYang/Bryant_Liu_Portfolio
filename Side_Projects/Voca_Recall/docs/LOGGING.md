# Logging System Documentation

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
  - [Backend Logging](#backend-logging)
  - [Frontend Logging](#frontend-logging)
- [Configuration](#configuration)
  - [Backend](#backend-backendapplogging_configpy)
  - [Frontend](#frontend-env)
- [Log Files](#log-files)
- [Usage Examples](#usage-examples)
  - [Backend Logging](#backend-logging-1)
  - [Request Tracking](#request-tracking)
  - [Frontend Logging](#frontend-logging-1)
- [Log Levels](#log-levels)
- [Environment-Specific Settings](#environment-specific-settings)
  - [Development](#development)
  - [Production](#production)
- [Log Analysis & Monitoring](#log-analysis--monitoring)
  - [Common Queries](#common-queries)
  - [Key Metrics to Monitor](#key-metrics-to-monitor)
  - [Integration Options](#integration-options)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Performance Tips](#performance-tips)
- [Security Best Practices](#security-best-practices)
- [Example Log Outputs](#example-log-outputs)
- [Quick Reference](#quick-reference)

## Overview

Comprehensive logging system for the Voca Recaller application with structured logs, request tracking, and automatic error capture for both backend (Python/Flask) and frontend (React/JavaScript).

## Key Features

### Backend Logging
- **Structured logs** with timestamps, context, and unique request IDs
- **Timezone-aware** timestamps (Asia/Taipei)
- **File rotation** (10MB max, 5 backup files)
- **Request tracking** across entire request lifecycle
- **Performance monitoring** with response time tracking
- **Colored console output** for development
- **Separate files** for backend and frontend logs

### Frontend Logging
- **Context-aware** logging by component
- **Backend forwarding** for warnings and errors
- **API call tracking** with automatic logging
- **Development/Production modes** with different behaviors
- **Connection testing** and retry logic

## Configuration

### Backend (`backend/app/logging_config.py`)
```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Send logs to stdout (for Docker containers)
LOG_TO_STDOUT=true
```

### Frontend (`.env`)
```bash
# Set log level (debug, info, warn, error)
REACT_APP_LOG_LEVEL=info

# API base URL
REACT_APP_API_URL=http://localhost:5000

# Enable backend forwarding
REACT_APP_SEND_LOGS_TO_SERVER=true
```

## Log Files

Location: `backend/logs/` directory

**Backend logs:**
- `notion-email-backend-YYYY-MM-DD.log` - All backend logs (INFO+)
- `notion-email-backend-error-YYYY-MM-DD.log` - Backend errors only

**Frontend logs** (forwarded to backend):
- `notion-email-frontend-YYYY-MM-DD.log` - All frontend logs (INFO+)
- `notion-email-frontend-error-YYYY-MM-DD.log` - Frontend errors only

## Usage Examples

### Backend Logging

**Basic logging:**
```python
from app.logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

**API endpoint logging:**
```python
from app.middleware import log_api_call

@app.route('/api/example')
@log_api_call("Example API operation")
def example_endpoint():
    # Your code here
    pass
```

**Function logging:**
```python
from app.middleware import log_function_call

@log_function_call("Email sending")
def send_email(to_email, subject, content):
    # Your code here
    pass
```

**Database operation logging:**
```python
from app.middleware import log_database_operations

@log_database_operations
def create_user(user_data):
    # Your database code here
    pass
```

### Request Tracking

Each HTTP request gets a unique 8-character request ID:

```
[2025-12-08 10:30:15] INFO in middleware: [a1b2c3d4] GET /api/user/profile - IP: 127.0.0.1 - User: john@example.com
[2025-12-08 10:30:15] INFO in user: [a1b2c3d4] Starting API operation: Get user profile
[2025-12-08 10:30:15] INFO in user: [a1b2c3d4] API operation completed in 45.23ms
[2025-12-08 10:30:15] INFO in middleware: [a1b2c3d4] Response: 200 - Time: 47.85ms
```

### Frontend Logging

**Basic logging:**
```javascript
import logger from '../utils/logger';

logger.debug("Debug message", { key: "value" });
logger.info("Info message", { userId: 123 });
logger.warn("Warning message", { component: "Dashboard" });
logger.error("Error message", error, { context: "login" });
```

**Context-specific logging:**
```javascript
import { authLogger, apiLogger, dashboardLogger } from '../utils/logger';

authLogger.info("User logged in", { userId: user.id });
apiLogger.apiCall("GET", "/api/user/profile");
dashboardLogger.userAction("Export data", { format: "csv" });
```

**API calls** (automatically logged by `apiService`):
```javascript
import apiService from '../utils/apiService';

const response = await apiService.get('/api/user/profile');
// Auto-logs: API GET /api/user/profile - 200 (response time)
```

## Log Levels

| Level | Backend | Frontend | Usage |
|-------|---------|----------|-------|
| **DEBUG** | Detailed diagnostics | Dev only | Troubleshooting |
| **INFO** | Application flow | General events | Normal operations |
| **WARNING/WARN** | Potentially harmful | Warnings | Issues to watch |
| **ERROR** | Errors (app continues) | Error conditions | Failures |
| **CRITICAL** | Serious errors | N/A | App may abort |

## Environment-Specific Settings

### Development
```bash
# Backend
LOG_LEVEL=DEBUG
LOG_TO_STDOUT=true

# Frontend
REACT_APP_LOG_LEVEL=debug
REACT_APP_SEND_LOGS_TO_SERVER=true
```

### Production
```bash
# Backend
LOG_LEVEL=WARNING
LOG_TO_STDOUT=true

# Frontend
REACT_APP_LOG_LEVEL=warn
REACT_APP_SEND_LOGS_TO_SERVER=true
```

## Log Analysis & Monitoring

### Common Queries

**Find user-specific logs:**
```bash
grep "User: john@example.com" backend/logs/notion-email-backend-*.log
```

**Track specific request:**
```bash
grep "a1b2c3d4" backend/logs/notion-email-backend-*.log
```

**View today's errors:**
```bash
cat backend/logs/notion-email-backend-error-$(date +%Y-%m-%d).log
```

**Check email-related logs:**
```bash
grep -i "send_email\|Processing email service" backend/logs/notion-email-backend-$(date +%Y-%m-%d).log
```

**Monitor API failures:**
```bash
grep "API.*failed\|Response: 5[0-9][0-9]" backend/logs/notion-email-backend-*.log
```

### Key Metrics to Monitor
- Error rate by endpoint
- Average response times
- Failed login attempts
- Database operation performance
- Email delivery success/failure rates
- Request volume patterns

### Integration Options

**Log Aggregation Services:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd for log collection
- Splunk for enterprise analysis
- DataDog for monitoring
- New Relic for APM

**Docker integration example:**
```yaml
services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.15.0
    volumes:
      - ./backend/logs:/var/log/app:ro
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Log files not created | Check `backend/logs/` directory permissions |
| No console output | Verify `LOG_LEVEL` environment variable |
| Too many logs | Increase log level (INFO → WARNING → ERROR) |
| Missing request IDs | Ensure middleware is registered |
| High disk usage | Check log rotation (10MB max per file) |

### Performance Tips
- Logging adds minimal overhead (~1-2ms per request)
- File I/O is the main performance factor
- Use appropriate log levels (WARNING in production)
- Monitor log file sizes and rotation

## Security Best Practices

**Never log:**
- Passwords or authentication tokens
- Full credit card numbers
- Personal identification numbers (SSN, etc.)
- API keys or secrets

**Always:**
- Sanitize user input before logging
- Restrict log file access in production
- Implement log retention policies
- Use structured logging for consistency

## Example Log Outputs

**Backend request flow:**
```
[2025-12-08 10:30:15] INFO in middleware: [a1b2c3d4] POST /api/auth/login - IP: 127.0.0.1 - User: Anonymous
[2025-12-08 10:30:15] INFO in auth: [a1b2c3d4] Starting API operation: User login
[2025-12-08 10:30:15] INFO in auth: [a1b2c3d4] User login successful for john@example.com
[2025-12-08 10:30:15] INFO in auth: [a1b2c3d4] API operation completed in 234.56ms
[2025-12-08 10:30:15] INFO in middleware: [a1b2c3d4] Response: 200 - Time: 237.42ms
```

**Frontend logs:**
```
[10:30:15] [API] INFO: API POST /api/auth/login
[10:30:15] [API] INFO: API POST /api/auth/login - 200 (245ms)
[10:30:15] [Auth] INFO: User logged in { userId: 123, email: "john@example.com" }
```

## Quick Reference

### View Logs
```bash
# Today's backend logs
cat backend/logs/notion-email-backend-$(date +%Y-%m-%d).log

# Today's errors
cat backend/logs/notion-email-backend-error-$(date +%Y-%m-%d).log

# Follow logs in real-time
tail -f backend/logs/notion-email-backend-$(date +%Y-%m-%d).log

# Last 50 lines
tail -50 backend/logs/notion-email-backend-$(date +%Y-%m-%d).log
```

### Container Logs
```bash
# Backend container
docker logs voca_recaller_backend --tail 50

# Celery worker
docker logs voca_recaller_celery --tail 50

# Celery beat scheduler
docker logs voca_recaller_celery_beat --tail 50
```

## Related Documentation
- `EMAIL_SCHEDULING.md` - Email system logs and monitoring
- `check_email_status.sh` - Automated diagnostic script
