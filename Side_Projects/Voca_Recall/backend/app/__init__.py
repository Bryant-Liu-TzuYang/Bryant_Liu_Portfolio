from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from celery import Celery
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
celery = Celery()

# Import logging components
from .logging_config import setup_logging, get_logger
from .middleware import log_requests

def create_celery(app):
    """Create Celery instance"""
    # Update Celery config with Redis broker
    celery.conf.update(
        broker_url=app.config['REDIS_URL'],
        result_backend=app.config['REDIS_URL'],
        task_serializer='json',
        accept_content=['json'],  
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        # Explicitly set broker transport options
        broker_connection_retry_on_startup=True,
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    # Setup logging first
    log_level = 'DEBUG' if config_name == 'development' else 'INFO'
    setup_logging('notion-email-backend', log_level)
    
    # Get logger for this module
    logger = get_logger(__name__)
    logger.info(f"Starting Notion Email application in {config_name} mode")
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Setup request logging middleware
    log_requests(app)
    logger.info("Request logging middleware configured")
    
    # Initialize Celery
    create_celery(app)
    logger.info("Celery configured")
    
    # Register blueprints
    from .auth import auth_bp
    from .user import user_bp
    from .database import database_bp
    from .email import email_bp
    from .frontend_logs import frontend_logs_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(database_bp, url_prefix='/api/databases')
    app.register_blueprint(email_bp, url_prefix='/api/email')
    app.register_blueprint(frontend_logs_bp, url_prefix='/api/frontend')
    
    logger.info("All blueprints registered")
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    # Validate SMTP credentials on startup
    with app.app_context():
        from .smtp_validator import validate_smtp_from_config
        logger.info("Validating SMTP credentials...")
        success, error = validate_smtp_from_config(app.config)
        
        if not success:
            logger.error("=" * 70)
            logger.error("⚠️  SMTP CREDENTIALS VALIDATION FAILED!")
            logger.error(f"Error: {error}")
            logger.error("")
            logger.error("Email functionality will not work until this is resolved.")
            logger.error("Please check your .env file and update:")
            logger.error("  - SMTP_USER")
            logger.error("  - SMTP_PASSWORD")
            logger.error("  - SMTP_HOST")
            logger.error("  - SMTP_PORT")
            logger.error("")
            logger.error("For Gmail users:")
            logger.error("  1. Enable 2-factor authentication")
            logger.error("  2. Generate App Password: https://myaccount.google.com/apppasswords")
            logger.error("  3. Use App Password (not your regular password)")
            logger.error("=" * 70)
            
            # In production, you might want to prevent startup
            if config_name == 'production':
                raise RuntimeError(f"SMTP validation failed: {error}")
        else:
            logger.info("✅ SMTP credentials validated successfully")
    
    logger.info("Notion Email application initialized successfully")
    return app 