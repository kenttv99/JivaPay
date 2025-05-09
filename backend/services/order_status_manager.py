"""Service for managing order status transitions."""

import logging
from typing import Optional, Any # Placeholder for User/Actor type

from sqlalchemy.orm import Session

# Attempt to import models, DB utils, exceptions, and worker tasks
try:
    # !! Models needed: OrderHistory, User (or specific actor models), potentially UploadedDocument !!
    from backend.database.db import OrderHistory, UploadedDocument, User
    from backend.database.utils import get_db_session, atomic_transaction, update_object_db, create_object
    from backend.utils.exceptions import (
        InvalidOrderStatus, AuthorizationError, DatabaseError, OrderProcessingError
    )
    # !! Need worker task for async balance update !!
    from backend.worker.tasks import update_balances_task # Assuming this task exists
    # !! Need S3 client if handling uploads here !!
    from backend.utils.s3_client import upload_fileobj
    from backend.config.logger import get_logger
    from backend.services.balance_manager import update_balances_for_completed_order
    from backend.config.settings import settings
    from backend.services.audit_logger import log_event
except ImportError as e:
    raise ImportError(f"Could not import required modules for OrderStatusManager: {e}. Ensure models and worker tasks are available.")

logger = get_logger(__name__)

# Define expected order statuses (replace with actual Enum when available)
# Example:
# class OrderStatusEnum(str, Enum):
#     PENDING = "pending"
#     AWAITING_CLIENT_CONFIRMATION = "awaiting_client_confirmation" # PayIn
#     AWAITING_TRADER_CONFIRMATION = "awaiting_trader_confirmation" # PayOut?
#     AWAITING_TRADER_ACTION = "awaiting_trader_action" # PayIn
#     CONFIRMED_BY_CLIENT = "confirmed_by_client"
#     COMPLETED = "completed"
#     CANCELED = "canceled"
#     DISPUTED = "disputed"
#     FAILED = "failed"
VALID_STATUSES_FOR_CLIENT_CONFIRM = ["awaiting_client_confirmation"] # Example
VALID_STATUSES_FOR_TRADER_CONFIRM = ["awaiting_trader_action", "confirmed_by_client"] # Example
VALID_STATUSES_FOR_CANCEL = ["pending", "awaiting_client_confirmation", "awaiting_trader_action"] # Example

def _check_permissions(actor: Any, order: OrderHistory, required_role: str) -> None:
    """Placeholder for permission checks."""
    logger.debug(f"Checking permissions for Actor {getattr(actor, 'id', 'N/A')} (role={getattr(actor, 'role', None)}) on Order {order.id}")
    if not actor:
        raise AuthorizationError("Action requires an authenticated user.")
    role = getattr(actor.role, 'name', None)
    if required_role == 'merchant':
        if role not in ('merchant', 'admin'):
            raise AuthorizationError("Only merchant or admin can perform this action.")
        if order.merchant_id != getattr(actor.merchant_profile, 'id', None):
            raise AuthorizationError("Merchant unauthorized for this order.")
    elif required_role == 'trader':
        if role not in ('trader', 'admin'):
            raise AuthorizationError("Only trader or admin can perform this action.")
        if order.trader_id != getattr(actor.trader_profile, 'id', None):
            raise AuthorizationError("Trader unauthorized for this order.")
    elif required_role == 'admin':
        if role != 'admin':
            raise AuthorizationError("Only admin can perform this action.")
    else:
        raise AuthorizationError(f"Unknown required role: {required_role}")

def _add_uploaded_document(db: Session, order_id: int, actor_id: int, file_url: str, doc_type: str):
    """Placeholder for saving document info to DB."""
    # Save document record in UploadedDocument table
    try:
        create_object(db, UploadedDocument, {
            'order_id': order_id,
            'actor_id': actor_id,
            'file_url': file_url,
            'doc_type': doc_type
        })
        logger.info(f"UploadedDocument saved: order={order_id}, actor={actor_id}, url={file_url}")
    except Exception as e:
        logger.error(f"Failed to save UploadedDocument for order {order_id}: {e}")
        raise DatabaseError(f"Could not save uploaded document: {e}")

