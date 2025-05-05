#!/usr/bin/env python3
"""
Script to seed initial roles and default admin user into the database.
Usage:
    python backend/scripts/seed_data.py
"""

import logging
from sqlalchemy.exc import IntegrityError
from backend.database.utils import get_db_session
from backend.database.db import Role, User, Admin
from backend.config.crypto import hash_password


def seed_data():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initial roles to seed
    roles = [
        {"name": "admin", "description": "Administrator role", "applies_to": "admin"},
        {"name": "support", "description": "Support role", "applies_to": "support"},
        {"name": "merchant", "description": "Merchant role", "applies_to": "merchant"},
        {"name": "trader", "description": "Trader role", "applies_to": "trader"},
    ]

    with get_db_session() as session:
        # Seed roles
        for role_data in roles:
            existing = session.query(Role).filter_by(name=role_data["name"]).one_or_none()
            if existing:
                logger.info(f"Role '{role_data['name']}' already exists, skipping.")
            else:
                role = Role(**role_data)
                session.add(role)
                try:
                    session.commit()
                    logger.info(f"Created role '{role_data['name']}'.")
                except IntegrityError:
                    session.rollback()
                    logger.warning(f"Failed to create role '{role_data['name']}', likely already exists.")

        # Seed default admin user
        admin_email = "admin@example.com"
        admin_password = "adminpass"
        admin_username = "Administrator"

        # Fetch admin role
        admin_role = session.query(Role).filter_by(name="admin").one()

        existing_user = session.query(User).filter_by(email=admin_email).one_or_none()
        if existing_user:
            logger.info("Default admin user already exists, skipping.")
        else:
            hashed_password = hash_password(admin_password)
            user = User(
                email=admin_email,
                password_hash=hashed_password,
                role_id=admin_role.id,
                is_active=True
            )
            session.add(user)
            session.flush()
            admin_profile = Admin(
                user_id=user.id,
                username=admin_username,
                can_manage_other_admins=True,
                can_manage_supports=True,
                can_manage_merchants=True,
                can_manage_traders=True,
                can_edit_system_settings=True,
                can_edit_limits=True,
                can_view_full_logs=True,
                can_handle_appeals=True
            )
            session.add(admin_profile)
            session.commit()
            logger.info("Created default admin user and profile.")

    logger.info("Initial data seeding complete.")


if __name__ == "__main__":
    seed_data() 