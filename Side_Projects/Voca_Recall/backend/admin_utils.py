#!/usr/bin/env python3
"""
Admin utility script for managing user roles
Usage:
    python admin_utils.py --list                    # List all users
    python admin_utils.py --promote email@example.com admin     # Set user as admin
    python admin_utils.py --promote email@example.com developer # Set user as developer
    python admin_utils.py --demote email@example.com            # Set user back to user role
"""

import sys
import os
import argparse

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User
from application import app  # Reuse the app creation from application.py

def list_users():
    """List all users with their roles"""
    with app.app_context():
        users = User.query.order_by(User.created_at.desc()).all()
        
        if not users:
            print("No users found in the database")
            return
        
        print("\n" + "="*80)
        print(f"{'ID':<5} {'Email':<30} {'Name':<25} {'Role':<12} {'Active'}")
        print("="*80)
        
        for user in users:
            name = f"{user.first_name} {user.last_name}"
            active_status = "✓" if user.is_active else "✗"
            print(f"{user.id:<5} {user.email:<30} {name:<25} {user.role:<12} {active_status}")
        
        print("="*80)
        print(f"Total users: {len(users)}\n")

def promote_user(email, role):
    """Promote a user to a specific role"""
    valid_roles = ['user', 'developer', 'admin']
    
    if role not in valid_roles:
        print(f"Error: Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}")
        return False
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Error: User with email '{email}' not found")
            return False
        
        old_role = user.role
        user.role = role
        db.session.commit()
        
        print(f"✓ Successfully updated user role")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Old role: {old_role}")
        print(f"  New role: {role}")
        
        return True

def demote_user(email):
    """Demote a user back to regular user role"""
    return promote_user(email, 'user')

def main():
    parser = argparse.ArgumentParser(description='User role management utility')
    parser.add_argument('--list', action='store_true', help='List all users')
    parser.add_argument('--promote', nargs=2, metavar=('EMAIL', 'ROLE'), 
                       help='Promote user to role (admin, developer, or user)')
    parser.add_argument('--demote', metavar='EMAIL', 
                       help='Demote user to regular user role')
    
    args = parser.parse_args()
    
    if args.list:
        list_users()
    elif args.promote:
        email, role = args.promote
        promote_user(email, role)
    elif args.demote:
        demote_user(args.demote)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python admin_utils.py --list")
        print("  python admin_utils.py --promote user@example.com admin")
        print("  python admin_utils.py --promote user@example.com developer")
        print("  python admin_utils.py --demote user@example.com")

if __name__ == '__main__':
    main()
