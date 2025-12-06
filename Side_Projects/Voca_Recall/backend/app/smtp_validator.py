"""
SMTP Credential Validator
Validates SMTP credentials by attempting to connect and authenticate
"""
import smtplib
from .logging_config import get_logger

logger = get_logger(__name__)


def validate_smtp_credentials(smtp_host, smtp_port, smtp_user, smtp_password, use_tls=True):
    """
    Validate SMTP credentials by attempting to connect and authenticate.
    
    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port
        smtp_user: SMTP username/email
        smtp_password: SMTP password
        use_tls: Whether to use TLS (default: True)
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Check if credentials are provided
    if not smtp_user or not smtp_password:
        error_msg = "SMTP_USER and SMTP_PASSWORD must be configured"
        logger.error(f"SMTP validation failed: {error_msg}")
        return False, error_msg
    
    # Check if credentials are placeholder values
    placeholder_values = [
        'your_email@gmail.com',
        'your_app_password',
        'your-email@example.com',
        'change-me',
        'placeholder'
    ]
    
    if smtp_user.lower() in placeholder_values or smtp_password.lower() in placeholder_values:
        error_msg = f"SMTP credentials appear to be placeholder values. Please configure with actual credentials."
        logger.error(f"SMTP validation failed: {error_msg}")
        return False, error_msg
    
    # Validate email format for smtp_user
    if '@' not in smtp_user or '.' not in smtp_user.split('@')[1]:
        error_msg = f"SMTP_USER '{smtp_user}' does not appear to be a valid email address"
        logger.warning(f"SMTP validation warning: {error_msg}")
        # Don't return False here - some SMTP servers allow usernames without @ symbol
    
    # Attempt to connect and authenticate
    try:
        logger.info(f"Validating SMTP credentials for {smtp_user} on {smtp_host}:{smtp_port}")
        
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.set_debuglevel(0)  # Disable debug output
            
            if use_tls:
                logger.debug("Initiating TLS connection")
                server.starttls()
            
            logger.debug("Attempting SMTP authentication")
            server.login(smtp_user, smtp_password)
            
        logger.info(f"✅ SMTP credentials validated successfully for {smtp_user}")
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP authentication failed for {smtp_user}. Please check your username and password."
        logger.error(f"SMTP validation failed: {error_msg} - {str(e)}")
        return False, error_msg
        
    except smtplib.SMTPConnectError as e:
        error_msg = f"Failed to connect to SMTP server {smtp_host}:{smtp_port}"
        logger.error(f"SMTP validation failed: {error_msg} - {str(e)}")
        return False, error_msg
        
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(f"SMTP validation failed: {error_msg}")
        return False, error_msg
        
    except TimeoutError:
        error_msg = f"Connection to SMTP server {smtp_host}:{smtp_port} timed out"
        logger.error(f"SMTP validation failed: {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error during SMTP validation: {str(e)}"
        logger.error(f"SMTP validation failed: {error_msg}")
        return False, error_msg


def validate_smtp_from_config(app_config):
    """
    Validate SMTP credentials from Flask app config.
    
    Args:
        app_config: Flask application config object
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    smtp_host = app_config.get('SMTP_HOST')
    smtp_port = app_config.get('SMTP_PORT')
    smtp_user = app_config.get('SMTP_USER')
    smtp_password = app_config.get('SMTP_PASSWORD')
    use_tls = app_config.get('SMTP_USE_TLS', True)
    
    if not smtp_host or not smtp_port:
        error_msg = "SMTP_HOST and SMTP_PORT must be configured"
        logger.error(f"SMTP validation failed: {error_msg}")
        return False, error_msg
    
    return validate_smtp_credentials(
        smtp_host=smtp_host,
        smtp_port=int(smtp_port),
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        use_tls=use_tls
    )
