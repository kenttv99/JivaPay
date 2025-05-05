from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import logging

from backend.database.utils import get_db_session
from backend.security import get_current_active_user
from backend.database.db import Trader, OrderHistory
from backend.services.order_status_manager import confirm_order_by_trader, cancel_order
from backend.shemas_enums.order import OrderHistoryRead, OrderCancelPayload

logger = logging.getLogger(__name__)


def get_current_active_trader(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Trader:
    """Retrieve the Trader profile for the currently authenticated user."""
    trader = db.query(Trader).filter_by(user_id=current_user.id).one_or_none()
    if not trader:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a trader")
    return trader

router = APIRouter(
    prefix="/trader",
    tags=["Trader Orders"]
)

@router.get(
    "/orders",
    response_model=List[OrderHistoryRead],
    summary="List Trader's Assigned Orders"
)
def list_trader_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_trader: Trader = Depends(get_current_active_trader)
) -> List[OrderHistory]:
    """List orders assigned to the current trader."""
    try:
        query = db.query(OrderHistory).filter_by(trader_id=current_trader.id)
        orders = query.offset(skip).limit(limit).all()
        return orders
    except Exception as e:
        logger.error(f"Error listing orders for trader {current_trader.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not list orders.")

@router.post(
    "/orders/{order_id}/confirm",
    response_model=OrderHistoryRead,
    summary="Confirm order by trader (upload receipt)"
)
async def confirm_trader_order(
    order_id: int,
    receipt_file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_trader: Trader = Depends(get_current_active_trader)
) -> OrderHistory:
    """Trader confirms and uploads receipt for an order."""
    content = await receipt_file.read()
    try:
        updated = confirm_order_by_trader(
            order_id=order_id,
            receipt=content,
            filename=receipt_file.filename,
            trader_id=current_trader.id,
            db_session=db
        )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming order {order_id} by trader {current_trader.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/orders/{order_id}/cancel",
    response_model=OrderHistoryRead,
    summary="Cancel an assigned order by trader"
)
def cancel_trader_order(
    order_id: int,
    payload: OrderCancelPayload,
    db: Session = Depends(get_db_session),
    current_trader: Trader = Depends(get_current_active_trader)
) -> OrderHistory:
    """Trader cancels an order with a reason."""
    try:
        updated = cancel_order(
            order_id=order_id,
            actor=current_trader,
            reason=payload.reason,
            db=db
        )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling order {order_id} by trader {current_trader.id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 