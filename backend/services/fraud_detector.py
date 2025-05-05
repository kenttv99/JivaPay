#!/usr/bin/env python3
"""
Service for fraud detection of incoming orders.
Provides a function to check orders against fraud rules.
"""

import logging
from enum import Enum
from sqlalchemy.orm import Session

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
    # TODO: Implement actual fraud detection rules
    # Example: check order.amount_fiat > threshold -> REQUIRE_MANUAL_REVIEW
    # For now, allow all
    return FraudStatus.ALLOW 