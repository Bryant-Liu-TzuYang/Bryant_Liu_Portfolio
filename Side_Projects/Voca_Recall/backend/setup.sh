#!/bin/bash

# Notion Email Backend Setup and Run Script
# Thecho "Setup complete! 🎉"
echo ""
echo "To start the development server, run:"
echo "  ./run.sh"
echo ""
echo "The server will be available at: http://localhost:5001"
echo "API endpoints will be at: http://localhost:5001/api/"ps set up the Python virtual environment and run the Flask application

set -e  # Exit on any error

BACKEND_DIR="/Users/bryant_lue/Coding/Notion Email/backend"
VENV_DIR="$BACKEND_DIR/venv"

echo "🚀 Notion Email Backend Setup"
echo "=============================="

# Change to backend directory
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp ../env.example .env
    echo "✅ Created .env file - please edit it with your configuration"
else
    echo "✅ .env file already exists"
fi

# Set up Flask environment
export FLASK_APP=app.py
export FLASK_ENV=development

# Initialize database if needed
echo "🗄️ Setting up database..."
if [ ! -f "notion_email_dev.db" ]; then
    echo "Creating database with migrations..."
    flask db upgrade
    echo "✅ Database created and migrated"
else
    echo "✅ Database already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  cd '$BACKEND_DIR'"
echo "  source venv/bin/activate"
echo "  export FLASK_APP=app.py"
echo "  python app.py"
echo ""
echo "Or simply run: ./run.sh"
echo ""
echo "The server will be available at: http://localhost:5001"
echo "API endpoints will be at: http://localhost:5001/api/"
echo ""

# Ask if user wants to start the server
read -p "🚀 Would you like to start the server now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting Flask development server..."
    python app.py
fi
