from datetime import datetime, timedelta
import secrets
from . import db, bcrypt

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    databases = db.relationship('NotionDatabase', backref='user', lazy=True, cascade='all, delete-orphan')
    notion_tokens = db.relationship('NotionToken', backref='user', lazy=True, cascade='all, delete-orphan')
    email_settings = db.relationship('EmailSettings', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

    def generate_password_reset_token(self):
        """Generate a password reset token"""
        # Invalidate any existing tokens
        existing_tokens = PasswordResetToken.query.filter_by(user_id=self.id, is_used=False).all()
        for token in existing_tokens:
            token.is_used = True
        
        # Create new token
        reset_token = PasswordResetToken(
            user_id=self.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
        )
        db.session.add(reset_token)
        db.session.commit()
        
        return reset_token.token

    @staticmethod
    def verify_password_reset_token(token):
        """Verify password reset token and return user if valid"""
        reset_token = PasswordResetToken.query.filter_by(
            token=token, 
            is_used=False
        ).first()
        
        if not reset_token or reset_token.expires_at < datetime.utcnow():
            return None
        
        return reset_token.user

class PasswordResetToken(db.Model):
    """Password reset token model"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'token': self.token,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_used': self.is_used,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }

class NotionToken(db.Model):
    """Notion API token model for storing user tokens"""
    __tablename__ = 'notion_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)  # Encrypted token
    token_name = db.Column(db.String(100), nullable=True)  # Optional label for the token
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    databases = db.relationship('NotionDatabase', backref='notion_token', lazy=True)
    
    def to_dict(self, include_token=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'token_name': self.token_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'database_count': len(self.databases)
        }
        if include_token:
            result['token'] = self.token
        return result

class NotionDatabase(db.Model):
    """Notion database model"""
    __tablename__ = 'notion_databases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_id = db.Column(db.Integer, db.ForeignKey('notion_tokens.id'), nullable=True)  # Link to stored token
    database_id = db.Column(db.String(255), nullable=False)
    database_name = db.Column(db.String(255), nullable=False)
    database_url = db.Column(db.String(500), nullable=False)
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, custom - per database
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'database_id': self.database_id,
            'database_name': self.database_name,
            'database_url': self.database_url,
            'frequency': self.frequency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'token_id': self.token_id
        }

class EmailSettings(db.Model):
    """Email settings model"""
    __tablename__ = 'email_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vocabulary_count = db.Column(db.Integer, default=10)
    send_time = db.Column(db.Time, default=datetime.strptime('09:00', '%H:%M').time())
    timezone = db.Column(db.String(50), default='UTC')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'vocabulary_count': self.vocabulary_count,
            'send_time': self.send_time.strftime('%H:%M'),
            'timezone': self.timezone,
            'is_active': self.is_active
        }

class EmailLog(db.Model):
    """Email log model for tracking sent emails"""
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    vocabulary_items = db.Column(db.JSON)  # Store the vocabulary items sent
    status = db.Column(db.String(20), default='sent')  # sent, failed
    error_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sent_at': self.sent_at.isoformat(),
            'vocabulary_items': self.vocabulary_items,
            'status': self.status,
            'error_message': self.error_message
        } 