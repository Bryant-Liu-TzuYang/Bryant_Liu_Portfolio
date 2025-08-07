#!/bin/bash

# Notion Email Vocabulary Recall - Setup Script
# This script helps you set up the application for development and production

set -e

echo "🚀 Notion Email Vocabulary Recall - Setup Script"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp backend/env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo "✅ .env file already exists."
fi

# Function to setup development environment
setup_development() {
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
}

# Function to setup production environment
setup_production() {
    echo "🚀 Setting up production environment..."
    
    # Check if .env file has production values
    if grep -q "your-" .env; then
        echo "⚠️  Please update your .env file with production values before continuing."
        echo "   Edit the .env file and replace all 'your-*' values with actual values."
        exit 1
    fi
    
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
    echo "  dev          Setup development environment"
    echo "  prod         Setup production environment"
    echo "  stop         Stop all services"
    echo "  logs         View logs"
    echo "  cleanup      Clean up all containers and volumes"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev       # Setup development environment"
    echo "  $0 prod      # Setup production environment"
    echo "  $0 stop      # Stop all services"
}

# Main script logic
case "${1:-help}" in
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