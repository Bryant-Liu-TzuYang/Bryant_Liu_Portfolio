# Environment Variables Documentation

This document categorizes all environment variables used in the Voca_Recaller application based on their necessity for proper application functioning in **Development** and **Production** environments.

---

# 🔧 Development Environment

Configuration for local development and testing. The application prioritizes ease of setup with sensible defaults.

## Category 1: Absolutely Required

These variables **must be set** for core application functionality to work in development.

### 1-1. Email Configuration (SMTP)

| Variable | Description | Default | Why Required |
|----------|-------------|---------|--------------|
| `SMTP_USER` | SMTP account username/email | None | ✅ **Email sending** |
| `SMTP_PASSWORD` | SMTP account password/app password | None | ✅ **Email authentication** |

**Why Critical**: The core purpose of this application is to send vocabulary emails from Notion databases. Without SMTP credentials, the `send_email()` function returns `False` and you cannot test:
- Vocabulary email sending
- Password reset functionality
- Any email-related features

**Setup Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

---

## Category 2: Can Use Defaults (But Change in Production)

These variables have **insecure defaults** that work for development but **MUST be changed** for production.

### 2-1. Security Configuration

| Variable | Description | Default | Dev Status |
|----------|-------------|---------|------------|
| `SECRET_KEY` | Flask session encryption key | `'dev-secret-key-change-in-production'` | ⚠️ **Has insecure default** |
| `JWT_SECRET_KEY` | JWT token signing key | `'jwt-secret-key'` | ⚠️ **Has insecure default** |

**Why Defaults Work in Dev**: These insecure defaults are sufficient for local testing. Authentication and sessions will work properly. However, these defaults are **publicly known** and create severe security vulnerabilities in production.

⚠️ **Important**: These defaults should **NEVER** be used in production. Generate new secure keys before deployment.

### 2-2. SMTP Server Configuration

| Variable | Description | Default | Dev Status |
|----------|-------------|---------|------------|
| `SMTP_HOST` | SMTP server hostname | `'smtp.gmail.com'` | ⚠️ **Has default** |
| `SMTP_PORT` | SMTP server port | `587` | ⚠️ **Has default** |

**Why Defaults Work in Dev**: Gmail SMTP settings work for most development testing scenarios.

---

## Category 3: Can Skip Entirely

These variables have **sensible defaults** or are **optional features** that can be completely omitted during development.

### 3-1. Database Configuration

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `DATABASE_URL` | Full database connection string | SQLite: `sqlite:///instance/voca_recaller_dev.db` | ❌ **Auto-uses SQLite** |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | N/A | ❌ **Only for MySQL setup** |
| `MYSQL_DATABASE` | MySQL database name | N/A | ❌ **Only for MySQL setup** |
| `MYSQL_USER` | MySQL username | N/A | ❌ **Only for MySQL setup** |
| `MYSQL_PASSWORD` | MySQL user password | N/A | ❌ **Only for MySQL setup** |

**Why Skippable**: The application automatically uses SQLite for local development with zero configuration. Data is stored in `backend/instance/voca_recaller_dev.db`.

**When to Set**: Only if you specifically want to test with MySQL in development.

### 3-2. Celery/Background Tasks

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `REDIS_URL` | Redis connection URL for Celery | `'redis://localhost:6379/0'` | ❌ **Not needed for basic dev** |

**Why Skippable**: Background tasks (scheduled email sending) are not required for basic development. You can:
- Test email sending directly via API endpoints
- Skip running the Celery worker
- Skip installing/running Redis

**When to Set**: Only if you're specifically testing scheduled email functionality.

### 3-3. Frontend Configuration

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `FRONTEND_URL` | Frontend application URL | `'http://localhost:3000'` | ❌ **Works with default** |
| `REACT_APP_API_URL` | Backend API base URL | `'/api'` (relative path) | ❌ **Works with default** |

**Why Skippable**: Defaults work perfectly for local development setup (backend on port 5000, frontend on port 3000).

### 3-4. Logging Configuration

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `LOG_LEVEL` | Backend logging level | `'INFO'` (Dev mode: `'DEBUG'`) | ❌ **Defaults are fine** |
| `LOG_TO_STDOUT` | Log to stdout | `false` | ❌ **Defaults are fine** |
| `REACT_APP_LOG_LEVEL` | Frontend logging level | `'info'` | ❌ **Defaults are fine** |
| `REACT_APP_SEND_LOGS_TO_SERVER` | Send frontend logs to backend | `'true'` | ❌ **Defaults are fine** |

**Why Skippable**: Defaults provide appropriate verbosity for development debugging.

