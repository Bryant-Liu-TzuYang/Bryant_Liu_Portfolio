#!/bin/bash

# Voca Recaller - Setup Script
# This script helps you set up the application for development and production

set -e

echo "🚀 Voca Recaller - Setup Script"
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

# Function to update or add a variable in .env file
update_env_var() {
    local var_name=$1
    local var_value=$2
    local env_file=".env"
    
    # Escape special characters for sed
    local escaped_value=$(echo "$var_value" | sed 's/[\/&]/\\&/g')
    
    if grep -q "^${var_name}=" "$env_file" 2>/dev/null; then
        # Update existing variable (handle both commented and uncommented)
        sed -i.bak "s|^${var_name}=.*|${var_name}=${escaped_value}|" "$env_file"
    elif grep -q "^# ${var_name}=" "$env_file" 2>/dev/null; then
        # Uncomment and update
        sed -i.bak "s|^# ${var_name}=.*|${var_name}=${escaped_value}|" "$env_file"
    else
        # Add new variable
        echo "${var_name}=${escaped_value}" >> "$env_file"
    fi
    
    # Remove backup file
    rm -f "${env_file}.bak"
}

# Function to generate a secure random key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32
}

# Function for interactive environment setup
interactive_setup() {
    local env_type=$1
    
    echo ""
    echo "🎯 Interactive Environment Setup"
    echo "=================================="
    echo ""
    echo "This wizard follows a 3-tier configuration approach:"
    echo "  Category 1: Absolutely Required (must configure)"
    echo "  Category 2: Can Use Defaults (optional to customize)"
    echo "  Category 3: Can Skip Entirely (optional features)"
    echo ""
    echo "You can type 'skip' at category prompts to move to next tier or finish."
    echo ""
    
    if [ "$env_type" = "dev" ]; then
        # ==============================================================
        # CATEGORY 1: ABSOLUTELY REQUIRED
        # ==============================================================
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 CATEGORY 1: ABSOLUTELY REQUIRED"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📧 Email Configuration (SMTP)"
        echo "Required for core email functionality"
        echo ""
        echo "For Gmail users:"
        echo "1. Enable 2-factor authentication on your Google account"
        echo "2. Generate an App Password: https://myaccount.google.com/apppasswords"
        echo "3. Use the App Password (not your regular password)"
        echo ""
        
        read -p "Configure SMTP credentials now? (y/n): " configure_smtp
        if [ "$configure_smtp" != "y" ] && [ "$configure_smtp" != "Y" ]; then
            echo ""
            echo "⏸️  Setup paused. SMTP credentials are required for email functionality."
            echo "📝 Please edit .env manually and run './setup.sh dev' again."
            exit 0
        fi
        
        # SMTP_USER
        read -p "Enter your SMTP email address: " smtp_user
        if [ "$smtp_user" = "skip" ]; then
            echo ""
            echo "⏸️  Setup paused. Please edit .env manually and run './setup.sh dev' again."
            exit 0
        fi
        
        if [ -n "$smtp_user" ]; then
            update_env_var "SMTP_USER" "$smtp_user"
            echo "✅ SMTP_USER set to: $smtp_user"
        fi
        
        # SMTP_PASSWORD
        read -s -p "Enter your SMTP password/App Password: " smtp_password
        echo ""
        if [ "$smtp_password" = "skip" ]; then
            echo ""
            echo "⏸️  Setup paused. Please edit .env manually and run './setup.sh dev' again."
            exit 0
        fi
        
        if [ -n "$smtp_password" ]; then
            update_env_var "SMTP_PASSWORD" "$smtp_password"
            echo "✅ SMTP_PASSWORD set"
        fi
        
        echo ""
        echo "✅ Category 1 complete!"
        echo ""
        
        # ==============================================================
        # CATEGORY 2: CAN USE DEFAULTS
        # ==============================================================
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 CATEGORY 2: CAN USE DEFAULTS (Optional)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "These have defaults that work for development but are insecure."
        echo "Current defaults:"
        echo "  - SECRET_KEY: dev-secret-key-for-local-development"
        echo "  - JWT_SECRET_KEY: dev-jwt-secret-key-for-local"
        echo "  - SMTP_HOST: smtp.gmail.com"
        echo "  - SMTP_PORT: 587"
        echo ""
        
        read -p "Customize these settings? (y/n to use defaults): " customize_defaults
        if [ "$customize_defaults" != "y" ] && [ "$customize_defaults" != "Y" ]; then
            echo "⏭️  Using default values for Category 2"
            echo ""
        else
            # SECRET_KEY
            read -p "Enter SECRET_KEY (or press Enter for default): " secret_key
            if [ -n "$secret_key" ] && [ "$secret_key" != "skip" ]; then
                update_env_var "SECRET_KEY" "$secret_key"
                echo "✅ SECRET_KEY set"
            fi
            
            # JWT_SECRET_KEY
            read -p "Enter JWT_SECRET_KEY (or press Enter for default): " jwt_key
            if [ -n "$jwt_key" ] && [ "$jwt_key" != "skip" ]; then
                update_env_var "JWT_SECRET_KEY" "$jwt_key"
                echo "✅ JWT_SECRET_KEY set"
            fi
            
            # SMTP_HOST
            read -p "SMTP Host [smtp.gmail.com]: " smtp_host
            if [ -n "$smtp_host" ] && [ "$smtp_host" != "skip" ]; then
                update_env_var "SMTP_HOST" "$smtp_host"
                echo "✅ SMTP_HOST set to: $smtp_host"
            fi
            
            # SMTP_PORT
            read -p "SMTP Port [587]: " smtp_port
            if [ -n "$smtp_port" ] && [ "$smtp_port" != "skip" ]; then
                update_env_var "SMTP_PORT" "$smtp_port"
                echo "✅ SMTP_PORT set to: $smtp_port"
            fi
            
            echo ""
            echo "✅ Category 2 complete!"
            echo ""
        fi
        
        # ==============================================================
        # CATEGORY 3: CAN SKIP ENTIRELY
        # ==============================================================
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 CATEGORY 3: CAN SKIP ENTIRELY (Optional Features)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Optional configurations with sensible defaults or not needed for basic dev:"
        echo "  - Notion API Key (can configure via UI later)"
        echo "  - Database (auto-uses SQLite)"
        echo "  - Redis (not needed for basic dev)"
        echo "  - Logging (defaults are fine)"
        echo ""
        
        read -p "Configure optional features? (y/n): " configure_optional
        if [ "$configure_optional" != "y" ] && [ "$configure_optional" != "Y" ]; then
            echo "⏭️  Skipping optional features"
            echo ""
        else
            # Notion API Key
            echo ""
            echo "📝 Notion API Key"
            echo "You can provide a Notion API key now or configure it later through the UI."
            read -p "Enter Notion API Key (or press Enter to skip): " notion_key
            
            if [ -n "$notion_key" ] && [ "$notion_key" != "skip" ]; then
                update_env_var "NOTION_API_KEY" "$notion_key"
                echo "✅ NOTION_API_KEY set"
            fi
            
            echo ""
            echo "✅ Category 3 complete!"
            echo ""
        fi
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ Development environment configured!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Validate SMTP credentials immediately
        echo "🔐 Validating SMTP credentials..."
        if command -v python3 &> /dev/null; then
            if python3 backend/validate_smtp.py; then
                echo ""
            else
                echo ""
                read -p "⚠️  SMTP validation failed. Continue anyway? (y/n): " continue_anyway
                if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
                    echo "Setup paused. Please fix SMTP credentials and run './setup.sh dev' again."
                    exit 1
                fi
            fi
        fi
        echo ""
        
    else
        # ==============================================================
        # CATEGORY 1: CRITICAL VARIABLES (MUST BE SET)
        # ==============================================================
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 CATEGORY 1: CRITICAL VARIABLES (MUST BE SET)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # 1-1. Security Configuration
        echo "🔒 Security Configuration"
        echo ""
        read -p "Auto-generate secure SECRET_KEY and JWT_SECRET_KEY? (y/n): " generate_keys
        if [ "$generate_keys" != "y" ] && [ "$generate_keys" != "Y" ]; then
            echo ""
            echo "⏸️  Setup paused. Security keys are required for production."
            echo "📝 Please edit .env manually and run './setup.sh prod' again."
            exit 0
        fi
        
        echo "Generating SECRET_KEY..."
        secret_key=$(generate_secret_key)
        update_env_var "SECRET_KEY" "$secret_key"
        echo "✅ SECRET_KEY generated and set"
        
        echo "Generating JWT_SECRET_KEY..."
        jwt_secret_key=$(generate_secret_key)
        update_env_var "JWT_SECRET_KEY" "$jwt_secret_key"
        echo "✅ JWT_SECRET_KEY generated and set"
        
        # 1-2. Database Configuration
        echo ""
        echo "🗄️  Database Configuration"
        echo ""
        echo "Choose database setup method:"
        echo "1. Use Docker Compose MySQL (recommended for quick setup)"
        echo "2. Use external/managed database (provide DATABASE_URL)"
        read -p "Enter choice (1/2): " db_choice
        
        if [ "$db_choice" != "1" ] && [ "$db_choice" != "2" ]; then
            echo ""
            echo "⏸️  Setup paused. Database configuration is required for production."
            echo "📝 Please configure database settings in .env and run './setup.sh prod' again."
            exit 0
        fi
        
        if [ "$db_choice" = "1" ]; then
            read -p "MySQL root password: " mysql_root_pass
            if [ "$mysql_root_pass" = "skip" ]; then
                echo "⏸️  Setup paused. Please edit .env manually."
                exit 0
            fi
            update_env_var "MYSQL_ROOT_PASSWORD" "$mysql_root_pass"
            
            read -p "Database name [voca_recaller_prod]: " mysql_db
            mysql_db=${mysql_db:-voca_recaller_prod}
            update_env_var "MYSQL_DATABASE" "$mysql_db"
            
            read -p "MySQL user [voca_recaller_user]: " mysql_user
            mysql_user=${mysql_user:-voca_recaller_user}
            update_env_var "MYSQL_USER" "$mysql_user"
            
            read -p "MySQL password: " mysql_pass
            update_env_var "MYSQL_PASSWORD" "$mysql_pass"
            
            echo "✅ MySQL Docker configuration set"
        elif [ "$db_choice" = "2" ]; then
            echo "Format: mysql+pymysql://user:password@host:3306/database"
            read -p "DATABASE_URL: " database_url
            if [ "$database_url" = "skip" ]; then
                echo "⏸️  Setup paused. Please edit .env manually."
                exit 0
            fi
            update_env_var "DATABASE_URL" "$database_url"
            echo "✅ DATABASE_URL set"
        fi
        
        # 1-3. Email Configuration (SMTP)
        echo ""
        echo "📧 Email Configuration (SMTP)"
        echo ""
        read -p "Configure SMTP settings now? (y/n): " configure_smtp
        if [ "$configure_smtp" != "y" ] && [ "$configure_smtp" != "Y" ]; then
            echo ""
            echo "⏸️  Setup paused. SMTP configuration is required for email functionality."
            echo "📝 Please edit .env manually and run './setup.sh prod' again."
            exit 0
        fi
        
        read -p "SMTP Host [smtp.gmail.com]: " smtp_host
        smtp_host=${smtp_host:-smtp.gmail.com}
        update_env_var "SMTP_HOST" "$smtp_host"
        
        read -p "SMTP Port [587]: " smtp_port
        smtp_port=${smtp_port:-587}
        update_env_var "SMTP_PORT" "$smtp_port"
        
        read -p "SMTP User/Email: " smtp_user
        if [ "$smtp_user" = "skip" ]; then
            echo "⏸️  Setup paused. Please edit .env manually."
            exit 0
        fi
        update_env_var "SMTP_USER" "$smtp_user"
        
        read -s -p "SMTP Password: " smtp_password
        echo ""
        if [ "$smtp_password" = "skip" ]; then
            echo "⏸️  Setup paused. Please edit .env manually."
            exit 0
        fi
        update_env_var "SMTP_PASSWORD" "$smtp_password"
        
        echo "✅ Email configuration set"
        
        # 1-4. Environment Configuration
        echo ""
        echo "Setting FLASK_ENV=production..."
        update_env_var "FLASK_ENV" "production"
        echo "✅ FLASK_ENV set to production"
        
        echo ""
        echo "✅ Category 1 complete!"
        echo ""
        
        # ==============================================================
        # CATEGORY 2: HIGHLY RECOMMENDED VARIABLES
        # ==============================================================
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 CATEGORY 2: HIGHLY RECOMMENDED VARIABLES"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "These have defaults but should be configured for production:"
        echo "  - Frontend URL (required for password reset emails)"
        echo "  - Redis (required for scheduled email sending)"
        echo "  - Logging (production defaults are sensible)"
        echo "  - Email template variables (professional appearance)"
        echo ""
        
        read -p "Configure highly recommended settings? (y/n to use defaults): " configure_recommended
        if [ "$configure_recommended" != "y" ] && [ "$configure_recommended" != "Y" ]; then
            echo "⚠️  Skipping highly recommended settings - some features may not work correctly"
            echo "   You can configure these later by editing .env"
            echo ""
        else
            # Frontend URL
            echo ""
            echo "🌐 Frontend Configuration"
            echo ""
            read -p "Frontend URL (e.g., https://yourdomain.com): " frontend_url
            if [ "$frontend_url" = "skip" ] || [ -z "$frontend_url" ]; then
                echo "⚠️  Frontend URL not set - password reset emails will use default"
            else
                update_env_var "FRONTEND_URL" "$frontend_url"
                echo "✅ FRONTEND_URL set"
            fi
            
            # Redis
            echo ""
            echo "🔴 Redis Configuration"
            echo ""
            read -p "Redis URL [redis://localhost:6379/0]: " redis_url
            redis_url=${redis_url:-redis://localhost:6379/0}
            if [ "$redis_url" = "skip" ]; then
                echo "⚠️  Redis not configured - scheduled emails will not work"
            else
                update_env_var "REDIS_URL" "$redis_url"
                echo "✅ REDIS_URL set"
            fi
            
            # Logging
            echo ""
            echo "📊 Logging Configuration"
            echo ""
            read -p "Configure logging? (y/n to use production defaults): " configure_logging
            if [ "$configure_logging" = "y" ]; then
                read -p "Log Level [WARNING]: " log_level
                log_level=${log_level:-WARNING}
                update_env_var "LOG_LEVEL" "$log_level"
                echo "✅ LOG_LEVEL set to $log_level"
            else
                echo "⏭️  Using production logging defaults"
            fi
            
            # Email template variables
            echo ""
            echo "📝 Email Template Variables"
            echo ""
            read -p "From Email Name [Notion Email Vocabulary]: " from_name
            from_name=${from_name:-Notion Email Vocabulary}
            update_env_var "FROM_EMAIL_NAME" "$from_name"
            echo "✅ FROM_EMAIL_NAME set"
            
            read -p "Support Email (or press Enter to use SMTP_USER): " support_email
            if [ -n "$support_email" ] && [ "$support_email" != "skip" ]; then
                update_env_var "SUPPORT_EMAIL" "$support_email"
                echo "✅ SUPPORT_EMAIL set"
            fi
            
            echo ""
            echo "✅ Category 2 complete!"
            echo ""
        fi
        
        # ==============================================================
        # OPTIONAL: Notion Integration
        # ==============================================================
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 OPTIONAL: Notion Integration"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Users can provide their own Notion tokens via UI."
        echo "A global key simplifies onboarding but is not required."
        echo ""
        
        read -p "Configure Notion API Key? (y/n): " configure_notion
        if [ "$configure_notion" = "y" ]; then
            read -p "Notion API Key: " notion_key
            if [ -n "$notion_key" ] && [ "$notion_key" != "skip" ]; then
                update_env_var "NOTION_API_KEY" "$notion_key"
                echo "✅ NOTION_API_KEY set"
            fi
        else
            echo "⏭️  Skipping Notion API Key"
        fi
        
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ Production environment configured!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Validate SMTP credentials immediately
        echo "🔐 Validating SMTP credentials..."
        if command -v python3 &> /dev/null; then
            if python3 backend/validate_smtp.py; then
                echo ""
            else
                echo ""
                echo "❌ SMTP validation failed!"
                echo "Production environment requires valid SMTP credentials."
                echo "Please fix the configuration and run './setup.sh prod' again."
                exit 1
            fi
        else
            echo "⚠️  Python3 not found, skipping SMTP validation"
            echo "   SMTP credentials will be validated when the application starts"
        fi
        echo ""
    fi
    
    echo "🎉 Configuration complete! Starting validation..."
    echo ""
}

# Function to validate environment configuration
validate_environment() {
    echo "🔐 Validating environment configuration..."
    echo ""
    
    local env_type=$1
    local is_new_env=false
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from template..."
        local template_file="docs/Examples/env_files/${env_type}-env.example"
        if [ -f "$template_file" ]; then
            cp "$template_file" .env
            echo "✅ .env file created from $template_file"
            is_new_env=true
        else
            echo "❌ Error: $template_file not found!"
            exit 1
        fi
    else
        echo "✅ .env file found"
        echo "ℹ️  To use the ${env_type} template, remove .env and run this command again"
    fi
    
    # If new .env file was created, offer interactive setup
    if [ "$is_new_env" = true ]; then
        echo ""
        read -p "Would you like to configure environment variables interactively? (y/n): " answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            interactive_setup "$env_type"
        else
            echo ""
            echo "⏸️  Skipping interactive setup."
            echo "📝 Please edit .env file manually with your configuration."
            echo "🔄 Run './setup.sh $env_type' again when ready."
            exit 0
        fi
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
    
    # Validate SMTP credentials
    echo "🔐 Validating SMTP credentials..."
    if command -v python3 &> /dev/null; then
        # Try to validate SMTP credentials
        if python3 backend/validate_smtp.py 2>&1; then
            echo ""
        else
            echo ""
            echo "⚠️  SMTP validation failed, but continuing setup..."
            echo "   You may need to update your SMTP credentials for email functionality to work."
            echo ""
        fi
    else
        echo "⚠️  Python3 not found, skipping SMTP validation"
        echo "   SMTP credentials will be validated when the application starts"
        echo ""
    fi
    
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
    
    # Validate environment first (pass 'dev' to use dev template)
    if ! validate_environment "dev"; then
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
    
    # Validate environment first (pass 'prod' to use prod template)
    if ! validate_environment "prod"; then
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
    echo "  1. Run: $0 dev (or $0 prod)"
    echo "  2. Edit .env file with your configuration"
    echo "  3. Run: $0 dev (or $0 prod) again to start services"
}

# Main script logic
case "${1:-help}" in
    "env")
        echo "⚠️  Please specify environment type: './setup.sh dev' or './setup.sh prod'"
        echo "This will validate the appropriate environment template."
        exit 1
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