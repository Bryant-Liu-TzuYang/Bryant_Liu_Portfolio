# Email Scheduling & Monitoring Guide

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
  - [Components](#components)
  - [Flow](#flow)
- [Implementation Details](#implementation-details)
  - [1. Redis Priority Queue Scheduler](#1-redis-priority-queue-scheduler-backendschedulerpy)
  - [2. Email Sending Task](#2-email-sending-task-backendappemailpy)
  - [3. Schedule Reloading](#3-schedule-reloading)
- [Email Tracking System](#email-tracking-system)
  - [Email Logs Table](#email-logs-table-email_logs)
  - [Access Methods](#access-methods)
- [Database Schema](#database-schema)
- [Docker Configuration](#docker-configuration)
- [Testing](#testing)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
  - [Issue 1: Email Not Received at Scheduled Time](#issue-1-email-not-received-at-scheduled-time)
  - [Issue 2: Failed Email Deliveries](#issue-2-failed-email-deliveries)
  - [Issue 3: Schedule Not Updating](#issue-3-schedule-not-updating)
- [Monitoring & Health Checks](#monitoring--health-checks)

## Overview
This document covers the email scheduling system, monitoring tools, and troubleshooting for the Voca Recaller application. All scheduled emails are automatically tracked and logged.

## Architecture

### Components

1. **Backend API** (`backend/app/email_service.py`)
   - CRUD API endpoints for email services
   - Manages EmailService records in database
   
2. **Celery Worker** (`backend/celery_worker.py`)
   - Processes async tasks
   - Executes email sending tasks
   - Container: `voca_recaller_celery`

3. **Redis Scheduler** (`backend/scheduler.py`)
   - Polls Redis ZSET for due tasks
   - Triggers email tasks
   - Container: `voca_recaller_celery_beat` (running `scheduler.py`)

4. **Email Tracking System** (`email_logs` table)
   - Logs every sent email with timestamp, status, and content
   - Accessible via API endpoint and web interface

### Flow

```
User creates EmailService → Database stores config → Redis ZSET updated → 
Scheduler polls Redis (every 1s) → 
If due, Scheduler sends task to Redis → 
Celery Worker picks up task → 
Worker executes send_email_service_task → 
Email sent and logged to email_logs table
```

## Implementation Details

### 1. Redis Priority Queue Scheduler (`backend/scheduler.py`)

**Purpose**: High-precision scheduling using Redis Sorted Sets (ZSET)

**Key Logic**:
- **Storage**: Redis ZSET `email_schedule`. Member: `Service_ID`, Score: `Unix Timestamp`.
- **Polling**:
  - Runs every 1 second (high precision).
  - `zrangebyscore`: Fetches tasks where score <= current timestamp.
- **Execution**:
  - Removes task from Redis (prevents double execution).
  - Triggers `send_email_service_task` (Celery).
  - Calculates next run time.
  - Adds task back to Redis with new timestamp.

**Sync Phase**:
- On startup, the scheduler populates Redis from the SQL database to ensure consistency.

**Timezone Handling**: 
- `EmailService` calculates UTC timestamps for Redis scores.

### 2. Email Sending Task (`backend/app/email.py`)

**Task**: `send_email_service_task(service_id)`

**Process**:
1. Load EmailService configuration from database
2. Verify service, database, and user are active
3. Get vocabulary from Notion using selection method:
   - `random`: Random sample of N items
   - `latest`: N most recently created items
   - `date_range`: Items created between start and end dates
4. Generate HTML email content
5. Send email via SMTP
6. Update `last_sent_at` timestamp
7. **Log result to `email_logs` table** (status, timestamp, vocabulary items, errors)

**Error Handling**:
- Logs errors with full traceback
- Returns False on failure
- Continues with other services if one fails
- Error details stored in `email_logs.error_message`

### 3. Schedule Reloading

*Obsolete with Database Poller architecture.*
The `reload_email_schedules` task is no longer used. The poller query handles all active services dynamically.

**Note**: The scheduler automatically picks up changes to service configuration immediately (within 60s), as it queries the database on every tick. No restart is required.

## Email Tracking System

### Email Logs Table (`email_logs`)
All sent emails are tracked with:
- **id**: Unique identifier
- **user_id**: Recipient user ID
- **sent_at**: Timestamp (UTC)
- **vocabulary_items**: JSON array of items sent
- **status**: 'sent' or 'failed'
- **error_message**: Error details (if failed)

### Access Methods

**1. Web Interface** (Easiest)
- Navigate to **Email Logs** in the menu
- View history with filters (All/Sent/Failed)
- See timestamps, vocabulary counts, and errors
- Real-time refresh available

**2. API Endpoint**
```bash
GET /api/email/logs
Authorization: Bearer <JWT_TOKEN>

# Query params: page (default: 1), per_page (default: 10)
```

**3. Database Query**
```bash
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT id, sent_at, status, error_message FROM email_logs ORDER BY sent_at DESC LIMIT 10;"
```

**4. Diagnostic Script**
```bash
./check_email_status.sh
```

## Database Schema

### EmailService Table
```python
id = Integer (Primary Key)
user_id = ForeignKey(User)
database_id = ForeignKey(NotionDatabase)
service_name = String(200)
description = Text (optional)
send_time = String(10)  # Format: "HH:MM"
timezone = String(50)   # e.g., "Asia/Taipei"
frequency = String(20)  # "daily", "weekly", "monthly"
vocabulary_count = Integer
selection_method = String(20)  # "random", "latest", "date_range"
date_range_start = DateTime (optional)
date_range_end = DateTime (optional)
is_active = Boolean
last_sent_at = DateTime
created_at = DateTime
updated_at = DateTime
```

## Docker Configuration

### docker-compose.yml

Added new service:
```yaml
celery-beat:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: voca_recaller_celery_beat
  restart: unless-stopped
  environment:
    # Same as backend and celery
  volumes:
    - ./backend:/app
    - /app/__pycache__
  depends_on:
    - mysql
    - redis
    - backend
    - celery
  networks:
    - voca_recaller_network
  command: python scheduler.py
```



## Testing

### Send Test Email via API
```bash
curl -X POST http://localhost:5001/api/email/test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"database_id": 1, "vocabulary_count": 5}'
```

### Manual Task Execution
```bash
docker exec -it voca_recaller_backend python flask_shell.py

# In Python shell:
from app.email import send_email_service_task
result = send_email_service_task.delay(1)  # service_id = 1
print(result.get())
```

### Verify Schedule Loading
```bash
docker logs voca_recaller_celery_beat | grep "Scheduled:"
```
Look for: `Loaded N email service schedules` and `Scheduled: [Service Name]`

## Troubleshooting Common Issues

### Issue 1: Email Not Received at Scheduled Time

**Symptoms**: Service configured and active, but no email received

**Root Causes & Solutions**:

1. **Celery Beat outdated schedule**
   ```bash
   # Restart to reload schedule immediately
   docker restart voca_recaller_celery_beat
   ```

2. **SMTP credentials not configured**
   ```bash
   # Verify SMTP environment variables
   docker exec voca_recaller_backend printenv | grep SMTP
   ```
   Required: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`

3. **Service or database inactive**
   ```bash
   # Check service status
   docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
   "SELECT id, service_name, is_active FROM email_services;"
   ```

4. **Check schedule loaded**
   ```bash
   docker logs voca_recaller_celery_beat 2>&1 | grep "Scheduled:"
   ```

### Issue 2: Failed Email Deliveries

**Check failed emails**:
```bash
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT id, sent_at, error_message FROM email_logs WHERE status='failed' ORDER BY sent_at DESC LIMIT 5;"
```

**Common Errors**:

1. **"SMTP credentials not configured"** → Set environment variables in docker-compose.yml or .env

2. **"Authentication failed"** → For Gmail, use App Password instead of regular password

3. **"Connection refused"** → Check SMTP_HOST and SMTP_PORT, ensure firewall allows connections

4. **"No vocabulary items found"** → Verify Notion database has content and token has access

### Issue 3: Schedule Not Updating

**Symptom**: Updated send_time but old schedule still runs

**Solution**: The poller recalculates `next_run_at` immediately when `EmailService` is updated.
If persistent issues occur, check if the scheduler loop is stuck:
```bash
docker logs voca_recaller_celery_beat --tail 50
```

## Monitoring & Health Checks

### Regular Monitoring

**Check email delivery rate**:
```bash
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT 
  DATE(sent_at) as date,
  COUNT(*) as total,
  SUM(CASE WHEN status='sent' THEN 1 ELSE 0 END) as successful,
  SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed
FROM email_logs 
WHERE sent_at > NOW() - INTERVAL 7 DAY
GROUP BY DATE(sent_at)
ORDER BY date DESC;"
```

**Monitor Celery health**:
```bash
# Check containers running
docker ps --filter "name=voca_recaller_celery"

# View worker logs
docker logs voca_recaller_celery --tail 50

# View scheduler logs
docker logs voca_recaller_celery_beat --tail 50
```

**Backend application logs**:
```bash
# Check email sending attempts
grep -i "send_email\|Processing email service" backend/logs/notion-email-backend-$(date +%Y-%m-%d).log

# Check errors
cat backend/logs/notion-email-backend-error-$(date +%Y-%m-%d).log
```

### Automated Health Checks

Use the diagnostic script for comprehensive system checks:
```bash
./check_email_status.sh
```

Checks: time zones, container status, email configs, recent logs, SMTP settings, Celery status

### Alert Setup (Optional)

Monitor failed emails:
```bash
FAILED_COUNT=$(docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev \
  -e "SELECT COUNT(*) FROM email_logs WHERE status='failed' AND sent_at > NOW() - INTERVAL 1 DAY;" \
  -N 2>/dev/null)

if [ "$FAILED_COUNT" -gt 0 ]; then
  echo "WARNING: $FAILED_COUNT failed emails in the last 24 hours"
fi
```

## Security & Best Practices

### SMTP Credentials
- Store in environment variables (never in code)
- Use App Passwords for Gmail
- Never log credentials in plain text

### Database Access
- EmailService records are user-scoped
- Worker validates user ownership before sending
- Notion tokens stored securely per user

### Schedule Reload
- Auto-reloads every 5 minutes (no restart needed)
- Manual restart for immediate updates: `docker restart voca_recaller_celery_beat`

## Related Files

- `backend/beat.py` - Celery Beat entry point
- `backend/app/email.py` - Email tasks and API
- `backend/app/email_service.py` - EmailService CRUD API
- `backend/app/models.py` - Database models
- `frontend/src/pages/EmailLogs.js` - Email logs UI
- `check_email_status.sh` - Diagnostic script
- `docker-compose.yml` - Container configuration



## Deployment

### Development
```bash
./setup.sh dev
```

### Production
```bash
./setup.sh prod
```

Ensure:
- Redis has persistence enabled
- Celery Beat schedule file backed up
- Worker and Beat logs rotated
- SMTP credentials secure
- Firewall allows SMTP ports

## Quick Reference

### Common Commands

```bash
# Restart Celery Beat (force schedule reload)
docker restart voca_recaller_celery_beat

# Check recent emails
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e \
"SELECT id, sent_at, status FROM email_logs ORDER BY sent_at DESC LIMIT 5;"

# View Celery logs
docker logs voca_recaller_celery --tail 50
docker logs voca_recaller_celery_beat --tail 50

# Run diagnostic
./check_email_status.sh

# Test SMTP connection
docker exec voca_recaller_backend python validate_smtp.py
```

### Timezone Notes
- Database stores all timestamps in UTC
- Email services use local timezone (e.g., Asia/Taipei)
- Celery Beat converts local time to UTC for scheduling
- Example: 09:42 Taipei = 01:42 UTC

## Summary

The email scheduling system provides:
- ✅ **Automated scheduling** - Daily/weekly/monthly email delivery
- ✅ **Complete tracking** - Every email logged with status and errors
- ✅ **Multiple selection methods** - Random, latest, or date range vocabulary selection
- ✅ **Dynamic updates** - Auto-reload every 5 minutes (or restart for immediate)
- ✅ **Web monitoring** - Email Logs page for easy tracking
- ✅ **Comprehensive diagnostics** - Logs, queries, and automated health checks
- ✅ **Error handling** - Failed emails logged with detailed error messages

Users can create, edit, and manage email services through the Services UI. All deliveries are tracked in the `email_logs` table and accessible via web interface, API, or database queries.
