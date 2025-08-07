from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from email_validator import validate_email, EmailNotValidError
from .models import User, PasswordResetToken, db
from . import bcrypt
from .logging_config import get_logger
from .middleware import log_api_call, log_database_operations
from .email import send_email

auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

@auth_bp.route('/register', methods=['POST'])
@log_api_call("User Registration")
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        logger.info(f"Registration attempt for email: {data.get('email', 'unknown')}")
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Registration failed: missing field '{field}'")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            logger.warning(f"Registration failed: invalid email format '{data.get('email')}'")
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"Registration failed: user already exists '{data.get('email')}'")
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Validate password strength
        if len(data['password']) < 8:
            logger.warning(f"Registration failed: password too short for '{data.get('email')}'")
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
        
        # Create access and refresh tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
@log_api_call("User Login")
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        logger.info(f"Login attempt for email: {data.get('email', 'unknown')}")
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            logger.warning("Login failed: missing email or password")
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            logger.warning(f"Login failed: invalid credentials for '{data.get('email')}'")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            logger.warning(f"Login failed: account deactivated for '{data.get('email')}'")
            return jsonify({'error': 'Account is deactivated'}), 401
        
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
        
        # Create access and refresh tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@log_api_call("Token Refresh")
def refresh():
    """Refresh access token endpoint"""
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Token refresh for user ID: {current_user_id}")
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@log_api_call("User Logout")
def logout():
    """User logout endpoint"""
    current_user_id = int(get_jwt_identity())
    logger.info(f"User logged out: ID {current_user_id}")
    # In a real application, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@log_api_call("Get Current User")
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            logger.warning(f"User not found for ID: {current_user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user information', 'details': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
@log_api_call("Forgot Password Request")
def forgot_password():
    """Request password reset endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            logger.warning("Forgot password failed: no email provided")
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            logger.warning(f"Forgot password failed: invalid email format '{email}'")
            return jsonify({'error': 'Invalid email format'}), 400
        
        logger.info(f"Password reset requested for email: {email}")
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Password reset failed: user not found '{email}'")
            # Don't reveal if user exists or not for security
            return jsonify({
                'message': 'If an account with this email exists, you will receive a password reset link.'
            }), 200
        
        if not user.is_active:
            logger.warning(f"Password reset failed: account deactivated '{email}'")
            return jsonify({
                'message': 'If an account with this email exists, you will receive a password reset link.'
            }), 200
        
        # Generate password reset token
        reset_token = user.generate_password_reset_token()
        
        # Create password reset email
        reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request - Notion Email Vocabulary"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello {user.first_name},</p>
                    <p>We received a request to reset your password for your Notion Email Vocabulary account.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong> This link is valid for 1 hour only and can only be used once.
                    </div>
                    
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Your Password</a>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 5px;">{reset_url}</p>
                    
                    <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    
                    <div class="footer">
                        <p>Best regards,<br>Notion Email Vocabulary Team</p>
                        <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request - Notion Email Vocabulary
        
        Hello {user.first_name},
        
        We received a request to reset your password for your Notion Email Vocabulary account.
        
        Click this link to reset your password (valid for 1 hour):
        {reset_url}
        
        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
        
        Best regards,
        Notion Email Vocabulary Team
        """
        
        # Send password reset email
        success, error = send_email(user.email, subject, html_content, text_content)
        
        if not success:
            logger.error(f"Failed to send password reset email to {email}: {error}")
            if "SMTP credentials not configured" in str(error):
                return jsonify({
                    'error': 'Email service is not configured. Please contact the administrator.'
                }), 503
            return jsonify({'error': 'Failed to send password reset email'}), 500
        
        logger.info(f"Password reset email sent successfully to {email}")
        
        return jsonify({
            'message': 'If an account with this email exists, you will receive a password reset link.'
        }), 200
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Password reset request failed', 'details': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
@log_api_call("Password Reset")
def reset_password():
    """Reset password with token endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            logger.warning("Password reset failed: missing token or password")
            return jsonify({'error': 'Token and new password are required'}), 400
        
        # Validate password strength
        if len(new_password) < 8:
            logger.warning("Password reset failed: password too short")
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        logger.info(f"Password reset attempt with token: {token[:8]}...")
        
        # Verify token and get user
        user = User.verify_password_reset_token(token)
        
        if not user:
            logger.warning(f"Password reset failed: invalid or expired token {token[:8]}...")
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        if not user.is_active:
            logger.warning(f"Password reset failed: account deactivated for user {user.id}")
            return jsonify({'error': 'Account is deactivated'}), 400
        
        # Update password
        user.set_password(new_password)
        
        # Mark token as used
        reset_token = PasswordResetToken.query.filter_by(token=token, is_used=False).first()
        if reset_token:
            reset_token.mark_as_used()
        
        db.session.commit()
        
        logger.info(f"Password reset successful for user: {user.email} (ID: {user.id})")
        
        # Send confirmation email
        subject = "Password Reset Successful - Notion Email Vocabulary"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; color: #155724; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Password Reset Successful</h1>
                </div>
                <div class="content">
                    <p>Hello {user.first_name},</p>
                    
                    <div class="success">
                        <strong>✅ Success!</strong> Your password has been reset successfully.
                    </div>
                    
                    <p>Your password for your Notion Email Vocabulary account has been changed. You can now log in with your new password.</p>
                    
                    <p>If you didn't make this change, please contact our support team immediately.</p>
                    
                    <div class="footer">
                        <p>Best regards,<br>Notion Email Vocabulary Team</p>
                        <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Successful - Notion Email Vocabulary
        
        Hello {user.first_name},
        
        Your password for your Notion Email Vocabulary account has been changed successfully. You can now log in with your new password.
        
        If you didn't make this change, please contact our support team immediately.
        
        Best regards,
        Notion Email Vocabulary Team
        """
        
        # Send confirmation email (don't fail if this fails)
        send_email(user.email, subject, html_content, text_content)
        
        return jsonify({
            'message': 'Password reset successful. You can now log in with your new password.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Password reset failed', 'details': str(e)}), 500

@auth_bp.route('/validate-reset-token', methods=['POST'])
@log_api_call("Validate Reset Token")
def validate_reset_token():
    """Validate password reset token endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            logger.warning("Token validation failed: no token provided")
            return jsonify({'error': 'Token is required'}), 400
        
        logger.info(f"Validating reset token: {token[:8]}...")
        
        # Verify token
        user = User.verify_password_reset_token(token)
        
        if not user:
            logger.warning(f"Token validation failed: invalid or expired token {token[:8]}...")
            return jsonify({'valid': False, 'error': 'Invalid or expired reset token'}), 400
        
        logger.info(f"Token validation successful for user: {user.email}")
        
        return jsonify({
            'valid': True,
            'user_email': user.email
        }), 200
        
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Token validation failed', 'details': str(e)}), 500

@auth_bp.route('/dev/reset-tokens', methods=['GET'])
@log_api_call("List Reset Tokens (Development)")
def list_reset_tokens():
    """Development endpoint to list all reset tokens"""
    # Only enable in development mode
    if not current_app.config.get('DEBUG'):
        return jsonify({'error': 'This endpoint is only available in development mode'}), 403
    
    try:
        tokens = PasswordResetToken.query.order_by(PasswordResetToken.created_at.desc()).limit(10).all()
        
        return jsonify({
            'tokens': [token.to_dict() for token in tokens]
        }), 200
    
    except Exception as e:
        logger.error(f"List reset tokens error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to list reset tokens', 'details': str(e)}), 500 