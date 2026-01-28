import os
from dotenv import load_dotenv
from app import create_app, celery
from app.logging_config import get_logger, setup_logging

# Load environment variables from backend directory
load_dotenv()

app = create_app()
logger = get_logger(__name__)

if __name__ == '__main__':
    setup_logging()  # Now uses default 'notion-email-backend' and environment LOG_LEVEL
    logger = get_logger(__name__)
    logger.info("Starting Notion Email Backend server...")
    app.run(host='0.0.0.0', port=5000, debug=True)  