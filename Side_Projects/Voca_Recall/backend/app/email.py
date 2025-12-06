from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from notion_client import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from datetime import datetime
from .models import User, NotionDatabase, NotionToken, EmailSettings, EmailLog, db
from . import celery
from .logging_config import get_logger
from .middleware import log_api_call, log_function_call

email_bp = Blueprint('email', __name__)
logger = get_logger(__name__)

@log_function_call("Email sending")
def send_email(to_email, subject, html_content, text_content=None):
    """Send email using SMTP"""
    try:
        logger.info(f"Preparing to send email to {to_email} with subject: {subject}")
        
        # Check if SMTP is configured
        smtp_user = current_app.config.get('SMTP_USER')
        smtp_password = current_app.config.get('SMTP_PASSWORD')
        
        if not smtp_user or not smtp_password:
            logger.warning("SMTP credentials not configured, cannot send email")
            return False, "SMTP credentials not configured"
        
        # Ensure smtp_user is a string (decode if bytes)
        if isinstance(smtp_user, bytes):
            smtp_user = smtp_user.decode('utf-8')
        else:
            smtp_user = str(smtp_user)
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Ensure password is a string (decode if bytes)
        if isinstance(smtp_password, bytes):
            password = smtp_password.decode('utf-8')
        elif smtp_password:
            password = str(smtp_password)
        else:
            password = ""
        
        # Send email
        with smtplib.SMTP(current_app.config['SMTP_HOST'], current_app.config['SMTP_PORT']) as server:
            if current_app.config['SMTP_USE_TLS']:
                server.starttls()
            server.login(smtp_user, password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True, None
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False, str(e)

@log_function_call("Notion vocabulary fetch")
def get_vocabulary_from_notion(api_key, database_id, count=10):
    """Get random vocabulary items from Notion database"""
    try:
        logger.info(f"Fetching {count} vocabulary items from Notion database {database_id}")
        
        notion = Client(auth=api_key)
        
        # Get all items from database
        response = notion.databases.query(
            database_id=database_id,
            page_size=100  # Adjust based on your needs
        )
        
        items = response.get('results', [])
        
        if not items:
            logger.warning(f"No items found in Notion database {database_id}")
            return []
        
        logger.info(f"Found {len(items)} total items in database")
        
        # Randomly select items
        selected_items = random.sample(items, min(count, len(items)))
        
        vocabulary_items = []
        for item in selected_items:
            properties = item.get('properties', {})
            item_data = {}
            
            # Extract common vocabulary fields
            for prop_name, prop_value in properties.items():
                prop_type = prop_value.get('type')
                
                if prop_type == 'title':
                    title = prop_value.get('title', [])
                    item_data[prop_name] = title[0].get('plain_text', '') if title else ''
                elif prop_type == 'rich_text':
                    rich_text = prop_value.get('rich_text', [])
                    item_data[prop_name] = rich_text[0].get('plain_text', '') if rich_text else ''
                elif prop_type == 'select':
                    select = prop_value.get('select')
                    item_data[prop_name] = select.get('name', '') if select else ''
                elif prop_type == 'multi_select':
                    multi_select = prop_value.get('multi_select', [])
                    item_data[prop_name] = [option.get('name', '') for option in multi_select]
                elif prop_type == 'url':
                    item_data[prop_name] = prop_value.get('url', '')
                elif prop_type == 'email':
                    item_data[prop_name] = prop_value.get('email', '')
                elif prop_type == 'phone_number':
                    item_data[prop_name] = prop_value.get('phone_number', '')
                elif prop_type == 'number':
                    item_data[prop_name] = prop_value.get('number', '')
                elif prop_type == 'checkbox':
                    item_data[prop_name] = prop_value.get('checkbox', False)
                elif prop_type == 'date':
                    date_obj = prop_value.get('date')
                    if date_obj:
                        item_data[prop_name] = date_obj.get('start', '')
                    else:
                        item_data[prop_name] = ''
            
            vocabulary_items.append(item_data)
        
        logger.info(f"Successfully fetched {len(vocabulary_items)} vocabulary items")
        return vocabulary_items
        
    except Exception as e:
        logger.error(f"Error fetching vocabulary from Notion database {database_id}: {str(e)}")
        return []

@log_function_call("Email content creation")
def create_email_content(vocabulary_items, user_name):
    """Create HTML email content"""
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
            .vocabulary-item {{ background: white; margin: 15px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .word {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
            .definition {{ font-size: 16px; color: #555; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📚 Daily Vocabulary Recall</h1>
                <p>Hello {user_name}, here are your vocabulary words for today!</p>
            </div>
            <div class="content">
                <h2>Today's Vocabulary ({len(vocabulary_items)} words)</h2>
    """
    
    for i, item in enumerate(vocabulary_items, 1):
        # Try to find common vocabulary fields
        word = ''
        definition = ''
        
        # Look for common field names
        for key, value in item.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ['word', 'term', 'vocabulary', 'name']):
                word = str(value) if value else ''
            elif any(term in key_lower for term in ['definition', 'meaning', 'description', 'explanation']):
                definition = str(value) if value else ''
        
        # If no specific fields found, use first two fields
        if not word and not definition:
            fields = list(item.items())
            if len(fields) >= 1:
                word = str(fields[0][1]) if fields[0][1] else ''
            if len(fields) >= 2:
                definition = str(fields[1][1]) if fields[1][1] else ''
        
        html_content += f"""
                <div class="vocabulary-item">
                    <div class="word">{i}. {word}</div>
                    <div class="definition">{definition}</div>
                </div>
        """
    
    html_content += """
            </div>
            <div class="footer">
                <p>Keep learning and expanding your vocabulary! 🚀</p>
                <p>This email was sent by Notion Email Vocabulary Recall</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

@email_bp.route('/send-test', methods=['POST'])
@jwt_required()
@log_api_call("Send test email")
def send_test_email():
    """Send a test email to the user"""
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Processing test email request for user {current_user_id}")
        
        user = User.query.get(current_user_id)
        
        if not user:
            logger.warning(f"User {current_user_id} not found for test email")
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        database_pk = data.get('database_pk')
        vocabulary_count = data.get('vocabulary_count', 5)
        
        # Support both new (database_pk) and legacy (notion_api_key + database_id) methods
        if database_pk:
            # New method: use stored database and token
            database = NotionDatabase.query.filter_by(
                id=database_pk,
                user_id=current_user_id
            ).first()
            
            if not database:
                return jsonify({'error': 'Database not found'}), 404
            
            if not database.token_id:
                return jsonify({'error': 'Database has no associated token. Please update the database configuration.'}), 400
            
            token = NotionToken.query.filter_by(
                id=database.token_id,
                user_id=current_user_id,
                is_active=True
            ).first()
            
            if not token:
                return jsonify({'error': 'Token not found or inactive'}), 404
            
            api_key = token.token
            database_id = database.database_id
        else:
            # Legacy method: use provided API key and database ID
            api_key = data.get('notion_api_key')
            database_id = data.get('database_id')
            
            if not api_key or not database_id:
                return jsonify({'error': 'Either database_pk or (notion_api_key and database_id) are required'}), 400
        
        # Get vocabulary items
        vocabulary_items = get_vocabulary_from_notion(api_key, database_id, vocabulary_count)
        
        if not vocabulary_items:
            return jsonify({'error': 'No vocabulary items found in the database'}), 400
        
        # Create email content
        html_content = create_email_content(vocabulary_items, user.first_name)
        text_content = f"Hello {user.first_name}, here are your vocabulary words for today!\n\n"
        
        for i, item in enumerate(vocabulary_items, 1):
            word = ''
            definition = ''
            for key, value in item.items():
                key_lower = key.lower()
                if any(term in key_lower for term in ['word', 'term', 'vocabulary', 'name']):
                    word = str(value) if value else ''
                elif any(term in key_lower for term in ['definition', 'meaning', 'description']):
                    definition = str(value) if value else ''
            
            if not word and not definition:
                fields = list(item.items())
                if len(fields) >= 1:
                    word = str(fields[0][1]) if fields[0][1] else ''
                if len(fields) >= 2:
                    definition = str(fields[1][1]) if fields[1][1] else ''
            
            text_content += f"{i}. {word}: {definition}\n\n"
        
        # Send email
        success, error = send_email(
            user.email,
            "Test: Daily Vocabulary Recall",
            html_content,
            text_content
        )
        
        if not success:
            return jsonify({'error': 'Failed to send email', 'details': error}), 500
        
        # Log the email
        email_log = EmailLog(
            user_id=current_user_id,
            vocabulary_items=vocabulary_items,
            status='sent'
        )
        db.session.add(email_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Test email sent successfully',
            'vocabulary_count': len(vocabulary_items)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to send test email for user {current_user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to send test email', 'details': str(e)}), 500

@email_bp.route('/logs', methods=['GET'])
@jwt_required()
@log_api_call("Get email logs")
def get_email_logs():
    """Get user's email logs"""
    try:
        current_user_id = int(get_jwt_identity())
        logger.info(f"Fetching email logs for user {current_user_id}")
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        logs = EmailLog.query.filter_by(user_id=current_user_id)\
            .order_by(EmailLog.sent_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get email logs', 'details': str(e)}), 500

@celery.task
def send_daily_vocabulary_email(user_id):
    """Celery task to send daily vocabulary email"""
    try:
        with current_app.app_context():
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return False
            
            # Get user's email settings
            email_settings = EmailSettings.query.filter_by(user_id=user_id).first()
            if not email_settings or not email_settings.is_active:
                return False
            
            # Get user's active databases
            databases = NotionDatabase.query.filter_by(user_id=user_id, is_active=True).all()
            if not databases:
                return False
            
            # For now, use the first database (could be enhanced to use multiple)
            database = databases[0]
            
            # Get vocabulary items (this would need the user's Notion API key)
            # For now, we'll create a placeholder
            vocabulary_items = [
                {'word': 'Sample Word', 'definition': 'This is a sample definition'}
            ]
            
            # Create email content
            html_content = create_email_content(vocabulary_items, user.first_name)
            
            # Send email
            success, error = send_email(
                user.email,
                "Daily Vocabulary Recall",
                html_content
            )
            
            # Log the email
            email_log = EmailLog(
                user_id=user_id,
                vocabulary_items=vocabulary_items,
                status='sent' if success else 'failed',
                error_message=error if not success else None
            )
            db.session.add(email_log)
            db.session.commit()
            
            return success
            
    except Exception as e:
        return False 