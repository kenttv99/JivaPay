"""API Router for Merchant operations."""

import logging
from typing import List, Optional, Any # Any for placeholder user model

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

# Attempt imports (adjusting paths based on new location)
try:
    from backend.database.utils import get_db_session
    from backend.shemas_enums.order import IncomingOrderCreate, IncomingOrderRead, OrderHistoryRead # Import schemas
    # !! Need authentication dependency and user model !!
    # from backend.security import get_current_active_merchant # Assuming specific auth per role
    # from backend.database.models import MerchantUser, OrderHistory, IncomingOrder # Import models
    # !! Need services !!
    # from backend.services import order_service, gateway_service # Example service imports
    from backend.utils.exceptions import JivaPayException, AuthorizationError, DatabaseError
    from backend.security import get_current_active_user
    from backend.database.db import Merchant
except ImportError as e:
    # Make error message clearer about location
    raise ImportError(f"Could not import required modules for merchant router (in api_routers/merchant/router.py): {e}")

logger = logging.getLogger(__name__)

def get_current_active_merchant(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Merchant:
    """Retrieve the Merchant profile for the currently authenticated user."""
    merchant = db.query(Merchant).filter_by(user_id=current_user.id).one_or_none()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a merchant")
    return merchant

router = APIRouter()

# --- Order Endpoints --- #

@router.post(
    "/orders",
    response_model=IncomingOrderRead, # Return the created incoming order details
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Incoming Order (PayIn/PayOut request)",
    tags=["Merchant Orders"] # Tags for OpenAPI docs
)
def create_incoming_order(
    order_data: IncomingOrderCreate, # Use the creation schema for input
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant) # Use placeholder auth
):
    """Endpoint for a merchant to initiate a new PayIn or PayOut order."""
    logger.info(f"Merchant {current_merchant.id} creating order. Data: {order_data.dict()}")
    try:
        # TODO: Implement order creation logic
        # 1. Identify merchant store ID (e.g., from current_merchant.store_id)
        # 2. Potentially validate order_data against store settings
        # 3. Call a service function (e.g., gateway_service or order_service) to create IncomingOrder in DB
        #    - incoming_order = gateway_service.create_incoming_order_from_merchant(store_id=current_merchant.store_id, order_data=order_data, db=db)
        # 4. Return the created order details using IncomingOrderRead schema

        # Placeholder implementation:
        logger.warning(f"Order creation logic for merchant {current_merchant.id} is not implemented.")
        # Simulate creation and return dummy data matching the response model
        from datetime import datetime
        dummy_order = {
            "id": 123,
            "merchant_store_id": current_merchant.store_id,
            "amount": order_data.amount,
            "currency_id": order_data.currency_id,
            "payment_method_id": order_data.payment_method_id,
            "direction": order_data.direction,
            "customer_id": order_data.customer_id,
            "return_url": order_data.return_url,
            "callback_url": order_data.callback_url,
            "status": "new", # Placeholder status
            "assigned_order_id": None,
            "failure_reason": None,
            "retry_count": 0,
            "created_at": datetime.utcnow(),
            "last_attempt_at": None
        }
        return dummy_order # Pydantic will validate this dict against IncomingOrderRead

    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except JivaPayException as e:
        # Handle known application errors (e.g., validation errors from service)
        logger.warning(f"App error creating order for merchant {current_merchant.id}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error creating order for merchant {current_merchant.id}: {e}", exc_info=True)
        # report_critical_error(e, context...)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")

@router.get(
    "/orders",
    response_model=List[OrderHistoryRead], # Return a list of orders
    summary="List Merchant's Orders",
    tags=["Merchant Orders"] # Tags for OpenAPI docs
)
def list_merchant_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None, # Example filter
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
):
    """Endpoint to list orders associated with the current merchant."""
    logger.info(f"Merchant {current_merchant.id} listing orders. Skip: {skip}, Limit: {limit}, Status: {status_filter}")
    try:
        # TODO: Implement order listing logic
        # 1. Get merchant store ID
        # 2. Call a service function to query OrderHistory (or IncomingOrder based on need)
        #    - Filter by merchant_store_id
        #    - Apply pagination (skip, limit)
        #    - Apply filters (status_filter, date range, etc.)
        #    - orders = order_service.get_merchant_orders(store_id=current_merchant.store_id, skip=skip, limit=limit, status=status_filter, db=db)
        # 3. Return the list of orders

        # Placeholder implementation:
        logger.warning(f"Order listing logic for merchant {current_merchant.id} is not implemented.")
        return [] # Return empty list

    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DatabaseError as e:
         logger.error(f"DB error listing orders for merchant {current_merchant.id}: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred.")
    except Exception as e:
        logger.error(f"Unexpected error listing orders for merchant {current_merchant.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")

# TODO: Add other merchant endpoints:
# - GET /orders/{order_id} (Get specific order details)
# - POST /orders/{order_id}/confirm_payment (If merchant confirms client payment - depends on flow)
# - GET /balance (Get merchant balance)
# - etc. 