"""Service for orchestrating the processing of incoming orders."""

import logging
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select

# Attempt to import models, DB utils, other services, and exceptions
try:
    # !! Models needed: IncomingOrder, OrderHistory, etc. !!
    from backend.database.db import IncomingOrder, OrderHistory # Add others as needed
    from backend.database.utils import get_db_session, atomic_transaction, create_object, update_object_db
    from backend.utils.exceptions import (
        RequisiteNotFound, LimitExceeded, OrderProcessingError, DatabaseError, ConfigurationError, FraudDetectedError # Add others
    )
    from backend.utils.notifications import report_critical_error
    # !! Services needed: requisite_selector, balance_manager, fraud_detector (when created) !!
    from backend.services import requisite_selector, balance_manager, fraud_detector
    from backend.services.fraud_detector import FraudStatus
    # !! Need config loader for retries !!
    from backend.utils.config_loader import get_typed_config_value
except ImportError as e:
    raise ImportError(f"Could not import required modules for OrderProcessor: {e}. Ensure models and other services are available.")

logger = logging.getLogger(__name__)

def process_incoming_order(incoming_order_id: int):
    """Processes a single incoming order by finding a requisite and creating an OrderHistory record.

    Handles idempotency, transaction management, and status updates on failure.

    Args:
        incoming_order_id: The ID of the IncomingOrder to process.

    Raises:
        Propagates exceptions like DatabaseError if status update fails critically.
        Other exceptions during processing (like RequisiteNotFound, LimitExceeded) are
        generally caught and result in status updates for the IncomingOrder.
    """
    logger.info(f"Starting processing for IncomingOrder ID: {incoming_order_id}")
    # 1. Idempotency check: skip if already processed or not in correct status
    with get_db_session() as db_check:
        existing = db_check.query(OrderHistory).filter(OrderHistory.incoming_order_id == incoming_order_id).one_or_none()
        if existing:
            logger.warning(f"OrderHistory already exists for IncomingOrder ID {incoming_order_id}. Skipping.")
            return
        inc = db_check.query(IncomingOrder).filter(IncomingOrder.id == incoming_order_id).one_or_none()
        if not inc or inc.status not in ['new', 'retrying']:
            logger.warning(f"IncomingOrder {incoming_order_id} status '{inc.status if inc else None}' invalid for processing. Skipping.")
            return

    failure_reason: str | None = None
    processing_exception: Exception | None = None
    assigned_requisite_id: int | None = None
    assigned_trader_id: int | None = None

    # 2. Main processing transaction
    try:
        with get_db_session() as db_main:
            with atomic_transaction(db_main):
                # 2.1 Load and lock the incoming order
                incoming_order = (
                    db_main.query(IncomingOrder)
                    .filter(IncomingOrder.id == incoming_order_id)
                    .with_for_update()
                    .one_or_none()
                )
                if not incoming_order:
                    raise OrderProcessingError(f"IncomingOrder not found: {incoming_order_id}")
                # 2.2 Fraud detection
                fraud_status = FraudStatus.ALLOW
                try:
                    fraud_status = fraud_detector.check_incoming_order(incoming_order, db_main)
                except FraudDetectedError as fe:
                    fraud_status = fe.limit_type if hasattr(fe, 'limit_type') else FraudStatus.DENY
                if fraud_status == FraudStatus.DENY:
                    incoming_order.status = 'failed'
                    db_main.flush()
                    raise FraudDetectedError("Order denied by fraud detector.", order_id=incoming_order_id)
                if fraud_status == FraudStatus.REQUIRE_MANUAL_REVIEW:
                    incoming_order.status = 'retrying'
                    incoming_order.retry_count = (incoming_order.retry_count or 0) + 1
                    db_main.flush()
                    raise FraudDetectedError("Order requires manual fraud review.", order_id=incoming_order_id)
                # 2.3 Select requisite
                req_id, trader_id = requisite_selector.find_suitable_requisite(incoming_order, db_main)
                if not req_id or not trader_id:
                    raise RequisiteNotFound(f"No suitable requisite found for order {incoming_order_id}")
                # 2.4 Calculate commissions (IncomingOrder ещё не содержит trader_id, поэтому передаём явным аргументом)
                store_comm, trader_comm = balance_manager.calculate_commissions(
                    incoming_order,
                    db_main,
                    trader_id=trader_id,
                )
                # 2.5 Create OrderHistory record
                oh_data = {
                    'incoming_order_id': incoming_order.id,
                    'hash_id': uuid.uuid4().hex,  # generated unique hash
                    'trader_id': trader_id,
                    'requisite_id': req_id,
                    'merchant_id': incoming_order.merchant_id,
                    'gateway_id': incoming_order.gateway_id,
                    'store_id': incoming_order.store_id,
                    'method_id': incoming_order.target_method_id,
                    'bank_id': incoming_order.target_bank_id,
                    'crypto_currency_id': incoming_order.crypto_currency_id,
                    'fiat_id': incoming_order.fiat_currency_id,
                    'order_type': incoming_order.order_type,
                    'exchange_rate': incoming_order.exchange_rate,
                    'amount_currency': incoming_order.amount_crypto or Decimal('0'),
                    'total_fiat': incoming_order.amount_fiat or Decimal('0'),
                    'store_commission': store_comm,
                    'trader_commission': trader_comm,
                    'status': 'pending'
                }
                new_oh = create_object(db_main, OrderHistory, oh_data)
                # 2.6 Update incoming order status
                update_object_db(db_main, incoming_order, {
                    'status': 'assigned',
                    'retry_count': incoming_order.retry_count or 0
                })
                logger.info(f"Processed IncomingOrder {incoming_order_id}, created OrderHistory ID {new_oh.id}")

    except (RequisiteNotFound, LimitExceeded, FraudDetectedError, ConfigurationError, OrderProcessingError, DatabaseError) as e:
        # Catch expected processing errors from within the transaction
        logger.warning(f"Processing failed for IncomingOrder ID {incoming_order_id} due to {type(e).__name__}: {e}")
        processing_exception = e
        failure_reason = str(e)[:255] # Truncate reason for DB

    except Exception as e:
        # Catch unexpected errors during the main transaction
        logger.error(f"Unexpected error during processing of IncomingOrder ID {incoming_order_id}. Error: {e}", exc_info=True)
        processing_exception = e
        failure_reason = f"Unexpected error: {str(e)[:200]}"
        # Report unexpected errors immediately
        report_critical_error(e, context_message="Unexpected error in order processor main transaction", incoming_order_id=incoming_order_id)

    # --- 3. Status Update on Failure (runs if an exception occurred above) --- #
    if processing_exception:
        logger.info(f"Attempting to update status for failed IncomingOrder ID: {incoming_order_id}")
        # Update status (retrying or failed) reliably in separate transaction
        try:
            with get_db_session() as db_status:
                with atomic_transaction(db_status):
                    order_to_update = db_status.query(IncomingOrder).filter_by(id=incoming_order_id).one_or_none()
                    if not order_to_update:
                        raise DatabaseError(f"IncomingOrder {incoming_order_id} not found during status update.")
                    # Determine new status based on retry count
                    max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db_status, int, default=3)
                    current_retries = (order_to_update.retry_count or 0)
                    next_retries = current_retries + 1
                    new_status = "retrying" if next_retries < max_retries else "failed"
                    update_data = {
                        'status': new_status,
                        'failure_reason': failure_reason,
                        'retry_count': next_retries,
                        'last_attempt_at': datetime.utcnow()
                    }
                    update_object_db(db_status, order_to_update, update_data)
                    logger.info(f"IncomingOrder {incoming_order_id} status updated to '{new_status}' with reason: {failure_reason}")
        except Exception as status_update_exc:
            logger.critical(
                f"CRITICAL: Could not update status for IncomingOrder ID {incoming_order_id} after failure: {status_update_exc}",
                exc_info=True
            )
            report_critical_error(
                status_update_exc,
                context_message="Failed to update order status after processing failure",
                incoming_order_id=incoming_order_id,
                original_error=str(processing_exception)
            )
            raise status_update_exc 