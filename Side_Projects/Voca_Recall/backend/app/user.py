from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, EmailSettings, db
from .logging_config import get_logger
from .middleware import log_api_call
from datetime import datetime

user_bp = Blueprint('user', __name__)
logger = get_logger(__name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
@log_api_call("Get user profile")
def get_profile():
    """Get user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Fetching profile for user {current_user_id}")
        
        user = User.query.get(current_user_id)
        
        if not user:
            logger.warning(f"User {current_user_id} not found")
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's email settings
        email_settings = EmailSettings.query.filter_by(user_id=current_user_id).first()
        
        response_data = {
            'user': user.to_dict(),
            'email_settings': email_settings.to_dict() if email_settings else None
        }
        
        logger.info(f"Successfully retrieved profile for user {current_user_id}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Failed to get profile for user {current_user_id}: {str(e)}")
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('first_name'):
            user.first_name = data['first_name']
        if data.get('last_name'):
            user.last_name = data['last_name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500



@user_bp.route('/email-settings', methods=['GET'])
@jwt_required()
@log_api_call("Get email settings")
def get_email_settings():
    """Get user's email settings
    
    DEPRECATED: This endpoint is kept for backward compatibility only.
    New implementations should use EmailService (/api/email-services) instead.
    EmailSettings provides global defaults but EmailService offers per-database scheduling.
    """
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Fetching email settings for user {current_user_id}")
        
        email_settings = EmailSettings.query.filter_by(user_id=current_user_id).first()
        
        if not email_settings:
            # Create default email settings if none exist
            email_settings = EmailSettings(user_id=current_user_id)
            db.session.add(email_settings)
            db.session.commit()
            logger.info(f"Created default email settings for user {current_user_id}")
        
        return jsonify(email_settings.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Failed to get email settings for user {current_user_id}: {str(e)}")
        return jsonify({'error': 'Failed to get email settings', 'details': str(e)}), 500

@user_bp.route('/email-settings', methods=['PUT'])
@jwt_required()
@log_api_call("Update email settings")
def update_email_settings():
    """Update user's email settings
    
    DEPRECATED: This endpoint is kept for backward compatibility only.
    New implementations should use EmailService (/api/email-services) instead.
    EmailSettings provides global defaults but EmailService offers per-database scheduling.
    """
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Updating email settings for user {current_user_id}")
        
        data = request.get_json()
        
        email_settings = EmailSettings.query.filter_by(user_id=current_user_id).first()
        
        if not email_settings:
            # Create new email settings if none exist
            email_settings = EmailSettings(user_id=current_user_id)
            db.session.add(email_settings)
        
        # Update send_time (expect format "HH:MM")
        if 'send_time' in data:
            try:
                time_str = data['send_time']
                send_time = datetime.strptime(time_str, '%H:%M').time()
                email_settings.send_time = send_time
                logger.info(f"Updated send_time to {time_str} for user {current_user_id}")
            except ValueError as e:
                logger.warning(f"Invalid send_time format for user {current_user_id}: {data['send_time']}")
                return jsonify({'error': 'Invalid time format. Expected HH:MM'}), 400
        
        # Update timezone
        if 'timezone' in data:
            email_settings.timezone = data['timezone']
            logger.info(f"Updated timezone to {data['timezone']} for user {current_user_id}")
        
        # Update vocabulary_count
        if 'vocabulary_count' in data:
            try:
                vocab_count = int(data['vocabulary_count'])
                if vocab_count < 1 or vocab_count > 50:
                    return jsonify({'error': 'Vocabulary count must be between 1 and 50'}), 400
                email_settings.vocabulary_count = vocab_count
                logger.info(f"Updated vocabulary_count to {vocab_count} for user {current_user_id}")
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid vocabulary count'}), 400
        
        # Update is_active
        if 'is_active' in data:
            email_settings.is_active = bool(data['is_active'])
            logger.info(f"Updated is_active to {data['is_active']} for user {current_user_id}")
        
        db.session.commit()
        logger.info(f"Successfully updated email settings for user {current_user_id}")
        
        return jsonify({
            'message': 'Email settings updated successfully',
            'email_settings': email_settings.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update email settings for user {current_user_id}: {str(e)}")
        return jsonify({'error': 'Failed to update email settings', 'details': str(e)}), 500

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get user statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get user's databases count
        from .models import NotionDatabase
        databases_count = NotionDatabase.query.filter_by(user_id=current_user_id, is_active=True).count()
        
        # Get email logs count
        from .models import EmailLog
        emails_sent = EmailLog.query.filter_by(user_id=current_user_id, status='sent').count()
        
        # Get last email sent
        last_email = EmailLog.query.filter_by(user_id=current_user_id, status='sent').order_by(EmailLog.sent_at.desc()).first()
        
        stats = {
            'databases_count': databases_count,
            'emails_sent': emails_sent,
            'last_email_sent': last_email.sent_at.isoformat() + 'Z' if last_email else None
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500 