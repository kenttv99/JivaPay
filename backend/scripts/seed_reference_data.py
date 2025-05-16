#!/usr/bin/env python3
"""
Script to seed default reference data (currencies) into the database.
Usage:
    python backend/scripts/seed_reference_data.py
"""

import logging
from backend.database.utils import get_db_session_cm
from backend.database.db import FiatCurrency, CryptoCurrency, Country


def seed_reference_data():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    with get_db_session_cm() as session:
        # Seed default country for currencies
        default_country = session.query(Country).filter_by(country_code_iso="US").one_or_none()
        if not default_country:
            default_country = Country(
                country_name="United States",
                country_code_iso="US",
                public_name="United States",
                description="Default country"
            )
            session.add(default_country)
            session.flush()
            logger.info("Created default country United States.")
        country_id = default_country.id
        # Seed fiat currency USD
        if session.query(FiatCurrency).filter_by(currency_code="USD").one_or_none():
            logger.info("Fiat currency USD already exists, skipping.")
        else:
            session.add(FiatCurrency(
                country_id=country_id,
                currency_name="US Dollar",
                currency_code="USD",
                public_name="US Dollar",
                description="Default fiat currency"
            ))
            logger.info("Created fiat currency USD.")
        # Seed crypto currency USDT
        if session.query(CryptoCurrency).filter_by(currency_code="USDT").one_or_none():
            logger.info("Crypto currency USDT already exists, skipping.")
        else:
            session.add(CryptoCurrency(
                currency_name="USDT",
                currency_code="USDT",
                public_name="USDT",
                description="Default crypto currency"
            ))
            logger.info("Created crypto currency USDT.")
        session.commit()
    logger.info("Reference data seeding complete.")


if __name__ == "__main__":
    seed_reference_data() 