# Database System Documentation

## Table of Contents
- [Database System Documentation](#database-system-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Current Database Configuration](#current-database-configuration)
    - [Production/Docker Environment](#productiondocker-environment)
    - [Local Development (Docker or Direct MySQL)](#local-development-docker-or-direct-mysql)
  - [Database Tables](#database-tables)
    - [Core Tables](#core-tables)
      - [1. `users`](#1-users)
      - [2. `notion_tokens`](#2-notion_tokens)
      - [3. `notion_databases`](#3-notion_databases)
      - [4. `email_services`](#4-email_services)
      - [5. `email_logs`](#5-email_logs)
      - [6. `email_settings` (DEPRECATED)](#6-email_settings-deprecated)
      - [7. `password_reset_tokens`](#7-password_reset_tokens)
  - [Database Architecture](#database-architecture)
    - [Relationships](#relationships)
    - [Data Flow](#data-flow)
  - [Database Storage Locations](#database-storage-locations)
    - [Docker/Production (MySQL)](#dockerproduction-mysql)
    - [Local Development (MySQL)](#local-development-mysql)
  - [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
    - [Configuration Files](#configuration-files)
  - [Database Operations](#database-operations)
    - [Access MySQL Database](#access-mysql-database)
    - [Common Queries](#common-queries)
  - [Database Migrations](#database-migrations)
    - [Initial Setup](#initial-setup)
    - [Schema Updates](#schema-updates)
  - [Backup \& Recovery](#backup--recovery)
    - [Backup MySQL Database](#backup-mysql-database)
    - [Restore MySQL Database](#restore-mysql-database)
    - [Backup Docker Volume](#backup-docker-volume)
  - [Troubleshooting](#troubleshooting)
    - [Issue: Wrong Database Being Used](#issue-wrong-database-being-used)
    - [Issue: Outdated SQLite Files](#issue-outdated-sqlite-files)
    - [Issue: Database Connection Failed](#issue-database-connection-failed)
    - [Issue: Data Loss After Restart](#issue-data-loss-after-restart)
    - [Issue: Table Doesn't Exist](#issue-table-doesnt-exist)
  - [Performance Considerations](#performance-considerations)
    - [Indexing](#indexing)
    - [Connection Pooling](#connection-pooling)
    - [Query Optimization](#query-optimization)
  - [Security Best Practices](#security-best-practices)
    - [Credentials](#credentials)
    - [Access Control](#access-control)
    - [Data Protection](#data-protection)
  - [Monitoring](#monitoring)
    - [Database Health Checks](#database-health-checks)
    - [Key Metrics to Monitor](#key-metrics-to-monitor)
  - [Related Documentation](#related-documentation)
  - [Summary](#summary)

## Overview

Voca Recaller uses **MySQL 8.0** for all active environments (production, Docker-based development, and local development with `DATABASE_URL` set). SQLite is only used by the test configuration and legacy files, and is not part of the normal development workflow.

## Current Database Configuration

### Production/Docker Environment
- **Database**: MySQL 8.0
- **Host**: `mysql` container (Docker) or `localhost:3306`
- **Database Name**: `voca_recaller_dev`
- **User**: `user`
- **Password**: `password` (change in production)
- **Connection String**: `mysql+pymysql://user:password@mysql:3306/voca_recaller_dev`

### Local Development (Docker or Direct MySQL)
- **Database**: MySQL 8.0
- **Host**: `mysql` container (Docker) or `localhost:3306` when running MySQL locally
- **Connection String** (typical local): `mysql+pymysql://user:password@localhost:3306/voca_recaller_dev`

**⚠️ Note**: The `backend/instance/` directory may contain legacy SQLite files (`notion_email_dev.db`, `voca_recaller_dev.db`). These are no longer used in development; only the testing configuration touches SQLite (`backend/instance/test.db`). Safe to delete the legacy files if present.

## Database Tables

### Core Tables

#### 1. `users`
User accounts and authentication.

**Columns:**
- `id` - Primary key
- `email` - Unique email address
- `password_hash` - Bcrypt hashed password
- `first_name` - User's first name
- `last_name` - User's last name
- `is_active` - Account status (boolean)
- `is_admin` - Admin privileges (boolean)
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp

**Current Count**: 2 users

#### 2. `notion_tokens`
Notion API integration tokens.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users
- `token_name` - Descriptive name for the token
- `token` - Encrypted Notion API token
- `is_active` - Token status (boolean)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Current Count**: 1 token

#### 3. `notion_databases`
Notion databases connected to user accounts.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users
- `token_id` - Foreign key to notion_tokens
- `database_id` - Notion database ID
- `database_name` - User-friendly name
- `database_url` - Full Notion database URL
- `is_active` - Database status (boolean)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Current Count**: 1 database

#### 4. `email_services`
Scheduled email service configurations.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users
- `database_id` - Foreign key to notion_databases
- `service_name` - Service display name
- `description` - Optional description
- `send_time` - Time to send (TIME type: HH:MM:SS)
- `timezone` - Timezone string (e.g., "Asia/Taipei")
- `frequency` - Schedule frequency ("daily", "weekly", "monthly")
- `vocabulary_count` - Number of vocabulary items to send
- `selection_method` - Selection strategy ("random", "latest", "date_range")
- `date_range_start` - Start date for date_range method (DATE)
- `date_range_end` - End date for date_range method (DATE)
- `is_active` - Service status (boolean)
- `last_sent_at` - Timestamp of last successful send (DATETIME)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Current Count**: 1 service

#### 5. `email_logs`
Complete history of all sent emails.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users
- `sent_at` - Send timestamp (UTC, DATETIME)
- `vocabulary_items` - JSON array of vocabulary sent
- `status` - Delivery status ("sent", "failed")
- `error_message` - Error details if status is "failed"

**Current Count**: 14 emails logged

#### 6. `email_settings` (DEPRECATED)
Legacy table for email settings. Use `email_services` instead.

#### 7. `password_reset_tokens`
Temporary tokens for password reset functionality.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users
- `token` - Unique reset token (hashed)
- `expires_at` - Token expiration timestamp
- `used` - Whether token has been used (boolean)
- `created_at` - Creation timestamp

## Database Architecture

### Relationships

```
users (1) ──→ (N) notion_tokens
users (1) ──→ (N) notion_databases
users (1) ──→ (N) email_services
users (1) ──→ (N) email_logs
users (1) ──→ (N) password_reset_tokens

notion_tokens (1) ──→ (N) notion_databases
notion_databases (1) ──→ (N) email_services
```

### Data Flow

```
User Authentication
  ↓
User creates Notion Token
  ↓
User connects Notion Database (using token)
  ↓
User creates Email Service (using database)
  ↓
Celery Beat schedules email task
  ↓
Celery Worker sends email
  ↓
Email Log created with status
```

## Database Storage Locations

### Docker/Production (MySQL)
- **Container**: `voca_recaller_mysql`
- **Volume**: `voca_recaller_mysql_data` (Docker managed volume)
- **Persistent**: Yes, data survives container restarts
- **Backup**: Managed through Docker volumes

### Local Development (MySQL)
- **Container/Service**: Local MySQL instance or `mysql` container
- **Persistent**: Use Docker volume or local MySQL data directory
- **Backup**: Dump via `mysqldump` as in production

## Configuration

### Environment Variables

**Docker (docker-compose.yml):**
```yaml
DATABASE_URL=mysql+pymysql://user:password@mysql:3306/voca_recaller_dev
```

**Local Development (Docker or direct MySQL):**
```bash
# Example for local MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/voca_recaller_dev
```

### Configuration Files
- `backend/config.py` - Database configuration
- `docker-compose.yml` - MySQL service definition
- `backend/app/models.py` - SQLAlchemy models

## Database Operations

### Access MySQL Database

**Via Docker:**
```bash
# Connect to MySQL container
docker exec -it voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev

# Run query directly
docker exec voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev -e "SELECT * FROM users;"
```

**Via MySQL Client:**
```bash
mysql -h localhost -P 3306 -u user -ppassword voca_recaller_dev
```

### Common Queries

**View all tables:**
```sql
SHOW TABLES;
```

**Check table structure:**
```sql
DESCRIBE email_services;
```

**View recent emails:**
```sql
SELECT id, user_id, sent_at, status FROM email_logs ORDER BY sent_at DESC LIMIT 10;
```

**Check email service configuration:**
```sql
SELECT id, service_name, send_time, timezone, frequency, is_active, last_sent_at 
FROM email_services;
```

**View user accounts:**
```sql
SELECT id, email, first_name, is_active, is_admin FROM users;
```

## Database Migrations

### Initial Setup

The database is automatically initialized when Docker containers start:
1. MySQL container creates the database
2. Flask app creates tables via SQLAlchemy on first run
3. Tables are created based on models in `backend/app/models.py`

### Schema Updates

When models change:
1. Update model definitions in `backend/app/models.py`
2. Restart containers to apply changes (for simple additions)
3. For complex migrations, consider using Flask-Migrate (Alembic)

**Note**: Currently no formal migration system is in place. Schema changes are applied manually.

## Backup & Recovery

### Backup MySQL Database

**Export all data:**
```bash
docker exec voca_recaller_mysql mysqldump -uuser -ppassword voca_recaller_dev > backup_$(date +%Y%m%d).sql
```

**Export specific table:**
```bash
docker exec voca_recaller_mysql mysqldump -uuser -ppassword voca_recaller_dev email_logs > email_logs_backup.sql
```

### Restore MySQL Database

**From backup file:**
```bash
docker exec -i voca_recaller_mysql mysql -uuser -ppassword voca_recaller_dev < backup_20251208.sql
```

### Backup Docker Volume

```bash
# Create volume backup
docker run --rm -v voca_recaller_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_volume_backup.tar.gz /data

# Restore volume backup
docker run --rm -v voca_recaller_mysql_data:/data -v $(pwd):/backup alpine tar xzf /backup/mysql_volume_backup.tar.gz
```

## Troubleshooting

### Issue: Wrong Database Being Used

**Symptom**: Data changes not reflected, different data in UI vs queries

**Solution**: Verify the app is pointed at MySQL (not the SQLite fallback in `DevelopmentConfig`):
```bash
# Check environment variable inside the backend container
docker exec voca_recaller_backend printenv | grep DATABASE_URL

# Should show: mysql+pymysql://user:password@mysql:3306/voca_recaller_dev
```
If `DATABASE_URL` is unset, Flask will fall back to SQLite. Set `DATABASE_URL` in your dev environment to keep everything on MySQL.

### Issue: Outdated SQLite Files

**Symptom**: Legacy `.db` files remain in `backend/instance/`

**Solution**: These files are no longer used for development. Safe to delete:
```bash
rm backend/instance/notion_email_dev.db
rm backend/instance/voca_recaller_dev.db
```

### Issue: Database Connection Failed

**Symptom**: Backend can't connect to MySQL

**Check**:
1. MySQL container is running: `docker ps | grep mysql`
2. Database credentials are correct in docker-compose.yml
3. MySQL service is healthy: `docker logs voca_recaller_mysql`

### Issue: Data Loss After Restart

**Symptom**: All data disappears after container restart

**Solution**: Ensure Docker volume is properly configured:
```bash
# Check volume exists
docker volume ls | grep voca_recaller

# Inspect volume
docker volume inspect voca_recaller_mysql_data
```

### Issue: Table Doesn't Exist

**Symptom**: SQL error about missing table

**Solution**: Tables are auto-created on first app start. If missing:
```bash
# Restart backend to trigger table creation
docker restart voca_recaller_backend

# Or recreate from scratch
docker-compose down -v
docker-compose up -d
```

## Performance Considerations

### Indexing
Current tables have primary keys but no additional indexes. Consider adding indexes on:
- `users.email` (for login lookups)
- `email_logs.sent_at` (for log queries)
- `email_services.user_id` (for user-specific queries)
- `notion_databases.user_id` (for user-specific queries)

### Connection Pooling
SQLAlchemy handles connection pooling automatically with default settings.

### Query Optimization
- Email logs query uses `ORDER BY sent_at DESC LIMIT 10` - efficient with proper index
- User lookups by email should use index
- Consider pagination for large result sets

## Security Best Practices

### Credentials
- **Never commit** database passwords to version control
- Use environment variables for all credentials
- Change default passwords in production
- Use strong passwords (16+ characters, mixed case, numbers, symbols)

### Access Control
- Limit MySQL user permissions to only required operations
- Use separate database users for different environments
- Restrict MySQL port (3306) access to necessary services only

### Data Protection
- All passwords stored with bcrypt hashing
- Notion tokens should be encrypted (implement encryption)
- Regular backups of database
- Use SSL/TLS for MySQL connections in production

## Monitoring

### Database Health Checks

```bash
# Check MySQL status
docker exec voca_recaller_mysql mysqladmin -uuser -ppassword status

# Check database size
docker exec voca_recaller_mysql mysql -uuser -ppassword -e "
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'voca_recaller_dev'
GROUP BY table_schema;"

# Check table sizes
docker exec voca_recaller_mysql mysql -uuser -ppassword -e "
SELECT 
    table_name AS 'Table',
    table_rows AS 'Rows',
    ROUND(data_length / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'voca_recaller_dev'
ORDER BY data_length DESC;"
```

### Key Metrics to Monitor
- Database size growth rate
- Table row counts
- Email log volume
- Failed email count
- Active services count

## Related Documentation
- `EMAIL_SCHEDULING.md` - Email system using database
- `LOGGING.md` - Application logging
- `docker-compose.yml` - MySQL container configuration
- `backend/app/models.py` - Database models

## Summary

✅ **Primary Database**: MySQL 8.0 for production and development
✅ **Tables**: 7 tables (users, tokens, databases, services, logs, settings, password resets)
✅ **Current Data**: 2 users, 1 service, 14 email logs
✅ **Storage**: Docker volume `voca_recaller_mysql_data`
✅ **Backup**: Manual mysqldump or volume backup
✅ **Access**: Via Docker exec or MySQL client on port 3306
⚠️ **SQLite**: Only used by automated tests; legacy dev `.db` files can be removed
