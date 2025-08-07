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

### Development (M1 MacBook Pro)

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

### Production (Ubuntu Linux)

1. **Deploy with production Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

## Environment Variables

Create `.env` files in both backend and frontend directories:

### Backend (.env)
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost/notion_email
NOTION_API_KEY=your-notion-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000
```

## Logging

The application includes a comprehensive logging system for both backend and frontend. See [LOGGING.md](LOGGING.md) for detailed documentation.

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

### Setup Password Reset
Run the setup script to configure password reset:
```bash
./setup-password-reset.sh
```

## License

MIT License 