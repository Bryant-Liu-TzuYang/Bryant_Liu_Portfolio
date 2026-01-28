#!/usr/bin/env python
"""
Celery Beat scheduler entry point.
Dynamically loads email service schedules from the database.
"""
import os
import sys
from datetime import datetime, time
from celery.schedules import crontab
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, celery
from app.models import EmailService
from application import app  # Reuse the app creation from application.py


def load_email_service_schedule():
    """
    Load email service schedules from database and update Celery Beat config.
    This function runs periodically to pick up new/updated services.
    """
    with app.app_context():
        try:
            # Get all active email services
            services = EmailService.query.filter_by(is_active=True).all()
            beat_schedule = {}
            
            for service in services:
                try:
                    # Convert service time from local timezone to UTC
                    # Service stores time in local timezone (e.g., Asia/Shanghai)
                    # Celery Beat schedules in UTC, so we need to convert
                    local_tz = pytz.timezone(service.timezone)
                    utc_tz = pytz.UTC
                    
                    # Create a datetime object for today with the service time
                    today = datetime.now(local_tz).date()
                    local_datetime = local_tz.localize(datetime.combine(today, service.send_time))
                    
                    # Convert to UTC
                    utc_datetime = local_datetime.astimezone(utc_tz)
                    hour = utc_datetime.hour
                    minute = utc_datetime.minute
                    
                    # Create cron schedule based on frequency
                    if service.frequency == 'daily':
                        schedule = crontab(hour=hour, minute=minute)
                    elif service.frequency == 'weekly':
                        # Default to Monday (day_of_week=1)
                        schedule = crontab(hour=hour, minute=minute, day_of_week=1)
                    elif service.frequency == 'monthly':
                        # Default to 1st of month
                        schedule = crontab(hour=hour, minute=minute, day_of_month=1)
                    else:
                        app.logger.warning(f"Unknown frequency '{service.frequency}' for service {service.id}")
                        continue
                    
                    # Add to beat schedule
                    task_name = f'email-service-{service.id}-{service.service_name}'
                    beat_schedule[task_name] = {
                        'task': 'app.email.send_email_service_task',
                        'schedule': schedule,
                        'args': (service.id,),
                        'options': {
                            'expires': 3600,  # Task expires after 1 hour if not picked up
                        }
                    }
                    
                    app.logger.info(
                        f"Scheduled: {service.service_name} (ID: {service.id}) "
                        f"at {service.send_time} {service.timezone} "
                        f"(UTC: {hour:02d}:{minute:02d}) ({service.frequency})"
                    )
                    
                except Exception as e:
                    app.logger.error(f"Error scheduling service {service.id}: {e}")
                    continue
            
            # Update Celery Beat configuration
            celery.conf.beat_schedule = beat_schedule
            
            taipei_tz = pytz.timezone('Asia/Taipei')
            app.logger.info(f"Loaded {len(beat_schedule)} email service schedules at {datetime.now(taipei_tz)}")
            
        except Exception as e:
            app.logger.error(f"Error loading email service schedules: {e}", exc_info=True)


# Initial schedule load
with app.app_context():
    app.logger.info("=== Starting Celery Beat Scheduler ===")
    load_email_service_schedule()

# Create a custom scheduler that reloads periodically
# from celery.beat import PersistentScheduler
from celery.beat import Scheduler
import time as time_module

class DynamicScheduler(Scheduler):
    """Custom scheduler that reloads email service schedules periodically"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_reload_time = time_module.time()
    
    def tick(self, *args, **kwargs):
        """Override tick to reload schedules every 5 minutes"""
        # Call the parent tick method
        result = super().tick(*args, **kwargs)
        
        # Reload schedules every 300 seconds (5 minutes)
        current_time = time_module.time()
        
        if current_time - self._last_reload_time >= 300:
            with app.app_context():
                app.logger.info("⏰ Auto-reloading email service schedules...")
                load_email_service_schedule()
                self._last_reload_time = current_time
        
        return result

# Configure Celery to use the custom scheduler
celery.conf.beat_scheduler = DynamicScheduler

if __name__ == '__main__':
    # Push Flask app context
    with app.app_context():
        # Start Celery Beat with custom scheduler
        celery.start(['beat', '--loglevel=info'])