def confirm_payment_by_client(
    order_id: int,
    receipt: bytes,
    filename: str,
    db_session: Session
) -> OrderHistory:
    """
    Updates OrderHistory after merchant client confirms payment and uploads receipt.
    Uploads receipt to S3, updates order status to 'pending_trader_confirmation'.
    """
    order = db_session.query(OrderHistory).filter_by(id=order_id).one_or_none()
    if not order:
        raise InvalidOrderStatus(f"Order with ID {order_id} not found.")
    if order.status != 'assigned':
        raise InvalidOrderStatus(f"Order {order_id} is not in 'assigned' status.")

    # Upload receipt to S3
    bucket = settings.S3_BUCKET_NAME
    key = f"receipts/{order_id}/{filename}"
    receipt_url = upload_fileobj(receipt, bucket, key)
    # Save uploaded document record
    _add_uploaded_document(db_session, order_id, None, receipt_url, 'client_receipt')

    # Update order fields
    order.status = 'pending_trader_confirmation'
    order.payment_details_submitted = True
    order.receipt_url = receipt_url  # Ensure this column exists in model
    db_session.add(order)
    db_session.flush()
    logger.info(f"Order {order_id} updated to 'pending_trader_confirmation', receipt uploaded: {receipt_url}")
    # Audit log
    log_event(
        user_id=None,
        action='confirm_payment_by_client',
        target_entity='OrderHistory',
        target_id=order_id,
        details={'receipt_url': receipt_url}
    )
    return order

def confirm_order_by_trader(
    order_id: int,
    receipt: bytes,
    filename: str,
    trader_id: int,
    db_session: Session
) -> OrderHistory:
    """
    Confirms order by trader, uploads receipt if needed, updates status and triggers balance update.
    """
    order = db_session.query(OrderHistory).filter_by(id=order_id).one_or_none()
    if not order or order.trader_id != trader_id:
        raise InvalidOrderStatus(f"Order {order_id} not assigned to trader {trader_id}.")
    if order.status not in ['pending_trader_confirmation', 'pending_client_confirmation']:
        raise InvalidOrderStatus(f"Order {order_id} is not in confirmation status.")

    # Upload receipt for PayOut if provided
    bucket = settings.S3_BUCKET_NAME
    key = f"receipts/{order_id}/{filename}"
    receipt_url = upload_fileobj(receipt, bucket, key)
    # Save uploaded document record
    _add_uploaded_document(db_session, order_id, trader_id, receipt_url, 'trader_receipt')
    
    # Update order
    order.status = 'completed'
    order.payment_details_submitted = True
    order.trader_receipt_url = receipt_url  # Ensure this column exists in model
    db_session.add(order)
    db_session.flush()
    logger.info(f"Order {order_id} confirmed by trader {trader_id}, receipt uploaded: {receipt_url}")
    # Audit log
    log_event(
        user_id=trader_id,
        action='confirm_order_by_trader',
        target_entity='OrderHistory',
        target_id=order_id,
        details={'receipt_url': receipt_url}
    )
    # Trigger balance update asynchronously, here a direct call
    update_balances_for_completed_order(order_id, db_session)
    return order

