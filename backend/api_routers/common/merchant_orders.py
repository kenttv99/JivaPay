from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any
import logging

from backend.database.utils import get_db_session
from backend.database.db import Merchant, OrderHistory
from backend.services.gateway_service import handle_init_request
from backend.services.order_status_manager import confirm_payment_by_client as confirm_payment_service
from backend.schemas_enums.order import IncomingOrderCreate, IncomingOrderRead, OrderHistoryRead
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_merchant
from backend.services import order_service
from backend.utils.exceptions import AuthorizationError

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/",
    response_model=IncomingOrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required("merchant_orders:create"))]
)
def create_incoming_order(
    order_data: IncomingOrderCreate,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Create a new Incoming Order (PayIn/PayOut request)."""
    logger.info(f"Merchant {current_merchant.id} creating order. Data: {order_data.dict()}")
    merchant_store = current_merchant.stores[0]
    direction_str = order_data.direction.value.replace('_', '').upper()
    return handle_init_request(
        api_key=merchant_store.public_api_key,
        request_data=order_data,
        direction=direction_str,
        db=db
    )

@router.get(
    "/",
    response_model=List[OrderHistoryRead],
    dependencies=[Depends(permission_required("merchant_orders:read"))]
)
def list_merchant_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
) -> List[OrderHistoryRead]:
    """List orders associated with the current merchant by calling the service layer."""
    try:
        orders = order_service.get_orders_for_merchant(
            session=db,
            current_merchant_user=current_merchant,
            skip=skip,
            limit=limit,
            status_filter=status_filter
        )
        return [OrderHistoryRead.from_orm(order) for order in orders]
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in common list_merchant_orders: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing merchant orders.")

@router.post(
    "/{order_id}/confirm_payment",
    response_model=OrderHistoryRead,
    dependencies=[Depends(permission_required("merchant_orders:confirm"))]
)
async def confirm_payment(
    order_id: int,
    receipt_file: Any,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
) -> OrderHistoryRead:
    """Merchant confirms client payment and uploads receipt for the order."""
    return confirm_payment_service(
        order_id=order_id,
        receipt=await receipt_file.read(),
        filename=receipt_file.filename,
        db_session=db
    ) 