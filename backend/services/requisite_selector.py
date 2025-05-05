"""Service for selecting the most suitable requisite for an incoming order."""

import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

# Attempt to import models, DB utils, and exceptions
try:
    # !! These models need to be defined in backend/database/models.py !!
    from backend.database.models import (
        IncomingOrder, Trader, ReqTrader, FullRequisitesSettings, OrderHistory
    )
    from backend.database.utils import atomic_transaction # Assuming we might update last_used_at within selection
    from backend.utils.exceptions import (
        RequisiteNotFound, LimitExceeded, DatabaseError, OrderProcessingError
    )
except ImportError as e:
    # This service heavily depends on models, raise clearly if they are missing
    raise ImportError(f"Could not import required models or utils for RequisiteSelector: {e}. Ensure models (IncomingOrder, Trader, ReqTrader, FullRequisitesSettings, OrderHistory) are defined.")

logger = logging.getLogger(__name__)


def find_suitable_requisite(
    incoming_order: IncomingOrder, db_session: Session
) -> Tuple[Optional[int], Optional[int]]:
    """Finds the most suitable trader's requisite for a given incoming order.

    Args:
        incoming_order: The IncomingOrder object needing a requisite.
        db_session: The SQLAlchemy session (should be part of the main order processing transaction).

    Returns:
        A tuple containing (requisite_id, trader_id) if found, otherwise (None, None).
        Can raise exceptions like LimitExceeded or DatabaseError.
    """
    logger.info(f"Attempting to find suitable requisite for IncomingOrder ID: {incoming_order.id}")

    # Реальная логика выбора реквизита
    try:
        order_type = incoming_order.order_type
        amount = incoming_order.amount_fiat if order_type == 'pay_in' else incoming_order.amount_crypto
        # Построение запроса для статического выбора
        query = (
            db_session.query(ReqTrader, FullRequisitesSettings)
            .join(Trader, ReqTrader.trader_id == Trader.id)
            .join(FullRequisitesSettings, FullRequisitesSettings.requisite_id == ReqTrader.id)
            .filter(Trader.in_work == True)
            .filter(getattr(FullRequisitesSettings, 'pay_in' if order_type == 'pay_in' else 'pay_out') == True)
            .filter(FullRequisitesSettings.lower_limit <= amount)
            .filter(FullRequisitesSettings.upper_limit >= amount)
            .with_for_update(skip_locked=True)
            .order_by(Trader.trafic_priority.asc(), ReqTrader.last_used_at.asc().nullsfirst())
            .limit(1)
        )
        result = query.one_or_none()
        if not result:
            logger.warning(f"No suitable static candidate found for IncomingOrder ID: {incoming_order.id}")
            return None, None
        req, frs = result
        # Проверка динамических лимитов
        period = timedelta(minutes=frs.turnover_limit_minutes)
        window_start = datetime.utcnow() - period
        total = (
            db_session.query(func.coalesce(
                func.sum(OrderHistory.amount_fiat if order_type == 'pay_in' else OrderHistory.amount_crypto), 0
            ))
            .filter(
                OrderHistory.requisite_id == req.id,
                OrderHistory.created_at >= window_start
            )
            .scalar() or 0
        )
        if total + amount > frs.total_limit:
            logger.warning(f"Dynamic limit exceeded for Requisite ID {req.id} (Order ID: {incoming_order.id})")
            raise LimitExceeded(f"Dynamic limit exceeded for requisite {req.id}", limit_type="dynamic", order_id=incoming_order.id)
        # Обновление last_used_at
        req.last_used_at = datetime.utcnow()
        db_session.flush()
        logger.info(f"Selected Requisite ID {req.id}, Trader ID {req.trader_id} for IncomingOrder ID {incoming_order.id}")
        return req.id, req.trader_id
    except Exception as e:
        logger.error(f"Error finding suitable requisite: {e}", exc_info=True)
        raise DatabaseError(f"Error finding suitable requisite for order {incoming_order.id}: {e}") from e 