### 3-5. Email Template Variables

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `FROM_EMAIL_NAME` | Display name in From field | Uses `SMTP_USER` | ❌ **Cosmetic only** |
| `SUPPORT_EMAIL` | Support contact email | Falls back to `SMTP_USER` | ❌ **Cosmetic only** |

**Why Skippable**: These are purely cosmetic. Emails will send fine without them.

### 3-6. Notion Integration

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `NOTION_API_KEY` | Notion Integration Token | None | ❌ **Users can provide via UI** |

**Why Skippable**: Users can provide their own Notion integration tokens via the UI (stored in `NotionToken` model). Having a global key simplifies testing but isn't required if you're willing to input tokens through the interface.

### 3-7. Flask Environment

| Variable | Description | Default | Why Skippable |
|----------|-------------|---------|---------------|
| `FLASK_ENV` | Flask environment mode | `'development'` | ❌ **Auto-defaults to dev** |

**Why Skippable**: Automatically defaults to development mode.

---

# 🚀 Production Environment

Configuration for production deployment. Security and reliability are paramount.

## Category 1: Critical Variables (Must Be Set)

These variables **MUST** be configured with real-world, secure values for production deployment.

### 1-1. Database Configuration

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `DATABASE_URL` | Full database connection string | Falls back to SQLite ⚠️ | ✅ **REQUIRED** |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | N/A | ✅ **REQUIRED** (Docker) |
| `MYSQL_DATABASE` | MySQL database name | N/A | ✅ **REQUIRED** (Docker) |
| `MYSQL_USER` | MySQL username | N/A | ✅ **REQUIRED** (Docker) |
| `MYSQL_PASSWORD` | MySQL user password | N/A | ✅ **REQUIRED** (Docker) |

**Why Critical in Prod**: 
- SQLite is **NOT suitable** for production (no concurrent writes, no scalability)
- MySQL/PostgreSQL required for data persistence, concurrent users, and reliability
- Format: `mysql+pymysql://user:password@host:port/database`

**Docker Note**: If using `docker-compose.prod.yml`, set all MySQL variables. If using external database, only set `DATABASE_URL`.

### 1-2. Security Configuration

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `SECRET_KEY` | Flask session encryption key | `'dev-secret-key-change-in-production'` ⚠️ | ✅ **REQUIRED** |
| `JWT_SECRET_KEY` | JWT token signing key | `'jwt-secret-key'` ⚠️ | ✅ **REQUIRED** |

**Why Critical in Prod**: 
- Default keys are **publicly known** and create severe security vulnerabilities
- Attackers can forge sessions and JWT tokens with default keys
- **MUST** be cryptographically secure random strings

**Generate Secure Keys**:
```python
import secrets
print(secrets.token_urlsafe(32))  # Run this twice for two different keys
```

⚠️ **CRITICAL**: Use different keys for each environment. Never reuse development keys in production.

### 1-3. Email Configuration (SMTP)

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `SMTP_USER` | SMTP account username/email | None | ✅ **REQUIRED** |
| `SMTP_PASSWORD` | SMTP account password/app password | None | ✅ **REQUIRED** |
| `SMTP_HOST` | SMTP server hostname | `'smtp.gmail.com'` | ✅ **Recommended** |
| `SMTP_PORT` | SMTP server port | `587` | ✅ **Recommended** |

**Why Critical in Prod**: 
- Core application functionality depends on sending emails
- Password reset feature requires email
- No SMTP = no vocabulary emails to users

**Production Recommendations**:
- Use a dedicated SMTP service (SendGrid, AWS SES, Mailgun)
- Don't use personal Gmail accounts
- Set up SPF/DKIM/DMARC records
- Monitor email deliverability

### 1-4. Notion Integration

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `NOTION_API_KEY` | Notion Integration Token | None | ⚠️ **Recommended** |

**Why Recommended in Prod**: While users can provide their own tokens, having a global key:
- Simplifies user onboarding
- Provides fallback if user tokens expire
- Enables admin testing/debugging

**Alternative**: Require all users to bring their own Notion integration tokens.

### 1-5. Environment Configuration

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `FLASK_ENV` | Flask environment mode | `'development'` | ✅ **REQUIRED** |

**Why Critical in Prod**: 
- Set to `production` to enable production-specific behaviors:
  - Disables debug mode
  - Enables secure cookies
  - Sets appropriate logging levels
  - Enforces production database requirement

**Value**: Must be set to `production`.

## Category 2: Highly Recommended Variables

These variables have defaults but should be configured for production for optimal operation.

