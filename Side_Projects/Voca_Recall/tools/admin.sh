#!/bin/bash

# Notion Email Vocabulary Recall - Admin Script
# Helper script for common administrative tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Voca Recaller Admin Tool${NC}"
echo "================================"

# Function to list all users
list_users() {
    echo -e "\n${GREEN}📋 Registered Users${NC}"
    echo "================================"
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    users = User.query.all()
    if users:
        print(f'\n{\"=\"*80}')
        for user in users:
            print(f'ID: {user.id:4d} | Email: {user.email:30s} | Name: {user.first_name} {user.last_name}')
            print(f'         | Created: {user.created_at} | Active: {user.is_active}')
            print(f'{\"=\"*80}')
        print(f'\n✅ Total users: {len(users)}')
    else:
        print('\n⚠️  No users registered yet.')
"
}

# Function to create a new user
create_user() {
    echo -e "\n${GREEN}➕ Create New User${NC}"
    echo "================================"
    read -p "Email: " email
    read -p "First Name: " first_name
    read -p "Last Name: " last_name
    read -s -p "Password: " password
    echo ""
    
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    # Check if user exists
    existing = User.query.filter_by(email='$email').first()
    if existing:
        print('❌ Error: User with this email already exists!')
        exit(1)
    
    # Create new user
    user = User(
        email='$email',
        first_name='$first_name',
        last_name='$last_name'
    )
    user.set_password('$password')
    db.session.add(user)
    db.session.commit()
    print(f'✅ User created successfully! ID: {user.id}')
"
}

# Function to delete a user
delete_user() {
    echo -e "\n${RED}🗑️  Delete User${NC}"
    echo "================================"
    read -p "Enter user email or ID: " identifier
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "❌ Deletion cancelled."
        return
    fi
    
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    # Try to find by email first, then by ID
    user = User.query.filter_by(email='$identifier').first()
    if not user:
        try:
            user = User.query.get(int('$identifier'))
        except:
            pass
    
    if not user:
        print('❌ User not found!')
        exit(1)
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    print(f'✅ User {email} deleted successfully!')
"
}

# Function to reset user password
reset_password() {
    echo -e "\n${YELLOW}🔑 Reset User Password${NC}"
    echo "================================"
    read -p "Enter user email: " email
    read -s -p "New Password: " password
    echo ""
    
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='$email').first()
    if not user:
        print('❌ User not found!')
        exit(1)
    
    user.set_password('$password')
    db.session.commit()
    print(f'✅ Password reset successfully for {user.email}!')
"
}

# Function to view user details
view_user() {
    echo -e "\n${GREEN}👤 User Details${NC}"
    echo "================================"
    read -p "Enter user email or ID: " identifier
    
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User, NotionDatabase, EmailService
app = create_app()
with app.app_context():
    # Try to find by email first, then by ID
    user = User.query.filter_by(email='$identifier').first()
    if not user:
        try:
            user = User.query.get(int('$identifier'))
        except:
            pass
    
    if not user:
        print('❌ User not found!')
        exit(1)
    
    print(f'\n📧 Email: {user.email}')
    print(f'👤 Name: {user.first_name} {user.last_name}')
    print(f'🆔 ID: {user.id}')
    print(f'📅 Created: {user.created_at}')
    print(f'✅ Active: {user.is_active}')
    print(f'🔐 Password Hash: {user.password_hash}')
    
    # Show databases
    databases = NotionDatabase.query.filter_by(user_id=user.id).all()
    print(f'\n📚 Notion Databases: {len(databases)}')
    for db_item in databases:
        print(f'  - {db_item.database_name} ({db_item.database_id})')
    
    # Show email services
    services = EmailService.query.filter_by(user_id=user.id).all()
    if services:
        print(f'\n📧 Email Services: {len(services)}')
        for service in services:
            print(f'  - {service.service_name}')
            print(f'    Database ID: {service.database_id}')
            print(f'    Frequency: {service.frequency}')
            print(f'    Send Time: {service.send_time} ({service.timezone})')
            print(f'    Vocabulary Count: {service.vocabulary_count}')
            print(f'    Active: {service.is_active}')
    else:
        print(f'\n📧 Email Services: None configured')
"
}

# Function to view user tokens
view_tokens() {
    echo -e "\n${GREEN}🔑 User Tokens and Databases${NC}"
    echo "================================"
    read -p "Enter user email or ID: " identifier
    
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User, NotionDatabase, NotionToken
app = create_app()
with app.app_context():
    # Try to find by email first, then by ID
    user = User.query.filter_by(email='$identifier').first()
    if not user:
        try:
            user = User.query.get(int('$identifier'))
        except:
            pass
    
    if not user:
        print('❌ User not found!')
        exit(1)
    
    print(f'\n📧 User: {user.email}')
    print(f'👤 Name: {user.first_name} {user.last_name}')
    print(f'🆔 ID: {user.id}')
    
    # Show all tokens
    tokens = NotionToken.query.filter_by(user_id=user.id).all()
    print(f'\n🔑 Notion Tokens: {len(tokens)}')
    print(f'{\"=\"*100}')
    
    if not tokens:
        print('⚠️  No tokens stored.')
    else:
        for token in tokens:
            print(f'\nToken ID: {token.id}')
            print(f'Token Name: {token.token_name or \"Unnamed\"}')
            print(f'Token: {token.token[:20]}...{token.token[-10:] if len(token.token) > 30 else \"\"}')
            print(f'Active: {token.is_active}')
            print(f'Created: {token.created_at}')
            
            # Show databases using this token
            dbs = NotionDatabase.query.filter_by(token_id=token.id).all()
            if dbs:
                print(f'Connected Databases ({len(dbs)}):')
                for db in dbs:
                    print(f'  - [{db.id}] {db.database_name}')
                    print(f'    Database ID: {db.database_id}')
                    print(f'    Frequency: {db.frequency}')
                    print(f'    Active: {db.is_active}')
            else:
                print('Connected Databases: None')
            print(f'{\"=\"*100}')
    
    # Show databases without tokens (legacy)
    orphan_dbs = NotionDatabase.query.filter_by(user_id=user.id, token_id=None).all()
    if orphan_dbs:
        print(f'\n⚠️  Databases without stored tokens: {len(orphan_dbs)}')
        for db in orphan_dbs:
            print(f'  - [{db.id}] {db.database_name} ({db.database_id})')
            print(f'    Frequency: {db.frequency}, Active: {db.is_active}')
"
}

