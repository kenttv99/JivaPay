from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database.utils import get_db_session
from backend.database.db import OrderHistory
from backend.schemas_enums.order import OrderHistoryRead
from backend.common.permissions import permission_required
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Payload for support updates
class SupportUpdatePayload(BaseModel):
    status: str
    cancellation_reason: str = None

@router.get(
    "/orders",
    response_model=List[OrderHistoryRead],
    dependencies=[Depends(permission_required("support_orders:read"))]
)
def list_orders(
    db: Session = Depends(get_db_session)
):
    """List all orders for support."""
    return db.query(OrderHistory).all()

@router.patch(
    "/orders/{order_id}",
    response_model=OrderHistoryRead,
    dependencies=[Depends(permission_required("support_orders:update"))]
)
def update_order(
    order_id: int,
    payload: SupportUpdatePayload,
    db: Session = Depends(get_db_session)
):
    """Support updates status or cancellation reason of an order."""
    order = db.query(OrderHistory).filter_by(id=order_id).one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if payload.status:
        order.status = payload.status
    if payload.cancellation_reason:
        order.cancellation_reason = payload.cancellation_reason
    db.commit()
    logger.info(f"Support updated order {order_id}: status={order.status}")
    return order 