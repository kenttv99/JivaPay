#!/usr/bin/env python3
"""
Service for fraud detection of incoming orders.
Provides a function to check orders against fraud rules.
"""

import logging
from enum import Enum
from decimal import Decimal
import asyncio # Added for potential to_thread if needed later
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession # Changed from sqlalchemy.orm import Session

from backend.utils.config_loader import get_typed_config_value # Assuming this can work or be adapted for async context
from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions # Decorator is already async-aware

from backend.database.db import IncomingOrder
from backend.utils.exceptions import FraudDetectedError

logger = get_logger(__name__)
SERVICE_NAME = "fraud_detector_async"

class FraudStatus(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_MANUAL_REVIEW = "manual_review"

@handle_service_exceptions(logger, service_name=SERVICE_NAME) # Uncommented and applied
async def check_incoming_order_async(
    incoming_order: IncomingOrder,
    # db_session: AsyncSession, # db_session might not be needed if config values are fetched without it or get_typed_config_value is adapted
    # If get_typed_config_value requires a session, it should be an AsyncSession.
    # For this example, we assume it can work without a session or with an adapted one for these specific keys.
    # If it needs a sync session, we'd have to use asyncio.to_thread, which is less ideal.
    # Let's assume for now that config values can be retrieved without a direct session pass here,
    # or that `get_typed_config_value` can be made to work with an AsyncSession if passed one.
    # For ultimate clarity, this function could receive thresholds as arguments instead of fetching them internally.
    # For this refactoring, we assume thresholds are passed in or can be fetched simply.
    # If they are not passed, the function relies on them being None initially.
    # A more robust solution would require clarity on get_typed_config_value.
    # For simplicity in this step, assuming they are passed or are globally available/simply fetched.
    # Let's stick to the passed arguments for now for better testability and async purity.
    manual_threshold_config: Optional[Decimal] = None, # Thresholds could be passed in
    deny_threshold_config: Optional[Decimal] = None
) -> FraudStatus:
    """
    Performs fraud checks on the incoming order asynchronously.

    Args:
        incoming_order: The incoming order to evaluate.
        manual_threshold_config: Pre-fetched manual review threshold.
        deny_threshold_config: Pre-fetched deny threshold.
        # db_session: AsyncSession if get_typed_config_value needs it and is async.

    Returns:
        A FraudStatus indicating the result.

    Raises:
        FraudDetectedError: For explicit deny or manual review triggers.
    """
    # The following log is now handled by the decorator if DEBUG is enabled for it.
    # logger.info(f"Running async fraud check for IncomingOrder ID: {incoming_order.id}") 
    
    manual_threshold = manual_threshold_config
    deny_threshold = deny_threshold_config

    if manual_threshold is None or deny_threshold is None:
        # This specific warning might be better inside the decorator or as a separate log if thresholds are critical
        logger.warning("Fraud thresholds not provided to check_incoming_order_async. This might lead to all checks passing.")

    amount = getattr(incoming_order, 'amount_fiat', None)

    if amount is None:
        # This log is fine as it's specific to a condition leading to an exception
        logger.warning(f"IncomingOrder {incoming_order.id} has no amount_fiat. Flagging for manual review.")
        raise FraudDetectedError(f"Order {incoming_order.id} has no amount_fiat, requires manual review.", limit_type=FraudStatus.REQUIRE_MANUAL_REVIEW)

    if deny_threshold is not None and amount > deny_threshold:
        logger.warning(f"IncomingOrder {incoming_order.id} denied by fraud (>{deny_threshold}).")
        raise FraudDetectedError(f"Order {incoming_order.id} denied by fraud amount > {deny_threshold}.", limit_type=FraudStatus.DENY)

    if manual_threshold is not None and amount > manual_threshold:
        logger.info(f"IncomingOrder {incoming_order.id} requires manual review (>{manual_threshold}).")
        raise FraudDetectedError(f"Order {incoming_order.id} requires manual review amount > {manual_threshold}.", limit_type=FraudStatus.REQUIRE_MANUAL_REVIEW)

    return FraudStatus.ALLOW 