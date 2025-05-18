"""Asynchronous database utility functions."""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from backend.database.db_ops import get_async_db_engine # Предполагаем, что такая функция есть для получения AsyncEngine
# или from backend.database.db import async_engine # Если движок создается напрямую

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")

@asynccontextmanager
async def get_async_db_session_cm() -> AsyncSession:
    """Provide an AsyncSession an a context manager."""
    engine = get_async_db_engine() # Убедитесь, что эта функция или импорт движка корректны
    async_session_factory = AsyncSession(bind=engine, expire_on_commit=False)
    
    session: AsyncSession = async_session_factory()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Async session error: {e}", exc_info=True)
        await session.rollback()
        raise
    finally:
        await session.close()

@asynccontextmanager
async def atomic_transaction_async(session: AsyncSession):
    """Context manager for handling atomic transactions with AsyncSession.
    
    Args:
        session: The AsyncSession to use for the transaction.
    """
    if not session.in_transaction(): # Только начинаем новую транзакцию, если еще не в ней
        async with session.begin():
            try:
                logger.debug("Starting async atomic transaction.")
                yield session
                # Commit происходит автоматически при выходе из session.begin(), если не было исключений
                logger.debug("Async atomic transaction committed successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Error in async atomic transaction: {e}", exc_info=True)
                # Rollback происходит автоматически при исключении из session.begin()
                raise # Перевыбрасываем исключение, чтобы его обработал вызывающий код
            except Exception as e:
                logger.error(f"Unexpected non-SQLAlchemyError in async atomic transaction: {e}", exc_info=True)
                # Rollback также должен произойти автоматически
                raise
    else: # Если уже в транзакции, просто используем существующую
        logger.debug("Joining existing async transaction.")
        yield session


async def create_object_async(
    session: AsyncSession, model_class: Type[ModelType], data: Dict[str, Any]
) -> ModelType:
    """
    Creates and saves a new object to the database asynchronously.

    Args:
        session: The AsyncSession for database operations.
        model_class: The SQLAlchemy model class to create.
        data: A dictionary containing the data for the new object.

    Returns:
        The created model instance.
    """
    try:
        instance = model_class(**data)
        session.add(instance)
        await session.flush()  # Чтобы получить ID и другие автогенерируемые значения
        await session.refresh(instance) # Чтобы обновить instance данными из БД
        logger.debug(f"Successfully created {model_class.__name__} object with ID {getattr(instance, 'id', 'N/A')}")
        return instance
    except SQLAlchemyError as e:
        logger.error(f"Error creating {model_class.__name__} object: {e}", exc_info=True)
        raise # Передаем исключение дальше для обработки в atomic_transaction_async или выше

async def update_object_db_async(
    session: AsyncSession, instance: ModelType, data: Dict[str, Any]
) -> ModelType:
    """
    Updates an existing database object with new data asynchronously.

    Args:
        session: The AsyncSession for database operations.
        instance: The SQLAlchemy model instance to update.
        data: A dictionary containing the new data.

    Returns:
        The updated model instance.
    """
    try:
        for key, value in data.items():
            setattr(instance, key, value)
        session.add(instance) # Добавляем в сессию, чтобы отслеживать изменения
        await session.flush()
        await session.refresh(instance)
        logger.debug(f"Successfully updated {instance.__class__.__name__} object with ID {getattr(instance, 'id', 'N/A')}")
        return instance
    except SQLAlchemyError as e:
        logger.error(f"Error updating {instance.__class__.__name__} object: {e}", exc_info=True)
        raise

async def get_entity_by_id_async(
    session: AsyncSession, model_class: Type[ModelType], entity_id: Any, options: Optional[list] = None
) -> Optional[ModelType]:
    """
    Retrieves an entity by its ID asynchronously.

    Args:
        session: The AsyncSession for database operations.
        model_class: The SQLAlchemy model class.
        entity_id: The ID of the entity to retrieve.
        options: Optional list of SQLAlchemy loader options (e.g., joinedload).

    Returns:
        The entity instance or None if not found.
    """
    try:
        stmt = select(model_class).where(model_class.id == entity_id)
        if options:
            stmt = stmt.options(*options)
        result = await session.execute(stmt)
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving {model_class.__name__} with ID {entity_id}: {e}", exc_info=True)
        raise


async def get_object_or_none_async(
    session: AsyncSession, model_class: Type[ModelType], **kwargs: Any
) -> Optional[ModelType]:
    """
    Retrieves a single object by arbitrary keyword arguments or None if not found.

    Args:
        session: The AsyncSession for database operations.
        model_class: The SQLAlchemy model class.
        **kwargs: Keyword arguments to filter by.

    Returns:
        The entity instance or None if not found.
    """
    try:
        stmt = select(model_class).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving {model_class.__name__} with criteria {kwargs}: {e}", exc_info=True)
        raise

# Пример использования get_entity_by_id_logged_async, если он будет здесь,
# или его можно оставить в db_ops и импортировать оттуда, если он уже там есть.
# async def get_entity_by_id_logged_async(...):
#    ... (similar to synchronous version but using await and async session)

# Убедитесь, что get_async_db_engine() определена в backend.database.db_ops или backend.database.db.
# Пример в db_ops.py или db.py:
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
# from backend.config.settings import settings
#
# _async_engine: Optional[AsyncEngine] = None
#
# def get_async_db_engine() -> AsyncEngine:
#     global _async_engine
#     if _async_engine is None:
#         _async_engine = create_async_engine(
#             settings.ASYNC_DATABASE_URL, # Убедитесь, что эта настройка есть
#             echo=settings.DB_ECHO_LOG,
#             pool_pre_ping=True,
#             # Другие параметры pool, если нужны
#         )
#     return _async_engine 