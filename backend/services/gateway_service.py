"""Service handling the logic for Gateway API requests."""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.database.db import OrderHistory

# Attempt imports
try:
    # !! Models needed: MerchantStore, IncomingOrder !!
    from backend.database.db import MerchantStore, IncomingOrder
    from backend.database.utils import get_object_or_none, create_object
    # !! Need Schemas !!
    # from backend.sсhemas_enums.gateway import GatewayInitRequest # Specific schemas?
    from backend.schemas_enums.order import IncomingOrderCreate # Reusing for now
    # !! Need Order Service (or create order directly here) !!
    # from backend.services import order_service
    # !! Need Order Status Manager !!
    from backend.services import order_status_manager
    # !! Need S3 client !!
    # from backend.utils.s3_client import upload_file
    from backend.utils.exceptions import (
        AuthenticationError, AuthorizationError, ConfigurationError, 
        OrderProcessingError, DatabaseError, JivaPayException, S3Error
    )
    from backend.worker.tasks import process_order_task
except ImportError as e:
    raise ImportError(f"Could not import required modules for GatewayService: {e}")

logger = logging.getLogger(__name__)

def _get_merchant_store_by_api_key(api_key: Optional[str], db: Session) -> MerchantStore:
    """Authenticates and retrieves the merchant store based on API key."""
    if not api_key:
        raise AuthenticationError("API key is missing.")
    
    # Secure API key lookup using public_api_key field
    store = get_object_or_none(db, MerchantStore, public_api_key=api_key)
    
    if not store:
        raise AuthenticationError("Invalid API key.")
    if not store.access:
        raise AuthorizationError("Merchant store is inactive.")
    
    logger.debug(f"Authenticated merchant store ID: {store.id} using API key.")
    return store

def handle_init_request(
    api_key: Optional[str],
    request_data: IncomingOrderCreate, # Or specific GatewayInitRequest schema
    direction: str, # "PAYIN" or "PAYOUT"
    db: Session
) -> IncomingOrder: # Return the created IncomingOrder object
    """Handles the initialization request from the gateway.

    - Identifies merchant.
    - Validates request against store settings.
    - Creates the IncomingOrder record.
    """
    # 1. Identify Merchant
    merchant_store = _get_merchant_store_by_api_key(api_key, db)
    logger.info(f"Handling {direction} init request for Store ID: {merchant_store.id}")

    # 2. Validate Request Data against Store Settings
    # TODO: Implement validation
    # - Check if merchant_store allows this direction (payin_enabled/payout_enabled)
    # - Check if request has required params based on store settings (gateway_require_customer_id, etc.)
    # - Check currency/payment method compatibility with store
    # - Raise ConfigurationError or OrderProcessingError (4xx) if validation fails
    if direction == "PAYIN" and not merchant_store.pay_in_enabled:
         raise AuthorizationError(f"Pay-In is not enabled for store {merchant_store.id}")
    if direction == "PAYOUT" and not merchant_store.pay_out_enabled:
         raise AuthorizationError(f"Pay-Out is not enabled for store {merchant_store.id}")
    # Example check for required param:
    # if merchant_store.gateway_require_customer_id and not request_data.customer_id:
    #     raise OrderProcessingError("Customer ID is required for this merchant.", status_code=400)
    logger.debug(f"Request validation passed (placeholder) for Store ID: {merchant_store.id}")

    # 3. Create IncomingOrder record
    try:
        order_data = request_data.dict(exclude_unset=True)
        order_data.update({
            'merchant_id': merchant_store.merchant_id,
            'store_id': merchant_store.id,
            'gateway_id': merchant_store.id, # Use the store's configured gateway record if applicable
            'status': 'new',
            'retry_count': 0
        })
        created_order = create_object(db, IncomingOrder, order_data)
        logger.info(f"Created IncomingOrder ID {created_order.id} for Store ID {merchant_store.id}")
        # Immediately enqueue the order for processing to achieve real-time handling
        process_order_task.delay(created_order.id)
        return created_order
    except Exception as e:
        msg = f"Failed to create IncomingOrder for Store {merchant_store.id}: {e}"
        logger.error(msg, exc_info=True)
        if isinstance(e, DatabaseError):
            raise
        raise OrderProcessingError(msg) from e

def get_order_status(order_identifier: str, db: Session) -> Any: # Return type depends on desired response schema
    """Retrieves the status details for a given order identifier."""
    logger.debug(f"Getting status for order identifier: {order_identifier}")
    # 1. Try to find in OrderHistory
    order = get_object_or_none(db, OrderHistory, hash_id=order_identifier)
    if order:
        return order
    # 2. Try to find in IncomingOrder by ID
    try:
        incoming_id = int(order_identifier)
        order = get_object_or_none(db, IncomingOrder, id=incoming_id)
        if order:
            return order
    except ValueError:
        pass
    raise OrderProcessingError(f"Order not found: {order_identifier}", status_code=404)

def handle_client_confirmation(
    order_identifier: str, 
    uploaded_url: Optional[str], 
    db: Session
) -> None:
    """Handles the client confirmation action from the gateway."""
    logger.info(f"Handling client confirmation for order identifier: {order_identifier}, receipt URL: {uploaded_url}")
    # 1. Retrieve OrderHistory
    oh = get_object_or_none(db, OrderHistory, hash_id=order_identifier)
    if not oh:
        raise OrderProcessingError(f"Order not found: {order_identifier}", status_code=404)
    # 2. Permission: merchant
    # Actor not identified here; assume system actor for gateway
    from backend.utils.exceptions import AuthorizationError
    # 3. Call status manager
    updated = order_status_manager.confirm_payment_by_client(
        order_id=oh.id,
        receipt=uploaded_url.encode('utf-8'),
        filename=uploaded_url.split('/')[-1],
        db_session=db
    )
    return updated 