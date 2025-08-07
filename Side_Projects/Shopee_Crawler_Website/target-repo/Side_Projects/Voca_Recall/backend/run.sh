#!/bin/bash

# Quick run script for Notion Email Backend
# Usage: ./run.sh

BACKEND_DIR="/Users/bryant_lue/Coding/Notion Email/backend"

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set Flask environment
export FLASK_APP=app.py
export FLASK_ENV=development

echo "Starting Flask development server..."
echo ""
echo "🚀 Starting Notion Email Backend..."
echo "Server will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
python app.py
