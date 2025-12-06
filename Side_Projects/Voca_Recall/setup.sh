#!/bin/bash

# Notion Email Vocabulary Recall - Setup Script
# This script helps you set up the application for development and production

set -e

echo "🚀 Notion Email Vocabulary Recall - Setup Script"
echo "================================================"

# Function to check if variable exists in .env
check_env_var() {
    local var_name=$1
    if grep -q "^${var_name}=" .env 2>/dev/null; then
        local value=$(grep "^${var_name}=" .env | cut -d '=' -f2-)
        if [ -n "$value" ] && [ "$value" != "your_email@gmail.com" ] && [ "$value" != "your_app_password" ] && [ "$value" != "your-secret-key" ] && [ "$value" != "your-" ]; then
            echo "✅ $var_name is configured"
            return 0
        else
            echo "⚠️  $var_name needs to be configured in .env"
            return 1
        fi
    else
        echo "❌ $var_name is missing from .env"
        return 1
    fi
}

# Function to validate environment configuration
validate_environment() {
    echo "🔐 Validating environment configuration..."
    echo ""
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from template..."
        if [ -f "backend/env.example" ]; then
            cp backend/env.example .env
            echo "✅ .env file created from backend/env.example"
        else
            echo "❌ Error: backend/env.example not found!"
            exit 1
        fi
    else
        echo "✅ .env file found"
    fi
    
    # Check required environment variables
    echo ""
    echo "📋 Checking required environment variables..."
    
    local all_configured=true
    
    check_env_var "SMTP_HOST" || all_configured=false
    check_env_var "SMTP_PORT" || all_configured=false
    check_env_var "SMTP_USER" || all_configured=false
    check_env_var "SMTP_PASSWORD" || all_configured=false
    check_env_var "SECRET_KEY" || all_configured=false
    check_env_var "JWT_SECRET_KEY" || all_configured=false
    
    if [ "$all_configured" = false ]; then
        echo ""
        echo "⚠️  Some environment variables need configuration!"
        echo ""
        echo "📧 Email Configuration Setup:"
        echo "For Gmail users:"
        echo "1. Enable 2-factor authentication on your Google account"
        echo "2. Generate an App Password: https://myaccount.google.com/apppasswords"
        echo "3. Use the App Password (not your regular password) in SMTP_PASSWORD"
        echo ""
        echo "For other email providers:"
        echo "- Update SMTP_HOST and SMTP_PORT accordingly"
        echo "- Use appropriate authentication credentials"
        echo ""
        echo "🔑 Security Keys:"
        echo "- Generate secure random strings for SECRET_KEY and JWT_SECRET_KEY"
        echo "- You can use: openssl rand -hex 32"
        echo ""
        echo "📝 Please edit .env file with your actual values before continuing."
        return 1
    fi
    
    echo ""
    echo "✅ All required environment variables are configured!"
    echo ""
    echo "📚 Security Notes:"
    echo "- Reset tokens expire after 1 hour"
    echo "- Tokens can only be used once"
    echo "- All password reset attempts are logged"
    echo "- Consider rate limiting in production"
    echo ""
    return 0
}

# Function to setup development environment
setup_development() {
    # Check Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Validate environment first
    if ! validate_environment; then
        exit 1
    fi
    
    echo "🔧 Setting up development environment..."
    
    # Create necessary directories
    mkdir -p mysql/init
    
    # Build and start services
    echo "🐳 Building and starting Docker containers..."
    docker-compose up --build -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    echo "✅ Development environment is ready!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:5000"
    echo "🗄️  MySQL: localhost:3306"
    echo "🔴 Redis: localhost:6379"
    echo ""
    echo "🧪 Next steps:"
    echo "1. Visit http://localhost:3000 to access the application"
    echo "2. Register a new account or login"
    echo "3. Test the password reset functionality at /forgot-password"
}

# Function to setup production environment
setup_production() {
    # Check Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Validate environment first
    if ! validate_environment; then
        exit 1
    fi
    
    echo "🚀 Setting up production environment..."
    
    # Create nginx configuration directory
    mkdir -p nginx/ssl
    
    echo "🐳 Building and starting production containers..."
    docker-compose -f docker-compose.prod.yml up --build -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 45
    
    echo "✅ Production environment is ready!"
    echo "🌐 Application: http://localhost (or your domain)"
    echo "🔧 API: http://localhost/api"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    echo "✅ Services stopped."
}

# Function to view logs
view_logs() {
    echo "📋 Viewing logs..."
    docker-compose logs -f
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down -v
    docker-compose -f docker-compose.prod.yml down -v
    docker system prune -f
    echo "✅ Cleanup completed."
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  env          Validate environment configuration"
    echo "  dev          Setup development environment (includes env validation)"
    echo "  prod         Setup production environment (includes env validation)"
    echo "  stop         Stop all services"
    echo "  logs         View logs"
    echo "  cleanup      Clean up all containers and volumes"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 env       # Check environment configuration only"
    echo "  $0 dev       # Setup development environment"
    echo "  $0 prod      # Setup production environment"
    echo "  $0 stop      # Stop all services"
    echo ""
    echo "First time setup:"
    echo "  1. Run: $0 env"
    echo "  2. Edit .env file with your configuration"
    echo "  3. Run: $0 dev"
}

# Main script logic
case "${1:-help}" in
    "env")
        validate_environment
        ;;
    "dev")
        setup_development
        ;;
    "prod")
        setup_production
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        view_logs
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        show_help
        ;;
esac 