### 2-1. Celery/Background Tasks

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `REDIS_URL` | Redis connection URL for Celery | `'redis://localhost:6379/0'` | ✅ **Recommended** |

**Why Recommended in Prod**: 
- Required for scheduled vocabulary email sending (core feature)
- Required for background task processing
- Default assumes Redis on localhost (may not work in containerized/cloud environments)

**Production Setup**:
- Use managed Redis service (AWS ElastiCache, Redis Cloud, Azure Redis)
- Or configure Redis in your deployment
- Format: `redis://host:port/db`

### 2-2. Frontend Configuration

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `FRONTEND_URL` | Frontend application URL | `'http://localhost:3000'` | ✅ **REQUIRED** |
| `REACT_APP_API_URL` | Backend API base URL | `'/api'` (relative path) | ⚠️ Optional |

**Why Critical in Prod**: 
- `FRONTEND_URL`: Used in password reset emails - must point to your actual domain
- Default localhost URL will break email links for users
- Example: `https://yourdomain.com`

**REACT_APP_API_URL**: Usually fine with relative path if frontend and backend share domain.

### 2-3. Logging Configuration

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `LOG_LEVEL` | Backend logging level | `'INFO'` (Prod auto: `'WARNING'`) | ⚠️ Optional |
| `LOG_TO_STDOUT` | Log to stdout | `false` (Prod auto: `true`) | ⚠️ Optional |
| `REACT_APP_LOG_LEVEL` | Frontend logging level | `'info'` | ⚠️ Optional |
| `REACT_APP_SEND_LOGS_TO_SERVER` | Send frontend logs to backend | `'true'` | ⚠️ Optional |

**Why Recommended in Prod**: 
- Production mode automatically sets sensible defaults
- `LOG_TO_STDOUT=true` is required for containerized deployments (Docker, Kubernetes)
- Consider setting `LOG_LEVEL=WARNING` or `ERROR` to reduce noise
- Frontend logging helps debug production issues

### 2-4. Email Template Variables

| Variable | Description | Default | Prod Requirement |
|----------|-------------|---------|------------------|
| `FROM_EMAIL_NAME` | Display name in From field | Uses `SMTP_USER` | ✅ **Recommended** |
| `SUPPORT_EMAIL` | Support contact email | Falls back to `SMTP_USER` | ✅ **Recommended** |

**Why Recommended in Prod**: 
- Professional appearance in user emails
- Proper branding
- Clear support contact information

**Example**:
- `FROM_EMAIL_NAME=Voca Recaller`
- `SUPPORT_EMAIL=support@yourcompany.com`

---

# 📝 Configuration Templates

## Development `.env` Template

**Minimal configuration for local development** (from `backend/dev-env.example`):

```bash
##################################
# DEVELOPMENT ENVIRONMENT CONFIG
##################################

# ============================================================
# REQUIRED - Email Configuration (for testing email features)
# ============================================================
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

# ============================================================
# OPTIONAL - Security (defaults provided, but insecure)
# ============================================================
# Leave commented to use defaults, or set custom values:
# SECRET_KEY=dev-secret-key-change-in-production
# JWT_SECRET_KEY=jwt-secret-key

# ============================================================
# OPTIONAL - Notion Integration
# ============================================================
# Uncomment if you want a global token (otherwise use UI):
# NOTION_API_KEY=your_notion_api_key_here

# ============================================================
# OPTIONAL - Everything below has working defaults
# ============================================================
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# REDIS_URL=redis://localhost:6379/0
# FRONTEND_URL=http://localhost:3000
# LOG_LEVEL=DEBUG
# FLASK_ENV=development
```

**Setup Instructions (Automated - Recommended):**
1. Run `./setup.sh dev` to create `.env` from `backend/dev-env.example`
2. Choose `y` for interactive setup wizard:
   - Enter SMTP credentials (use Gmail App Password)
   - Optionally add Notion API key
3. Script validates and starts services automatically

**Setup Instructions (Manual):**
1. Run `./setup.sh dev` and choose `n` or `skip` for interactive setup
2. Edit `.env` and set `SMTP_USER` and `SMTP_PASSWORD` 
3. Optionally set `NOTION_API_KEY`
4. Run `./setup.sh dev` again to start services

**Alternative Manual Setup:**
1. Copy `backend/dev-env.example` to `.env` (in project root)
2. Follow manual steps 2-4 above

---

## Production `.env` Template

**Complete production configuration** (from `backend/prod-env.example`):

