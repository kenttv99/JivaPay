#!/usr/bin/env python3
"""
Script to seed default configuration settings into the database.
Usage:
    python backend/scripts/seed_config.py
"""

import logging
from backend.database.utils import get_db_session_cm
from backend.database.db import ConfigurationSetting


def seed_config():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Default configuration values
    defaults = {
        "MAX_ORDER_RETRIES": "5",
        "RETRY_BACKOFF_FACTOR": "2",
        "RATE_LIMIT_DEFAULT": "100/minute",
        # add other default keys here as needed
    }

    with get_db_session_cm() as session:
        for key, value in defaults.items():
            existing = session.get(ConfigurationSetting, key)
            if existing:
                logger.info(f"Configuration '{key}' already exists, skipping.")
            else:
                logger.info(f"Creating configuration '{key}' with default '{value}'.")
                setting = ConfigurationSetting(key=key, value=value, description="Default setting")
                session.add(setting)
        session.commit()
    logger.info("Default configuration seeding complete.")


if __name__ == "__main__":
    seed_config() 