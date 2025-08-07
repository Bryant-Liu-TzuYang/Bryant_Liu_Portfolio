#!/usr/bin/env python
import os
from dotenv import load_dotenv
from app import create_app, celery

# Load environment variables
load_dotenv()

# Create the Flask app to initialize Celery properly
app = create_app()

if __name__ == '__main__':
    # Make sure we're in the Flask app context
    with app.app_context():
        celery.start()