def cancel_order(
    order_id: int,
    actor: Any, # User performing the cancellation (Trader, Merchant, Admin)
    reason: str,
    db: Session
) -> OrderHistory:
    """Implements order cancellation with permission and status checks."""
    with atomic_transaction(db):
        # Load and lock order
        order = db.query(OrderHistory).filter_by(id=order_id).with_for_update().one_or_none()
        if not order:
            raise OrderProcessingError(f"Order not found: {order_id}")
        # Permission: merchant, trader or admin
        role = getattr(actor.role, 'name', None)
        required = 'merchant' if role == 'merchant' else ('trader' if role=='trader' else 'admin')
        _check_permissions(actor, order, required)
        # Status check
        if order.status not in VALID_STATUSES_FOR_CANCEL:
            raise InvalidOrderStatus(f"Order {order_id} cannot be cancelled from status {order.status}.")
        # Update status and reason
        update_data = {'status': 'canceled', 'cancellation_reason': reason}
        updated_order = update_object_db(db, order, update_data)
        logger.info(f"Order {order_id} canceled by actor {getattr(actor, 'id', None)}, reason: {reason}")
        # Audit log
        log_event(
            user_id=getattr(actor, 'id', None),
            action='cancel_order',
            target_entity='OrderHistory',
            target_id=order_id,
            details={'reason': reason}
        )
        return updated_order

# Additional status management functions
def dispute_order(order_id: int, actor: Any, reason: str, db: Session) -> OrderHistory:
    """Marks an order as disputed."""
    with atomic_transaction(db):
        order = db.query(OrderHistory).filter_by(id=order_id).with_for_update().one_or_none()
        if not order:
            raise OrderProcessingError(f"Order not found: {order_id}")
        _check_permissions(actor, order, 'support' if getattr(actor.role, 'name', '')=='support' else 'admin')
        if order.status in ['completed', 'canceled', 'failed', 'disputed']:
            raise InvalidOrderStatus(f"Order {order_id} cannot be disputed from status {order.status}.")
        updated = update_object_db(db, order, {'status': 'disputed', 'cancellation_reason': reason})
        log_event(user_id=getattr(actor, 'id', None), action='dispute_order', target_entity='OrderHistory', target_id=order_id, details={'reason': reason})
        return updated

def resolve_dispute(order_id: int, actor: Any, resolution_details: dict, final_status: str, db: Session) -> OrderHistory:
    """Resolves a disputed order by setting a final status."""
    with atomic_transaction(db):
        order = db.query(OrderHistory).filter_by(id=order_id).with_for_update().one_or_none()
        if not order:
            raise OrderProcessingError(f"Order not found: {order_id}")
        _check_permissions(actor, order, 'admin')
        if order.status != 'disputed':
            raise InvalidOrderStatus(f"Order {order_id} is not in disputed status.")
        if final_status not in ['completed', 'canceled', 'failed']:
            raise InvalidOrderStatus(f"Invalid final status: {final_status}.")
        update_data = {'status': final_status, 'cancellation_reason': resolution_details.get('reason')}
        updated = update_object_db(db, order, update_data)
        log_event(user_id=getattr(actor, 'id', None), action='resolve_dispute', target_entity='OrderHistory', target_id=order_id, details=resolution_details)
        return updated

def fail_order(order_id: int, actor: Any, reason: str, db: Session) -> OrderHistory:
    """Marks an order as failed (manual intervention)."""
    with atomic_transaction(db):
        order = db.query(OrderHistory).filter_by(id=order_id).with_for_update().one_or_none()
        if not order:
            raise OrderProcessingError(f"Order not found: {order_id}")
        _check_permissions(actor, order, 'admin')
        if order.status in ['completed', 'canceled', 'failed']:
            raise InvalidOrderStatus(f"Order {order_id} cannot be failed from status {order.status}.")
        updated = update_object_db(db, order, {'status': 'failed', 'cancellation_reason': reason})
        log_event(user_id=getattr(actor, 'id', None), action='fail_order', target_entity='OrderHistory', target_id=order_id, details={'reason': reason})
        return updated

# TODO: Implement other status management functions as needed:
# - dispute_order(order_id, actor, reason, db)
# - resolve_dispute(order_id, admin_actor, resolution_details, final_status, db)
# - fail_order(order_id, system_or_admin_actor, reason, db) # For manual intervention or timeouts 