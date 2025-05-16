#!/usr/bin/env python3
"""
Script to seed default reference data (currencies) into the database.
Usage:
    python backend/scripts/seed_reference_data.py
"""

import logging
from backend.database.utils import get_db_session_cm
from backend.database.db import FiatCurrency, CryptoCurrency


def seed_reference_data():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    with get_db_session_cm() as session:
        # Seed fiat currency USD
        if session.query(FiatCurrency).filter_by(currency_code="USD").one_or_none():
            logger.info("Fiat currency USD already exists, skipping.")
        else:
            session.add(FiatCurrency(
                country_id=1 if hasattr(FiatCurrency, 'country_id') else None,
                currency_name="US Dollar",
                currency_code="USD",
                public_name="US Dollar",
                description="Default fiat currency"
            ))
            logger.info("Created fiat currency USD.")
        # Seed crypto currency BTC
        if session.query(CryptoCurrency).filter_by(currency_code="BTC").one_or_none():
            logger.info("Crypto currency BTC already exists, skipping.")
        else:
            session.add(CryptoCurrency(
                currency_name="USDT",
                currency_code="usdt",
                public_name="USDT",
                description="Default crypto currency"
            ))
            logger.info("Created crypto currency BTC.")
        session.commit()
    logger.info("Reference data seeding complete.")


if __name__ == "__main__":
    seed_reference_data() 