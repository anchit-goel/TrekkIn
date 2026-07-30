import redis
import json
from config import Config

redis_client = redis.Redis.from_url(Config.CELERY_BROKER_URL, decode_responses=True)


def cache_get(key):
    value = redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


def cache_set(key, value, ttl_seconds=60):
    redis_client.setex(key, ttl_seconds, json.dumps(value))


def cache_delete(*keys):
    for key in keys:
        redis_client.delete(key)