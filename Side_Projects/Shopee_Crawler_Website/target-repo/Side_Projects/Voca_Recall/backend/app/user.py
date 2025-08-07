from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, EmailSettings, db
from .logging_config import get_logger
from .middleware import log_api_call

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

@user_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Get user email settings"""
    try:
        current_user_id = int(get_jwt_identity())
        email_settings = EmailSettings.query.filter_by(user_id=current_user_id).first()
        
        if not email_settings:
            return jsonify({'error': 'Email settings not found'}), 404
        
        return jsonify({
            'email_settings': email_settings.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get settings', 'details': str(e)}), 500

@user_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update user email settings"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Get or create email settings
        email_settings = EmailSettings.query.filter_by(user_id=current_user_id).first()
        
        if not email_settings:
            email_settings = EmailSettings(user_id=current_user_id)
            db.session.add(email_settings)
        
        # Update settings
        if data.get('frequency') in ['daily', 'weekly', 'custom']:
            email_settings.frequency = data['frequency']
        
        if data.get('vocabulary_count') and isinstance(data['vocabulary_count'], int):
            if 1 <= data['vocabulary_count'] <= 50:  # Limit to reasonable range
                email_settings.vocabulary_count = data['vocabulary_count']
            else:
                return jsonify({'error': 'Vocabulary count must be between 1 and 50'}), 400
        
        if data.get('send_time'):
            try:
                from datetime import datetime
                send_time = datetime.strptime(data['send_time'], '%H:%M').time()
                email_settings.send_time = send_time
            except ValueError:
                return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
        
        if data.get('timezone'):
            email_settings.timezone = data['timezone']
        
        if data.get('is_active') is not None:
            email_settings.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully',
            'email_settings': email_settings.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update settings', 'details': str(e)}), 500

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
            'last_email_sent': last_email.sent_at.isoformat() if last_email else None
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500 