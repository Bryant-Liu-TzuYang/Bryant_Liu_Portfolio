# Logging System Documentation

This document describes the comprehensive logging system implemented in the Notion Email Vocabulary Recall application.

## Overview

The application uses a structured logging approach with different logging levels and contexts for both backend (Python/Flask) and frontend (React/JavaScript) components.

## Backend Logging (Python/Flask)

### Features

- **Structured Logging**: JSON-like structured logs with timestamps, context, and request IDs
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **File Rotation**: Automatic log file rotation (10MB max, 5 backup files)
- **Request Tracking**: Each HTTP request gets a unique ID for tracking
- **Error Handling**: Automatic exception logging with stack traces
- **Performance Monitoring**: Request/response time tracking
- **Database Operation Logging**: Special logging for database operations
- **Colored Console Output**: Development-friendly colored console logs

### Configuration

The logging system is configured in `backend/app/logging_config.py` and can be customized using environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Send logs to stdout (useful for Docker containers)
LOG_TO_STDOUT=true
```

### Log Files

Backend logs are written to the `backend/logs/` directory:

- `notion-email-backend-YYYY-MM-DD.log` - Backend application logs (INFO level and above)
- `notion-email-backend-error-YYYY-MM-DD.log` - Backend error logs only (ERROR level and above)
- `notion-email-frontend-YYYY-MM-DD.log` - Frontend logs forwarded from the web app (INFO level and above)
- `notion-email-frontend-error-YYYY-MM-DD.log` - Frontend error logs only (ERROR level and above)

### Usage Examples

#### Basic Logging
```python
from app.logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

#### API Endpoint Logging
```python
from app.middleware import log_api_call

@app.route('/api/example')
@log_api_call("Example API operation")
def example_endpoint():
    # Your code here
    pass
```

#### Function Logging
```python
from app.middleware import log_function_call

@log_function_call("Email sending")
def send_email(to_email, subject, content):
    # Your code here
    pass
```

#### Database Operation Logging
```python
from app.middleware import log_database_operations

@log_database_operations
def create_user(user_data):
    # Your database code here
    pass
```

### Request Tracking

Each HTTP request gets a unique 8-character request ID that appears in all related log entries:

```
[2025-07-31 10:30:15] INFO in middleware: [a1b2c3d4] GET /api/user/profile - IP: 127.0.0.1 - User: john@example.com - User-Agent: Mozilla/5.0...
[2025-07-31 10:30:15] INFO in user: [a1b2c3d4] Starting API operation: Get user profile
[2025-07-31 10:30:15] INFO in user: [a1b2c3d4] API operation Get user profile completed in 45.23ms
[2025-07-31 10:30:15] INFO in middleware: [a1b2c3d4] Response: 200 - Time: 47.85ms
```

## Frontend Logging (React/JavaScript)

### Features

- **Context-Aware Logging**: Different loggers for different parts of the app
- **Development/Production Modes**: Different behavior based on environment
- **API Call Logging**: Automatic logging of HTTP requests and responses
- **User Action Tracking**: Log user interactions and navigation
- **Error Boundary Integration**: Catch and log React errors
- **Backend Log Forwarding**: Send error and warning logs to backend for persistent storage
- **Connection Testing**: Built-in connection testing for backend logging
- **Retry Logic**: Automatic retry for failed log transmissions

### Configuration

Frontend logging is configured using environment variables:

```bash
# Set log level (debug, info, warn, error)
REACT_APP_LOG_LEVEL=info

# API base URL for sending logs to server
REACT_APP_API_URL=http://localhost:5000

# Enable/disable sending logs to backend server
REACT_APP_SEND_LOGS_TO_SERVER=true
```

### Backend Integration

Frontend logs (warning and error levels) are automatically sent to the backend and stored separately in:
- `backend/logs/notion-email-frontend-YYYY-MM-DD.log` (all frontend logs)
- `backend/logs/notion-email-frontend-error-YYYY-MM-DD.log` (error logs only)

Backend logs remain in:
- `backend/logs/notion-email-backend-YYYY-MM-DD.log` (backend application logs)
- `backend/logs/notion-email-backend-error-YYYY-MM-DD.log` (backend error logs)

Backend endpoints:
- `POST /api/frontend/logs` - Receive frontend logs
- `POST /api/frontend/logs/test` - Test connection
- `GET /api/frontend/logs/info` - Get log files information

### Usage Examples

#### Basic Logging
```javascript
import logger from '../utils/logger';

logger.debug("Debug message", { key: "value" });
logger.info("Info message", { userId: 123 });
logger.warn("Warning message", { component: "Dashboard" });
logger.error("Error message", error, { context: "login" });
```

#### Context-Specific Logging
```javascript
import { authLogger, apiLogger, dashboardLogger } from '../utils/logger';

// Auth-related logging
authLogger.info("User logged in", { userId: user.id });

// API-related logging (handled automatically by apiService)
apiLogger.apiCall("GET", "/api/user/profile");

// Dashboard-specific logging
dashboardLogger.userAction("Export data", { format: "csv" });
```

