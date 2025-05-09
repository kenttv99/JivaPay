import os
from dotenv import load_dotenv
import logging
import sys
from logging.handlers import RotatingFileHandler

load_dotenv()

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", None)

# Гибкая функция для создания логгера

def get_logger(name: str, log_file: str = LOG_FILE, level: int = getattr(logging, LOG_LEVEL)) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)

    # Консольный вывод
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Файловый вывод (если указан)
    if log_file:
        fh = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=5)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger 