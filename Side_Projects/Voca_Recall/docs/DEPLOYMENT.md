# Deployment Guide

This guide will help you deploy the Notion Email Vocabulary Recall application on both development (M1 MacBook Pro) and production (Ubuntu Linux) environments.

## Prerequisites

### For Development (M1 MacBook Pro)
- Docker Desktop for Mac (with Apple Silicon support)
- Git
- Terminal access

### For Production (Ubuntu Linux)
- Ubuntu 20.04 or later
- Docker Engine
- Docker Compose
- Git
- Nginx (optional, for reverse proxy)
- SSL certificates (for HTTPS)

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd notion-email
```

### 2. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your configuration
nano .env
```

### 3. Run the Application

#### Development (M1 MacBook Pro)
```bash
# Use the setup script
./setup.sh dev

# Or manually
docker-compose up --build -d
```

#### Production (Ubuntu Linux)
```bash
# Use the setup script
./setup.sh prod

# Or manually
docker-compose -f docker-compose.prod.yml up --build -d
```

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
MYSQL_ROOT_PASSWORD=your_secure_mysql_root_password
MYSQL_DATABASE=notion_email_prod
MYSQL_USER=notion_user
MYSQL_PASSWORD=your_secure_mysql_password

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Notion API
NOTION_API_KEY=your_notion_api_key_here

# Email Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
```

### Getting Notion API Key

1. Go to [Notion Developers](https://developers.notion.com/)
2. Create a new integration
3. Copy the "Internal Integration Token"
4. Add the integration to your database with appropriate permissions

### Setting up Gmail for SMTP

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. Use the generated password as `SMTP_PASSWORD`

## Development Setup (M1 MacBook Pro)

### Features
- Hot reloading for both frontend and backend
- Volume mounting for live code changes
- Development-friendly logging
- Easy debugging

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

### Development Commands
```bash
# Start development environment
./setup.sh dev

# View logs
./setup.sh logs

# Stop services
./setup.sh stop

# Clean up
./setup.sh cleanup
```

## Production Setup (Ubuntu Linux)

### Server Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ available space
- **Network**: Stable internet connection

### Installation Steps

#### 1. Install Docker and Docker Compose
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
```

#### 2. Clone and Setup Application
```bash
# Clone repository
git clone <your-repository-url>
cd notion-email

# Setup environment
cp env.example .env
nano .env  # Edit with production values

# Make setup script executable
chmod +x setup.sh
```

#### 3. Deploy Application
```bash
# Deploy production environment
./setup.sh prod

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### Production Access Points
- **Application**: http://your-domain.com (or http://localhost)
- **API**: http://your-domain.com/api
- **Health Check**: http://your-domain.com/api/health

### SSL/HTTPS Setup (Optional)

#### Using Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Cloudflare (Recommended)
1. Point your domain to Cloudflare
2. Enable "Always Use HTTPS"
3. Set SSL/TLS encryption mode to "Full (strict)"

## Monitoring and Maintenance

### Health Checks
```bash
# Check application health
curl http://localhost/api/health

# Check container status
docker-compose -f docker-compose.prod.yml ps
```

### Logs
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs celery
```

### Database Backup
```bash
# Create backup
docker exec notion_email_mysql_prod mysqldump -u root -p notion_email_prod > backup.sql

# Restore backup
docker exec -i notion_email_mysql_prod mysql -u root -p notion_email_prod < backup.sql
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000

# Kill the process or change ports in docker-compose.yml
```

#### 2. Database Connection Issues
```bash
# Check MySQL container
docker-compose -f docker-compose.prod.yml logs mysql

# Reset database (WARNING: This will delete all data)
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Email Not Sending
- Check SMTP credentials in `.env`
- Verify Gmail app password is correct
- Check firewall settings
- Review email logs: `docker-compose -f docker-compose.prod.yml logs celery`

#### 4. Notion API Issues
- Verify Notion API key is correct
- Check database permissions
- Ensure integration is added to database

### Performance Optimization

#### For High Traffic
1. **Scale Celery workers**:
   ```bash
   # Edit docker-compose.prod.yml
   celery:
     command: celery -A app.celery worker --loglevel=info --concurrency=8
   ```

2. **Add Redis persistence**:
   ```yaml
   redis:
     volumes:
       - redis_data_prod:/data
   ```

3. **Database optimization**:
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_email_logs_user_id ON email_logs(user_id);
   CREATE INDEX idx_email_logs_sent_at ON email_logs(sent_at);
   ```

## Security Considerations

### Production Security Checklist
- [ ] Change all default passwords
- [ ] Use strong, unique passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting (optional)

### Firewall Configuration (Ubuntu)
```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review application logs
3. Check GitHub issues
4. Create a new issue with detailed information

## License

This project is licensed under the MIT License. 