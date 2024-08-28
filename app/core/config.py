# Emprestimo-Facil\app\core\config.py

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import secrets
from functools import lru_cache
import logging
from datetime import datetime, timedelta
import aioredis
from pydantic_settings import BaseSettings
from abc import ABC, abstractmethod

class Environment:
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class BaseConfig(ABC, BaseSettings):
    @abstractmethod
    def get_database_settings(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_redis_settings(self) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_email_settings(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_security_settings(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_pagination_settings(self) -> Dict[str, int]:
        pass

    @abstractmethod
    def get_notification_settings(self) -> Dict[str, Optional[str]]:
        pass

    @abstractmethod
    def validate(self) -> None:
        pass

class Settings(BaseConfig):
    # Configurações básicas
    project_name: str = "Empréstimo Fácil"
    api_v1_str: str = "/api/v1"
    
    
    # Segurança
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # Banco de dados
    database_url: str
    
    # Rate limiting
    rate_limit_max_calls: int
    rate_limit_time_frame: int
    
    # Logging
    logging_level: str
    
    # CORS
    allowed_origins: List[str]
    
    # Ambiente
    environment: str

    # Configurações específicas de e-mail
    smtp_tls: bool = True
    smtp_port: Optional[int] = None
    smtp_host: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    emails_from_email: Optional[str] = None
    emails_from_name: Optional[str] = None

    # Configurações de paginação
    pagination_page_size: int
    max_pagination_page_size: int

    # Serviços de Notificação
    whatsapp_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    sms_api_key: Optional[str] = None
    sms_sender_id: Optional[str] = None

    # Rotação de Chave
    secret_key_rotation_days: int = 30

    # Redis
    # URL do Redis para uso geral (cache, filas, etc.)
    redis_url: str = "redis://localhost:6379/0"

    # URL do Redis específica para cache (opcional)
    redis_cache_url: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def backend_cors_origins(self) -> List[str]:
        return self.allowed_origins

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.environment.lower() == Environment.TESTING

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == Environment.PRODUCTION

    def get_database_settings(self) -> Dict[str, Any]:
        return {
            "url": self.database_url,
            "echo": self.is_development,
        }

    def get_redis_settings(self) -> Optional[Dict[str, Any]]:
        if self.redis_url:
            return {"url": self.redis_url}
        return None
    
    async def get_redis_connection(self):
        if self.redis_url:
            return await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return None

    def get_email_settings(self) -> Dict[str, Any]:
        return {
            "smtp_tls": self.smtp_tls,
            "smtp_port": self.smtp_port,
            "smtp_host": self.smtp_host,
            "smtp_user": self.smtp_user,
            "smtp_password": self.smtp_password,
            "emails_from_email": self.emails_from_email,
            "emails_from_name": self.emails_from_name,
        }

    def get_security_settings(self) -> Dict[str, Any]:
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
        }

    def get_pagination_settings(self) -> Dict[str, int]:
        return {
            "page_size": self.pagination_page_size,
            "max_page_size": self.max_pagination_page_size,
        }

    def get_notification_settings(self) -> Dict[str, Optional[str]]:
        return {
            "whatsapp_api_key": self.whatsapp_api_key,
            "telegram_bot_token": self.telegram_bot_token,
            "sms_api_key": self.sms_api_key,
            "sms_sender_id": self.sms_sender_id,
        }
    
    def get_redis_cache_url(self) -> str:
        return self.redis_cache_url or self.redis_url

    def should_rotate_secret_key(self) -> bool:
        # Implementação básica, pode ser expandida para uma lógica mais complexa
        return (datetime.now() - self.secret_key_last_rotated).days >= self.secret_key_rotation_days

    def rotate_secret_key(self) -> None:
        self.secret_key = secrets.token_urlsafe(32)
        self.secret_key_last_rotated = datetime.now()

    def validate(self) -> None:
        if not self.secret_key:
            raise ValueError("SECRET_KEY must be set")
        if not self.database_url:
            raise ValueError("DATABASE_URL must be set")
        # Adicione mais validações conforme necessário


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings

# Configuração de logging
def setup_logging(settings: Settings):
    logging.basicConfig(
        level=getattr(logging, settings.logging_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

settings = get_settings()
setup_logging(settings)