import logging
from logging.handlers import RotatingFileHandler
import os
from app.core.config import settings

class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.module = record.module.ljust(20)
        return super().format(record)

def setup_logger():
    logger = logging.getLogger(settings.project_name)
    logger.setLevel(settings.logging_level)

    formatter = CustomFormatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')

    # Configuração do arquivo de log com rotação
    log_file = os.path.join(settings.log_directory, f"{settings.project_name}.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # Configuração do console log
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Configuração de níveis de log personalizados por módulo
    for module, level in settings.module_log_levels.items():
        logging.getLogger(module).setLevel(level)

    return logger

logger = setup_logger()

def get_logger(module_name):
    return logging.getLogger(f"{settings.project_name}.{module_name}")
