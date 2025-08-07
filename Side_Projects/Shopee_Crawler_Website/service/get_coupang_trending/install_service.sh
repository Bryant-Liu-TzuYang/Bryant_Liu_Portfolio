#!/bin/bash

# Coupang Crawler Service Installation Script
# This script installs the daily Coupang crawler as a macOS Launch Agent

echo "🚀 Installing Coupang Safari Crawler Daily Service"
echo "=================================================="

# Service details
SERVICE_NAME="com.user.coupang.crawler.login"
PLIST_FILE="$SERVICE_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PROJECT_DIR="/Users/bryant_lue/Documents/GitHub/Shopee_Crawler_Website"
SERVICE_DIR="$PROJECT_DIR/service/get_coupang_trending"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

echo "📁 Setting up directories..."

# Make sure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Make the runner script executable with full permissions
echo "🔧 Making scripts executable..."
chmod 777 "$SERVICE_DIR/run_coupang_crawler.sh"
chmod +x "$SERVICE_DIR"/*.sh

# Check for Full Disk Access permissions
echo "🔐 Checking macOS permissions..."
echo ""
echo "⚠️  IMPORTANT: macOS Security Requirements"
echo "===========================================" 
echo "For the service to work properly, you may need to:"
echo "1. Grant Terminal 'Full Disk Access' permission:"
echo "   System Preferences > Security & Privacy > Privacy > Full Disk Access"
echo "   Add Terminal.app and check the box"
echo ""
echo "2. If you're using iTerm2 or another terminal, add that instead"
echo ""
echo "3. You may also need to add the script to 'Developer Tools' if prompted"
echo ""

# Copy the plist file to LaunchAgents directory
echo "📋 Installing service configuration..."
cp "$SERVICE_DIR/$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# Load the service
echo "⚡ Loading the service..."
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo ""
echo "✅ Installation completed!"
echo ""
echo "📊 Service Information:"
echo "  Service Name: $SERVICE_NAME"
echo "  Trigger: Run once per day at first login"
echo "  Service Directory: $SERVICE_DIR"
echo "  Logs Directory: $PROJECT_DIR/logs/"
echo "  Configuration: $LAUNCH_AGENTS_DIR/$PLIST_FILE"
echo ""
echo "🔧 Management Commands:"
echo "  Check status: launchctl list | grep coupang"
echo "  Start now:    launchctl start $SERVICE_NAME"
echo "  Stop:         launchctl stop $SERVICE_NAME"
echo "  Unload:       launchctl unload $LAUNCH_AGENTS_DIR/$PLIST_FILE"
echo "  Reload:       launchctl unload $LAUNCH_AGENTS_DIR/$PLIST_FILE && launchctl load $LAUNCH_AGENTS_DIR/$PLIST_FILE"
echo ""
echo "📝 Important Notes:"
echo "  1. Make sure Safari has 'Allow Remote Automation' enabled"
echo "  2. The service will run once per day at first login"
echo "  3. Safari windows will be visible during execution"
echo "  4. If you log in multiple times per day, it will only run once"
echo "  5. Check logs in $PROJECT_DIR/logs/ for debugging"
echo ""
echo "🧪 To test the service immediately:"
echo "  launchctl start $SERVICE_NAME"
echo ""
echo "💡 Use the management script for easier control:"
echo "  $SERVICE_DIR/manage_service.sh"
echo ""
