#!/bin/bash

# Coupang Crawler Daily Runner Script (Login-triggered)
# This script sets up the environment and runs the Safari-based Coupang crawler
# It only runs once per day, triggered by login

# Set the working directory to the project root
PROJECT_ROOT="/Users/bryant_lue/Documents/GitHub/Shopee_Crawler_Website"
cd "$PROJECT_ROOT"

# Log file for the service (use absolute paths)
LOG_FILE="$PROJECT_ROOT/logs/coupang_crawler_service.log"
ERROR_LOG="$PROJECT_ROOT/logs/coupang_crawler_error.log"
LAST_RUN_FILE="$PROJECT_ROOT/logs/.last_crawler_run"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to log errors with timestamp
log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$ERROR_LOG"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
}

# Check if crawler already ran today
TODAY=$(date '+%Y-%m-%d')
if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN=$(cat "$LAST_RUN_FILE" 2>/dev/null || echo "")
    if [ "$LAST_RUN" = "$TODAY" ]; then
        log_message "Crawler already ran today ($TODAY). Skipping execution."
        exit 0
    fi
fi

log_message "Starting Coupang Safari crawler service (login-triggered)"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    log_message "Activating virtual environment"
    source .venv/bin/activate
    
    # Verify Python and required packages
    if ! python -c "import selenium, pandas, pytz" 2>/dev/null; then
        log_error "Required Python packages not found. Installing requirements..."
        pip install -r requirements.txt
    fi
else
    log_error "Virtual environment not found at .venv"
    log_message "Attempting to use system Python"
fi

# Set Python path to include the project directory
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Check if Safari allows remote automation
log_message "Checking Safari remote automation settings"

# Change to the service directory and run the Safari crawler
log_message "Executing Safari Coupang crawler"
cd "$PROJECT_ROOT/service/get_coupang_trending"
python get_trending_coupang_safari.py 2>> "$ERROR_LOG"

# Check the exit status
if [ $? -eq 0 ]; then
    log_message "Coupang Safari crawler completed successfully"
    # Record successful run
    echo "$TODAY" > "$LAST_RUN_FILE"
else
    log_error "Coupang Safari crawler failed with exit code $?"
fi

# Log completion
log_message "Coupang Safari crawler service finished"

# Clean up old log files (keep last 30 days)
cd "$PROJECT_ROOT"
find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null

log_message "Service execution completed"

# Commit and push changes to the Git repository
log_message "pushing changes to Git repository"
git add . 2>> "$ERROR_LOG"
git commit -m "Daily update: Coupang crawler run on $TODAY" 2>> "$ERROR_LOG"
if [ $? -ne 0 ]; then
    log_error "Git commit failed. Check if there are changes to commit."
    exit 1
fi
log_message "Pushing changes to remote repository"

git push origin main 2>> "$ERROR_LOG"