```bash
##################################
# PRODUCTION ENVIRONMENT CONFIG
##################################

# ============================================================
# CRITICAL - Database (REQUIRED)
# ============================================================
# Use DATABASE_URL for external/managed database:
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname

# OR use these for Docker Compose deployment:
MYSQL_ROOT_PASSWORD=<strong-random-password>
MYSQL_DATABASE=voca_recaller_prod
MYSQL_USER=voca_recaller_user
MYSQL_PASSWORD=<strong-random-password>

# ============================================================
# CRITICAL - Security (MUST GENERATE NEW KEYS!)
# ============================================================
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=<generate-secure-random-string>
JWT_SECRET_KEY=<generate-different-secure-random-string>

# ============================================================
# CRITICAL - Email Configuration (REQUIRED)
# ============================================================
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
FROM_EMAIL_NAME=Voca Recaller
SUPPORT_EMAIL=support@yourdomain.com

# ============================================================
# CRITICAL - Environment (REQUIRED)
# ============================================================
FLASK_ENV=production

# ============================================================
# HIGHLY RECOMMENDED - Background Tasks
# ============================================================
REDIS_URL=redis://your-redis-host:6379/0

# ============================================================
# HIGHLY RECOMMENDED - Frontend Configuration
# ============================================================
FRONTEND_URL=https://yourdomain.com
REACT_APP_API_URL=/api

# ============================================================
# RECOMMENDED - Notion Integration
# ============================================================
NOTION_API_KEY=your_notion_api_key_here

# ============================================================
# OPTIONAL - Logging (Production defaults are fine)
# ============================================================
LOG_LEVEL=WARNING
LOG_TO_STDOUT=true
REACT_APP_LOG_LEVEL=warn
REACT_APP_SEND_LOGS_TO_SERVER=true
```

**Setup Instructions (Automated - Recommended):**
1. Run `./setup.sh prod` to create `.env` from `backend/prod-env.example`
2. Choose `y` for interactive setup wizard:
   - Auto-generates `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure database (Docker MySQL or external)
   - Set SMTP credentials
   - Set frontend URL
   - Configure Redis
   - Optional: Notion API key, email template variables
3. Script validates and starts services automatically

**Setup Instructions (Manual):**
1. Run `./setup.sh prod` and choose `n` or `skip` for interactive setup
2. Edit `.env` with all production values (see checklist below)
3. Run `./setup.sh prod` again to start services

**Alternative Manual Setup:**
1. Copy `backend/prod-env.example` to `.env` (in project root)
2. Follow manual steps 2-3 above

**Production Deployment Checklist:**
1. ✅ Generate unique `SECRET_KEY` and `JWT_SECRET_KEY`
2. ✅ Configure production database (MySQL/PostgreSQL)
3. ✅ Set up production SMTP service (SendGrid, AWS SES, etc.)
4. ✅ Set `FLASK_ENV=production`
5. ✅ Configure Redis for background tasks
6. ✅ Update `FRONTEND_URL` to your domain
7. ✅ Set professional `FROM_EMAIL_NAME` and `SUPPORT_EMAIL`
8. ✅ Test email sending before going live
9. ✅ Verify database migrations are applied
10. ✅ Ensure `.env` is in `.gitignore`

---

## Security Notes

⚠️ **Never commit real credentials to version control!**

- Use different `SECRET_KEY` and `JWT_SECRET_KEY` for each environment
- For production, generate cryptographically secure random strings:
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```
- Use Gmail App Passwords (not regular passwords) for `SMTP_PASSWORD`
- Keep `.env` files in `.gitignore`
- Rotate secrets periodically

---

## Environment-Specific Behavior

The application automatically adjusts behavior based on configuration:

- **Development** (`FLASK_ENV=development`): Uses SQLite by default, debug logging, development CORS
- **Production** (`FLASK_ENV=production`): Requires MySQL, warning-level logging, secure cookies
- **Testing** (`FLASK_ENV=testing`): Uses in-memory SQLite, test-specific settings

---

## Troubleshooting

### "SMTP credentials not configured" Error
- Ensure `SMTP_USER` and `SMTP_PASSWORD` are set in `.env`
- Verify credentials are correct
- For Gmail, use an App Password, not your regular password

### Database Connection Errors
- Check `DATABASE_URL` format: `mysql+pymysql://user:password@host:port/database`
- Verify MySQL is running and accessible
- In development, you can omit this to use SQLite

### JWT Token Errors
- Ensure `JWT_SECRET_KEY` is set and consistent across restarts
- Changing this key will invalidate all existing user tokens

### Notion API Errors
- Verify `NOTION_API_KEY` has proper permissions
- Users can provide their own integration tokens through the UI if global key is not set
