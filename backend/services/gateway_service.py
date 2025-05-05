"""Service handling the logic for Gateway API requests."""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# Attempt imports
try:
    # !! Models needed: MerchantStore, IncomingOrder !!
    from backend.database.models import MerchantStore, IncomingOrder
    from backend.database.utils import get_object_or_none, create_object
    # !! Need Schemas !!
    # from backend.shemas_enums.gateway import GatewayInitRequest # Specific schemas?
    from backend.shemas_enums.order import IncomingOrderCreate # Reusing for now
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
except ImportError as e:
    raise ImportError(f"Could not import required modules for GatewayService: {e}")

logger = logging.getLogger(__name__)

def _get_merchant_store_by_api_key(api_key: Optional[str], db: Session) -> MerchantStore:
    """Authenticates and retrieves the merchant store based on API key."""
    if not api_key:
        raise AuthenticationError("API key is missing.")
    
    # TODO: Implement secure API key lookup
    # - Fetch MerchantStore based on api_key hash?
    # - Ensure the key/store is active.
    store = get_object_or_none(db, MerchantStore, api_key=api_key) # Assuming direct key lookup for now (INSECURE)
    
    if not store:
        raise AuthenticationError("Invalid API key.")
    if not store.is_active:
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
    if direction == "PAYIN" and not merchant_store.payin_enabled: # Assuming flags exist
         raise AuthorizationError(f"Pay-In is not enabled for store {merchant_store.id}")
    if direction == "PAYOUT" and not merchant_store.payout_enabled:
         raise AuthorizationError(f"Pay-Out is not enabled for store {merchant_store.id}")
    # Example check for required param:
    # if merchant_store.gateway_require_customer_id and not request_data.customer_id:
    #     raise OrderProcessingError("Customer ID is required for this merchant.", status_code=400)
    logger.debug(f"Request validation passed (placeholder) for Store ID: {merchant_store.id}")

    # 3. Create IncomingOrder
    # TODO: Call order_service or implement creation logic here
    # Ensure all necessary fields are mapped correctly
    try:
        # incoming_order_data = request_data.dict()
        # incoming_order_data['merchant_store_id'] = merchant_store.id
        # incoming_order_data['status'] = 'new' # Initial status
        # incoming_order_data['direction'] = direction # Set direction
        # created_order = create_object(db, IncomingOrder, incoming_order_data)

        # Placeholder Creation:
        from datetime import datetime
        created_order = IncomingOrder(
             id=123, # Dummy ID
             merchant_store_id=merchant_store.id,
             amount=request_data.amount,
             currency_id=request_data.currency_id,
             payment_method_id=request_data.payment_method_id,
             direction=direction,
             customer_id=request_data.customer_id,
             return_url=request_data.return_url,
             callback_url=request_data.callback_url,
             status="new",
             created_at=datetime.utcnow(),
             retry_count=0
         )
        logger.info(f"Created IncomingOrder (placeholder) ID {created_order.id} for Store ID {merchant_store.id}")
        return created_order

    except DatabaseError as e:
        logger.error(f"Failed to create IncomingOrder for Store {merchant_store.id}: {e}", exc_info=True)
        raise # Re-raise DB error
    except Exception as e:
        logger.error(f"Unexpected error creating IncomingOrder for Store {merchant_store.id}: {e}", exc_info=True)
        raise OrderProcessingError(f"Failed to create order: {e}") from e

def get_order_status(order_identifier: str, db: Session) -> Any: # Return type depends on desired response schema
    """Retrieves the status details for a given order identifier."""
    logger.debug(f"Getting status for order identifier: {order_identifier}")
    # TODO: Implement status retrieval
    # - Try to find OrderHistory first by ID
    # - If not found, try IncomingOrder by ID
    # - Format the response based on GatewayStatusResponse schema
    # - Handle not found cases -> OrderProcessingError(status_code=404)
    
    # Placeholder:
    raise OrderProcessingError("Order not found (placeholder)", status_code=404)

def handle_client_confirmation(
    order_identifier: str, 
    uploaded_url: Optional[str], 
    db: Session
) -> None:
    """Handles the client confirmation action from the gateway."""
    logger.info(f"Handling client confirmation for order identifier: {order_identifier}, receipt URL: {uploaded_url}")
    # TODO: Implement confirmation handling
    # 1. Find the OrderHistory record by identifier.
    #    order = get_object_or_none(db, OrderHistory, id=int(order_identifier)) # Assuming identifier is ID
    #    if not order: raise OrderProcessingError(f"Order not found: {order_identifier}", status_code=404)
    # 2. Determine the actor (this might be tricky if the endpoint isn't authenticated).
    #    - Use a system actor? Pass merchant ID? Requires careful design.
    #    actor = None # Placeholder - Needs a way to identify who is allowed to confirm
    # 3. Call the order status manager.
    #    order_status_manager.confirm_payment_by_client(order.id, client_actor=actor, uploaded_receipt_url=uploaded_url, db=db)
    
    # Placeholder:
    logger.warning(f"Client confirmation logic for {order_identifier} not implemented.")
    pass # Simulate successful handling 