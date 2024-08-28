from alembic.config import Config
from alembic import command
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise
