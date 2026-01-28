#!/usr/bin/env python
import os
from dotenv import load_dotenv
from app import create_app, celery
from application import app  # Reuse the app creation from application.py

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Make sure we're in the Flask app context
    with app.app_context():
        celery.start()
