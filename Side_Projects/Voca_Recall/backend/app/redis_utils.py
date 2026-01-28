from flask import current_app
import redis
import time

SCHEDULE_KEY = 'email_schedule'

def get_redis_client():
    return redis.from_url(current_app.config['REDIS_URL'])

def add_to_schedule(service_id, timestamp):
    """Add a service to the schedule ZSET"""
    client = get_redis_client()
    # timestamp can be float or int
    client.zadd(SCHEDULE_KEY, {str(service_id): float(timestamp)})

def remove_from_schedule(service_id):
    """Remove a service from the schedule ZSET"""
    client = get_redis_client()
    client.zrem(SCHEDULE_KEY, str(service_id))
