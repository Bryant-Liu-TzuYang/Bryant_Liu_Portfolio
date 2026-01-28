from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

def migrate():
    with app.app_context():
        logger.info("Starting migration...")
        with db.engine.connect() as conn:
            # Check if columns exist by trying to add them. 
            # This is a bit brute force but works for simple migrations without Alembic.
            
            # 1. Add next_run_at
            try:
                logger.info("Attempting to add next_run_at column...")
                conn.execute(text("ALTER TABLE email_services ADD COLUMN next_run_at DATETIME"))
                logger.info("Added column next_run_at")
            except Exception as e:
                logger.warning(f"Could not add next_run_at (might exist): {e}")

            # 2. Add status
            try:
                logger.info("Attempting to add status column...")
                conn.execute(text("ALTER TABLE email_services ADD COLUMN status VARCHAR(20) DEFAULT 'PENDING'"))
                logger.info("Added column status")
            except Exception as e:
                logger.warning(f"Could not add status (might exist): {e}")
                
            conn.commit()
            logger.info("Migration completed.")

if __name__ == "__main__":
    migrate()
