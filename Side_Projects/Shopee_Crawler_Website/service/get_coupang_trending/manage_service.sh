#!/bin/bash

# Coupang Crawler Service Management Script
# This script provides easy management of the daily Coupang crawler service

SERVICE_NAME="com.user.coupang.crawler.login"
PLIST_FILE="$SERVICE_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PROJECT_DIR="/Users/bryant_lue/Documents/GitHub/Shopee_Crawler_Website"
SERVICE_DIR="$PROJECT_DIR/service/get_coupang_trending"

show_usage() {
    echo "🛠️  Coupang Safari Crawler Service Manager"
    echo "=========================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status       - Show service status"
    echo "  start        - Start the service immediately"
    echo "  stop         - Stop the service"
    echo "  restart      - Restart the service"
    echo "  logs         - Show recent logs"
    echo "  install      - Install the service"
    echo "  uninstall    - Uninstall the service"
    echo "  test         - Run the crawler manually for testing"
    echo "  reset        - Reset daily run tracker (allows re-running today)"
    echo "  permissions  - Check and fix file permissions"
    echo "  debug        - Show detailed debugging information"
    echo "  create-app   - Create Automator app for Login Items (alternative)"
    echo ""
}

show_status() {
    echo "📊 Service Status"
    echo "=================="
    
    if launchctl list | grep -q "$SERVICE_NAME"; then
        echo "✅ Service is loaded"
        echo ""
        echo "Service details:"
        launchctl list | grep "$SERVICE_NAME"
    else
        echo "❌ Service is not loaded"
    fi
    
    echo ""
    echo "📁 Configuration file:"
    if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE" ]; then
        echo "✅ $LAUNCH_AGENTS_DIR/$PLIST_FILE exists"
    else
        echo "❌ $LAUNCH_AGENTS_DIR/$PLIST_FILE not found"
    fi
    
    echo ""
    echo "📝 Recent log files:"
    ls -la "$PROJECT_DIR/logs/" 2>/dev/null | tail -5
}

start_service() {
    echo "🚀 Starting service..."
    launchctl start "$SERVICE_NAME"
    if [ $? -eq 0 ]; then
        echo "✅ Service started successfully"
    else
        echo "❌ Failed to start service"
    fi
}

stop_service() {
    echo "🛑 Stopping service..."
    launchctl stop "$SERVICE_NAME"
    if [ $? -eq 0 ]; then
        echo "✅ Service stopped successfully"
    else
        echo "❌ Failed to stop service"
    fi
}

restart_service() {
    echo "🔄 Restarting service..."
    stop_service
    sleep 2
    start_service
}

show_logs() {
    echo "📝 Recent Service Logs"
    echo "======================"
    
    if [ -f "$PROJECT_DIR/logs/coupang_crawler_service.log" ]; then
        echo "--- Service Log (last 20 lines) ---"
        tail -20 "$PROJECT_DIR/logs/coupang_crawler_service.log"
    fi
    
    echo ""
    
    if [ -f "$PROJECT_DIR/logs/coupang_crawler_error.log" ]; then
        echo "--- Error Log (last 10 lines) ---"
        tail -10 "$PROJECT_DIR/logs/coupang_crawler_error.log"
    fi
    
    echo ""
    
    if [ -f "$PROJECT_DIR/logs/launchd_stdout.log" ]; then
        echo "--- LaunchD Stdout (last 10 lines) ---"
        tail -10 "$PROJECT_DIR/logs/launchd_stdout.log"
    fi
    
    if [ -f "$PROJECT_DIR/logs/launchd_stderr.log" ]; then
        echo "--- LaunchD Stderr (last 10 lines) ---"
        tail -10 "$PROJECT_DIR/logs/launchd_stderr.log"
    fi
}

install_service() {
    echo "🔧 Installing service..."
    cd "$SERVICE_DIR"
    ./install_service.sh
}

uninstall_service() {
    echo "🗑️  Uninstalling service..."
    cd "$SERVICE_DIR"
    ./uninstall_service.sh
}

test_crawler() {
    echo "🧪 Running crawler manually for testing..."
    cd "$SERVICE_DIR"
    ./run_coupang_crawler.sh
}

reset_daily_tracker() {
    echo "🔄 Resetting daily run tracker..."
    LAST_RUN_FILE="$PROJECT_DIR/logs/.last_crawler_run"
    if [ -f "$LAST_RUN_FILE" ]; then
        rm "$LAST_RUN_FILE"
        echo "✅ Daily run tracker reset. Service will run on next trigger."
    else
        echo "ℹ️  No daily run tracker found. Service will run normally."
    fi
}

