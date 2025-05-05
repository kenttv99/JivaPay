"""Service for orchestrating the processing of incoming orders."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

# Attempt to import models, DB utils, other services, and exceptions
try:
    # !! Models needed: IncomingOrder, OrderHistory, etc. !!
    from backend.database.models import IncomingOrder, OrderHistory # Add others as needed
    from backend.database.utils import get_db_session, atomic_transaction, create_object, update_object_db
    from backend.utils.exceptions import (
        RequisiteNotFound, LimitExceeded, OrderProcessingError, DatabaseError, ConfigurationError, FraudDetectedError # Add others
    )
    from backend.utils.notifications import report_critical_error
    # !! Services needed: requisite_selector, balance_manager, fraud_detector (when created) !!
    from backend.services import requisite_selector, balance_manager #, fraud_detector
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

    # --- 1. Idempotency Check (before main transaction) --- # 
    # Check if an OrderHistory already exists for this incoming_order_id
    # Or if the IncomingOrder status is already 'assigned', 'completed', 'failed' etc.
    # TODO: Implement idempotency check
    # Example:
    # with get_db_session() as db_check:
    #     existing_order_history = db_check.query(OrderHistory).filter(OrderHistory.incoming_order_id == incoming_order_id).first()
    #     if existing_order_history:
    #         logger.warning(f"OrderHistory already exists for IncomingOrder ID {incoming_order_id}. Skipping processing.")
    #         return
    #     inc_order_status = db_check.query(IncomingOrder.status).filter(IncomingOrder.id == incoming_order_id).scalar()
    #     if inc_order_status not in ['new', 'retrying']: # Use Enums
    #          logger.warning(f"IncomingOrder ID {incoming_order_id} has status {inc_order_status}. Skipping processing.")
    #          return
    logger.debug(f"Idempotency check passed for IncomingOrder ID: {incoming_order_id}")

    failure_reason: str | None = None
    processing_exception: Exception | None = None
    assigned_requisite_id: int | None = None
    assigned_trader_id: int | None = None

    # --- 2. Main Processing Logic (within an atomic transaction) --- #
    try:
        with get_db_session() as db_main:
            with atomic_transaction(db_main):
                # TODO: Implement Main Processing Logic based on README_IMPLEMENTATION_PLAN.md 3.3
                # --------------------------------------------------------------------------------

                # 2.1 Load IncomingOrder with lock
                # incoming_order = db_main.query(IncomingOrder).filter(IncomingOrder.id == incoming_order_id).with_for_update().one_or_none()
                # if not incoming_order:
                #     raise OrderProcessingError(f"IncomingOrder not found: {incoming_order_id}") # This specific error will likely abort before status update

                # 2.2 Check Status
                # if incoming_order.status not in ['new', 'retrying']: # Use Enums
                #     logger.warning(f"IncomingOrder {incoming_order_id} status changed before processing ({incoming_order.status}). Aborting.")
                #     # Exit transaction cleanly, idempotency check should have caught this but double-check
                #     return

                # !! Placeholder: Need the actual incoming_order object for next steps !!
                # !! Remove this placeholder load once the real load+lock is implemented !!
                incoming_order = db_main.get(IncomingOrder, incoming_order_id)
                if not incoming_order: raise OrderProcessingError(f"IncomingOrder not found: {incoming_order_id}")

                # 2.3 Call Fraud Detector (TODO: Create fraud_detector service)
                # fraud_result = fraud_detector.check_incoming_order(incoming_order, db_main)
                # if fraud_result == FraudStatus.DENY:
                #     raise FraudDetectedError("Denied by fraud detector", reason="specific rule", order_id=incoming_order_id)
                # if fraud_result == FraudStatus.REQUIRE_MANUAL_REVIEW:
                #     raise FraudDetectedError("Requires manual review by fraud detector", reason="specific rule", order_id=incoming_order_id)
                logger.debug(f"Fraud check passed (placeholder) for IncomingOrder ID: {incoming_order_id}")

                # 2.4 Find Requisite
                # req_id, trad_id = requisite_selector.find_suitable_requisite(incoming_order, db_main)
                # assigned_requisite_id = req_id
                # assigned_trader_id = trad_id
                # if not assigned_requisite_id or not assigned_trader_id:
                #     raise RequisiteNotFound(f"No suitable requisite found for order {incoming_order_id}")
                # !! Using placeholder values !!
                assigned_requisite_id = 1 # Placeholder
                assigned_trader_id = 1 # Placeholder
                logger.info(f"Requisite found (placeholder) for {incoming_order_id}: Req={assigned_requisite_id}, Trader={assigned_trader_id}")

                # 2.5 Calculate Commissions (only needed if stored on OrderHistory)
                # store_comm, trader_comm = balance_manager.calculate_commissions(order=None, db_session=db_main) # Need order obj or details
                store_comm, trader_comm = Decimal("0.10"), Decimal("0.05") # Placeholder

                # 2.6 Create OrderHistory
                # order_history_data = {
                #     "incoming_order_id": incoming_order.id,
                #     "merchant_store_id": incoming_order.store_id,
                #     "requisite_id": assigned_requisite_id,
                #     "trader_id": assigned_trader_id,
                #     "amount": incoming_order.amount,
                #     "currency_id": incoming_order.currency_id,
                #     "status": "pending", # Initial status, use Enum
                #     "direction": incoming_order.direction, # Use Enum
                #     "store_commission": store_comm, # Store calculated commission
                #     "trader_commission": trader_comm, # Store calculated commission
                #     "fixed_exchange_rate": None, # TODO: Fetch and fix rate if applicable
                #     # ... other fields from incoming_order ...
                # }
                # new_order_history = create_object(db_main, OrderHistory, order_history_data)
                logger.info(f"OrderHistory created (placeholder) for IncomingOrder ID: {incoming_order_id}")
                new_order_history_id = 999 # Placeholder

                # 2.7 Update IncomingOrder
                # update_data = {
                #     "status": "assigned", # Use Enum
                #     "assigned_order_id": new_order_history.id,
                #     "failure_reason": None,
                #     "retry_count": incoming_order.retry_count, # Keep current count
                #     "last_attempt_at": datetime.utcnow()
                # }
                # update_object_db(db_main, incoming_order, update_data)
                logger.info(f"IncomingOrder {incoming_order_id} status updated to 'assigned' (placeholder).")

                # If we reach here, the main transaction will commit automatically
                logger.info(f"Successfully processed IncomingOrder ID: {incoming_order_id}. Assigned OrderHistory ID: {new_order_history_id}")

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
        try:
            with get_db_session() as db_status:
                with atomic_transaction(db_status):
                    # TODO: Implement Status Update Logic based on README_IMPLEMENTATION_PLAN.md 3.3
                    # -------------------------------------------------------------------------------
                    # 3.1 Load IncomingOrder (no lock needed now)
                    # order_to_update = db_status.get(IncomingOrder, incoming_order_id)
                    # if not order_to_update:
                    #     logger.error(f"CRITICAL: IncomingOrder {incoming_order_id} not found during status update after failure!")
                    #     # Cannot update status, original error is the primary issue.
                    #     # Maybe report this specific inconsistency?
                    #     report_critical_error(processing_exception, context_message="Failed to find order for status update after primary failure", incoming_order_id=incoming_order_id)
                    #     return # Exit, can't update

                    # !! Placeholder Load !!
                    order_to_update = db_status.get(IncomingOrder, incoming_order_id)
                    if not order_to_update: raise DatabaseError(f"Order {incoming_order_id} missing for status update")

                    # 3.2 Determine New Status (Retrying or Failed)
                    # max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db_status, int, default=3)
                    # current_retries = order_to_update.retry_count or 0
                    # new_status = "retrying" if current_retries < max_retries else "failed"
                    new_status = "failed" # Placeholder
                    current_retries = (order_to_update.retry_count or 0) + 1 # Placeholder increment

                    # 3.3 Prepare Update Data
                    # update_data = {
                    #     "status": new_status, # Use Enum
                    #     "failure_reason": failure_reason,
                    #     "retry_count": (order_to_update.retry_count or 0) + 1,
                    #     "last_attempt_at": datetime.utcnow()
                    # }
                    # update_object_db(db_status, order_to_update, update_data)
                    logger.info(f"Updating IncomingOrder {incoming_order_id} status to '{new_status}' (placeholder) with reason: {failure_reason}")

            logger.info(f"Successfully updated status for failed IncomingOrder ID: {incoming_order_id} to '{new_status}'")

            # If status is now 'failed', maybe report it (if not already reported as unexpected)
            if new_status == 'failed' and not isinstance(processing_exception, (RequisiteNotFound, LimitExceeded, FraudDetectedError)):
                 # Report potentially persistent failures
                 report_critical_error(processing_exception, context_message="Order processing failed after retries", incoming_order_id=incoming_order_id, final_status=new_status)

        except Exception as status_update_exc:
            # CRITICAL: Failed to even update the status after a processing failure
            logger.critical(f"CRITICAL FAILURE: Could not update status for IncomingOrder ID {incoming_order_id} after initial processing error. Status Update Error: {status_update_exc}", exc_info=True)
            # Report this critical situation
            report_critical_error(
                status_update_exc,
                context_message="CRITICAL: Failed to update order status after processing failure",
                incoming_order_id=incoming_order_id,
                original_error=str(processing_exception)
            )
            # Re-raise the status update exception as it's critical
            raise status_update_exc 