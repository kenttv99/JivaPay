#!/usr/bin/env python3
"""
Script to seed default payment methods, banks, and their availability.
Usage:
    python backend/scripts/seed_payment_references.py
"""
import logging
from sqlalchemy.orm import Session
from backend.database.utils import get_db_session_cm
from backend.database.db import PaymentMethod, BanksTrader, AvalibleBankMethod, FiatCurrency

def seed_payment_methods_main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    with get_db_session_cm() as session:
        # --- Get prerequisite FiatCurrency (e.g., USD) ---
        usd_currency = session.query(FiatCurrency).filter_by(currency_code="USD").one_or_none()
        
        if not usd_currency:
            logger.error("USD currency (fiat_code='USD') not found. Please ensure 'seed_reference_data' command was executed successfully before this one. Aborting payment method seeding.")
            return # Stop execution if USD is not found
        
        usd_fiat_id = usd_currency.id
        logger.info(f"Using USD currency with id {usd_fiat_id} for seeding payment methods.")

        # --- PaymentMethods ---
        payment_methods_data = [
            {"fiat_id": usd_fiat_id, "method_name": "BANK_CARD_USD", "public_name": "Bank Card (USD)", "access": True},
            {"fiat_id": usd_fiat_id, "method_name": "WIRE_TRANSFER_USD", "public_name": "Wire Transfer (USD)", "access": True},
        ]

        created_payment_methods = {}
        for pm_data in payment_methods_data:
            existing_pm = session.query(PaymentMethod).filter_by(method_name=pm_data["method_name"], fiat_id=pm_data["fiat_id"]).one_or_none()
            if existing_pm:
                logger.info(f"PaymentMethod '{pm_data['method_name']}' for fiat_id {pm_data['fiat_id']} already exists with id {existing_pm.id}.")
                created_payment_methods[pm_data["method_name"]] = existing_pm
            else:
                pm = PaymentMethod(**pm_data)
                session.add(pm)
                session.flush() # Flush to get ID
                logger.info(f"Creating PaymentMethod '{pm_data['method_name']}' with id {pm.id}.")
                created_payment_methods[pm_data["method_name"]] = pm
        
        # --- BanksTrader ---
        banks_data = [
            {"fiat_id": usd_fiat_id, "bank_name": "GLOBAL_BANK_USD", "public_name": "Global Bank (USD)", "access": True, "interbank": False},
            {"fiat_id": usd_fiat_id, "bank_name": "CITY_BANK_USD", "public_name": "City Bank (USD)", "access": True, "interbank": False},
        ]
        
        created_banks = {}
        for bank_data in banks_data:
            existing_bank = session.query(BanksTrader).filter_by(bank_name=bank_data["bank_name"], fiat_id=bank_data["fiat_id"]).one_or_none()
            if existing_bank:
                logger.info(f"Bank '{bank_data['bank_name']}' for fiat_id {bank_data['fiat_id']} already exists with id {existing_bank.id}.")
                created_banks[bank_data["bank_name"]] = existing_bank
            else:
                bank = BanksTrader(**bank_data)
                session.add(bank)
                session.flush() # Flush to get ID
                logger.info(f"Creating Bank '{bank_data['bank_name']}' with id {bank.id}.")
                created_banks[bank_data["bank_name"]] = bank

        # --- AvalibleBankMethod ---
        # Example: Link "Bank Card (USD)" method with "Global Bank (USD)"
        global_bank_usd = created_banks.get("GLOBAL_BANK_USD")
        bank_card_usd_pm = created_payment_methods.get("BANK_CARD_USD")

        if global_bank_usd and bank_card_usd_pm:
            avalible_data = {
                "fiat_id": usd_fiat_id,
                "bank_id": global_bank_usd.id,
                "method_id": bank_card_usd_pm.id,
                "access": True
            }
            existing_abm = session.query(AvalibleBankMethod).filter_by(
                bank_id=global_bank_usd.id, method_id=bank_card_usd_pm.id, fiat_id=usd_fiat_id
            ).one_or_none()
            if existing_abm:
                logger.info(f"AvalibleBankMethod for Global Bank (USD) Card Transfer already exists.")
            else:
                abm = AvalibleBankMethod(**avalible_data)
                session.add(abm)
                logger.info("Creating AvalibleBankMethod for Global Bank (USD) Card Transfer.")
        else:
            logger.warning("Could not link Global Bank (USD) with Bank Card (USD) - one or both not found/created after attempting to fetch/create them.")

        try:
            session.commit()
            logger.info("Payment references seeding committed successfully.")
        except Exception as e:
            logger.error(f"Error committing payment references: {e}")
            session.rollback()

if __name__ == "__main__":
    seed_payment_methods_main() 