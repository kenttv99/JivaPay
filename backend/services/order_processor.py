"""Service for orchestrating the processing of incoming orders."""

import logging
from datetime import datetime
from decimal import Decimal
import uuid
from typing import Optional # Added for Optional types
import asyncio # Added asyncio
import io # Added for BytesIO

from sqlalchemy.orm import Session
from sqlalchemy import select
# For async
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.utils_async import get_async_db_session_cm, atomic_transaction_async, create_object_async, update_object_db_async # Assuming these exist or will be created
from backend.config.settings import settings # Added settings

from backend.config.logger import get_logger

# Attempt to import models, DB utils, other services, and exceptions
try:
    # !! Models needed: IncomingOrder, OrderHistory, etc. !!
    from backend.database.db import IncomingOrder, OrderHistory, UploadedDocument, PaymentSession # Added UploadedDocument, PaymentSession
    from backend.database.utils import get_db_session, get_db_session_cm, atomic_transaction, create_object, update_object_db
    from backend.utils.exceptions import (
        RequisiteNotFound, LimitExceeded, OrderProcessingError, DatabaseError, ConfigurationError, FraudDetectedError, InvalidInputError, ObjectNotFoundError # Added InvalidInputError
    )
    from backend.utils.notifications import report_critical_error
    # !! Services needed: requisite_selector, balance_manager, fraud_detector (when created) !!
    from backend.services import requisite_selector, balance_manager, fraud_detector
    from backend.services.fraud_detector import FraudStatus
    from backend.utils import s3_client # Added s3_client
    from backend.services.audit_service import log_event_async # Added audit_service
    from backend.schemas_enums.audit import AuditEvent, EventObjectType, EventObjectIdentifierType # Added Audit imports
    # !! Need config loader for retries !!
    from backend.utils.config_loader import get_typed_config_value_async # UPDATED to async version
    # Import refactored async services
    from backend.services.fraud_detector import check_incoming_order_async
    from backend.services.requisite_selector import find_suitable_requisite_async
    from backend.services.balance_manager import calculate_commissions_async
except ImportError as e:
    raise ImportError(f"Could not import required modules for OrderProcessor: {e}. Ensure models and other services are available.")

logger = get_logger(__name__)

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
    with get_db_session_cm() as db_check:
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
        with get_db_session_cm() as db_main:
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
                
                # 2.2 Fraud detection - moved outside the main try-except for specific handling before general processing
                try:
                    fraud_status_check_result = fraud_detector.check_incoming_order(incoming_order, db_main)
                    # If check_incoming_order returns a status (e.g. ALLOW), it means no FraudDetectedError was raised by it.
                    # If it raises FraudDetectedError, it will be caught below.
                except FraudDetectedError as fe:
                    logger.warning(f"Fraud check resulted in an exception for IncomingOrder {incoming_order_id}: {fe.limit_type}")
                    if fe.limit_type == FraudStatus.DENY:
                        update_object_db(db_main, incoming_order, {
                            'status': 'failed',
                            'failure_reason': f"Fraud: Denied - {str(fe)[:200]}",
                            'last_attempt_at': datetime.utcnow()
                        })
                        logger.info(f"IncomingOrder {incoming_order_id} status set to 'failed' due to fraud denial.")
                        # Commit this status change and stop further processing for this order
                        # This commit is within the atomic_transaction of db_main
                        return # Stop processing this order further
                    elif fe.limit_type == FraudStatus.REQUIRE_MANUAL_REVIEW:
                        update_object_db(db_main, incoming_order, {
                            'status': 'manual_review', # Special status for manual check
                            'failure_reason': f"Fraud: Manual Review - {str(fe)[:180]}",
                            'last_attempt_at': datetime.utcnow()
                            # retry_count is not incremented here as it's not a typical retry scenario
                        })
                        logger.info(f"IncomingOrder {incoming_order_id} status set to 'manual_review' due to fraud check.")
                        # Commit this status change and stop further processing for this order
                        return # Stop processing this order further
                    else: # Should not happen if FraudDetectedError always has a valid limit_type
                        update_object_db(db_main, incoming_order, {
                            'status': 'failed',
                            'failure_reason': f"Fraud: Unknown - {str(fe)[:200]}",
                            'last_attempt_at': datetime.utcnow()
                        })
                        return # Stop processing
                # If no FraudDetectedError was raised, and check_incoming_order returned (e.g. FraudStatus.ALLOW)
                # then we can proceed with normal processing.

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

    # --- 3. Status Update on Failure (runs if an exception occurred in 2.3 onwards) --- #
    # This block is now only for errors *after* fraud check (if fraud check passed or led to return)
    if processing_exception:
        logger.info(f"Attempting to update status for failed IncomingOrder ID: {incoming_order_id} due to {type(processing_exception).__name__}")
        # Update status (retrying or failed) reliably in separate transaction
        try:
            with get_db_session_cm() as db_status:
                with atomic_transaction(db_status):
                    order_to_update = db_status.query(IncomingOrder).filter_by(id=incoming_order_id).one_or_none()
                    if not order_to_update:
                        raise DatabaseError(f"IncomingOrder {incoming_order_id} not found during status update.")
                    
                    # Determine new status based on retry count
                    # This logic should not apply if the failure was a FraudDetectedError that was re-raised,
                    # as those should have set a final status already. However, FraudDetectedError is now handled and returned from above.
                    # So, any exception reaching here is a non-fraud processing error.
                    max_retries = get_typed_config_value_async("MAX_ORDER_RETRIES", db_status, int, default=3)
                    current_retries = (order_to_update.retry_count or 0)
                    next_retries = current_retries + 1
                    
                    new_status = "retrying"
                    if next_retries >= max_retries:
                        new_status = "failed"
                    
                    # If it was already 'manual_review' or 'failed' by fraud, do not change it by retry logic
                    if order_to_update.status in ['manual_review', 'failed'] and \
                       (failure_reason and "Fraud:" in failure_reason):
                        logger.warning(f"Order {incoming_order_id} already in terminal fraud status '{order_to_update.status}'. Preserving status.")
                        # We might just log and not update, or only update last_attempt_at
                        # For now, let the update proceed but new_status should be preserved if it was terminal due to fraud
                        # However, the new logic implies we RETURN from fraud block, so this path might be less common for fraud.
                        # This `if` condition here becomes a safeguard.
                        if order_to_update.status == 'manual_review': new_status = 'manual_review'
                        elif order_to_update.status == 'failed' and "Fraud: Denied" in (failure_reason or "") : new_status = 'failed'
                        # If it was another type of failure reason for 'failed' status, standard retry logic applies.

                    update_data = {
                        'status': new_status,
                        'failure_reason': failure_reason, # This is the new failure_reason from the processing_exception
                        'retry_count': next_retries if new_status == "retrying" else current_retries, 
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

# New asynchronous function to finalize order after client confirmation
async def finalize_order_after_client_confirmation_async(
    db: AsyncSession,
    incoming_order_id: int,
    receipt_content: Optional[bytes] = None,
    receipt_filename: Optional[str] = None,
    payment_token: Optional[str] = None
):
    logger.info(f"Starting finalize_order_after_client_confirmation_async for IncomingOrder ID: {incoming_order_id}")

    stmt_incoming_order = (
        select(IncomingOrder)
        .options(select(IncomingOrder.payment_session))
        .where(IncomingOrder.id == incoming_order_id)
    )
    result = await db.execute(stmt_incoming_order)
    incoming_order = result.scalars().first()

    if not incoming_order:
        raise ObjectNotFoundError(detail=f"IncomingOrder {incoming_order_id} not found for finalization.")

    if incoming_order.status != "client_payment_confirmed":
        raise InvalidInputError(f"IncomingOrder {incoming_order_id} status is '{incoming_order.status}', expected 'client_payment_confirmed'.")

    payment_session = incoming_order.payment_session
    if not payment_session:
        logger.warning(f"finalize_order: PaymentSession not found for IncomingOrder {incoming_order_id}. Proceeding with caution.")

    order_history_id: Optional[int] = None
    uploaded_document_id: Optional[int] = None
    final_incoming_order_status = incoming_order.status 
    final_payment_session_status = payment_session.status if payment_session else None
    failure_reason: Optional[str] = None

    # Load fraud thresholds using the new async config loader
    manual_threshold = None
    deny_threshold = None
    try:
        manual_threshold = await get_typed_config_value_async("FRAUD_MANUAL_REVIEW_THRESHOLD", db, Decimal, default=None)
        deny_threshold = await get_typed_config_value_async("FRAUD_DENY_THRESHOLD", db, Decimal, default=None)
        logger.info(f"Fraud thresholds loaded async: Manual={manual_threshold}, Deny={deny_threshold} for IOID: {incoming_order_id}")
    except Exception as config_exc:
        logger.error(f"Failed to load fraud thresholds async for IOID {incoming_order_id}: {config_exc}", exc_info=True)
        # Proceed with None thresholds, effectively disabling these specific fraud checks.

    async with atomic_transaction_async(db): # Main transaction block
        try:
            # 1. Fraud Detection
            fraud_check_status = await check_incoming_order_async(
                incoming_order=incoming_order, 
                manual_threshold_config=manual_threshold, 
                deny_threshold_config=deny_threshold
            )

            # 2. Select Requisite
            req_id, trader_id = await find_suitable_requisite_async(incoming_order, db)
            if not req_id or not trader_id:
                raise RequisiteNotFound(f"No suitable requisite found for order {incoming_order_id}")
            logger.info(f"Requisite {req_id} / Trader {trader_id} selected for IOID: {incoming_order_id}")

            # 3. Calculate Commissions
            store_comm, trader_comm = await calculate_commissions_async(incoming_order, db, trader_id=trader_id)
            logger.info(f"Commissions calculated for IOID: {incoming_order_id}. Store: {store_comm}, Trader: {trader_comm}")

            # 4. Create OrderHistory
            oh_data = {
                'incoming_order_id': incoming_order.id,
                'hash_id': uuid.uuid4().hex,
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
            new_oh = await create_object_async(db, OrderHistory, oh_data)
            order_history_id = new_oh.id
            logger.info(f"OrderHistory {order_history_id} created for IOID: {incoming_order_id}")

            # 5. Upload Receipt and Create UploadedDocument
            if receipt_content and receipt_filename and order_history_id:
                s3_path = f"receipts/incoming/{incoming_order.id}/{uuid.uuid4().hex}_{receipt_filename}"
                file_obj = io.BytesIO(receipt_content)
                try:
                    s3_uploaded_url = await s3_client.upload_fileobj_async(
                        fileobj=file_obj,
                        bucket=settings.S3_BUCKET_NAME,
                        key=s3_path
                    )
                    logger.info(f"Receipt uploaded to S3 for IOID {incoming_order.id} at {s3_uploaded_url}")
                    ud_data = {
                        "incoming_order_id": incoming_order.id,
                        "order_history_id": order_history_id,
                        "user_id": incoming_order.customer_id,
                        "document_type": "payment_receipt",
                        "file_path": s3_uploaded_url,
                        "original_filename": receipt_filename,
                        "file_size_bytes": len(receipt_content),
                        "status": "uploaded",
                    }
                    new_ud = await create_object_async(db, UploadedDocument, ud_data)
                    uploaded_document_id = new_ud.id
                    logger.info(f"UploadedDocument {uploaded_document_id} for OHID {order_history_id} created.")
                    
                    # TODO (Step 3 of improvements): Link UploadedDocument to OrderHistory if field exists.
                    # Example: if hasattr(new_oh, 'receipt_document_id'):
                    #    await update_object_db_async(db, new_oh, {"receipt_document_id": uploaded_document_id})

                except Exception as s3_ud_exc:
                    logger.error(f"S3/UploadedDoc failed for IOID {incoming_order.id}: {s3_ud_exc}", exc_info=True)
                    failure_reason = f"Receipt handling failed: {str(s3_ud_exc)[:100]}"

            final_incoming_order_status = "processed" if not failure_reason else "failed_processing_receipt"
            final_payment_session_status = "completed" if not failure_reason else "completed_with_issues"
            logger.info(f"Finalization logic successful for IOID: {incoming_order_id}. OH_ID: {order_history_id}")

        except FraudDetectedError as fe:
            logger.warning(f"Fraud check failed for IOID {incoming_order_id}: {fe.limit_type} - {fe.detail}")
            failure_reason = f"Fraud: {fe.limit_type.value} - {str(fe.detail)[:150]}"
            if fe.limit_type == FraudStatus.DENY:
                final_incoming_order_status = "failed"
                if payment_session: final_payment_session_status = "failed_fraud_deny"
            elif fe.limit_type == FraudStatus.REQUIRE_MANUAL_REVIEW:
                final_incoming_order_status = "manual_review"
                if payment_session: final_payment_session_status = "manual_review_fraud"
        except RequisiteNotFound as e:
            logger.warning(f"Finalization RequisiteNotFound for IOID {incoming_order_id}: {e}")
            failure_reason = str(e)
            final_incoming_order_status = "failed_no_requisite"
            if payment_session: final_payment_session_status = "failed_processing"
        except InvalidInputError as e:
            logger.error(f"Internal InvalidInputError during finalization for IOID {incoming_order_id}: {e}", exc_info=True)
            failure_reason = f"Internal InvalidInput: {str(e.detail)[:150]}"
            final_incoming_order_status = "failed_internal_error"
            if payment_session: final_payment_session_status = "failed_processing"
        except Exception as e:
            logger.error(f"Unexpected error during finalization transaction for IOID {incoming_order_id}: {e}", exc_info=True)
            report_critical_error(e, context_message="Unexpected error in finalize_order_after_client_confirmation_async transaction", incoming_order_id=incoming_order_id)
            failure_reason = f"Unexpected finalization error: {str(e)[:150]}"
            final_incoming_order_status = "failed_unexpected"
            if payment_session: final_payment_session_status = "failed_processing"

        update_io_data = {"status": final_incoming_order_status, "last_attempt_at": datetime.utcnow()}
        if failure_reason:
            update_io_data["failure_reason"] = failure_reason
        await update_object_db_async(db, incoming_order, update_io_data)
        logger.info(f"IncomingOrder {incoming_order.id} status updated to: {final_incoming_order_status} within transaction.")

        if payment_session:
            update_ps_data = {"status": final_payment_session_status}
            if failure_reason and not payment_session.failure_reason:
                update_ps_data["failure_reason"] = failure_reason[:255]
            await update_object_db_async(db, payment_session, update_ps_data)
            logger.info(f"PaymentSession {payment_session.id} status updated to: {final_payment_session_status} within transaction.")
    
    user_id_for_audit = incoming_order.customer_id if incoming_order.customer_id else (incoming_order.merchant_id if incoming_order.merchant_id else None)
    user_type_for_audit = "customer" if incoming_order.customer_id else ("merchant" if incoming_order.merchant_id else "system")

    if order_history_id:
        await log_event_async(
            session=db,
            user_id=user_id_for_audit,
            user_type=user_type_for_audit,
            event_type=AuditEvent.ORDER_HISTORY_CREATED,
            object_type=EventObjectType.ORDER_HISTORY,
            object_id=order_history_id,
            context_payment_token=payment_token,
            context_incoming_order_id=incoming_order.id,
            details={"message": f"OrderHistory created for IncomingOrder {incoming_order.id}."}
        )
    
    if uploaded_document_id:
        await log_event_async(
            session=db,
            user_id=user_id_for_audit,
            user_type=user_type_for_audit,
            event_type=AuditEvent.DOCUMENT_UPLOADED,
            object_type=EventObjectType.UPLOADED_DOCUMENT,
            object_id=uploaded_document_id,
            object_identifier=receipt_filename,
            object_identifier_type=EventObjectIdentifierType.FILENAME,
            context_payment_token=payment_token,
            context_incoming_order_id=incoming_order.id,
            context_order_history_id=order_history_id,
            details={"message": f"Receipt {receipt_filename} uploaded for OrderHistory {order_history_id}."}
        )

    await log_event_async(
        session=db,
        user_id=user_id_for_audit,
        user_type=user_type_for_audit,
        event_type=AuditEvent.ORDER_PROCESSING_COMPLETED if not failure_reason else AuditEvent.ORDER_PROCESSING_FAILED,
        object_type=EventObjectType.INCOMING_ORDER,
        object_id=incoming_order.id,
        context_payment_token=payment_token,
        context_order_history_id=order_history_id,
        details={
            "message": f"Finalization attempt for IncomingOrder {incoming_order.id} finished.",
            "final_status_incoming_order": final_incoming_order_status,
            "final_status_payment_session": final_payment_session_status,
            "failure_reason": failure_reason
        }
    )
    await db.flush()
    
    return {
        "incoming_order_id": incoming_order.id,
        "order_history_id": order_history_id,
        "uploaded_document_id": uploaded_document_id,
        "status": final_incoming_order_status,
        "payment_session_status": final_payment_session_status,
        "failure_reason": failure_reason
    }

# Ensure to add/update __all__ if this file uses it
# Example:
# __all__ = ["process_incoming_order", "finalize_order_after_client_confirmation_async"]

# Remember to create/verify the existence of async DB utils:
# get_async_db_session_cm, atomic_transaction_async, create_object_async, update_object_db_async
# And adapt sync parts like requisite_selector, balance_manager, fraud_detector.

# Remember to create/verify the existence of async DB utils:
# get_async_db_session_cm, atomic_transaction_async, create_object_async, update_object_db_async
# And adapt sync parts like requisite_selector, balance_manager, fraud_detector. 