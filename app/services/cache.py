# Emprestimo-Facil\app\services\cache.py

from functools import wraps
from app.core.config import settings
import json
from typing import Any, Callable, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)

class Cache:
    def __init__(self):
        self.redis = settings.redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Erro ao obter dados do cache: {str(e)}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600):
        try:
            await self.redis.set(key, json.dumps(value), expire=expire)
        except Exception as e:
            logger.error(f"Erro ao definir dados no cache: {str(e)}")

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Erro ao deletar dados do cache: {str(e)}")

    async def clear_cache(self, pattern: str = "*"):
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Erro ao limpar o cache: {str(e)}")

cache = Cache()

def cache_decorator(expire_time: int = 3600):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            
            try:
                cached_result = await cache.get(cache_key)
                if cached_result:
                    return cached_result
                
                result = await func(*args, **kwargs)
                
                await cache.set(cache_key, result, expire=expire_time)
                
                return result
            except Exception as e:
                logger.error(f"Erro no cache_decorator: {str(e)}")
                return await func(*args, **kwargs)
        return wrapper
    return decorator

async def clear_cache(pattern: str = "*") -> None:
    await cache.clear_cache(pattern)

async def update_cache(key: str, value: Any, expire_time: int = 3600) -> None:
    await cache.set(key, value, expire=expire_time)

# Exemplo de uso:
# @cache_decorator(expire_time=300)
# async def get_user(user_id: int):
#     # Lógica para obter o usuário
#     pass