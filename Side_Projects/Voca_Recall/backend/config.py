import os
from datetime import timedelta

# Get the base directory path
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Notion API
    NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
    
    # Email configuration
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_USE_TLS = True
    
    # Redis for Celery
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Frontend URL for email links
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "instance", "notion_email_dev.db")}'
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    LOG_LEVEL = 'WARNING'
    LOG_TO_STDOUT = True
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "test.db")}'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'DEBUG'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 