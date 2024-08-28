# app/services/rate_limiter.py

from fastapi import HTTPException
import time
from functools import wraps
from typing import Callable, Any
from app.core.config import settings

class RateLimiter:
    def __init__(self, max_calls: int, time_frame: int):
        self.max_calls = max_calls
        self.time_frame = time_frame
        self.calls = []

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            
            # Remove chamadas antigas
            self.calls = [call for call in self.calls if call > now - self.time_frame]
            
            if len(self.calls) >= self.max_calls:
                raise HTTPException(status_code=429, detail="Taxa limite excedida. Tente novamente mais tarde.")
            
            self.calls.append(now)
            return await func(*args, **kwargs)
        
        return wrapper

# Função para criar um decorador de rate limiting
def rate_limit(max_calls: int, time_frame: int) -> Callable:
    return RateLimiter(max_calls, time_frame)

# Exemplo de uso:
# @rate_limit(max_calls=5, time_frame=60)
# async def create_user(user: UserCreate):
#     # Lógica para criar usuário
#     pass