"""Service for accessing reference data (e.g., banks, currencies) with caching."""

import logging
import os
import json
from typing import Optional, Any, Dict
from redis import Redis, RedisError
from sqlalchemy.orm import Session, joinedload
from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions

# Attempt to import models, DB utils, and exceptions
try:
    from backend.database.db import BanksTrader as Bank, FiatCurrency as Currency, PaymentMethod, ExchangeRate
    from backend.database.utils import get_object_or_none
    from backend.utils.exceptions import CacheError, DatabaseError, ConfigurationError
except ImportError:
    from ..database.db import BanksTrader as Bank, FiatCurrency as Currency, PaymentMethod, ExchangeRate
    from ..database.utils import get_object_or_none
    from ..utils.exceptions import CacheError, DatabaseError, ConfigurationError

logger = get_logger(__name__)
SERVICE_NAME = "reference_data_service"

# --- Redis Cache Client Configuration --- #
REDIS_URL = os.getenv("REDIS_URL")
CACHE_PREFIX = "ref_data:"
DEFAULT_CACHE_TTL_SECONDS = 3600 # 1 hour default TTL for reference data

redis_client: Optional[Redis] = None

def get_redis_client() -> Optional[Redis]:
    """Initializes and returns the Redis client instance, or None if not configured."""
    global redis_client
    if redis_client is None:
        if not REDIS_URL:
            logger.warning("REDIS_URL not set. Reference data caching is disabled.")
            return None
        try:
            # decode_responses=True ensures keys/values are returned as strings
            redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
            redis_client.ping() # Check connection
            logger.info("Redis client for caching initialized successfully.")
        except RedisError as e:
            logger.error(f"Failed to initialize Redis client for caching: {e}", exc_info=True)
            redis_client = None # Ensure it remains None on failure
        except Exception as e:
            logger.error(f"An unexpected error occurred during Redis client initialization: {e}", exc_info=True)
            redis_client = None
    return redis_client

# Initialize on module load (or call explicitly at startup)
get_redis_client()

# --- Cache Helper Functions --- #

def _get_from_cache(key: str) -> Optional[Any]:
    """Retrieves and deserializes data from Redis cache."""
    client = get_redis_client()
    if not client:
        return None
    try:
        cached_data = client.get(f"{CACHE_PREFIX}{key}")
        if cached_data:
            logger.debug(f"Cache HIT for key: {key}")
            return json.loads(cached_data)
        else:
            logger.debug(f"Cache MISS for key: {key}")
            return None
    except RedisError as e:
        logger.error(f"Redis GET error for key '{key}': {e}", exc_info=True)
        # Optional: report via notifications.report_critical_error(CacheError(...))
        raise CacheError(f"Failed to get data from cache for key: {key}", original_exception=e)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for cached key '{key}': {e}", exc_info=True)
        # Data is corrupted, treat as miss or raise error?
        # Let's treat as miss for now, maybe delete the corrupted key?
        _delete_from_cache(key) # Attempt to delete corrupted data
        return None

def _set_to_cache(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL_SECONDS):
    """Serializes and stores data in Redis cache with a TTL."""
    client = get_redis_client()
    if not client:
        return
    try:
        serialized_value = json.dumps(value)
        client.setex(f"{CACHE_PREFIX}{key}", ttl, serialized_value)
        logger.debug(f"Set cache for key: {key} with TTL: {ttl}s")
    except RedisError as e:
        logger.error(f"Redis SETEX error for key '{key}': {e}", exc_info=True)
        # Optional: report via notifications.report_critical_error(CacheError(...))
        # Don't raise here, as failure to cache shouldn't break the main flow
    except (TypeError, OverflowError) as e:
        logger.error(f"JSON serialization error for key '{key}': {e}", exc_info=True)
        # Cannot cache this value

def _delete_from_cache(key: str):
    """Deletes a key from the cache."""
    client = get_redis_client()
    if not client:
        return
    try:
        client.delete(f"{CACHE_PREFIX}{key}")
        logger.info(f"Deleted cache key: {key}")
    except RedisError as e:
        logger.error(f"Redis DELETE error for key '{key}': {e}", exc_info=True)

# --- Functions for explicit cache invalidation ---
def invalidate_bank_cache(bank_id: int):
    """Invalidates the cache for a specific bank."""
    cache_key = f"bank:{bank_id}"
    _delete_from_cache(cache_key)

def invalidate_payment_method_cache(method_id: int):
    """Invalidates the cache for a specific payment method."""
    cache_key = f"payment_method:{method_id}"
    _delete_from_cache(cache_key)

def invalidate_exchange_rate_cache(crypto_id: int, fiat_id: int):
    """Invalidates the cache for a specific exchange rate."""
    cache_key = f"exchange_rate:{crypto_id}:{fiat_id}"
    _delete_from_cache(cache_key)

# --- Service Functions --- #
# Note: These functions assume Pydantic schemas or dict representations for return values
# Adjust based on actual model structure and desired return type (e.g., SQLAlchemy objects)

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_bank_details(bank_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """Gets bank details, using cache first, then DB."""
    cache_key = f"bank:{bank_id}"
    cached_details = _get_from_cache(cache_key)
    if cached_details is not None:
        return cached_details

    bank = db.query(Bank).options(joinedload(Bank.fiat)).filter(Bank.id == bank_id).one_or_none()
    if bank:
        bank_details = {
            "id": bank.id,
            "name": bank.public_name or bank.bank_name,
            "fiat_currency_id": bank.fiat_id,
            "currency_code": bank.fiat.currency_code if bank.fiat else None,
            "access": bank.access,
        }
        _set_to_cache(cache_key, bank_details)
        return bank_details
    else:
        return None

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_payment_method_details(method_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """Gets payment method details, using cache first, then DB."""
    cache_key = f"payment_method:{method_id}"
    cached_details = _get_from_cache(cache_key)
    if cached_details is not None:
        return cached_details

    method = get_object_or_none(db, PaymentMethod, id=method_id)
    if method:
        method_details = {
            "id": method.id,
            "method_name": method.method_name,
            "public_name": method.public_name,
            "access": method.access,
        }
        _set_to_cache(cache_key, method_details)
        return method_details
    else:
        return None

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_exchange_rate(crypto_id: int, fiat_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """Gets exchange rate details, using cache first, then DB."""
    cache_key = f"exchange_rate:{crypto_id}:{fiat_id}"
    cached_details = _get_from_cache(cache_key)
    if cached_details is not None:
        return cached_details

    rate = get_object_or_none(db, ExchangeRate, crypto_currency_id=crypto_id, fiat_currency_id=fiat_id)
    if rate:
        rate_details = {
            "id": rate.id,
            "currency": rate.currency,
            "fiat": rate.fiat,
            "buy_rate": str(rate.buy_rate),
            "sell_rate": str(rate.sell_rate),
            "median_rate": str(rate.median_rate),
            "source": rate.source,
            "updated_at": rate.updated_at.isoformat() if rate.updated_at else None,
        }
        _set_to_cache(cache_key, rate_details)
        return rate_details
    else:
        logger.warning(f"Exchange rate not found for crypto {crypto_id} and fiat {fiat_id}")
        return None

# Add other functions for reference data (e.g., get_currency_details) following the same pattern. 