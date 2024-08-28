#Emprestimo-Facil\app\db\database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from app.core.config import settings
from app.core.logger import get_logger
import traceback

logger = get_logger(__name__)

db_settings = settings.get_database_settings()
engine = create_engine(db_settings["url"], echo=db_settings["echo"])


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        run_migrations()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

from app.db.migrations import run_migrations