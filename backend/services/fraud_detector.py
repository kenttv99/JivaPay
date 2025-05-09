#!/usr/bin/env python3
"""
Service for fraud detection of incoming orders.
Provides a function to check orders against fraud rules.
"""

import logging
from enum import Enum
from sqlalchemy.orm import Session
from decimal import Decimal
from backend.utils.config_loader import get_typed_config_value

from backend.database.db import IncomingOrder
from backend.utils.exceptions import FraudDetectedError

logger = logging.getLogger(__name__)

class FraudStatus(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_MANUAL_REVIEW = "manual_review"


def check_incoming_order(
    incoming_order: IncomingOrder,
    db_session: Session
) -> FraudStatus:
    """
    Performs fraud checks on the incoming order.

    Args:
        incoming_order: The incoming order to evaluate.
        db_session: The DB session for any lookups.

    Returns:
        A FraudStatus indicating the result.

    Raises:
        FraudDetectedError: For explicit deny or manual review triggers.
    """
    logger.info(f"Running fraud check for IncomingOrder ID: {incoming_order.id}")
    # Fetch thresholds from config
    try:
        manual_threshold = get_typed_config_value("FRAUD_MANUAL_REVIEW_THRESHOLD", db_session, Decimal, default=None)
        deny_threshold = get_typed_config_value("FRAUD_DENY_THRESHOLD", db_session, Decimal, default=None)
    except Exception as e:
        logger.warning(f"Could not load fraud thresholds: {e}. Defaulting to allow.")
        manual_threshold = None
        deny_threshold = None
    amount = getattr(incoming_order, 'amount_fiat', None)
    # Deny if above deny threshold
    if deny_threshold is not None and amount is not None and amount > deny_threshold:
        logger.warning(f"IncomingOrder {incoming_order.id} denied by fraud (>{deny_threshold}).")
        return FraudStatus.DENY
    # Manual review if above manual threshold
    if manual_threshold is not None and amount is not None and amount > manual_threshold:
        logger.info(f"IncomingOrder {incoming_order.id} requires manual review (>{manual_threshold}).")
        return FraudStatus.REQUIRE_MANUAL_REVIEW
    # Default allow
    return FraudStatus.ALLOW 