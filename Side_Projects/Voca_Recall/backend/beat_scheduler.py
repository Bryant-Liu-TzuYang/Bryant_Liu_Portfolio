"""
Celery Beat scheduler for email services.
This module dynamically loads email services from the database and schedules them.
"""
from celery import Celery
from celery.schedules import crontab
from datetime import datetime
import pytz
from app.models import EmailService, db
from application import app  # Reuse the app creation from application.py

def get_dynamic_schedule():
    """
    Dynamically generate Celery Beat schedule from EmailService records.
    This function is called by Celery Beat to load the schedule.
    """
    schedule = {}
    
    with app.app_context():
        try:
            # Get all active email services
            services = EmailService.query.filter_by(is_active=True).all()
            
            for service in services:
                # Parse send_time (format: "HH:MM")
                hour, minute = map(int, service.send_time.split(':'))
                
                # Create cron schedule based on frequency
                if service.frequency == 'daily':
                    cron_schedule = crontab(hour=hour, minute=minute)
                elif service.frequency == 'weekly':
                    # Default to Monday, could be enhanced to specify day
                    cron_schedule = crontab(hour=hour, minute=minute, day_of_week=1)
                elif service.frequency == 'monthly':
                    # Default to 1st of month
                    cron_schedule = crontab(hour=hour, minute=minute, day_of_month=1)
                else:
                    continue  # Skip unknown frequencies
                
                # Add to schedule with unique task name
                schedule[f'send-email-service-{service.id}'] = {
                    'task': 'app.email.send_email_service_task',
                    'schedule': cron_schedule,
                    'args': (service.id,),
                    'options': {
                        'expires': 3600,  # Task expires after 1 hour
                    }
                }
                
            app.logger.info(f"Loaded {len(schedule)} email service schedules")
            
        except Exception as e:
            app.logger.error(f"Error loading email service schedules: {e}")
            
    return schedule


class DynamicBeatScheduler:
    """
    Custom scheduler that reloads the schedule periodically.
    """
    def __init__(self, *args, **kwargs):
        self.schedule = get_dynamic_schedule()
    
    def tick(self):
        """Reload schedule every tick"""
        self.schedule = get_dynamic_schedule()
        return self.schedule
