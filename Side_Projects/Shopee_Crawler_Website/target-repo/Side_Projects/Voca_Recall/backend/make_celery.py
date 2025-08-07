#!/usr/bin/env python
"""
Celery worker entry point.
This file properly initializes the Flask app and Celery configuration.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app creation function and celery instance
from app import create_app, celery

# Create the Flask app to get the proper configuration
flask_app = create_app()

# Push the app context so Celery can access the configuration
flask_app.app_context().push()

if __name__ == '__main__':
    # Start the Celery worker
    celery.start()
