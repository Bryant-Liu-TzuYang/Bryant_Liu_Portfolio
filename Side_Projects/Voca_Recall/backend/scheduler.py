import time
import logging
import pytz
from datetime import datetime
from app import create_app, db
from app.models import EmailService
from app.email import send_email_service_task
from app.redis_utils import get_redis_client, SCHEDULE_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scheduler')

app = create_app()

def run_scheduler():
    logger.info("Starting Email Service Scheduler (Redis ZSET)...")
    
    redis_client = None
    
    with app.app_context():
        # Redis connection setup
        while redis_client is None:
            try:
                redis_client = get_redis_client()
                redis_client.ping()
                logger.info("Connected to Redis successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Retrying in 5s...")
                time.sleep(5)

        # 1. Sync Phase: Populate Redis from DB on startup
        # This ensures that if Redis was flushed, we recover the schedule from the DB source of truth.
        logger.info("Syncing schedule from database...")
        try:
            active_services = EmailService.query.filter_by(is_active=True).all()
            
            # Use a pipeline for efficiency
            pipeline = redis_client.pipeline()
            
            # Reset schedule to match DB truth
            pipeline.delete(SCHEDULE_KEY)
            
            count = 0
            now = datetime.utcnow().replace(tzinfo=pytz.UTC)
            
            for service in active_services:
                # If next_run_at is missing, calculate it
                if not service.next_run_at:
                    service.next_run_at = service.calculate_next_run(now)
                    db.session.add(service)
                
                # Ensure next_run_at is aware (UTC)
                next_run = service.next_run_at
                if next_run.tzinfo is None:
                    next_run = next_run.replace(tzinfo=pytz.UTC)
                    
                pipeline.zadd(SCHEDULE_KEY, {str(service.id): next_run.timestamp()})
                count += 1
                
            pipeline.execute()
            db.session.commit()
            logger.info(f"Synced {count} services to Redis ZSET.")
            
        except Exception as e:
            logger.error(f"Error during sync phase: {e}")
            # Continue to loop, maybe Redis serves old data or eventually recovers

    # 2. Polling Loop
    while True:
        try:
            # We don't strictly need app context for Redis ops, but we need it for DB ops (rescheduling)
            with app.app_context():
                now_ts = time.time()
                
                # Fetch tasks due (score <= now)
                # Redis zrangebyscore returns list of members (bytes)
                ready_tasks = redis_client.zrangebyscore(SCHEDULE_KEY, '-inf', now_ts)
                
                if ready_tasks:
                    logger.info(f"Found {len(ready_tasks)} due tasks")
                    
                    for service_id_bytes in ready_tasks:
                        service_id = int(service_id_bytes)
                        
                        # Atomicity Attempt: Remove it. If we remove it, we own it.
                        if redis_client.zrem(SCHEDULE_KEY, service_id_bytes) > 0:
                            logger.info(f"Processing task for service {service_id}")
                            
                            # 1. Dispatch Task to Worker
                            send_email_service_task.delay(service_id)
                            
                            # 2. Calculate Next Run & Re-schedule
                            service = EmailService.query.get(service_id)
                            
                            if service and service.is_active:
                                # Calculate next run relative to NOW
                                new_next_run = service.calculate_next_run(datetime.utcnow())
                                
                                # Update DB
                                service.next_run_at = new_next_run
                                db.session.commit()
                                
                                # Add back to Redis with new score
                                ts = new_next_run.replace(tzinfo=pytz.UTC).timestamp()
                                redis_client.zadd(SCHEDULE_KEY, {str(service.id): ts})
                                
                                logger.info(f"Rescheduled service {service_id} to {new_next_run}")
                            else:
                                logger.info(f"Service {service_id} stopped/removed (Active: {getattr(service, 'is_active', False)})")
                        else:
                            # Another scheduler instance picked it up (rare in this setup)
                            pass
                            
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            time.sleep(5) # Backoff on error
            
        # Poll frequently (e.g., every 1 second)
        # Using ZSET is efficient enough to poll often
        time.sleep(1)

if __name__ == '__main__':
    run_scheduler()
