#Emprestimo-Facil\app\cache\redis_cache.py

import redis
from app.core.config import settings

redis_settings = settings.get_redis_settings()

if redis_settings:
    redis_client = redis.Redis.from_url(redis_settings["url"])
else:
    redis_client = None

def get_cache():
    if redis_client:
        return redis_client
    return None

# ... funções de cache ...