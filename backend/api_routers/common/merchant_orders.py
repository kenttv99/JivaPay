from fastapi import APIRouter, Depends
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
):
    """List orders associated with the current merchant."""
    query = db.query(OrderHistory).filter_by(merchant_id=current_merchant.id)
    if status_filter:
        query = query.filter(OrderHistory.status == status_filter)
    return query.offset(skip).limit(limit).all()

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