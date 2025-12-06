# Notion Email Vocabulary Recall

A web application that helps users recall vocabulary from their Notion databases by sending daily email reminders with random vocabulary items.

## Features

- User authentication and registration
- **Password reset functionality with email verification**
- Connect multiple Notion databases
- Customizable daily email frequency and vocabulary count
- Secure storage of user preferences
- Daily automated email delivery
- Comprehensive logging system with request tracking and performance monitoring

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: React (JavaScript/TypeScript)
- **Database**: MySQL
- **Email Service**: SMTP (configurable)
- **Notion API**: Official Notion SDK

## Project Structure

```
notion-email/
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

## Quick Start

### Using Setup Script (Recommended)

The project includes a unified setup script that handles both environment configuration and Docker management:

```bash
# First time setup
./setup.sh env          # Validate environment configuration
# Edit .env with your actual values
./setup.sh dev          # Start development environment

# Other commands
./setup.sh prod         # Setup production environment
./setup.sh stop         # Stop all services
./setup.sh logs         # View logs
./setup.sh cleanup      # Clean up containers and volumes
```

The `dev` and `prod` commands automatically validate your environment before starting services.

**What the script does:**
1. Creates `.env` file from template if needed
2. Validates required environment variables:
   - `SECRET_KEY`, `JWT_SECRET_KEY` - Security keys
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email configuration
3. Provides setup guidance (Gmail App Passwords, security notes, etc.)
4. Starts Docker containers and services

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
# Minimal .env for development
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

All other variables have sensible defaults. See [ENV_VARIABLES.md](docs/ENV_VARIABLES.md) for the complete development and production templates.

## Documentation

- **[ENV_VARIABLES.md](docs/ENV_VARIABLES.md)** - Comprehensive environment variables guide
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

The setup script (`./setup.sh env`) will validate these settings and provide detailed guidance.

## License

MIT License
