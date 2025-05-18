"""Service for sending asynchronous callbacks to merchant URLs."""

import logging
import hashlib
import hmac
import json
import asyncio
from typing import Dict, Any, Optional

# Using httpx for making async HTTP requests
# Add 'httpx' to requirements.txt
import httpx 

# Attempt imports
try:
    # Models for storing and retrieving orders and merchant stores
    from backend.database.db import MerchantStore, OrderHistory, IncomingOrder
    # !! Need worker task if sending callbacks asynchronously !!
    # from backend.worker.app import celery_app # Example
    # !! Need DB session if fetching data within task !!
    # from backend.database.utils import get_db_session 
    from backend.database.utils import get_object_or_none
    from backend.utils.exceptions import NotificationError, ConfigurationError
    from backend.config.logger import get_logger
    from backend.utils.decorators import handle_service_exceptions
except ImportError as e:
     raise ImportError(f"Could not import required modules for CallbackService: {e}")

logger = get_logger(__name__)
SERVICE_NAME = "callback_service"

# --- Configuration --- #
CALLBACK_TIMEOUT_SECONDS = 15
CALLBACK_MAX_RETRIES = 3 
CALLBACK_RETRY_DELAY_SECONDS = 60 # Переименовано для ясности

def _generate_signature(payload: Dict[str, Any], secret_key: str) -> str:
    """Generates an HMAC-SHA256 signature for the callback payload."""
    # 1. Sort the payload by key
    sorted_payload = sorted(payload.items())
    # 2. Concatenate key-value pairs into a string (e.g., "key1=value1&key2=value2")
    #    Ensure consistent encoding and representation (e.g., booleans as 'true'/'false')
    message = "&".join([f"{k}={json.dumps(v, separators=(',', ':'))}" for k, v in sorted_payload])
    # 3. Calculate HMAC-SHA256 hash
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def _prepare_callback_payload(order: Any) -> Dict[str, Any]: # Accept OrderHistory or IncomingOrder
    """Formats the data to be sent in the callback.
    IMPORTANT: Ensure that all related objects (e.g., order.incoming_order, order.currency)
    are eager-loaded by the calling code to prevent additional DB queries here.
    """
    # TODO: Define the exact payload structure required by merchants
    # Include relevant order details like ID, merchant's order ID (if provided),
    # status, amount, currency, customer_id, timestamps etc.
    
    payload = {}
    order_id_val = getattr(order, 'id', None)

    if isinstance(order, OrderHistory):
        payload = {
            "order_id": order.id, # JivaPay OrderHistory ID
            "client_order_id": getattr(order, 'client_id', None), # Если мерчант передавал свой ID при создании OrderHistory
            "incoming_order_id": getattr(order, 'incoming_order_id', None),
            "merchant_internal_id": None, # Будет заполнено из IncomingOrder, если доступно
            "status": str(getattr(order, 'status', 'unknown')),
            "order_type": str(getattr(order, 'order_type', 'unknown')),
            "amount_fiat": str(getattr(order, 'total_fiat', '0.00')) if getattr(order, 'total_fiat', None) is not None else None,
            "amount_crypto": str(getattr(order, 'amount_crypto', '0.00000000')) if getattr(order, 'amount_crypto', None) is not None else None,
            "fiat_currency": None, # Будет заполнено из order.fiat, если доступно
            "crypto_currency": None, # Будет заполнено из order.crypto_currency, если доступно
            "customer_id": None, # Будет заполнено из IncomingOrder, если доступно
            "created_at": getattr(order, 'created_at').isoformat() if getattr(order, 'created_at', None) else None,
            "updated_at": getattr(order, 'updated_at').isoformat() if getattr(order, 'updated_at', None) else None,
            "completed_at": getattr(order, 'completed_at').isoformat() if getattr(order, 'completed_at', None) else None, # Пример, если есть такое поле
            "cancellation_reason": getattr(order, 'cancellation_reason', None) # Пример
        }
        if hasattr(order, 'fiat') and order.fiat:
            payload["fiat_currency"] = getattr(order.fiat, 'currency_code', None)
        if hasattr(order, 'crypto_currency') and order.crypto_currency:
            payload["crypto_currency"] = getattr(order.crypto_currency, 'currency_code', None)

        if hasattr(order, 'incoming_order') and order.incoming_order:
            payload["merchant_internal_id"] = getattr(order.incoming_order, 'client_id', None) # Предполагаем, что client_id в IncomingOrder это ID заказа у мерчанта
            payload["customer_id"] = getattr(order.incoming_order, 'customer_id', None)

    elif isinstance(order, IncomingOrder):
        payload = {
            "incoming_order_id": order.id, # JivaPay IncomingOrder ID
            "merchant_internal_id": getattr(order, 'client_id', None), # ID заказа у мерчанта
            "status": str(getattr(order, 'status', 'unknown')),
            "order_type": str(getattr(order, 'order_type', 'unknown')),
            "amount_fiat": str(getattr(order, 'amount_fiat', '0.00')) if getattr(order, 'amount_fiat', None) is not None else None,
            "amount_crypto": str(getattr(order, 'amount_crypto', '0.00000000')) if getattr(order, 'amount_crypto', None) is not None else None,
            "fiat_currency": None, # Будет заполнено из order.fiat_currency, если доступно
            "crypto_currency": None, # Будет заполнено из order.crypto_currency, если доступно
            "customer_id": getattr(order, 'customer_id', None),
            "created_at": getattr(order, 'created_at').isoformat() if getattr(order, 'created_at', None) else None,
            "updated_at": getattr(order, 'updated_at').isoformat() if getattr(order, 'updated_at', None) else None,
            # Добавить другие необходимые поля для IncomingOrder
        }
        if hasattr(order, 'fiat_currency') and order.fiat_currency: # У IncomingOrder может быть fiat_currency напрямую
            payload["fiat_currency"] = getattr(order.fiat_currency, 'currency_code', None)
        if hasattr(order, 'crypto_currency') and order.crypto_currency:
            payload["crypto_currency"] = getattr(order.crypto_currency, 'currency_code', None)
    else:
        logger.error(f"Cannot prepare callback payload for unknown type: {type(order)} for order_id_val {order_id_val}")
        return {}
    
    # Удаляем ключи со значением None для чистоты payload, если это требуется
    # return {k: v for k, v in payload.items() if v is not None} 
    return payload

