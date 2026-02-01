# Q&A - Voca Recaller

## Table of Contents
- [Q: How to test SMTP_USER and SMTP_PASSWORD validity?](#q-how-to-test-smtp_user-and-smtp_password-validity)
  - [1. Automatic Validation During Setup](#1-automatic-validation-during-setup)
  - [2. Manual Validation Script](#2-manual-validation-script)
  - [3. Automatic Validation on App Startup](#3-automatic-validation-on-app-startup)
  - [What Gets Validated](#what-gets-validated)
  - [Common Issues and Solutions](#common-issues-and-solutions)
- [Q: Why am I not receiving scheduled vocabulary emails?](#q-why-am-i-not-receiving-scheduled-vocabulary-emails)
  - [Architecture Overview](#architecture-overview)
  - [Checking if Services are Running](#checking-if-services-are-running)
  - [Common Issues and Solutions](#common-issues-and-solutions-1)
  - [How Scheduling Works](#how-scheduling-works)
  - [Verifying It's Working](#verifying-its-working)
  - [Testing Email Service Manually](#testing-email-service-manually)
  - [Troubleshooting Checklist](#troubleshooting-checklist)

## Q: How to test SMTP_USER and SMTP_PASSWORD validity?

**A:** The application provides multiple ways to validate your SMTP credentials:

### 1. Automatic Validation During Setup
When running the setup script, SMTP credentials are automatically validated:
```bash
./setup.sh dev   # For development
./setup.sh prod  # For production
```
- **Development**: Warns if credentials are invalid but allows you to continue
- **Production**: Fails setup and requires valid credentials before proceeding

### 2. Manual Validation Script
Run the standalone validation script anytime:
```bash
python3 backend/validate_smtp.py
```

This will:
- Load credentials from your `.env` file
- Attempt to connect to the SMTP server
- Authenticate with your credentials
- Display clear success/failure messages

### 3. Automatic Validation on App Startup
The Flask application validates SMTP credentials every time it starts:
- **Development mode**: Logs detailed warnings but allows startup
- **Production mode**: Prevents startup if credentials are invalid

### What Gets Validated
The validation performs these checks:
1. ✅ Credentials exist (not empty)
2. ✅ Not placeholder values (e.g., "your_email@gmail.com")
3. ✅ Email format is valid
4. ✅ Can connect to SMTP server
5. ✅ TLS/SSL connection works
6. ✅ Authentication succeeds

### Common Issues and Solutions

**Authentication Failed**
- **Gmail users**: Use App Password, not your regular password
  1. Enable 2-factor authentication
  2. Generate App Password: https://myaccount.google.com/apppasswords
  3. Use the 16-character App Password in `SMTP_PASSWORD`

**Connection Failed**
- Check `SMTP_HOST` and `SMTP_PORT` are correct
- Verify firewall isn't blocking the connection
- Ensure stable internet connection

**Timeout Error**
- Check network connectivity
- Verify SMTP server is reachable
- Try again after a few moments

### For More Details
See comprehensive documentation: `docs/Updates/20251206_smtp_validation.md`

---

## Q: Why am I not receiving scheduled vocabulary emails?

**A:** Scheduled emails require the Celery Beat scheduler to be running. Here's how the email scheduling system works:

### Architecture Overview
The application uses three services for scheduled emails:
1. **Backend API** - Manages email service configurations in the database
2. **Celery Worker** - Executes email sending tasks
3. **Celery Beat** - Schedules tasks based on email service configurations

### Checking if Services are Running

**In Docker (Development):**
```bash
# Check all services status
docker ps

# You should see these containers running:
# - voca_recaller_backend
# - voca_recaller_celery (worker)
# - voca_recaller_celery_beat (scheduler)
# - voca_recaller_redis

# Check Celery Beat logs
docker logs voca_recaller_celery_beat

# Check Celery Worker logs
docker logs voca_recaller_celery
```

### Common Issues and Solutions

**1. Celery Beat Not Running**
If you don't see the `voca_recaller_celery_beat` container:
```bash
# Restart all services
./setup.sh dev

# Or specifically restart Celery Beat
docker-compose up -d celery-beat
```

**2. Email Service Not Active**
- Go to the Services page in the UI
- Verify your email service has a green "Active" badge
- If inactive, click Edit and enable it

**3. No Email Services Created**
- Navigate to Services page
- Click "Add Service"
- Configure:
  - Service name
  - Database to use
  - Send time and timezone
  - Vocabulary count and selection method
  - Set as Active

**4. SMTP Credentials Not Configured**
- Check your `.env` file has valid SMTP credentials
- Run validation: `python3 backend/validate_smtp.py`
- See "How to test SMTP credentials" section above

**5. Wrong Timezone**
- Email services use the timezone you specify
- Verify your service timezone matches your expectation
- Example: If you want 9:00 AM Shanghai time, use "Asia/Shanghai"

**6. Schedule Not Loading**
Celery Beat reloads schedules every 5 minutes automatically. To force reload:
```bash
# Restart Celery Beat
docker-compose restart celery-beat

# Check logs to confirm schedules loaded
docker logs -f voca_recaller_celery_beat
```

### How Scheduling Works

1. **You create an email service** via the Services page
2. **Celery Beat reads services** from the database every 5 minutes
3. **Schedules are updated** with new/modified services
4. **At scheduled time**, Celery Beat sends a task to the worker
5. **Celery Worker executes** the email sending task
6. **Email is sent** and logged in the database

### Verifying It's Working

**Check Celery Beat logs:**
```bash
docker logs voca_recaller_celery_beat
```
You should see:
```
Loaded 1 email service schedules
Scheduled: Dictionary - Email Service (ID: 1) at 00:12 Asia/Shanghai (daily)
```

**Check Celery Worker logs when email should be sent:**
```bash
docker logs -f voca_recaller_celery
```
You should see:
```
Processing email service: Dictionary - Email Service (ID: 1) for user: your@email.com
Retrieved 10 vocabulary items for service 1
Successfully sent email for service 1 to your@email.com
```

**Check the Services page:**
- "Last Sent" field should update after email is sent
- Shows "Never" if email hasn't been sent yet

### Testing Email Service Manually

To test without waiting for scheduled time:
```bash
# Access backend container
docker exec -it voca_recaller_backend /bin/bash

# Run Python
python3

# Execute the task manually
from app import create_app, celery
from app.email import send_email_service_task
app = create_app()
with app.app_context():
    result = send_email_service_task(1)  # Replace 1 with your service ID
    print(f"Email sent: {result}")
```

### Troubleshooting Checklist
- [ ] Celery Beat container is running
- [ ] Celery Worker container is running
- [ ] Redis container is running
- [ ] Email service exists and is active
- [ ] SMTP credentials are valid
- [ ] Timezone is correct
- [ ] Send time is in the future
- [ ] Database connection is working
- [ ] Notion database is connected and active

### Related Documentation
- [Email Service Refactoring](./EMAIL_SERVICE_REFACTORING.md) - Backend implementation
- [Services Page](./SERVICES_PAGE.md) - Using the Services UI
- [Deployment Guide](./DEPLOYMENT.md) - Production setup
