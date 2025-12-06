#!/usr/bin/env python3
"""
Standalone SMTP Credential Validator for setup.sh
Can be run independently to validate SMTP credentials before starting the app
"""
import os
import sys
import smtplib
from dotenv import load_dotenv


def validate_smtp_credentials(smtp_host, smtp_port, smtp_user, smtp_password, use_tls=True):
    """
    Validate SMTP credentials by attempting to connect and authenticate.
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Check if credentials are provided
    if not smtp_user or not smtp_password:
        return False, "SMTP_USER and SMTP_PASSWORD must be configured"
    
    # Check if credentials are placeholder values
    placeholder_values = [
        'your_email@gmail.com',
        'your_app_password',
        'your-email@example.com',
        'change-me',
        'placeholder'
    ]
    
    smtp_user_lower = smtp_user.lower() if smtp_user else ''
    smtp_password_lower = smtp_password.lower() if smtp_password else ''
    
    if smtp_user_lower in placeholder_values or smtp_password_lower in placeholder_values:
        return False, "SMTP credentials appear to be placeholder values. Please configure with actual credentials."
    
    # Validate email format for smtp_user
    if '@' not in smtp_user or '.' not in smtp_user.split('@')[1]:
        print(f"⚠️  Warning: SMTP_USER '{smtp_user}' does not appear to be a valid email address", file=sys.stderr)
    
    # Attempt to connect and authenticate
    try:
        print(f"🔐 Validating SMTP credentials for {smtp_user} on {smtp_host}:{smtp_port}...", file=sys.stderr)
        
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.set_debuglevel(0)
            
            if use_tls:
                server.starttls()
            
            server.login(smtp_user, smtp_password)
        
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        return False, f"Authentication failed. Please check your username and password. Error: {str(e)}"
        
    except smtplib.SMTPConnectError as e:
        return False, f"Failed to connect to SMTP server {smtp_host}:{smtp_port}. Error: {str(e)}"
        
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
        
    except TimeoutError:
        return False, f"Connection to SMTP server {smtp_host}:{smtp_port} timed out"
        
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def main():
    """Main function to validate SMTP from environment variables"""
    # Load .env file
    load_dotenv()
    
    # Get SMTP configuration from environment
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    use_tls = os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'
    
    print("=" * 70, file=sys.stderr)
    print("🔍 SMTP Credentials Validation", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"SMTP Host: {smtp_host}", file=sys.stderr)
    print(f"SMTP Port: {smtp_port}", file=sys.stderr)
    print(f"SMTP User: {smtp_user}", file=sys.stderr)
    print(f"SMTP TLS:  {use_tls}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Validate credentials
    success, error = validate_smtp_credentials(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        use_tls=use_tls
    )
    
    if success:
        print("=" * 70, file=sys.stderr)
        print("✅ SMTP credentials validated successfully!", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("", file=sys.stderr)
        return 0
    else:
        print("=" * 70, file=sys.stderr)
        print("❌ SMTP CREDENTIALS VALIDATION FAILED", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"Error: {error}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please check your .env file and update:", file=sys.stderr)
        print("  - SMTP_USER", file=sys.stderr)
        print("  - SMTP_PASSWORD", file=sys.stderr)
        print("  - SMTP_HOST", file=sys.stderr)
        print("  - SMTP_PORT", file=sys.stderr)
        print("", file=sys.stderr)
        print("For Gmail users:", file=sys.stderr)
        print("  1. Enable 2-factor authentication on your Google account", file=sys.stderr)
        print("  2. Generate App Password: https://myaccount.google.com/apppasswords", file=sys.stderr)
        print("  3. Use the App Password (not your regular password)", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
