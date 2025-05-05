#!/usr/bin/env python3
"""
Script to initialize the database by creating all tables defined in SQLAlchemy models.
Usage:
    python scripts/init_db.py
"""

from backend.database.engine import engine
from backend.database.db import Base
import logging


def init_db():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    init_db() 