"""Service for selecting the most suitable requisite for an incoming order."""

import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime

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

    # TODO: Implement Requisite Selection Logic based on README_IMPLEMENTATION_PLAN.md 3.3
    # ---------------------------------------------------------------------------

    # 1. Construct Base Query:
    #    - SELECT ReqTrader.full_requisite_id, ReqTrader.trader_id
    #    - FROM ReqTrader
    #    - JOIN Trader ON Trader.id = ReqTrader.trader_id
    #    - JOIN FullRequisitesSettings ON FullRequisitesSettings.id = ReqTrader.full_requisite_id
    #    - WHERE conditions:
    #        - ReqTrader.is_active = True
    #        - Trader.is_active = True
    #        - FullRequisitesSettings.is_active = True
    #        - FullRequisitesSettings.direction = incoming_order.direction (or map enum)
    #        - FullRequisitesSettings.payment_method_id = incoming_order.payment_method_id
    #        - FullRequisitesSettings.currency_id = incoming_order.currency_id
    #        - FullRequisitesSettings.min_amount <= incoming_order.amount
    #        - FullRequisitesSettings.max_amount >= incoming_order.amount
    #        - FullRequisitesSettings.merchant_store_id = incoming_order.store_id (or maybe filter later? Check plan)
    #        - (Add any other static filters based on ReqTrader or FullRequisitesSettings)

    # 2. Apply Sorting:
    #    - ORDER BY
    #        - Trader.trafic_priority ASC, # Lower number = higher priority
    #        - ReqTrader.last_used_at ASC NULLS FIRST # Round-robin within the same priority

    # 3. Apply Locking and Limit:
    #    - .with_for_update(skip_locked=True)
    #    - .limit(1)

    # 4. Execute Query:
    #    - candidate = db_session.execute(query).first() # Or .one_or_none()

    # 5. Handle No Candidate Found:
    #    - if not candidate:
    #        - logger.warning(f"No suitable static candidate found for IncomingOrder ID: {incoming_order.id}")
    #        - # Option 1: Return None, None (Caller handles status update)
    #        - return None, None
    #        - # Option 2: Raise RequisiteNotFound (Requires try...except in caller)
    #        - # raise RequisiteNotFound(f"No static candidate found for order {incoming_order.id}")

    # 6. Extract IDs:
    #    - requisite_id = candidate.full_requisite_id
    #    - trader_id = candidate.trader_id
    #    - logger.info(f"Found static candidate for IncomingOrder ID {incoming_order.id}: Requisite ID {requisite_id}, Trader ID {trader_id}")

    # 7. Check Dynamic Limits (within the same transaction):
    #    - Query OrderHistory for the selected `requisite_id`:
    #        - Sum `amount` for orders within the dynamic limit period (e.g., last 24h, current month).
    #        - Compare sum + incoming_order.amount against FullRequisitesSettings.dynamic_limit_period_amount.
    #    - If limits exceeded:
    #        - logger.warning(f"Dynamic limit exceeded for Requisite ID {requisite_id} (Order ID: {incoming_order.id})")
    #        - # Option 1: Return None, None (Caller handles status update, maybe retry logic needs adjustment)
    #        - return None, None
    #        - # Option 2: Raise LimitExceeded (Requires try...except in caller)
    #        - # raise LimitExceeded(f"Dynamic limit exceeded for requisite {requisite_id}", limit_type="dynamic", order_id=incoming_order.id)
    #        - # Option 3: Potentially try the *next* candidate (more complex query/loop)

    # 8. Update last_used_at (if selection is final here):
    #    - Get the ReqTrader object: req_trader = db_session.get(ReqTrader, (requisite_id, trader_id)) # Assuming composite PK
    #    - if req_trader:
    #        - req_trader.last_used_at = datetime.utcnow()
    #        - db_session.add(req_trader)
    #        - db_session.flush() # Ensure update happens before returning
    #    - else: # Should not happen if candidate was found
    #        - logger.error(f"Could not find ReqTrader for Requisite ID {requisite_id}, Trader ID {trader_id} after selection!")
    #        - raise DatabaseError("Inconsistency: ReqTrader not found after selection.")

    # 9. Return Success:
    #    - logger.info(f"Successfully selected Requisite ID {requisite_id}, Trader ID {trader_id} for IncomingOrder ID {incoming_order.id}")
    #    - return requisite_id, trader_id

    # --- Placeholder Return --- #
    logger.warning(f"Requisite selection logic for IncomingOrder ID {incoming_order.id} is not implemented yet.")
    # Returning None, None as a default placeholder behavior
    return None, None 