import time
import logging
from datetime import datetime, timedelta
from app import create_app, db
from app.models import EmailService
from app.email import send_email_service_task
from application import app  # Reuse the app creation from application.py

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scheduler')

def run_scheduler():
    logger.info("Starting Email Service Poller (Database Driven)...")
    
    while True:
        try:
            with app.app_context():
                now = datetime.now()
                
                # 1. Initialize services that miss next_run_at (e.g. legacy data)
                # We do this first so they can be picked up in the same loop or next one
                services_to_init = EmailService.query.filter(
                    EmailService.is_active == True,
                    EmailService.next_run_at.is_(None)
                ).all()
                
                if services_to_init:
                    logger.info(f"Initializing schedule for {len(services_to_init)} services")
                    for service in services_to_init:
                        service.next_run_at = service.calculate_next_run(now)
                        service.status = 'PENDING'
                    db.session.commit()
                
                # 2. Find tasks due now or in the past
                # Query: Active, PENDING, next_run_at <= now
                due_services = EmailService.query.filter(
                    EmailService.is_active == True,
                    EmailService.status == 'PENDING',
                    EmailService.next_run_at <= now
                ).all()
                
                if due_services:
                    logger.info(f"Found {len(due_services)} due services")
                    
                    for service in due_services:
                        try:
                            logger.info(f"Scheduling service {service.id} ({service.service_name}) - Scheduled for: {service.next_run_at}")
                            
                            # Push to global Job Queue (Celery)
                            send_email_service_task.delay(service.id)
                            
                            # Advance schedule immediately
                            # Calculate next run relative to the current 'next_run_at' to maintain interval accuracy?
                            # Or relative to 'now'? 
                            # If we use next_run_at, we might schedule a bunch of catch-up emails if system was down.
                            # Usually for daily emails, we prefer skipping missed ones or sending just one.
                            # Let's calculate from 'now' to ensure we schedule for the FUTURE.
                            
                            service.next_run_at = service.calculate_next_run(now)
                            service.status = 'PENDING'
                            
                            # Note: last_sent_at is updated by the worker on success
                            
                            db.session.add(service) # Ensure session tracks it
                            
                        except Exception as e:
                            logger.error(f"Error processing service {service.id}: {e}")
                    
                    db.session.commit()
                
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            # Prevent busy loop on persistent db error
            time.sleep(5)
            
        # Poll every minute
        time.sleep(60)

if __name__ == '__main__':
    run_scheduler()
