from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from email_validator import validate_email, EmailNotValidError
from .models import User, db
from .logging_config import get_logger
from .middleware import log_api_call, admin_required

admin_bp = Blueprint('admin', __name__)
logger = get_logger(__name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
@log_api_call("List All Users")
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = User.query
        
        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.email.ilike(search_filter),
                    User.first_name.ilike(search_filter),
                    User.last_name.ilike(search_filter)
                )
            )
        
        # Paginate results
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = [user.to_dict() for user in pagination.items]
        
        logger.info(f"Listed {len(users_data)} users (page {page})")
        
        return jsonify({
            'users': users_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to list users', 'details': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required()
@log_api_call("Get User Details")
def get_user(user_id):
    """Get specific user details (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User not found: ID {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        logger.info(f"Retrieved user details for ID: {user_id}")
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required()
@log_api_call("Update User Role")
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        # Validate role
        valid_roles = ['user', 'developer', 'admin']
        if not new_role or new_role not in valid_roles:
            logger.warning(f"Invalid role provided: {new_role}")
            return jsonify({'error': f'Role must be one of: {", ".join(valid_roles)}'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User not found for role update: ID {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        logger.info(f"Updated user role: {user.email} from '{old_role}' to '{new_role}'")
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user role: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update user role', 'details': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required()
@log_api_call("Create New User")
def create_user():
    """Create a new user (admin only)"""
    try:
        data = request.get_json()
        logger.info(f"Admin creating user for email: {data.get('email', 'unknown')}")
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"User creation failed: missing field '{field}'")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            logger.warning(f"User creation failed: invalid email format '{data.get('email')}'")
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"User creation failed: user already exists '{data.get('email')}'")
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Validate password strength
        if len(data['password']) < 8:
            logger.warning(f"User creation failed: password too short")
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Validate role if provided
        role = data.get('role', 'user')
        valid_roles = ['user', 'developer', 'admin']
        if role not in valid_roles:
            logger.warning(f"User creation failed: invalid role '{role}'")
            return jsonify({'error': f'Role must be one of: {", ".join(valid_roles)}'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User created successfully by admin: {user.email} (ID: {user.id}, Role: {user.role})")
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"User creation error: {str(e)}", exc_info=True)
        return jsonify({'error': 'User creation failed', 'details': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/activate', methods=['PUT'])
@jwt_required()
@admin_required()
@log_api_call("Toggle User Active Status")
def toggle_user_active(user_id):
    """Activate or deactivate a user account (admin only)"""
    try:
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'is_active field is required'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User not found for activation toggle: ID {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = is_active
        db.session.commit()
        
        status = "activated" if is_active else "deactivated"
        logger.info(f"User {status}: {user.email} (ID: {user_id})")
        
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling user active status: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update user status', 'details': str(e)}), 500

@admin_bp.route('/users/search', methods=['GET'])
@jwt_required()
@admin_required()
@log_api_call("Search Users")
def search_users():
    """Search users by email or ID (admin only)"""
    try:
        email = request.args.get('email', '', type=str)
        user_id = request.args.get('id', None, type=int)
        
        if not email and not user_id:
            return jsonify({'error': 'Email or ID parameter required'}), 400
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                logger.info(f"Found user by ID: {user_id}")
                return jsonify({'users': [user.to_dict()]}), 200
            else:
                logger.info(f"No user found with ID: {user_id}")
                return jsonify({'users': []}), 200
        
        if email:
            # Exact match first
            user = User.query.filter_by(email=email).first()
            if user:
                logger.info(f"Found user by exact email match: {email}")
                return jsonify({'users': [user.to_dict()]}), 200
            
            # Partial match
            users = User.query.filter(User.email.ilike(f"%{email}%")).limit(10).all()
            logger.info(f"Found {len(users)} users by partial email match: {email}")
            return jsonify({'users': [u.to_dict() for u in users]}), 200
        
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to search users', 'details': str(e)}), 500
