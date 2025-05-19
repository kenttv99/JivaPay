"""Database utility functions for session management, transactions, and basic CRUD operations."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar, Type, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.future import select

from backend.database.engine import AsyncSessionLocal
from backend.database.db import Base
from backend.utils.exceptions import DatabaseError, JivaPayException
from backend.logger import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=Base)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional scope around a series of operations.

    Yields:
        An AsyncSession object.
    Ensures:
        The session is closed after use.
    """
    db = AsyncSessionLocal()
    logger.debug(f"DB Session {id(db)} opened.")
    try:
        yield db
    finally:
        logger.debug(f"DB Session {id(db)} closed.")
        await db.close()

@asynccontextmanager
async def get_db_session_cm() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional scope around operations via contextmanager."""
    db = AsyncSessionLocal()
    logger.debug(f"DB Session {id(db)} opened (cm).")
    try:
        yield db
    finally:
        logger.debug(f"DB Session {id(db)} closed (cm).")
        await db.close()

@asynccontextmanager
async def atomic_transaction(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Provides a context manager for atomic database transactions.

    Commits the transaction if the block executes successfully, otherwise rolls back.

    Args:
        db_session: The AsyncSession object to use for the transaction.

    Raises:
        DatabaseError: If any SQLAlchemyError occurs during commit or rollback.
    """
    if not db_session.is_active:
        logger.error(f"Attempted atomic transaction on inactive session {id(db_session)}")
        raise DatabaseError("Cannot start atomic transaction on an inactive session.")

    logger.debug(f"Starting atomic transaction on session {id(db_session)}.")
    try:
        async with db_session.begin_nested():
            yield
        await db_session.commit()
        logger.debug(f"Atomic transaction on session {id(db_session)} committed successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Atomic transaction on session {id(db_session)} failed. Rolling back. Error: {e}", exc_info=True)
        try:
            await db_session.rollback()
        except SQLAlchemyError as rb_exc:
            logger.critical(f"CRITICAL: Failed to rollback transaction on session {id(db_session)} after error! Error: {rb_exc}", exc_info=True)
            raise DatabaseError(f"Transaction failed AND rollback failed: {e}; Rollback error: {rb_exc}") from rb_exc
        raise DatabaseError(f"Transaction failed and rolled back: {e}") from e
    except Exception as e:
        logger.error(f"Non-SQLAlchemy error occurred during atomic transaction on session {id(db_session)}. Rolling back. Error: {e}", exc_info=True)
        try:
            await db_session.rollback()
        except SQLAlchemyError as rb_exc:
            logger.critical(f"CRITICAL: Failed to rollback transaction on session {id(db_session)} after non-SQLAlchemy error! Error: {rb_exc}", exc_info=True)
            raise DatabaseError(f"Non-SQLAlchemy error occurred AND rollback failed: {e}; Rollback error: {rb_exc}") from rb_exc
        if isinstance(e, JivaPayException):
            raise
        else:
            raise DatabaseError(f"Non-SQLAlchemy error occurred in transaction: {e}") from e

async def create_object(db: AsyncSession, model: Type[ModelType], data: Dict[str, Any]) -> ModelType:
    """Creates and saves a new object in the database.

    Args:
        db: The AsyncSession.
        model: The SQLAlchemy model class.
        data: A dictionary containing the object's data.

    Returns:
        The newly created object.

    Raises:
        DatabaseError: If an IntegrityError or other SQLAlchemyError occurs.
    """
    try:
        obj = model(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        logger.info(f"Created {model.__name__} object with PK: {getattr(obj, 'id', 'N/A')}")
        return obj
    except IntegrityError as e:
        logger.warning(f"Failed to create {model.__name__}: Integrity constraint violated. Data: {data}. Error: {e}")
        raise DatabaseError(f"Could not create {model.__name__}, data conflict: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"Failed to create {model.__name__}. Data: {data}. Error: {e}", exc_info=True)
        raise DatabaseError(f"Database error while creating {model.__name__}: {e}") from e

async def get_object_or_none(db: AsyncSession, model: Type[ModelType], **kwargs) -> Optional[ModelType]:
    """Retrieves an object by its attributes or returns None if not found.

    Args:
        db: The AsyncSession.
        model: The SQLAlchemy model class.
        **kwargs: Attributes to filter by (e.g., id=1, email='a@b.com').

    Returns:
        The found object or None.

    Raises:
        DatabaseError: If a SQLAlchemyError occurs (excluding NoResultFound).
    """
    try:
        stmt = select(model).filter_by(**kwargs)
        result = await db.execute(stmt)
        obj = result.scalars().first()
        if obj:
            logger.debug(f"Retrieved {model.__name__} object with filter: {kwargs}")
        else:
            logger.debug(f"{model.__name__} object not found with filter: {kwargs}")
        return obj
    except NoResultFound:
        logger.debug(f"{model.__name__} object not found with filter: {kwargs}")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving {model.__name__} with filter {kwargs}: {e}", exc_info=True)
        raise DatabaseError(f"Database error while retrieving {model.__name__}: {e}") from e

async def update_object_db(db: AsyncSession, obj: ModelType, data: Dict[str, Any]) -> ModelType:
    """Updates an existing database object with new data.

    Args:
        db: The AsyncSession.
        obj: The SQLAlchemy object instance to update.
        data: A dictionary containing the new data.

    Returns:
        The updated object.

    Raises:
        DatabaseError: If an IntegrityError or other SQLAlchemyError occurs.
    """
    try:
        pk_name = obj.__mapper__.primary_key[0].name
        pk_value = getattr(obj, pk_name, 'N/A')
        logger.debug(f"Attempting to update {obj.__class__.__name__} with PK {pk_value}. Data: {data}")

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                logger.warning(f"Attribute '{key}' not found on {obj.__class__.__name__} during update. Skipping.")

        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        logger.info(f"Updated {obj.__class__.__name__} object with PK: {pk_value}")
        return obj
    except IntegrityError as e:
        logger.warning(f"Failed to update {obj.__class__.__name__} (PK: {pk_value}): Integrity constraint violated. Data: {data}. Error: {e}")
        raise DatabaseError(f"Could not update {obj.__class__.__name__}, data conflict: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"Failed to update {obj.__class__.__name__} (PK: {pk_value}). Data: {data}. Error: {e}", exc_info=True)
        raise DatabaseError(f"Database error while updating {obj.__class__.__name__}: {e}") from e

# Add more specific CRUD or query functions as needed, e.g.:
# def get_active_users(db: Session) -> List[User]: ... 