# Function to view database statistics
view_stats() {
    echo -e "\n${GREEN}📊 Database Statistics${NC}"
    echo "================================"
    docker-compose exec -T backend python -c "
from app import create_app, db
from app.models import User, NotionDatabase, EmailService
app = create_app()
with app.app_context():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_databases = NotionDatabase.query.count()
    total_email_services = EmailService.query.count()
    enabled_services = EmailService.query.filter_by(is_active=True).count()
    
    print(f'\n👥 Total Users: {total_users}')
    print(f'✅ Active Users: {active_users}')
    print(f'❌ Inactive Users: {total_users - active_users}')
    print(f'\n📚 Total Notion Databases: {total_databases}')
    print(f'📧 Email Services Configured: {total_email_services}')
    print(f'✉️  Email Services Enabled: {enabled_services}')
"
}

# Function to backup database
backup_database() {
    echo -e "\n${GREEN}💾 Backup Database${NC}"
    echo "================================"
    BACKUP_DIR="./backups"
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/voca_recaller_backup_$TIMESTAMP.sql"
    
    echo "Creating backup..."
    docker-compose exec -T mysql mysqldump -uuser -ppassword voca_recaller_dev > "$BACKUP_FILE"
    
    if [ -f "$BACKUP_FILE" ]; then
        SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "✅ Backup created successfully!"
        echo -e "   File: $BACKUP_FILE"
        echo -e "   Size: $SIZE"
    else
        echo -e "❌ Backup failed!"
    fi
}

# Function to view logs
view_logs() {
    echo -e "\n${GREEN}📋 View Logs${NC}"
    echo "================================"
    echo "1) Backend logs"
    echo "2) Frontend logs"
    echo "3) Celery logs"
    echo "4) All logs"
    read -p "Choose option (1-4): " choice
    
    case $choice in
        1)
            docker-compose logs -f backend
            ;;
        2)
            docker-compose logs -f frontend
            ;;
        3)
            docker-compose logs -f celery
            ;;
        4)
            docker-compose logs -f
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
}

# Function to restart services
restart_services() {
    echo -e "\n${YELLOW}🔄 Restart Services${NC}"
    echo "================================"
    echo "1) Backend only"
    echo "2) Frontend only"
    echo "3) Celery only"
    echo "4) All services"
    read -p "Choose option (1-4): " choice
    
    case $choice in
        1)
            docker-compose restart backend
            echo "✅ Backend restarted"
            ;;
        2)
            docker-compose restart frontend
            echo "✅ Frontend restarted"
            ;;
        3)
            docker-compose restart celery
            echo "✅ Celery restarted"
            ;;
        4)
            docker-compose restart
            echo "✅ All services restarted"
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
}

# Function to check service status
check_status() {
    echo -e "\n${GREEN}📡 Service Status${NC}"
    echo "================================"
    docker-compose ps
}

# Function to access database shell
database_shell() {
    echo -e "\n${GREEN}🗄️  MySQL Shell${NC}"
    echo "================================"
    docker-compose exec mysql mysql -uuser -ppassword -D voca_recaller_dev
}

# Function to access Flask shell
flask_shell() {
    echo -e "\n${GREEN}🐍 Flask Shell${NC}"
    echo "================================"
    docker-compose exec backend python flask_shell.py
}

# Function to show help
show_help() {
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "User Management:"
    echo "  list-users       List all registered users"
    echo "  create-user      Create a new user"
    echo "  delete-user      Delete a user"
    echo "  view-user        View detailed user information"
    echo "  view-tokens      View user's Notion tokens and connected databases"
    echo "  reset-password   Reset user password"
    echo ""
    echo "System Management:"
    echo "  stats            View database statistics"
    echo "  status           Check service status"
    echo "  logs             View application logs"
    echo "  restart          Restart services"
    echo "  backup           Backup database"
    echo ""
    echo "Development Tools:"
    echo "  db-shell         Access MySQL shell"
    echo "  flask-shell      Access Flask/Python shell"
    echo ""
    echo "Examples:"
    echo "  $0 list-users    # List all users"
    echo "  $0 view-tokens   # View user tokens"
    echo "  $0 stats         # View statistics"
    echo "  $0 backup        # Backup database"
}

# Main script logic
case "${1:-help}" in
    "list-users"|"users")
        list_users
        ;;
    "create-user"|"add-user")
        create_user
        ;;
    "delete-user"|"remove-user")
        delete_user
        ;;
    "view-user"|"show-user")
        view_user
        ;;
    "view-tokens"|"tokens")
        view_tokens
        ;;
    "reset-password"|"reset-pwd")
        reset_password
        ;;
    "stats"|"statistics")
        view_stats
        ;;
    "status")
        check_status
        ;;
    "logs")
        view_logs
        ;;
    "restart")
        restart_services
        ;;
    "backup")
        backup_database
        ;;
    "db-shell"|"mysql")
        database_shell
        ;;
    "flask-shell"|"shell")
        flask_shell
        ;;
    "help"|*)
        show_help
        ;;
esac