# @celery_app.task(bind=True, max_retries=CALLBACK_MAX_RETRIES, default_retry_delay=CALLBACK_RETRY_DELAY_SECONDS)
# def send_merchant_callback_task(self, order_id: int, order_model_name: str):
@handle_service_exceptions(logger, service_name=SERVICE_NAME)
async def send_merchant_callback(
    order: Any, # Pass the loaded OrderHistory or IncomingOrder object
    merchant_store: MerchantStore # Pass the loaded MerchantStore object
):
    """Sends a callback notification to the merchant's configured URL.
    
    This function (or a Celery task wrapping it) should be called after
    significant order status changes.
    Ensures related objects on 'order' (e.g. incoming_order, currency) are pre-loaded.
    """
    order_id_log = getattr(order, 'id', 'N/A') # Для логирования

    # 1. Determine Callback URL (priority to order-specific, then store default)
    specific_callback_url = None
    if isinstance(order, OrderHistory):
        if hasattr(order, 'incoming_order') and order.incoming_order:
            specific_callback_url = getattr(order.incoming_order, 'callback_url', None)
    elif isinstance(order, IncomingOrder):
        specific_callback_url = getattr(order, 'callback_url', None)
    
    callback_url = specific_callback_url or getattr(merchant_store, 'callback_url', None)

    if not callback_url:
        logger.debug(f"No callback URL configured for Order ID {order_id_log} / Store ID {merchant_store.id}. Skipping callback.")
        return

    # 2. Check if Secret Key is configured
    secret_key = getattr(merchant_store, 'secret_key', None)
    if not secret_key:
        logger.warning(f"No secret key configured for Store ID {merchant_store.id}. Cannot sign callback for Order ID {order_id_log}. Skipping callback.")
        # Or send unsigned? Current policy: skip.
        return

    # 3. Prepare Payload
    payload = _prepare_callback_payload(order)
    if not payload: # Ошибка уже залогирована в _prepare_callback_payload
        logger.warning(f"Callback payload is empty for Order ID {order_id_log}. Skipping callback.")
        return

    # 4. Generate Signature
    signature = _generate_signature(payload, secret_key)

    # 5. Prepare Headers
    headers = {
        'Content-Type': 'application/json',
        'X-JivaPay-Signature': signature
        # Add other headers if needed (e.g., User-Agent)
    }
    
    logger.info(f"Attempting to send callback for Order ID {order_id_log} to URL: {callback_url}. Attempt 1/{CALLBACK_MAX_RETRIES}")

    # 6. Send HTTP POST Request with retries
    last_exception = None
    for attempt in range(CALLBACK_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=CALLBACK_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    callback_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status() # Raise exception for 4xx/5xx responses
            
            logger.info(f"Callback sent successfully for Order ID {order_id_log} (Attempt {attempt + 1}/{CALLBACK_MAX_RETRIES}). Merchant server responded with status: {response.status_code}")
            # TODO: Potentially log merchant response body if needed for debugging (e.g., if response.status_code is not 2xx)
            return # Callback successful
        
        except httpx.HTTPStatusError as e:
            last_exception = e
            logger.warning(
                f"HTTP Status Error sending callback for Order ID {order_id_log} to {callback_url} (Attempt {attempt + 1}/{CALLBACK_MAX_RETRIES}): {e.response.status_code} - {e.response.text}",
                exc_info=True
            )
        except httpx.RequestError as e: # Covers network errors, timeout, etc.
            last_exception = e
            logger.warning(
                f"Request Error sending callback for Order ID {order_id_log} to {callback_url} (Attempt {attempt + 1}/{CALLBACK_MAX_RETRIES}): {type(e).__name__} - {str(e)}",
                exc_info=True
            )
        except Exception as e: # Catch any other unexpected errors during callback sending
            last_exception = e
            logger.error( # Changed to error for unexpected issues within loop
                f"Unexpected error during callback for Order ID {order_id_log} to URL {callback_url} (Attempt {attempt + 1}/{CALLBACK_MAX_RETRIES}): {e}",
                exc_info=True
            )
            # For truly unexpected errors, we might want to break sooner or handle differently.
            # For now, it will retry.

        if attempt < CALLBACK_MAX_RETRIES - 1:
            logger.info(f"Retrying callback for Order ID {order_id_log} in {CALLBACK_RETRY_DELAY_SECONDS} seconds...")
            await asyncio.sleep(CALLBACK_RETRY_DELAY_SECONDS) # asyncio import will be needed at the top
        else:
            logger.error(f"Callback failed for Order ID {order_id_log} after {CALLBACK_MAX_RETRIES} attempts. Last error: {last_exception}")
            # Report to Sentry or raise a specific error if the caller needs to know about the persistent failure.
            # report_critical_error(last_exception, context_message="Callback failed after multiple retries", order_id=order_id_log)
            # Re-raising the last known exception or a generic NotificationError
            if isinstance(last_exception, httpx.HTTPStatusError):
                 # You might want to wrap this in a custom NotificationError
                raise NotificationError(f"Callback failed: Server returned {last_exception.response.status_code}") from last_exception
            elif isinstance(last_exception, httpx.RequestError):
                raise NotificationError("Callback failed: Request error") from last_exception
            elif last_exception: # If some other exception was caught
                raise NotificationError("Callback failed: Unexpected error during send") from last_exception
            else: # Should not happen if loop completed
                raise NotificationError(f"Callback failed for Order ID {order_id_log} after {CALLBACK_MAX_RETRIES} attempts.")

# --- Integration Point --- #
# This service (or a task calling it) should be invoked from places like:
# - order_status_manager.py (after status change commit)
# - order_processor.py (if callbacks are needed for intermediate statuses) 