"""Service for selecting the most suitable requisite for an incoming order."""

import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from decimal import Decimal

from backend.config.logger import get_logger
from backend.utils.query_filters import get_active_trader_filters, get_active_requisite_filters

# Attempt to import models, DB utils, and exceptions
try:
    # !! These models need to be defined in backend/database/models.py !!
    from backend.database.db import (
        IncomingOrder, Trader, ReqTrader, FullRequisitesSettings, OrderHistory, User
    )
    # Assuming atomic_transaction might not be needed if last_used_at is updated within the broader transaction
    # from backend.database.utils import atomic_transaction 
    from backend.utils.exceptions import (
        RequisiteNotFound, LimitExceeded, DatabaseError, OrderProcessingError
    )
except ImportError as e:
    # This service heavily depends on models, raise clearly if they are missing
    raise ImportError(f"Could not import required models or utils for RequisiteSelector: {e}. Ensure models (IncomingOrder, Trader, ReqTrader, FullRequisitesSettings, OrderHistory, User) are defined.")

logger = get_logger(__name__)


def find_suitable_requisite(
    incoming_order: IncomingOrder, db_session: Session
) -> Tuple[Optional[int], Optional[int]]:
    """Finds the most suitable trader's requisite for a given incoming order.

    Considers trader's overall status, teamlead traffic enable status, 
    trader's own work status, and requisite's specific pay_in/pay_out enablement.

    Args:
        incoming_order: The IncomingOrder object needing a requisite.
        db_session: The SQLAlchemy session (should be part of the main order processing transaction).

    Returns:
        A tuple containing (requisite_id, trader_id) if found, otherwise (None, None).
        Can raise exceptions like LimitExceeded or DatabaseError.
    """
    logger.info(f"Attempting to find suitable requisite for IncomingOrder ID: {incoming_order.id}")

    try:
        order_type = incoming_order.order_type
        # Ensure amount is correctly determined based on order type
        if order_type == 'pay_in':
            amount_to_check = incoming_order.amount_fiat
            if amount_to_check is None:
                raise OrderProcessingError(f"Amount_fiat is None for pay_in IncomingOrder ID: {incoming_order.id}")
            requisite_direction_filter = FullRequisitesSettings.pay_in == True
        elif order_type == 'pay_out':
            amount_to_check = incoming_order.amount_crypto
            if amount_to_check is None:
                raise OrderProcessingError(f"Amount_crypto is None for pay_out IncomingOrder ID: {incoming_order.id}")
            requisite_direction_filter = FullRequisitesSettings.pay_out == True
        else:
            raise OrderProcessingError(f"Unknown order_type: {order_type} for IncomingOrder ID: {incoming_order.id}")

        # Base query to find suitable requisites
        query = (
            db_session.query(ReqTrader, FullRequisitesSettings, Trader)
            .join(Trader, ReqTrader.trader_id == Trader.id)
            .join(User, Trader.user_id == User.id) # Join with User to check User.is_active
            .join(FullRequisitesSettings, FullRequisitesSettings.requisite_id == ReqTrader.id)
            .filter(User.is_active == True)  # Trader's main account must be active
            .filter(*get_active_trader_filters()) # Use filters for active trader
            .filter(*get_active_requisite_filters()) # Use filters for active requisite
            .filter(requisite_direction_filter) # Requisite enabled for pay_in or pay_out
            .filter(FullRequisitesSettings.lower_limit <= amount_to_check)
            .filter(FullRequisitesSettings.upper_limit >= amount_to_check)
            .order_by(Trader.trafic_priority.asc(), ReqTrader.last_used_at.asc().nullsfirst()) 
            # .with_for_update(skip_locked=True) # Consider if FOR UPDATE is needed here or at higher level
        )
        
        # Iterate through candidates to check dynamic limits
        # This avoids locking too many rows if the first few fail dynamic checks
        # Using offset and limit(1) in a loop can be an alternative for very high contention scenarios
        # but for now, let's fetch a small batch.
        
        candidates = query.limit(5).all() # Fetch a few candidates to check dynamic limits

        if not candidates:
            logger.warning(f"No suitable static candidate (Trader active, Requisite active & matching limits/direction) found for IncomingOrder ID: {incoming_order.id}")
            return None, None

        selected_requisite: Optional[ReqTrader] = None
        selected_trader: Optional[Trader] = None

        for req, frs, trader_profile in candidates:
            # Check dynamic limits (turnover)
            # Ensure datetime.utcnow() is used if DB stores naive UTC, or use timezone-aware datetimes consistently.
            # For this example, assuming naive UTC as per db.py utcnow() if it were used here.
            now_utc = datetime.utcnow() # Naive UTC datetime
            period_start = now_utc - timedelta(minutes=frs.turnover_limit_minutes)

            # Determine which amount to sum based on order type
            amount_field_to_sum = OrderHistory.amount_fiat if order_type == 'pay_in' else OrderHistory.amount_crypto

            current_turnover = (
                db_session.query(func.sum(amount_field_to_sum))
                .filter(
                    OrderHistory.requisite_id == req.id,
                    OrderHistory.status == 'completed', # Only count completed orders for turnover
                    OrderHistory.created_at >= period_start,
                    OrderHistory.created_at < now_utc # Ensure it's within the window precisely
                )
                .scalar()
            ) or Decimal('0.00') # Ensure Decimal for calculations
            
            logger.debug(f"Checking dynamic limit for Requisite ID {req.id}: Current turnover {current_turnover}, Amount to check {amount_to_check}, Total limit {frs.total_limit}")

            if (current_turnover + amount_to_check) <= frs.total_limit:
                # Check daily limit if applicable (this logic might need more precise definition)
                # For simplicity, a basic daily check (can be improved with date functions for specific timezones)
                today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
                daily_turnover = (
                    db_session.query(func.sum(amount_field_to_sum))
                    .filter(
                        OrderHistory.requisite_id == req.id,
                        OrderHistory.status == 'completed',
                        OrderHistory.created_at >= today_start,
                        OrderHistory.created_at < now_utc
                    )
                    .scalar()
                ) or Decimal('0.00')

                logger.debug(f"Checking daily limit for Requisite ID {req.id}: Current daily turnover {daily_turnover}, Amount to check {amount_to_check}, Daily max {frs.turnover_day_max}")
                if (daily_turnover + amount_to_check) <= frs.turnover_day_max:
                    selected_requisite = req
                    selected_trader = trader_profile # This is the Trader object from the join
                    break # Found a suitable requisite
                else:
                    logger.info(f"Daily turnover limit exceeded for Requisite ID {req.id} for IncomingOrder ID: {incoming_order.id}")    
            else:
                logger.info(f"Rolling turnover limit exceeded for Requisite ID {req.id} for IncomingOrder ID: {incoming_order.id}")

        if selected_requisite and selected_trader:
            # Lock the selected requisite and trader for update of last_used_at
            # This should be done carefully to avoid deadlocks
            # It might be better to handle the lock at the order_processor level if this requisite is chosen
            # For now, we assume the calling transaction handles the overall locking strategy.
            try:
                # Re-fetch with FOR UPDATE if not already locked by the initial query (if with_for_update was removed/conditional)
                # db_session.query(ReqTrader).filter(ReqTrader.id == selected_requisite.id).with_for_update().one()
                
                selected_requisite.last_used_at = datetime.utcnow() # Naive UTC
                db_session.add(selected_requisite)
                # db_session.flush() # Flush is often part of commit or handled by session autoflush
                logger.info(f"Selected Requisite ID {selected_requisite.id}, Trader ID {selected_trader.id} for IncomingOrder ID: {incoming_order.id}")
                return selected_requisite.id, selected_trader.id
            except Exception as e_lock_update: # More specific exceptions can be caught
                logger.error(f"Error locking/updating requisite {selected_requisite.id}: {e_lock_update}", exc_info=True)
                db_session.rollback() # Rollback this specific attempt if part of a sub-transaction or handle at higher level
                raise DatabaseError(f"Error updating requisite {selected_requisite.id} for order {incoming_order.id}") from e_lock_update
        else:
            logger.warning(f"No suitable candidate found after checking dynamic limits for IncomingOrder ID: {incoming_order.id}")
            return None, None

    except LimitExceeded: # Re-raise if it was a dynamic limit from our checks (though not explicitly raised above yet)
        raise
    except OrderProcessingError as ope:
        logger.error(f"Order processing error in requisite selection for order {incoming_order.id}: {ope}", exc_info=True)
        raise # Re-raise to be handled by order processor
    except Exception as e:
        logger.error(f"Unexpected error finding suitable requisite for order {incoming_order.id}: {e}", exc_info=True)
        # Avoid raising generic Exception; wrap in a custom one if possible
        raise DatabaseError(f"Unexpected error finding suitable requisite for order {incoming_order.id}: {e}") from e 