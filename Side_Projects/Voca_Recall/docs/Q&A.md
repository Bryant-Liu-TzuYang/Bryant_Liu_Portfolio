# Q&A - Voca Recaller

## Q: How to test SMTP_USER and SMTP_PASSWORD validity?

**A:** The application provides multiple ways to validate your SMTP credentials:

### 1. Automatic Validation During Setup
When running the setup script, SMTP credentials are automatically validated:
```bash
./setup.sh dev   # For development
./setup.sh prod  # For production
```
- **Development**: Warns if credentials are invalid but allows you to continue
- **Production**: Fails setup and requires valid credentials before proceeding

### 2. Manual Validation Script
Run the standalone validation script anytime:
```bash
python3 backend/validate_smtp.py
```

This will:
- Load credentials from your `.env` file
- Attempt to connect to the SMTP server
- Authenticate with your credentials
- Display clear success/failure messages

### 3. Automatic Validation on App Startup
The Flask application validates SMTP credentials every time it starts:
- **Development mode**: Logs detailed warnings but allows startup
- **Production mode**: Prevents startup if credentials are invalid

### What Gets Validated
The validation performs these checks:
1. ✅ Credentials exist (not empty)
2. ✅ Not placeholder values (e.g., "your_email@gmail.com")
3. ✅ Email format is valid
4. ✅ Can connect to SMTP server
5. ✅ TLS/SSL connection works
6. ✅ Authentication succeeds

### Common Issues and Solutions

**Authentication Failed**
- **Gmail users**: Use App Password, not your regular password
  1. Enable 2-factor authentication
  2. Generate App Password: https://myaccount.google.com/apppasswords
  3. Use the 16-character App Password in `SMTP_PASSWORD`

**Connection Failed**
- Check `SMTP_HOST` and `SMTP_PORT` are correct
- Verify firewall isn't blocking the connection
- Ensure stable internet connection

**Timeout Error**
- Check network connectivity
- Verify SMTP server is reachable
- Try again after a few moments

### For More Details
See comprehensive documentation: `docs/Updates/20251206_smtp_validation.md`
