#!/bin/bash

# Password Reset Setup Script
# This script helps set up the password reset functionality

echo "🔐 Setting up Password Reset functionality..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp env.example .env
    echo "✅ .env file created. Please update it with your actual values."
else
    echo "ℹ️  .env file already exists."
fi

# Check required environment variables
echo ""
echo "📋 Checking required environment variables..."

# Function to check if variable exists in .env
check_env_var() {
    local var_name=$1
    if grep -q "^${var_name}=" .env 2>/dev/null; then
        local value=$(grep "^${var_name}=" .env | cut -d '=' -f2-)
        if [ -n "$value" ] && [ "$value" != "your_email@gmail.com" ] && [ "$value" != "your_app_password" ]; then
            echo "✅ $var_name is configured"
        else
            echo "⚠️  $var_name needs to be configured in .env"
        fi
    else
        echo "❌ $var_name is missing from .env"
    fi
}

check_env_var "SMTP_HOST"
check_env_var "SMTP_PORT" 
check_env_var "SMTP_USER"
check_env_var "SMTP_PASSWORD"
check_env_var "SECRET_KEY"
check_env_var "JWT_SECRET_KEY"

echo ""
echo "📧 Email Configuration Setup:"
echo "For Gmail users:"
echo "1. Enable 2-factor authentication on your Google account"
echo "2. Generate an App Password: https://myaccount.google.com/apppasswords"
echo "3. Use the App Password (not your regular password) in SMTP_PASSWORD"
echo ""
echo "For other email providers:"
echo "- Update SMTP_HOST and SMTP_PORT accordingly"
echo "- Use appropriate authentication credentials"

echo ""
echo "🔧 Database Setup:"
echo "The password reset functionality requires a new database table."
echo "Make sure to run database migrations after setting up your environment."

echo ""
echo "🌐 Frontend Setup:"
echo "The following routes are now available:"
echo "- /forgot-password - Request password reset"
echo "- /reset-password?token=... - Reset password with token"

echo ""
echo "🧪 Testing the Setup:"
echo "1. Start your backend server"
echo "2. Start your frontend server"
echo "3. Visit /forgot-password to request a password reset"
echo "4. Check your email for the reset link"
echo "5. Use the link to reset your password"

echo ""
echo "📚 Security Notes:"
echo "- Reset tokens expire after 1 hour"
echo "- Tokens can only be used once"
echo "- All password reset attempts are logged"
echo "- Consider rate limiting in production"

echo ""
echo "🚀 Password reset functionality setup complete!"
echo "Please configure your environment variables and test the functionality."