#### API Service Integration
```javascript
import apiService from '../utils/apiService';

// All API calls are automatically logged
const response = await apiService.get('/api/user/profile');
// Logs: API GET /api/user/profile
// Logs: API GET /api/user/profile - 200 (response time)
```

#### User Action Logging
```javascript
import logger from '../utils/logger';

const handleButtonClick = () => {
  logger.userAction("Export button clicked", { 
    page: "dashboard",
    exportType: "vocabulary"
  });
  
  // Your export logic here
};
```

## Log Levels

### Backend (Python)
- **DEBUG**: Detailed diagnostic information
- **INFO**: General application flow and important events
- **WARNING**: Potentially harmful situations
- **ERROR**: Error events that allow the application to continue
- **CRITICAL**: Serious errors that may abort the application

### Frontend (JavaScript)
- **debug**: Detailed diagnostic information (only in development)
- **info**: General application flow
- **warn**: Warning messages
- **error**: Error conditions

## Production Considerations

### Backend
- Set `LOG_LEVEL=WARNING` or `LOG_LEVEL=ERROR` in production to reduce log volume
- Use `LOG_TO_STDOUT=true` for containerized deployments
- Consider external log aggregation services (ELK stack, Fluentd, etc.)
- Monitor log file sizes and rotation

### Frontend
- Set `REACT_APP_LOG_LEVEL=warn` or `REACT_APP_LOG_LEVEL=error` in production
- Consider implementing log shipping to backend or external service
- Be mindful of browser console noise in production

## Monitoring and Alerting

### Log Monitoring
- Monitor error rates and patterns
- Set up alerts for critical errors
- Track API response times and failure rates
- Monitor user action patterns

### Key Metrics to Track
- Error rate by endpoint
- Average response times
- Failed login attempts
- Database operation performance
- Email delivery success/failure rates

## Log Analysis

### Common Log Patterns

#### Finding User-Specific Logs
```bash
# Backend logs for specific user
grep "User: john@example.com" backend/logs/notion-email-backend-*.log

# Frontend logs (if sending to server)
grep "userId.*123" backend/logs/notion-email-backend-*.log
```

#### Request Tracking
```bash
# Follow a specific request through all logs
grep "a1b2c3d4" backend/logs/notion-email-backend-*.log
```

#### Error Analysis
```bash
# All errors in the last day
grep "ERROR" backend/logs/notion-email-backend-error-$(date +%Y-%m-%d).log

# API failures
grep "API.*failed" backend/logs/notion-email-backend-*.log
```

## Troubleshooting

### Common Issues

1. **Log files not created**: Check directory permissions for `backend/logs/`
2. **No console output**: Verify `LOG_LEVEL` environment variable
3. **Too many logs**: Increase log level or check for log loops
4. **Missing request IDs**: Ensure middleware is properly registered

### Performance Impact

- Logging adds minimal overhead in production
- File I/O is the main performance consideration
- Use appropriate log levels to balance detail vs. performance
- Consider async logging for high-traffic applications

## Integration with External Services

### Log Aggregation Services
The logging system can be integrated with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd** for log collection and forwarding
- **Splunk** for enterprise log analysis
- **DataDog** for monitoring and alerting
- **New Relic** for application performance monitoring

### Example ELK Integration
```yaml
# docker-compose.yml addition for ELK
services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.15.0
    volumes:
      - ./backend/logs:/var/log/app:ro
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
```

## Security Considerations

- **PII Logging**: Avoid logging sensitive personal information
- **Token Logging**: Never log authentication tokens or passwords
- **Data Sanitization**: Sanitize user input before logging
- **Access Control**: Restrict access to log files in production
- **Log Retention**: Implement appropriate log retention policies

## Development Tips

1. Use structured logging with consistent field names
2. Include relevant context in log messages
3. Use appropriate log levels consistently
4. Test logging in both development and production environments
5. Consider log message readability for future debugging
6. Use request IDs to trace operations across services
7. Monitor log file growth and rotation
8. Implement log-based monitoring and alerting

## Example Log Outputs

### Backend Request Flow
```
[2025-07-31 10:30:15] INFO in middleware: [a1b2c3d4] POST /api/auth/login - IP: 127.0.0.1 - User: Anonymous - User-Agent: Mozilla/5.0...
[2025-07-31 10:30:15] INFO in auth: [a1b2c3d4] Starting API operation: User login
[2025-07-31 10:30:15] INFO in auth: [a1b2c3d4] User login successful for john@example.com
[2025-07-31 10:30:15] INFO in auth: [a1b2c3d4] API operation User login completed in 234.56ms
[2025-07-31 10:30:15] INFO in middleware: [a1b2c3d4] Response: 200 - Time: 237.42ms
```

### Frontend API Call
```
[10:30:15] [API] INFO: API POST /api/auth/login { method: "POST", url: "/api/auth/login", requestData: "{\"email\":\"john@example.com\"}" }
[10:30:15] [API] INFO: API POST /api/auth/login - 200 { method: "POST", url: "/api/auth/login", status: 200, responseTime: "245ms" }
[10:30:15] [Auth] INFO: User logged in { userId: 123, email: "john@example.com" }
```
