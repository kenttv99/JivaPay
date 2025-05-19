from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Type, TypeVar, Any, Dict, Union
import logging
from cachetools import TTLCache, cached
from backend.database.db import ConfigurationSetting
from functools import lru_cache
import os
import json
from asyncache import cached as async_cached
from cachetools import TTLCache as AsyncTTLCache
from backend.logger import get_logger

logger = get_logger(__name__) # Use standard logging

T = TypeVar('T')

# TTL cache for config values (max 128 entries, TTL 300 seconds) - for sync version
_config_cache = TTLCache(maxsize=128, ttl=300)

# TTL cache for async config values
_async_config_cache = AsyncTTLCache(maxsize=128, ttl=300)

@cached(_config_cache)
def get_config_value(key: str, db: Session, default: Optional[str] = None) -> Optional[str]:
    """Fetches a configuration value (as string) from the database.

    Args:
        key: The unique key of the configuration setting.
        db: The SQLAlchemy session to use for querying.
        default: The default value to return if the key is not found or an error occurs.

    Returns:
        The configuration value as a string, or the default value.
    """
    try:
        setting = db.query(ConfigurationSetting).filter(ConfigurationSetting.key == key).one_or_none()
        if setting:
            logger.debug(f"Retrieved sync config key '{key}' from DB: '{setting.value}'")
            return setting.value
        else:
            logger.warning(f"Sync configuration key '{key}' not found in database. Returning default value: {default}")
            return default
    except Exception as e:
        logger.error(f"Error fetching sync configuration key '{key}' from database: {e}", exc_info=True)
        return default

def get_typed_config_value(key: str, db: Session, expected_type: Type[T], default: Optional[T] = None) -> Optional[T]:
    """Fetches a configuration value from the database and attempts to cast it to the expected type.

    Args:
        key: The unique key of the configuration setting.
        db: The SQLAlchemy session to use for querying.
        expected_type: The Python type to cast the value to (e.g., int, float, bool).
        default: The default value of the expected type to return on failure.

    Returns:
        The configuration value cast to the expected type, or the default value.
    """
    value_str = get_config_value(key, db)

    if value_str is None:
        return default

    try:
        if expected_type == bool:
            lower_val = value_str.lower()
            if lower_val in ['true', '1', 'yes', 'on']:
                return True
            elif lower_val in ['false', '0', 'no', 'off']:
                return False
            else:
                logger.warning(f"Could not convert sync config value '{value_str}' for key '{key}' to bool. Returning default.")
                return default
        else:
            return expected_type(value_str)
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to cast sync config value '{value_str}' for key '{key}' to type {expected_type.__name__}: {e}. Returning default.")
        return default

# --- Async versions --- #

@async_cached(_async_config_cache) # Use async-aware cache
async def get_config_value_async(key: str, db: AsyncSession, default: Optional[str] = None) -> Optional[str]:
    """Fetches a configuration value (as string) from the database asynchronously."""
    try:
        stmt = select(ConfigurationSetting).where(ConfigurationSetting.key == key)
        result = await db.execute(stmt)
        setting = result.scalars().one_or_none()
        if setting:
            logger.debug(f"Retrieved async config key '{key}' from DB: '{setting.value}'")
            return setting.value
        else:
            logger.warning(f"Async configuration key '{key}' not found in database. Returning default value: {default}")
            return default
    except Exception as e:
        logger.error(f"Error fetching async configuration key '{key}' from database: {e}", exc_info=True)
        return default

async def get_typed_config_value_async(key: str, db: AsyncSession, expected_type: Type[T], default: Optional[T] = None) -> Optional[T]:
    """Fetches a configuration value from the database asynchronously and casts it to the expected type."""
    value_str = await get_config_value_async(key, db)

    if value_str is None:
        return default

    try:
        if expected_type == bool:
            lower_val = value_str.lower()
            if lower_val in ['true', '1', 'yes', 'on']:
                return True
            elif lower_val in ['false', '0', 'no', 'off']:
                return False
            else:
                logger.warning(f"Could not convert async config value '{value_str}' for key '{key}' to bool. Returning default.")
                return default
        else:
            return expected_type(value_str)
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to cast async config value '{value_str}' for key '{key}' to type {expected_type.__name__}: {e}. Returning default.")
        return default

# Example Usage:
# Sync:
# max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db_session, int, default=5)
# Async (within an async function with an AsyncSession):
# max_retries_async = await get_typed_config_value_async("MAX_ORDER_RETRIES", async_db_session, int, default=5)

# Example Usage (within a context that has a db session):
# max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db_session, int, default=5)
# use_feature_x = get_typed_config_value("USE_FEATURE_X", db_session, bool, default=False)

"""
Configuration Loader Module

This module provides functionality for loading and caching configuration settings.
It supports both synchronous and asynchronous operations with built-in caching.

Caching Behavior:
---------------
1. Synchronous Functions:
   - Uses LRU cache with TTL (Time To Live)
   - Cache size: 100 items
   - Default TTL: 300 seconds (5 minutes)
   - Cache is shared across all instances

2. Asynchronous Functions:
   - Uses asyncache with TTL
   - Cache size: 100 items
   - Default TTL: 300 seconds (5 minutes)
   - Cache is shared across all instances

Usage Examples:
-------------
1. Synchronous:
   ```python
   from backend.utils.config_loader import get_config_value
   
   # Get config with default value
   value = get_config_value("key", default="default_value")
   
   # Get config with type conversion
   value = get_config_value("key", default=0, value_type=int)
   ```

2. Asynchronous:
   ```python
   from backend.utils.config_loader import get_config_value_async
   
   # Get config asynchronously
   value = await get_config_value_async("key", default="default_value")
   
   # Get config with type conversion
   value = await get_config_value_async("key", default=0, value_type=int)
   ```

Cache Invalidation:
-----------------
The cache is automatically invalidated when:
1. TTL expires (default: 5 minutes)
2. Cache size limit is reached (LRU eviction)
3. System restart

Note: For immediate cache invalidation, use the clear_cache() function.
""" 