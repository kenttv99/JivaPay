"""Service for sending asynchronous callbacks to merchant URLs."""

import logging
import hashlib
import hmac
import json
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
CALLBACK_MAX_RETRIES = 3 # Example retry count for failed callbacks
CALLBACK_RETRY_DELAY = 60 # Example delay in seconds

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
    """Formats the data to be sent in the callback."""
    # TODO: Define the exact payload structure required by merchants
    # Include relevant order details like ID, merchant's order ID (if provided),
    # status, amount, currency, customer_id, timestamps etc.
    if isinstance(order, OrderHistory):
        return {
            "order_id": order.id,
            "incoming_order_id": order.incoming_order_id,
            "merchant_order_id": order.incoming_order.merchant_order_id if order.incoming_order else None, # Example access
            "status": str(order.status), # Ensure string representation
            "amount": str(order.amount),
            "currency_code": order.currency.code if order.currency else None, # Example access
            "customer_id": order.incoming_order.customer_id if order.incoming_order else None,
            "completed_at": order.completed_at.isoformat() if order.completed_at else None,
            # Add other necessary fields
        }
    elif isinstance(order, IncomingOrder):
         return {
            "incoming_order_id": order.id,
            "merchant_order_id": order.merchant_order_id, # Example access
            "status": str(order.status),
            "amount": str(order.amount),
            "currency_code": order.currency.code if order.currency else None, # Example access
            "customer_id": order.customer_id,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            # Add other necessary fields based on when callback is sent
        }
    else:
        logger.error(f"Cannot prepare callback payload for unknown type: {type(order)}")
        return {}

# @celery_app.task(bind=True, max_retries=CALLBACK_MAX_RETRIES, default_retry_delay=CALLBACK_RETRY_DELAY)
# def send_merchant_callback_task(self, order_id: int, order_model_name: str):
@handle_service_exceptions(logger, service_name=SERVICE_NAME)
async def send_merchant_callback(
    order: Any, # Pass the loaded OrderHistory or IncomingOrder object
    merchant_store: MerchantStore # Pass the loaded MerchantStore object
):
    """Sends a callback notification to the merchant's configured URL.
    
    This function (or a Celery task wrapping it) should be called after
    significant order status changes.
    """
    
    # 1. Check if Callback URL is configured
    callback_url = order.callback_url # Or maybe merchant_store.callback_url?
    if not callback_url:
        logger.debug(f"No callback URL configured for Order ID {getattr(order, 'id', 'N/A')} / Store ID {merchant_store.id}. Skipping callback.")
        return

    # 2. Check if Secret Key is configured
    secret_key = merchant_store.secret_key
    if not secret_key:
        logger.warning(f"No secret key configured for Store ID {merchant_store.id}. Cannot sign callback for Order ID {getattr(order, 'id', 'N/A')}. Skipping callback.")
        # Or send unsigned? Decide policy.
        return

    # 3. Prepare Payload
    payload = _prepare_callback_payload(order)
    if not payload:
        return # Error already logged

    # 4. Generate Signature
    signature = _generate_signature(payload, secret_key)

    # 5. Prepare Headers
    headers = {
        'Content-Type': 'application/json',
        'X-JivaPay-Signature': signature
        # Add other headers if needed (e.g., User-Agent)
    }
    
    order_id_log = getattr(order, 'id', 'N/A')
    logger.info(f"Attempting to send callback for Order ID {order_id_log} to URL: {callback_url}")

    # 6. Send HTTP POST Request (using httpx for async)
    try:
        async with httpx.AsyncClient(timeout=CALLBACK_TIMEOUT_SECONDS) as client:
            response = await client.post(
                callback_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status() # Raise exception for 4xx/5xx responses
            
            logger.info(f"Callback sent successfully for Order ID {order_id_log}. Merchant server responded with status: {response.status_code}")
            # TODO: Potentially log merchant response body if needed for debugging

    except Exception as e:
        # Catch any other unexpected errors during callback sending
        logger.critical(f"Unexpected critical error during callback for Order ID {order_id_log} to URL {callback_url}: {e}", exc_info=True)
        # Report to Sentry? 
        # report_critical_error(e, context_message="Unexpected error sending callback", order_id=order_id_log)
        raise NotificationError("Unexpected error sending callback") from e

# --- Integration Point --- #
# This service (or a task calling it) should be invoked from places like:
# - order_status_manager.py (after status change commit)
# - order_processor.py (if callbacks are needed for intermediate statuses) 