check_permissions() {
    echo "🔐 Checking File Permissions and macOS Security"
    echo "==============================================="
    
    echo ""
    echo "📁 Service Directory Permissions:"
    ls -la "$SERVICE_DIR/"
    
    echo ""
    echo "🔧 Script Permissions:"
    ls -la "$SERVICE_DIR/run_coupang_crawler.sh"
    
    echo ""
    echo "📄 Plist File Permissions:"
    ls -la "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null || echo "Plist file not found"
    
    echo ""
    echo "🔍 Security & Privacy Requirements:"
    echo "1. Terminal App Permissions (REQUIRED FOR macOS 15+):"
    echo "   - Open System Settings (or System Preferences)"
    echo "   - Go to Privacy & Security > Privacy"
    echo "   - Click 'Full Disk Access' and add Terminal.app (or your terminal app)"
    echo "   - Make sure the checkbox is enabled"
    echo ""
    echo "2. Alternative: Grant permission to bash directly:"
    echo "   - In Full Disk Access, also add: /bin/bash"
    echo ""
    echo "3. If still failing, try:"
    echo "   - Add the entire project folder to 'Files and Folders' permissions"
    echo "   - Restart Terminal and try again"
    echo ""
    echo "4. Alternative Solution - Manual Setup:"
    echo "   - Instead of Launch Agent, add to Login Items manually:"
    echo "   - System Settings > General > Login Items"
    echo "   - Add the script: $SERVICE_DIR/run_coupang_crawler.sh"
    echo ""
    echo "5. Or create an Automator App:"
    echo "   - Open Automator > New Document > Application"
    echo "   - Add 'Run Shell Script' action"
    echo "   - Paste: $SERVICE_DIR/run_coupang_crawler.sh"
    echo "   - Save as 'CoupangCrawler.app'"
    echo "   - Add the app to Login Items"
    
    echo ""
    echo "🛠️  Attempting to fix common issues..."
    
    # Make sure all scripts are executable with full permissions
    chmod 777 "$SERVICE_DIR/run_coupang_crawler.sh"
    chmod +x "$SERVICE_DIR"/*.sh
    echo "✅ Set full execute permissions (777) on runner script"
    echo "✅ Made all scripts executable"
    
    # Remove quarantine attribute if present
    xattr -d com.apple.quarantine "$SERVICE_DIR/run_coupang_crawler.sh" 2>/dev/null && echo "✅ Removed quarantine attribute" || echo "ℹ️  No quarantine attribute found"
    
    # Try to fix directory permissions
    chmod 755 "$SERVICE_DIR"
    echo "✅ Set directory permissions"
    
    # Check if running in restricted environment
    echo ""
    echo "🔍 Current execution environment:"
    echo "USER: $USER"
    echo "HOME: $HOME"
    echo "PWD: $PWD"
    echo "PATH: $PATH"
}

show_debug_info() {
    echo "🐛 Debug Information"
    echo "==================="
    
    echo ""
    echo "📊 Service Status:"
    launchctl list | grep coupang || echo "No coupang services found"
    
    echo ""
    echo "📄 Plist Content:"
    if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE" ]; then
        cat "$LAUNCH_AGENTS_DIR/$PLIST_FILE"
    else
        echo "Plist file not found at $LAUNCH_AGENTS_DIR/$PLIST_FILE"
    fi
    
    echo ""
    echo "📝 Recent LaunchD Errors:"
    if [ -f "$PROJECT_DIR/logs/launchd_stderr.log" ]; then
        echo "--- Last 10 lines of launchd_stderr.log ---"
        tail -10 "$PROJECT_DIR/logs/launchd_stderr.log"
    else
        echo "No launchd stderr log found"
    fi
    
    echo ""
    echo "🔍 System Information:"
    echo "macOS Version: $(sw_vers -productVersion)"
    echo "Architecture: $(uname -m)"
    echo "Shell: $SHELL"
}

create_automator_app() {
    echo "🔧 Creating Automator App Alternative"
    echo "====================================="
    
    APP_PATH="$HOME/Desktop/CoupangCrawler.app"
    SCRIPT_CONTENT="$SERVICE_DIR/run_coupang_crawler.sh"
    
    echo ""
    echo "Creating Automator application..."
    echo "This will create an app you can add to Login Items manually."
    echo ""
    
    # Create the Automator workflow using AppleScript
    osascript << EOF
tell application "Automator"
    set newWorkflow to make new workflow document
    tell newWorkflow
        set the current application to "Automator"
        set theAction to make new action at end of actions with properties {name:"Run Shell Script"}
        tell theAction
            set value of setting named "inputMethod" to 0
            set value of setting named "source" to "$SCRIPT_CONTENT"
        end tell
        save newWorkflow as "application" in "$APP_PATH"
    end tell
    quit
end tell
EOF
    
    if [ -f "$APP_PATH" ]; then
        echo "✅ Created: $APP_PATH"
        echo ""
        echo "📋 Next Steps:"
        echo "1. Go to System Settings > General > Login Items"
        echo "2. Click '+' and add: $APP_PATH"
        echo "3. The crawler will run automatically at login"
        echo ""
        echo "🗑️  To remove: Delete the app and remove from Login Items"
    else
        echo "❌ Failed to create Automator app"
        echo "Please create manually:"
        echo "1. Open Automator"
        echo "2. New Document > Application"
        echo "3. Add 'Run Shell Script' action"
        echo "4. Set shell to /bin/bash"
        echo "5. Paste: $SCRIPT_CONTENT"
        echo "6. Save as CoupangCrawler.app"
        echo "7. Add to Login Items"
    fi
}

# Main script logic
case "$1" in
    status)
        show_status
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    logs)
        show_logs
        ;;
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    test)
        test_crawler
        ;;
    reset)
        reset_daily_tracker
        ;;
    permissions)
        check_permissions
        ;;
    debug)
        show_debug_info
        ;;
    create-app)
        create_automator_app
        ;;
    *)
        show_usage
        ;;
esac
