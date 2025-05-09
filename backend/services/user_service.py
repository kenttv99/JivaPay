#!/usr/bin/env python3
"""
Service for managing users and roles in JivaPay.
Provides functions for creating users, retrieving users by email, and authenticating users.
"""

import logging
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.config.crypto import hash_password, verify_password
from backend.database.db import User, Role
from backend.utils.exceptions import AuthenticationError, AuthorizationError, DatabaseError

logger = logging.getLogger(__name__)

def get_user_by_email(session: Session, email: str) -> User | None:
    """Retrieve a user by email or return None if not found."""
    try:
        return session.query(User).filter_by(email=email).one_or_none()
    except Exception as e:
        logger.error(f"Error retrieving user by email {email}: {e}", exc_info=True)
        raise DatabaseError(f"Error retrieving user by email {email}: {e}") from e


def create_user(session: Session, email: str, password: str, role_name: str) -> User:
    """Create a new user with the given email, password, and role."""
    try:
        if get_user_by_email(session, email):
            raise AuthorizationError(f"User with email '{email}' already exists.")
        role = session.query(Role).filter_by(name=role_name).one_or_none()
        if not role:
            raise DatabaseError(f"Role '{role_name}' not found.")
        hashed = hash_password(password)
        user = User(email=email, password_hash=hashed, role_id=role.id, is_active=True)
        session.add(user)
        session.flush()
        logger.info(f"Created user '{email}' with role '{role_name}'")
        return user
    except (AuthenticationError, AuthorizationError, DatabaseError):
        raise
    except Exception as e:
        logger.error(f"Error creating user '{email}': {e}", exc_info=True)
        raise DatabaseError(f"Error creating user '{email}': {e}") from e


def authenticate_user(session: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password. Returns the User if valid."""
    user = get_user_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password.")
    if not user.is_active:
        raise AuthorizationError("User account is inactive.")
    logger.info(f"Authenticated user '{email}' successfully.")
    return user 