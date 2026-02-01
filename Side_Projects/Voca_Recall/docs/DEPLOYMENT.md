# Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [Using Setup Script (Recommended)](#using-setup-script-recommended)
  - [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
  - [Quick Reference](#quick-reference)
  - [Gmail Setup (Recommended for Development)](#gmail-setup-recommended-for-development)
- [Development Environment](#development-environment)
  - [Access Points](#access-points)
  - [Commands](#commands)
  - [Features](#features)
- [Production Environment](#production-environment)
  - [Server Requirements](#server-requirements)
  - [Installation](#installation)
  - [Access Points](#access-points-1)
  - [SSL/HTTPS Setup](#sslhttps-setup)
- [Monitoring & Maintenance](#monitoring--maintenance)
  - [Health & Status](#health--status)
  - [Logs](#logs)
  - [Database Backup](#database-backup)
  - [Updates](#updates)
- [Troubleshooting](#troubleshooting)
  - [Port Conflicts](#port-conflicts)
  - [Database Issues](#database-issues)
  - [Email Not Sending](#email-not-sending)
  - [Notion API Issues](#notion-api-issues)
- [Performance Optimization](#performance-optimization)
- [Security](#security)
  - [Production Checklist](#production-checklist)
  - [Password Reset Security](#password-reset-security)
  - [Firewall (Ubuntu)](#firewall-ubuntu)
- [Support](#support)
- [License](#license)

Deploy the Voca Recaller application on development (M1 MacBook Pro) and production (Ubuntu Linux) environments.

## Prerequisites

**Development:**
- Docker Desktop for Mac (Apple Silicon support)
- Git

**Production:**
- Ubuntu 20.04+
- Docker Engine & Docker Compose
- Git
- (Optional) Nginx for reverse proxy, SSL certificates

## Quick Start

### Using Setup Script (Recommended)

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

### Manual Setup

```bash
# Clone repository
git clone <your-repository-url>
cd notion-email

# Development
docker-compose up --build -d

# Production
docker-compose -f docker-compose.prod.yml up --build -d
```

## Environment Configuration

**📖 Complete Documentation: [ENV_VARIABLES.md](ENV_VARIABLES.md)**

For comprehensive information about all environment variables, including:
- Development vs. Production requirements
- Detailed variable descriptions and defaults
- Security best practices
- Configuration templates
- Troubleshooting guide

Please refer to the [ENV_VARIABLES.md](ENV_VARIABLES.md) documentation.

### Quick Reference

The setup script (`./setup.sh env`) automatically creates a `.env` file from `backend/env.example` and validates required variables.

**Development - Minimal Required:**
- `SMTP_USER`, `SMTP_PASSWORD` - Email credentials

**Production - Critical Required:**
- `DATABASE_URL` (or MySQL variables) - Production database
- `SECRET_KEY`, `JWT_SECRET_KEY` - **Generate new secure keys!**
- `SMTP_USER`, `SMTP_PASSWORD` - Email credentials
- `FLASK_ENV=production` - Environment mode
- `FRONTEND_URL` - Your domain (for password reset links)
- `REDIS_URL` - For scheduled email tasks

### Gmail Setup (Recommended for Development)

1. Enable 2-factor authentication on your Google account
2. Generate App Password at https://myaccount.google.com/apppasswords
3. Use App Password (not regular password) in `SMTP_PASSWORD`
4. Set `SMTP_HOST=smtp.gmail.com` and `SMTP_PORT=587`

**Generate Secure Keys for Production:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Development Environment

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MySQL: localhost:3306
- Redis: localhost:6379

### Commands
```bash
./setup.sh env      # Validate environment
./setup.sh dev      # Start development
./setup.sh logs     # View logs
./setup.sh stop     # Stop services
./setup.sh cleanup  # Clean up containers and volumes
```

### Features
- Hot reloading for frontend and backend
- Live code changes via volume mounting
- Development-friendly logging

## Production Environment

### Server Requirements
- CPU: 2+ cores
- RAM: 4GB+ (8GB recommended)
- Storage: 20GB+
- Ubuntu 20.04+

### Installation

1. **Install Docker & Docker Compose**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login for group changes
```

2. **Deploy Application**
```bash
git clone <your-repository-url>
cd voca-recaller
chmod +x setup.sh
./setup.sh prod
```

### Access Points
- Application: http://your-domain.com (or http://localhost)
- API: http://your-domain.com/api
- Health Check: http://your-domain.com/api/health

### SSL/HTTPS Setup

**Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**Cloudflare (Recommended):**
- Point domain to Cloudflare
- Enable "Always Use HTTPS"
- Set SSL/TLS to "Full (strict)"

## Monitoring & Maintenance

### Health & Status
```bash
curl http://localhost/api/health
docker-compose -f docker-compose.prod.yml ps
```

### Logs
```bash
# All logs
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs backend
```

### Database Backup
```bash
# Backup
docker exec voca_recaller_mysql_prod mysqldump -u root -p voca_recaller_prod > backup.sql

# Restore
docker exec -i voca_recaller_mysql_prod mysql -u root -p voca_recaller_prod < backup.sql
```

### Updates
```bash
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

## Troubleshooting

### Port Conflicts
```bash
sudo netstat -tulpn | grep :80
# Kill process or change ports in docker-compose.yml
```

### Database Issues
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs mysql

# Reset (WARNING: Deletes all data)
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### Email Not Sending
- Verify SMTP credentials in `.env`
- Check Gmail App Password
- Review logs: `docker-compose -f docker-compose.prod.yml logs celery`

### Notion API Issues
- Verify API key
- Check database permissions
- Ensure integration is added to database

## Performance Optimization

**Scale Celery workers:**
```yaml
celery:
  command: celery -A app.celery worker --loglevel=info --concurrency=8
```

**Add Redis persistence:**
```yaml
redis:
  volumes:
    - redis_data_prod:/data
```

**Database indexes:**
```sql
CREATE INDEX idx_email_logs_user_id ON email_logs(user_id);
CREATE INDEX idx_email_logs_sent_at ON email_logs(sent_at);
```

## Security

### Production Checklist
- [ ] Change all default passwords
- [ ] Use strong, unique passwords (generate with `openssl rand -hex 32`)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting (optional)

### Password Reset Security
- Reset tokens expire after 1 hour
- Tokens can only be used once
- All attempts are logged

### Firewall (Ubuntu)
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Support

1. Check troubleshooting section
2. Review application logs
3. Check GitHub issues
4. Create new issue with details

## License

MIT License 