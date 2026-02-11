# Voca Recaller (Vocabulary Recall)

A web application that helps users recall vocabulary from their Notion databases by sending daily email reminders with random vocabulary items.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
   - [Using Setup Script (Recommended)](#using-setup-script-recommended)
   - [Manual Setup](#manual-setup)
      - [Development (M1 MacBook Pro)](#development-m1-macbook-pro)
      - [Production (Ubuntu Linux)](#production-ubuntu-linux)
- [Environment Variables](#environment-variables)
   - [Quick Setup](#quick-setup)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
   - [Setup & Configuration](#setup--configuration)
   - [Operations](#operations)
- [Logging](#logging)
   - [Backend Logging](#backend-logging)
   - [Frontend Logging](#frontend-logging)
- [API Endpoints](#api-endpoints)
   - [Authentication](#authentication)
   - [User Management](#user-management)
   - [Database Management](#database-management)
   - [Email & Settings](#email--settings)
- [Password Reset Flow](#password-reset-flow)
   - [Security Features](#security-features)
   - [Email Configuration for Password Reset](#email-configuration-for-password-reset)
   - [SMTP Validation](#smtp-validation)
- [License](#license)

## Features

- User authentication and registration
- **Password reset functionality with email verification**
- Connect multiple Notion databases
- Customizable email frequency and vocabulary count per email service
- Secure storage of user preferences
- Daily automated email delivery
- Comprehensive logging system with request tracking and performance monitoring

## Quick Start

### Using Setup Script (Recommended)

The project includes a unified setup script that handles both environment configuration and Docker management:

```bash
# First time setup for development (with interactive wizard)
./setup.sh dev          # Creates .env and offers interactive configuration
# Choose 'y' to use wizard or 'n' to configure manually
# If manual: edit .env, then run './setup.sh dev' again

# First time setup for production (with interactive wizard)
./setup.sh prod         # Creates .env and offers interactive configuration
# Wizard will guide you through all required settings
# If manual: edit .env, then run './setup.sh prod' again

# Other commands
./setup.sh stop         # Stop all services
./setup.sh logs         # View logs
./setup.sh cleanup      # Clean up containers and volumes
```

**Interactive Setup Features:**
- **Development**: Configure SMTP credentials, optionally add Notion API key
- **Production**: Auto-generates security keys, guides through database, email, and frontend setup
- **Flexible**: Type `skip` at any prompt to exit and configure manually
- **Safe**: Only prompts for configuration on first run (when `.env` is created)

The `dev` and `prod` commands automatically:
1. **Create `.env` file** from the appropriate template (`dev-env.example` or `prod-env.example`)
2. **Offer interactive setup** - Guide you through configuring required variables:
   - Development: SMTP credentials, optional Notion API key
   - Production: Security keys, database, SMTP, frontend URL, Redis
3. **Validate environment variables** before starting services
4. **Start Docker containers** and services

**Interactive Setup Options**:
- Type `y` to use the interactive wizard
- Type `n` or `skip` to configure `.env` manually
- At any prompt, type `skip` to exit and configure manually

**Note**: If `.env` already exists, the script will use it instead of creating a new one from the template.

**Development environment** includes:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MySQL: localhost:3306
- Redis: localhost:6379

**Production environment** includes:
- Application: http://localhost (or your domain)
- API: http://localhost/api

### Manual Setup

#### Development (M1 MacBook Pro)

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd notion-email
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

#### Production (Ubuntu Linux)

1. **Deploy with production Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

## Environment Variables

**📖 For complete environment variable documentation, see [ENV_VARIABLES.md](docs/ENV_VARIABLES.md)**

The documentation provides:
- Detailed categorization for Development and Production environments
- Required vs. optional variables
- Security best practices
- Configuration templates
- Troubleshooting guide

### Quick Setup

For **development**, you only need to set:
```bash
# Minimal .env for development (created from backend/dev-env.example)
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

For **production**, see the complete configuration in `backend/prod-env.example`.

All other variables have sensible defaults. See [ENV_VARIABLES.md](docs/ENV_VARIABLES.md) for detailed explanations and the complete development and production templates.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: React (JavaScript/TypeScript)
- **Database**: MySQL
- **Email Service**: SMTP (configurable)
- **Notion API**: Official Notion SDK

## Project Structure

```
voca-recaller/
├── backend/                 # Flask backend
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── config.py
├── frontend/               # React frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Development setup
├── docker-compose.prod.yml # Production setup
└── README.md
```



## Documentation

### Setup & Configuration
- **[SETUP_QUICK_REFERENCE.md](docs/SETUP_QUICK_REFERENCE.md)** ⚡ Quick reference card
- **[INTERACTIVE_SETUP.md](docs/INTERACTIVE_SETUP.md)** - Interactive setup wizard guide
- **[SETUP_FLOW.md](docs/SETUP_FLOW.md)** - Visual setup flow diagrams
- **[ENV_VARIABLES.md](docs/ENV_VARIABLES.md)** - Comprehensive environment variables guide

### Operations
- **[LOGGING.md](docs/LOGGING.md)** - Logging system documentation
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment guide

## Logging

The application includes a comprehensive logging system for both backend and frontend. See [LOGGING.md](docs/LOGGING.md) for detailed documentation.

### Backend Logging
- Structured logs with request tracking
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Automatic log rotation
- Performance monitoring

### Frontend Logging
- Context-aware logging
- API call tracking
- User action logging
- Development/production modes

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/validate-reset-token` - Validate reset token

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Database Management
- `POST /api/databases` - Add Notion database
- `GET /api/databases` - Get user databases
- `PUT /api/databases/:id` - Update database
- `DELETE /api/databases/:id` - Delete database

### Email & Settings
- `PUT /api/settings` - Update email settings
- `POST /api/email/send-test` - Send test email
- `GET /api/email/logs` - Get email logs

## Password Reset Flow

The application includes a secure password reset system:

1. **Request Reset**: User enters email on `/forgot-password`
2. **Email Sent**: System sends reset link via email (valid for 1 hour)
3. **Reset Password**: User clicks link and enters new password
4. **Confirmation**: User receives confirmation email

### Security Features
- Reset tokens expire after 1 hour
- Tokens can only be used once
- All attempts are logged for security monitoring
- Secure token generation using cryptographic methods

### Email Configuration for Password Reset

**Gmail Setup** (recommended for development):
1. Enable 2-factor authentication on your Google account
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the App Password in `SMTP_PASSWORD` (not your regular password)
4. Set `SMTP_HOST=smtp.gmail.com` and `SMTP_PORT=587`

**Other Email Providers**:
- Update `SMTP_HOST` and `SMTP_PORT` accordingly
- Use appropriate authentication credentials in `SMTP_USER` and `SMTP_PASSWORD`

### SMTP Validation

The application automatically validates SMTP credentials at two critical points:

1. **During Setup** (`./setup.sh dev` or `./setup.sh prod`)
   - Validates credentials after interactive configuration
   - Development: Warns but allows continuation
   - Production: Fails setup if credentials are invalid

2. **On Application Startup**
   - Validates credentials when Flask initializes
   - Development: Logs warnings but continues
   - Production: Prevents startup if credentials are invalid

**Manual Validation**:
```bash
# Test your SMTP credentials anytime
python3 backend/validate_smtp.py
```

**Common Validation Errors**:
- **Authentication Failed**: Check username/password, use App Password for Gmail
- **Connection Failed**: Verify SMTP_HOST and SMTP_PORT, check firewall
- **Placeholder Detected**: Replace example values with actual credentials

For detailed troubleshooting, see `docs/Updates/20251206_smtp_validation.md`.

## License

MIT License
