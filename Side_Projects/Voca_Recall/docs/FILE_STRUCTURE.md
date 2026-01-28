# File Structure Documentation

This document provides a comprehensive overview of the file structure and functionality of each component in the Voca Recaller project.

## Table of Contents
- [Root Level Files](#root-level-files)
- [Backend](#backend)
- [Frontend](#frontend)
- [Documentation](#documentation)
- [Kubernetes](#kubernetes)
- [MySQL](#mysql)
- [Tools](#tools)

---

## Root Level Files

### docker-compose.yml
**Purpose**: Development environment Docker Compose configuration  
**Functionality**: Defines and orchestrates all services needed for local development including:
- Flask backend service
- React frontend service
- MySQL database
- Redis for Celery task queue
- Celery worker and beat scheduler

### docker-compose.prod.yml
**Purpose**: Production environment Docker Compose configuration  
**Functionality**: Production-optimized service definitions with proper security settings, volume mounts, and network configurations for deployment.

### README.md
**Purpose**: Main project documentation  
**Functionality**: Provides project overview, features, tech stack, setup instructions, and usage guidelines. Entry point for understanding the project.

### setup.sh
**Purpose**: Unified setup and management script  
**Functionality**: Interactive script that handles:
- Environment variable configuration with wizard
- Docker container management (start/stop/rebuild)
- Development and production mode switching
- Initial project setup automation

### Voca_Recaller.code-workspace
**Purpose**: VS Code workspace configuration  
**Functionality**: Multi-root workspace settings for better IDE integration, allowing separate management of backend and frontend folders.

---

## Backend

### Core Application Files

#### app.py
**Purpose**: Main Flask application entry point  
**Functionality**: 
- Loads environment variables
- Creates and configures the Flask application
- Initializes logging system
- Starts the development server on port 5000

#### config.py
**Purpose**: Application configuration management  
**Functionality**: Defines the `Config` class containing:
- Database connection settings (MySQL)
- JWT authentication configuration
- Email SMTP settings
- Redis/Celery configuration
- Frontend URL for CORS and email links
- Environment-specific settings

#### celery_worker.py
**Purpose**: Celery worker process entry point  
**Functionality**: 
- Initializes Celery worker for asynchronous task processing
- Handles background tasks like sending scheduled emails
- Must be run as a separate process alongside the Flask app

#### beat_scheduler.py
**Purpose**: Celery Beat dynamic scheduler  
**Functionality**: 
- Dynamically loads email service schedules from the database
- Converts EmailService records into Celery Beat cron schedules
- Enables flexible, database-driven scheduling without code changes

#### beat.py
**Purpose**: Celery Beat launcher  
**Functionality**: 
- Starts the Celery Beat scheduler process
- Runs periodic tasks based on the schedule defined in beat_scheduler.py

#### make_celery.py
**Purpose**: Celery factory function  
**Functionality**: 
- Creates and configures Celery instance integrated with Flask
- Sets up broker and result backend connections
- Configures task serialization and timezone settings

#### admin_utils.py
**Purpose**: Command-line admin tool  
**Functionality**: 
- Lists all users in the system
- Promotes users to admin or developer roles
- Demotes users back to regular user role
- Direct database management utility

#### flask_shell.py
**Purpose**: Flask shell initialization  
**Functionality**: 
- Provides pre-configured shell environment for debugging
- Imports common models and utilities
- Enables interactive Python REPL with Flask context

#### validate_smtp.py
**Purpose**: SMTP configuration validator  
**Functionality**: 
- Tests SMTP server connectivity
- Validates email credentials
- Helps troubleshoot email delivery issues

#### requirements.txt
**Purpose**: Python dependencies specification  
**Functionality**: Lists all required Python packages with versions for pip installation.

#### Dockerfile
**Purpose**: Backend container image definition  
**Functionality**: 
- Defines Python environment setup
- Installs dependencies
- Configures application runtime
- Sets up working directory and entry point

---

### Backend `/app` Directory

#### \_\_init\_\_.py
**Purpose**: Flask application factory  
**Functionality**: 
- Initializes Flask extensions (SQLAlchemy, JWT, CORS, Bcrypt)
- Creates and configures the Flask app instance
- Registers all blueprints (routes)
- Sets up Celery integration
- Configures middleware and logging

#### models.py
**Purpose**: Database models definition  
**Functionality**: Defines SQLAlchemy ORM models:
- **User**: User accounts with authentication
- **NotionToken**: Notion API integration tokens
- **NotionDatabase**: Connected Notion databases
- **EmailSettings**: User email preferences (deprecated, migrated to EmailService)
- **EmailService**: Email scheduling services with frequency, time, and database associations
- **EmailLog**: Email delivery tracking and status
- **PasswordResetToken**: Password reset tokens with expiration
- **APIToken**: API authentication tokens for programmatic access

#### auth.py
**Purpose**: Authentication blueprint  
**Functionality**: Handles all authentication-related endpoints:
- User registration with email validation
- Login with JWT token generation
- Token refresh
- Password reset request
- Password reset confirmation
- Profile management
- Email verification

#### user.py
**Purpose**: User management blueprint  
**Functionality**: Provides user-related API endpoints:
- Get user profile
- Update user information
- Manage user settings
- User-specific operations

#### database.py
**Purpose**: Notion database management blueprint  
**Functionality**: Handles Notion database operations:
- Connect new Notion databases
- List user's databases
- Update database settings
- Delete database connections
- Fetch vocabulary items from Notion

#### email_service.py
**Purpose**: Email service management blueprint  
**Functionality**: CRUD operations for email services:
- Create scheduled email services
- List user's email services
- Update service configuration (frequency, time, word count)
- Delete services
- Toggle active/inactive status

#### email.py
**Purpose**: Email delivery functionality  
**Functionality**: 
- Send vocabulary emails via SMTP
- Format email content with HTML templates
- Handle password reset emails
- Celery task definitions for scheduled emails
- Email schedule reload mechanism

#### tokens.py
**Purpose**: API token management blueprint  
**Functionality**: 
- Create API tokens for programmatic access
- List user's tokens
- Revoke tokens
- Token-based authentication

#### admin.py
**Purpose**: Admin operations blueprint  
**Functionality**: Admin-only endpoints:
- User management (list, promote, demote)
- System statistics
- Global settings management
- Role-based access control enforcement

#### frontend_logs.py
**Purpose**: Frontend logging endpoint  
**Functionality**: 
- Receives logs from React frontend
- Centralizes logging from client-side
- Helps debug production issues

#### logging_config.py
**Purpose**: Logging system configuration  
**Functionality**: 
- Sets up structured logging with rotation
- Configures log levels and formats
- Provides logger factory functions
- Manages log file locations

#### middleware.py
**Purpose**: Request/response middleware  
**Functionality**: 
- Request logging with timing
- Performance monitoring
- Database operation tracking
- Decorators for API call logging

#### smtp_validator.py
**Purpose**: SMTP validation logic  
**Functionality**: 
- Validates SMTP server settings
- Tests email connectivity
- Returns detailed error messages

#### email.py (additional functions)
**Purpose**: Email template and sending logic  
**Functionality**: 
- HTML email template generation
- Vocabulary formatting
- SMTP connection management
- Error handling for email delivery

---

### Backend Subdirectories

#### `/instance`
**Purpose**: Flask instance-specific files  
**Functionality**: Contains SQLite database file in development mode (if used) and other runtime instance data.

#### `/logs`
**Purpose**: Application log storage  
**Functionality**: Stores rotating log files with timestamps for debugging and monitoring.

---

## Frontend

### Root Frontend Files

#### package.json
**Purpose**: Node.js project configuration  
**Functionality**: 
- Defines project metadata
- Lists npm dependencies (React, React Router, Axios, etc.)
- Defines build and start scripts

#### Dockerfile
**Purpose**: Frontend container image  
**Functionality**: 
- Multi-stage build for optimized production image
- Builds React app
- Serves static files via Nginx

#### nginx.conf
**Purpose**: Nginx web server configuration  
**Functionality**: 
- Serves React static files
- Configures routing for SPA
- Sets up proxy to backend API
- Handles CORS headers

#### postcss.config.js
**Purpose**: PostCSS configuration  
**Functionality**: Configures CSS processing with Tailwind CSS and autoprefixer.

#### tailwind.config.js
**Purpose**: Tailwind CSS configuration  
**Functionality**: 
- Defines design system (colors, spacing, etc.)
- Configures content paths for purging
- Customizes Tailwind utilities

---

### Frontend `/public` Directory

#### index.html
**Purpose**: HTML entry point  
**Functionality**: 
- Root HTML file for React app
- Contains root div for React mounting
- Includes meta tags and favicon

#### manifest.json
**Purpose**: Progressive Web App manifest  
**Functionality**: Defines app metadata for PWA installation and mobile behavior.

---

### Frontend `/src` Directory

#### index.js
**Purpose**: React application entry point  
**Functionality**: 
- Renders React root component
- Imports global styles
- Wraps app with necessary providers (Router, Auth)

#### App.js
**Purpose**: Main React component  
**Functionality**: 
- Defines application routing structure
- Implements protected routes
- Handles authentication-based navigation
- Renders layout and page components

#### index.css
**Purpose**: Global styles  
**Functionality**: 
- Imports Tailwind CSS base, components, and utilities
- Defines global CSS variables and styles

---

### Frontend `/src/components` Directory

#### Navbar.js
**Purpose**: Navigation bar component  
**Functionality**: 
- Displays app navigation menu
- Shows current user info
- Handles logout functionality
- Responsive mobile menu

#### LoadingSpinner.js
**Purpose**: Loading indicator component  
**Functionality**: Displays animated spinner during async operations.

#### LoggingStatus.js
**Purpose**: Logging status display component  
**Functionality**: Shows current logging configuration and status indicators.

#### EmailServiceModal.js
**Purpose**: Email service configuration modal  
**Functionality**: 
- Form for creating/editing email services
- Database selection
- Schedule configuration (time, frequency, word count)
- Validation and submission

---

### Frontend `/src/contexts` Directory

#### AuthContext.js
**Purpose**: Authentication context provider  
**Functionality**: 
- Manages global authentication state
- Provides login/logout functions
- Handles JWT token storage and refresh
- Protects routes based on auth status

---

### Frontend `/src/pages` Directory

#### Login.js
**Purpose**: Login page component  
**Functionality**: 
- User login form
- Email/password authentication
- JWT token handling
- Navigation to dashboard on success

#### Register.js
**Purpose**: Registration page component  
**Functionality**: 
- New user registration form
- Validation for email, password, names
- Account creation
- Auto-login after registration

#### ForgotPassword.js
**Purpose**: Password reset request page  
**Functionality**: 
- Email input for password reset
- Sends reset token email
- Confirmation message

#### ResetPassword.js
**Purpose**: Password reset confirmation page  
**Functionality**: 
- New password form
- Token validation from URL
- Password update
- Redirect to login

#### Dashboard.js
**Purpose**: Main dashboard page  
**Functionality**: 
- Overview of user's email services
- Quick statistics
- Recent activity
- Service status indicators

#### Databases.js
**Purpose**: Notion database management page  
**Functionality**: 
- List connected Notion databases
- Add new database connections
- Delete databases
- View database details

#### Services.js
**Purpose**: Email service management page  
**Functionality**: 
- List all email services
- Create new services
- Edit existing services
- Delete services
- Toggle active/inactive

#### Settings.js
**Purpose**: User settings page  
**Functionality**: 
- Update user profile
- Change password
- Configure email preferences
- Account settings

#### ManageTokens.js
**Purpose**: API token management page (Admin/Developer)  
**Functionality**: 
- Create API tokens
- List active tokens
- Revoke tokens
- Token usage information

#### ManageUsers.js
**Purpose**: User management page (Admin only)  
**Functionality**: 
- List all users
- Promote/demote user roles
- Deactivate accounts
- View user statistics

#### EmailLogs.js
**Purpose**: Email log viewer page  
**Functionality**: 
- View email delivery history
- Filter by status, date, service
- See error messages
- Track delivery success rates

---

### Frontend `/src/utils` Directory

#### apiService.js
**Purpose**: API client wrapper  
**Functionality**: 
- Centralized Axios configuration
- Request/response interceptors
- JWT token attachment
- Error handling
- Base URL configuration

#### logger.js
**Purpose**: Frontend logging utility  
**Functionality**: 
- Sends logs to backend endpoint
- Categorizes log levels (info, warn, error)
- Captures client-side errors
- Helps debug production issues

---

## Documentation (`/docs`)

### DATABASE.md
**Purpose**: Database schema documentation  
**Functionality**: Describes all database tables, columns, relationships, and migrations.

### DEPLOYMENT.md
**Purpose**: Deployment guide  
**Functionality**: Instructions for deploying to production environments using Docker Compose.

### EMAIL_SCHEDULING.md
**Purpose**: Email scheduling documentation  
**Functionality**: Explains how the Celery-based email scheduling system works.

### ENV_VARIABLES.md
**Purpose**: Environment variables reference  
**Functionality**: Complete list of all environment variables with descriptions and examples.

### K8S_BEGINNER_GUIDE.md
**Purpose**: Kubernetes beginner tutorial  
**Functionality**: Introduction to Kubernetes concepts for new users.

### K8S_DEPLOYMENT.md
**Purpose**: Kubernetes deployment guide  
**Functionality**: Instructions for deploying the application to Kubernetes clusters.

### LOGGING.md
**Purpose**: Logging system documentation  
**Functionality**: Explains logging configuration, log levels, and troubleshooting.

### Q&A.md
**Purpose**: Frequently asked questions  
**Functionality**: Common questions and answers about the application.

### ROLE_CONTROL.md
**Purpose**: Role-based access control documentation  
**Functionality**: Explains user roles (user, developer, admin) and their permissions.

### bryant_reading.md
**Purpose**: Personal development notes  
**Functionality**: Developer's reading list and learning resources.

---

### Documentation `/docs/Examples/env_files` Directory

#### dev-env.example
**Purpose**: Development environment template  
**Functionality**: Example .env file with placeholder values for development setup.

#### prod-env.example
**Purpose**: Production environment template  
**Functionality**: Example .env file with production-ready configurations and security notes.

---

### Documentation `/docs/Updates` Directory

#### 20251206_env_templates_split.md
**Purpose**: Update log  
**Functionality**: Documents the splitting of environment templates into dev and prod versions.

#### 20251206_refactor.md
**Purpose**: Refactoring log  
**Functionality**: Documents code refactoring changes made on December 6, 2025.

#### 20251206_smtp_validation.md
**Purpose**: Feature log  
**Functionality**: Documents the addition of SMTP validation functionality.

---

## Kubernetes (`/k8s`)

### backend.yaml
**Purpose**: Backend deployment configuration  
**Functionality**: Kubernetes deployment and service definitions for Flask backend with Celery workers.

### celery-worker.yaml
**Purpose**: Celery worker deployment  
**Functionality**: Separate Celery worker pods configuration for scalable task processing.

### frontend.yaml
**Purpose**: Frontend deployment configuration  
**Functionality**: Kubernetes deployment and service definitions for React frontend with Nginx.

### mysql.yaml
**Purpose**: MySQL database deployment  
**Functionality**: StatefulSet for MySQL with persistent storage configuration.

### mysql-pvc.yaml
**Purpose**: MySQL persistent volume claim  
**Functionality**: Defines storage requirements for MySQL data persistence.

### redis.yaml
**Purpose**: Redis deployment configuration  
**Functionality**: Redis service for Celery message broker and result backend.

### configmap.yaml
**Purpose**: Configuration map  
**Functionality**: Stores non-sensitive configuration data accessible to all pods.

### secret.yaml
**Purpose**: Secrets management  
**Functionality**: Template for storing sensitive data (passwords, API keys) in Kubernetes.

### ingress.yaml
**Purpose**: Ingress controller configuration  
**Functionality**: Defines HTTP routing rules and load balancing for external access.

### namespace.yaml
**Purpose**: Namespace definition  
**Functionality**: Creates isolated namespace for the application resources.

### deploy.sh
**Purpose**: Kubernetes deployment script  
**Functionality**: Automated script to apply all Kubernetes configurations in correct order.

### cleanup.sh
**Purpose**: Kubernetes cleanup script  
**Functionality**: Removes all deployed resources from the cluster.

### README.md
**Purpose**: Kubernetes setup documentation  
**Functionality**: Instructions for deploying and managing the application on Kubernetes.

### HEALTH_CHECK.md
**Purpose**: Health check documentation  
**Functionality**: Explains liveness and readiness probes configuration for pods.

---

## MySQL (`/mysql`)

### `/init` Directory
**Purpose**: Database initialization scripts directory  
**Functionality**: Contains SQL scripts run when MySQL container first starts.

### init.sql
**Purpose**: Initial database schema  
**Functionality**: 
- Creates database tables
- Sets up initial data
- Configures database users and permissions

---

## Tools (`/tools`)

### admin.sh
**Purpose**: Admin management script  
**Functionality**: 
- Wrapper around admin_utils.py
- Simplifies user role management commands
- Quick access to admin operations

### check_email_status.sh
**Purpose**: Email status checker  
**Functionality**: 
- Queries database for email service status
- Checks recent email logs
- Helps diagnose email delivery issues
- Provides quick status overview

---

## Summary

This file structure follows a modern full-stack application architecture:

- **Backend (Flask)**: RESTful API with JWT authentication, Celery for background tasks, and SQLAlchemy ORM
- **Frontend (React)**: Single-page application with React Router, context-based state management, and Tailwind CSS
- **Infrastructure**: Docker for containerization, Kubernetes for orchestration, and comprehensive documentation
- **DevOps**: Automated setup scripts, deployment automation, and monitoring tools

The modular structure allows for easy maintenance, testing, and scaling of individual components.
