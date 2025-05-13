from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database.utils import get_db_session
from backend.database.db import Trader, OrderHistory
from backend.services.order_status_manager import confirm_order_by_trader, cancel_order
from backend.schemas_enums.order import OrderHistoryRead, OrderCancelPayload
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_trader

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/",
    response_model=List[OrderHistoryRead],
    dependencies=[Depends(permission_required("trader_orders:read"))]
)
def list_trader_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_trader: Trader = Depends(get_current_active_trader)
) -> List[OrderHistory]:
    """List orders assigned to the current trader."""
    return db.query(OrderHistory).filter_by(trader_id=current_trader.id).offset(skip).limit(limit).all()

@router.post(
    "/{order_id}/confirm",
    response_model=OrderHistoryRead,
    dependencies=[Depends(permission_required("trader_orders:confirm"))]
)
async def confirm_trader_order(
    order_id: int,
    receipt_file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_trader: Trader = Depends(get_current_active_trader)
) -> OrderHistoryRead:
    """Trader confirms and uploads receipt for an order."""
    return confirm_order_by_trader(
        order_id=order_id,
        receipt=await receipt_file.read(),
        filename=receipt_file.filename,
        trader_id=current_trader.id,
        db_session=db
    )

@router.post(
    "/{order_id}/cancel",
    response_model=OrderHistoryRead,
    dependencies=[Depends(permission_required("trader_orders:cancel"))]
)
def cancel_trader_order(
    order_id: int,
    payload: OrderCancelPayload,
    db: Session = Depends(get_db_session),
    current_trader: Trader = Depends(get_current_active_trader)
) -> OrderHistoryRead:
    """Trader cancels an order with a reason."""
    return cancel_order(
        order_id=order_id,
        actor=current_trader,
        reason=payload.reason,
        db=db
    ) 