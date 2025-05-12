"""API Router for Merchant operations."""

import logging
from typing import List, Optional, Any # Any for placeholder user model

from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from sqlalchemy.orm import Session, selectinload

# Attempt imports (adjusting paths based on new location)
try:
    from backend.database.utils import get_db_session, create_object, update_object_db
    from backend.shemas_enums.order import IncomingOrderCreate, IncomingOrderRead, OrderHistoryRead # Import schemas
    # !! Need authentication dependency and user model !!
    # from backend.security import get_current_active_merchant # Assuming specific auth per role
    # from backend.database.models import MerchantUser, OrderHistory, IncomingOrder # Import models
    # !! Need services !!
    # from backend.services import order_service, gateway_service # Example service imports
    from backend.utils.exceptions import JivaPayException, AuthorizationError, DatabaseError
    from backend.security import get_current_active_user
    from backend.database.db import Merchant, OrderHistory, MerchantStore
    from backend.services.gateway_service import handle_init_request
    from backend.services.order_status_manager import confirm_payment_by_client as confirm_payment_service
    from backend.shemas_enums.merchant import MerchantStoreCreate, MerchantStoreRead, MerchantStoreUpdate
    import secrets
except ImportError as e:
    # Make error message clearer about location
    raise ImportError(f"Could not import required modules for merchant router (in api_routers/merchant/router.py): {e}")

logger = logging.getLogger(__name__)

def get_current_active_merchant(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Merchant:
    """Retrieve the Merchant profile for the currently authenticated user."""
    merchant = db.query(Merchant).options(selectinload(Merchant.stores)).filter_by(user_id=current_user.id).one_or_none()
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
        # Identify merchant's store (assumes single store per merchant)
        merchant_store = current_merchant.stores[0]
        # Convert direction to gateway format (e.g., PAYIN or PAYOUT)
        direction_str = order_data.direction.value.replace('_', '').upper()
        # Delegate to gateway service
        created_order = handle_init_request(
            api_key=merchant_store.public_api_key,
            request_data=order_data,
            direction=direction_str,
            db=db
        )
        return created_order

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
        # Query OrderHistory for this merchant
        query = db.query(OrderHistory).filter_by(merchant_id=current_merchant.id)
        if status_filter:
            query = query.filter(OrderHistory.status == status_filter)
        orders = query.offset(skip).limit(limit).all()
        return orders

    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DatabaseError as e:
         logger.error(f"DB error listing orders for merchant {current_merchant.id}: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred.")
    except Exception as e:
        logger.error(f"Unexpected error listing orders for merchant {current_merchant.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred.")

# --- Client Payment Confirmation Endpoint --- #
@router.post(
    "/orders/{order_id}/confirm_payment",
    response_model=OrderHistoryRead,
    summary="Confirm payment by client and upload receipt",
    tags=["Merchant Orders"]
)
async def confirm_payment_by_client(
    order_id: int,
    receipt_file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
) -> OrderHistoryRead:
    """Merchant confirms client payment and uploads receipt for the order."""
    content = await receipt_file.read()
    try:
        updated_order = confirm_payment_service(
            order_id=order_id,
            receipt=content,
            filename=receipt_file.filename,
            db_session=db
        )
        return updated_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment for order {order_id} by merchant {current_merchant.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Add merchant store management endpoints
@router.post(
    "/stores",
    response_model=MerchantStoreRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store for the current merchant",
    tags=["Merchant Stores"]
)
def create_store(
    store_data: MerchantStoreCreate,
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
):
    """Create a new store for the current merchant."""
    logger.info(f"Merchant {current_merchant.id} creating store. Data: {store_data.dict()}")
    try:
        public_key = secrets.token_urlsafe(32)
        private_key = secrets.token_urlsafe(64)
        data = store_data.dict()
        data.update({
            "merchant_id": current_merchant.id,
            "public_api_key": public_key,
            "private_api_key": private_key
        })
        new_store = create_object(db, MerchantStore, data)
        db.commit()
        return new_store
    except Exception as e:
        logger.error(f"Error creating store for merchant {current_merchant.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/stores",
    response_model=List[MerchantStoreRead],
    summary="List stores for the current merchant",
    tags=["Merchant Stores"]
)
def list_stores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
):
    """List stores for the current merchant."""
    stores = db.query(MerchantStore).filter_by(merchant_id=current_merchant.id).offset(skip).limit(limit).all()
    return stores

@router.get(
    "/stores/{store_id}",
    response_model=MerchantStoreRead,
    summary="Get details of a specific store",
    tags=["Merchant Stores"]
)
def get_store(
    store_id: int,
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
):
    """Get details of a specific store."""
    store = db.query(MerchantStore).filter_by(id=store_id, merchant_id=current_merchant.id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store

@router.patch(
    "/stores/{store_id}",
    response_model=MerchantStoreRead,
    summary="Update settings of an existing store",
    tags=["Merchant Stores"]
)
def update_store(
    store_id: int,
    store_update: MerchantStoreUpdate,
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
):
    """Update settings of an existing store."""
    store = db.query(MerchantStore).filter_by(id=store_id, merchant_id=current_merchant.id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    try:
        update_data = store_update.dict(exclude_unset=True)
        updated = update_object_db(db, store, update_data)
        db.commit()
        return updated
    except Exception as e:
        logger.error(f"Error updating store {store_id} for merchant {current_merchant.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete(
    "/stores/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a store for the current merchant",
    tags=["Merchant Stores"]
)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db_session),
    current_merchant: Any = Depends(get_current_active_merchant)
):
    """Delete a store for the current merchant."""
    store = db.query(MerchantStore).filter_by(id=store_id, merchant_id=current_merchant.id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    try:
        db.delete(store)
        db.commit()
    except Exception as e:
        logger.error(f"Error deleting store {store_id} for merchant {current_merchant.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# TODO: Add other merchant endpoints: