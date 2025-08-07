#!/bin/bash

# Coupang Crawler Service Uninstallation Script
# This script removes the daily Coupang crawler Launch Agent

echo "🗑️  Uninstalling Coupang Safari Crawler Daily Service"
echo "====================================================="

# Service details
SERVICE_NAME="com.user.coupang.crawler.login"
PLIST_FILE="$SERVICE_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🛑 Stopping and unloading the service..."

# Stop the service if it's running
launchctl stop "$SERVICE_NAME" 2>/dev/null

# Unload the service
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null

# Remove the plist file
echo "🗂️  Removing service configuration..."
rm -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

# Check if removal was successful
if [ ! -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE" ]; then
    echo "✅ Service uninstalled successfully!"
else
    echo "❌ Failed to remove service configuration file"
    exit 1
fi

echo ""
echo "📊 Cleanup completed!"
echo ""
echo "📝 Note: Log files in the project directory were preserved"
echo "  You can manually delete them from: logs/"
echo ""
echo "🔍 To verify removal:"
echo "  launchctl list | grep coupang (should return nothing)"
echo ""
