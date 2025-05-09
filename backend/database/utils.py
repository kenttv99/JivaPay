"""Database utility functions for session management, transactions, and basic CRUD operations."""

import logging
from contextlib import contextmanager
from typing import Generator, TypeVar, Type, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

# Attempt to import SessionLocal and Base
try:
    from backend.database.engine import SessionLocal
    from backend.database.models import Base # Assuming Base is defined here
except ImportError:
    # Adjust relative path if needed for different execution contexts
    from .engine import SessionLocal
    from .models import Base

# Attempt to import custom exceptions
try:
    from backend.utils.exceptions import DatabaseError, JivaPayException
except ImportError:
    from ..utils.exceptions import DatabaseError, JivaPayException # Adjust relative path

logger = logging.getLogger(__name__) # Use standard logging

ModelType = TypeVar("ModelType", bound=Base) # Generic type for SQLAlchemy models

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provides a transactional scope around a series of operations.

    Yields:
        A SQLAlchemy Session object.
    Ensures:
        The session is closed after use.
    """
    db = SessionLocal()
    logger.debug(f"DB Session {id(db)} opened.")
    try:
        yield db
    finally:
        logger.debug(f"DB Session {id(db)} closed.")
        db.close()

@contextmanager
def atomic_transaction(db_session: Session) -> Generator[None, None, None]:
    """Provides a context manager for atomic database transactions.

    Commits the transaction if the block executes successfully, otherwise rolls back.

    Args:
        db_session: The SQLAlchemy Session object to use for the transaction.

    Raises:
        DatabaseError: If any SQLAlchemyError occurs during commit or rollback.
    """
    if not db_session.is_active:
        # If the session provided is already closed or inactive, raise an error
        # or handle appropriately, e.g., start a new one if that makes sense.
        # Here, we'll raise an error.
        logger.error(f"Attempted atomic transaction on inactive session {id(db_session)}")
        raise DatabaseError("Cannot start atomic transaction on an inactive session.")

    logger.debug(f"Starting atomic transaction on session {id(db_session)}.")
    try:
        # Using nested transactions if the database/driver supports SAVEPOINTs
        # If not, begin() might raise an error if a transaction is already active.
        # Standard behavior is often to treat nested begins as essentially NOPs
        # until the outermost transaction commits/rolls back.
        with db_session.begin_nested():
            yield
        # Outer commit (or commit of the nested block if supported)
        # This commit might happen automatically if using db_session.begin() instead of begin_nested()
        # However, explicitly yielding within begin_nested ensures the block completes before commit.
        # If no exception occurred, the outer transaction managed by get_db_session
        # or another layer will handle the final commit.
        # Let's make it explicit for clarity within this context
        db_session.commit()
        logger.debug(f"Atomic transaction on session {id(db_session)} committed successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Atomic transaction on session {id(db_session)} failed. Rolling back. Error: {e}", exc_info=True)
        try:
            db_session.rollback()
        except SQLAlchemyError as rb_exc:
            logger.critical(f"CRITICAL: Failed to rollback transaction on session {id(db_session)} after error! Error: {rb_exc}", exc_info=True)
            # Raising a critical DatabaseError here
            raise DatabaseError(f"Transaction failed AND rollback failed: {e}; Rollback error: {rb_exc}") from rb_exc
        # Re-raise the original error wrapped in DatabaseError after successful rollback
        raise DatabaseError(f"Transaction failed and rolled back: {e}") from e
    except Exception as e:
        # Catch non-SQLAlchemy errors too, ensuring rollback
        logger.error(f"Non-SQLAlchemy error occurred during atomic transaction on session {id(db_session)}. Rolling back. Error: {e}", exc_info=True)
        try:
            db_session.rollback()
        except SQLAlchemyError as rb_exc:
             logger.critical(f"CRITICAL: Failed to rollback transaction on session {id(db_session)} after non-SQLAlchemy error! Error: {rb_exc}", exc_info=True)
             raise DatabaseError(f"Non-SQLAlchemy error occurred AND rollback failed: {e}; Rollback error: {rb_exc}") from rb_exc
        # Re-raise the original error (or wrap if it's not a JivaPayException)
        if isinstance(e, JivaPayException):
            raise
        else:
            raise DatabaseError(f"Non-SQLAlchemy error occurred in transaction: {e}") from e

# --- Basic CRUD Functions --- #

def create_object(db: Session, model: Type[ModelType], data: Dict[str, Any]) -> ModelType:
    """Creates and saves a new object in the database.

    Args:
        db: The SQLAlchemy session.
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
        db.flush() # Flush to catch potential errors like IntegrityError early
        db.refresh(obj) # Refresh to get DB-generated values like IDs
        logger.info(f"Created {model.__name__} object with PK: {getattr(obj, 'id', 'N/A')}") # Assumes 'id' pk
        return obj
    except IntegrityError as e:
        logger.warning(f"Failed to create {model.__name__}: Integrity constraint violated. Data: {data}. Error: {e}")
        raise DatabaseError(f"Could not create {model.__name__}, data conflict: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"Failed to create {model.__name__}. Data: {data}. Error: {e}", exc_info=True)
        raise DatabaseError(f"Database error while creating {model.__name__}: {e}") from e

def get_object_or_none(db: Session, model: Type[ModelType], **kwargs) -> Optional[ModelType]:
    """Retrieves an object by its attributes or returns None if not found.

    Args:
        db: The SQLAlchemy session.
        model: The SQLAlchemy model class.
        **kwargs: Attributes to filter by (e.g., id=1, email='a@b.com').

    Returns:
        The found object or None.

    Raises:
        DatabaseError: If a SQLAlchemyError occurs (excluding NoResultFound).
    """
    try:
        # Basic filtering, assumes exact matches
        query = db.query(model).filter_by(**kwargs)
        obj = query.one_or_none()
        if obj:
            logger.debug(f"Retrieved {model.__name__} object with filter: {kwargs}")
        else:
            logger.debug(f"{model.__name__} object not found with filter: {kwargs}")
        return obj
    except NoResultFound: # Should not happen with one_or_none, but belt and suspenders
        logger.debug(f"{model.__name__} object not found with filter: {kwargs}")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving {model.__name__} with filter {kwargs}: {e}", exc_info=True)
        raise DatabaseError(f"Database error while retrieving {model.__name__}: {e}") from e

def update_object_db(db: Session, obj: ModelType, data: Dict[str, Any]) -> ModelType:
    """Updates an existing database object with new data.

    Args:
        db: The SQLAlchemy session.
        obj: The SQLAlchemy object instance to update.
        data: A dictionary containing the new data.

    Returns:
        The updated object.

    Raises:
        DatabaseError: If an IntegrityError or other SQLAlchemyError occurs.
    """
    try:
        pk_name = obj.__mapper__.primary_key[0].name # Get primary key column name
        pk_value = getattr(obj, pk_name, 'N/A')
        logger.debug(f"Attempting to update {obj.__class__.__name__} with PK {pk_value}. Data: {data}")

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                logger.warning(f"Attribute '{key}' not found on {obj.__class__.__name__} during update. Skipping.")

        db.add(obj) # Add the modified object back to the session (important if it was detached)
        db.flush()  # Flush to catch potential errors
        db.refresh(obj) # Refresh to get any DB-level changes
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