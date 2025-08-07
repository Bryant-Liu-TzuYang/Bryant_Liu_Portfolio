from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from celery import Celery
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
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
    migrate.init_app(app, db)
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
    
    logger.info("Notion Email application initialized successfully")
    return app 