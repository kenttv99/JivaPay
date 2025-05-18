"""Service for managing order status transitions."""

import logging
from typing import Optional, Any, Dict # Added Dict
from decimal import Decimal # Added for commission default
import uuid # Added for hash_id generation

from sqlalchemy.ext.asyncio import AsyncSession # Changed from sqlalchemy.orm import Session
from sqlalchemy.future import select # For async select
from sqlalchemy.orm import joinedload # For eager loading

# Attempt to import models, DB utils, exceptions, and worker tasks

# !! Models needed: OrderHistory, User (or specific actor models), potentially UploadedDocument !!
from backend.database.db import OrderHistory, UploadedDocument, User, IncomingOrder # Added IncomingOrder
from backend.database.db_ops import get_entity_by_id_logged_async, create_object_async, update_object_db_async # Async versions
from backend.exceptions.custom_exceptions import (
    InvalidOrderStatus,
    AuthorizationError,
    DatabaseError,
    OrderProcessingError,
    ObjectNotFoundError # Added
)
# !! Need worker task for async balance update !!
# from backend.worker.tasks import update_balances_task # Assuming this task exists
# !! Need S3 client if handling uploads here !!
from backend.utils.s3_client import upload_fileobj_async # Expecting async version or wrapper
from backend.config.logger import get_logger
# from backend.services.balance_manager import update_balances_for_completed_order # Ensure this is async or called carefully
from backend.config.settings import settings
# from backend.services.audit_service import log_event # Needs to be async: log_event_async
from backend.services.audit_service import log_event_async # Expecting async version
from backend.utils.decorators import handle_service_exceptions
import datetime # For timezone.utc


logger = get_logger(__name__)
# SERVICE_NAME = "order_status_manager" # Defined within class methods via decorator now

class OrderStatusManager:
    """Manages order status transitions and related actions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_service_exceptions(logger, "OrderStatusManager", "Confirming Payment from Gateway Page")
    async def confirm_payment_from_gateway_page(
        self,
        incoming_order_id: int,
        # receipt_content: Optional[bytes], # Receipt handling moved to OrderProcessor or when OrderHistory is made
        # receipt_filename: Optional[str],
        notes: Optional[str] = None,
        actor_id: Optional[int] = None # System user or context-specific actor ID
    ) -> IncomingOrder: # Returns updated IncomingOrder
        """
        Handles payment confirmation from the dedicated gateway payment page.
        Updates IncomingOrder status. Receipt processing and OrderHistory creation
        are deferred to a later stage (e.g., OrderProcessor).
        """
        logger.info(f"Confirming payment from gateway page for IncomingOrder ID: {incoming_order_id}")

        incoming_order = await get_entity_by_id_logged_async(
            self.session, IncomingOrder, incoming_order_id, logger, "IncomingOrder for payment page confirmation"
        )
        if not incoming_order:
            raise ObjectNotFoundError(f"IncomingOrder with ID {incoming_order_id} not found.")

        valid_initial_statuses = ["new", "processing", "retrying", "payment_session_active"] # Added more specific status
        if incoming_order.status not in valid_initial_statuses :
            logger.warning(f"IncomingOrder {incoming_order.id} is not in a valid status for payment page confirmation. Status: {incoming_order.status}")
            raise InvalidOrderStatus(f"IncomingOrder {incoming_order.id} status '{incoming_order.status}' does not allow payment confirmation from page.")

        # Update IncomingOrder status
        incoming_order.status = "client_payment_confirmed" # New status indicating client action is done
        incoming_order.payment_details_submitted = True
        incoming_order.last_attempt_at = datetime.datetime.now(datetime.timezone.utc)
        
        # If notes are provided and there's a field for them in IncomingOrder, save them.
        # For example: if hasattr(incoming_order, 'client_notes'): incoming_order.client_notes = notes
        
        await self.session.flush()

        await log_event_async(
            session=self.session,
            user_id=actor_id,
            action="confirm_payment_from_gateway_page",
            target_entity="IncomingOrder", # Changed from OrderHistory
            target_id=incoming_order.id,
            details={
                "client_notes": notes,
                "new_incoming_order_status": incoming_order.status
            }
        )
        logger.info(f"IncomingOrder {incoming_order.id} status updated to '{incoming_order.status}' by payment page confirmation.")
        return incoming_order

    @handle_service_exceptions(logger, "OrderStatusManager", "Confirming Order by Trader")
    async def confirm_order_by_trader(
        self, 
        order_history_id: int, 
        actor_id: int, # Trader's user_id
        receipt_content: Optional[bytes] = None, 
        receipt_filename: Optional[str] = None,
        # other_details: Optional[Dict[str, Any]] = None # For future use
    ) -> OrderHistory:
        """
        Confirms an order by a trader. Primarily for PayOuts where trader uploads proof,
        or for PayIns if a specific trader confirmation step is needed after client.
        Updates order status to 'completed' and can trigger balance updates.
        """
        logger.info(f"Trader {actor_id} confirming OrderHistory ID: {order_history_id}")
        order_history = await get_entity_by_id_logged_async(
            self.session, OrderHistory, order_history_id, logger, "OrderHistory for trader confirmation",
            options=[joinedload(OrderHistory.trader)] # Eager load trader for permission check
        )
        if not order_history:
            raise ObjectNotFoundError(f"OrderHistory with ID {order_history_id} not found.")

        # Permission check: Ensure the actor is the assigned trader
        if not order_history.trader or order_history.trader.user_id != actor_id:
             # If trader is not yet assigned, or actor is not the assigned trader
            raise AuthorizationError(f"Trader {actor_id} is not authorized to confirm this order {order_history.id}.")

        # Status check: Define valid statuses for trader confirmation
        # Example: For PayIn, client confirms, then it becomes 'pending_trader_action' or similar.
        # For PayOut, it might be 'awaiting_trader_payout_proof'.
        valid_statuses_for_trader_confirm = ["pending_trader_confirmation", "awaiting_payout_proof"] # Example statuses
        if order_history.status not in valid_statuses_for_trader_confirm:
            logger.warning(f"OrderHistory {order_history.id} in status '{order_history.status}' cannot be confirmed by trader.")
            raise InvalidOrderStatus(f"Order {order_history.id} status '{order_history.status}' does not allow trader confirmation.")

        receipt_url_db = order_history.trader_receipt_url
        if receipt_content and receipt_filename:
            bucket = settings.S3_BUCKET_NAME
            s3_key = f"receipts_trader/order_{order_history.id}/{datetime.datetime.now(datetime.timezone.utc).timestamp()}_{receipt_filename}"
            try:
                uploaded_url = await upload_fileobj_async(receipt_content, bucket, s3_key)
                order_history.trader_receipt_url = uploaded_url # Assuming this field exists
                receipt_url_db = uploaded_url
                logger.info(f"Trader receipt uploaded to S3 for OrderHistory {order_history.id}: {uploaded_url}")
                doc_data = {
                    "order_id": order_history.id,
                    "actor_id": actor_id,
                    "file_url": uploaded_url,
                    "doc_type": "trader_receipt"
                }
                await create_object_async(self.session, UploadedDocument, doc_data)
                logger.info(f"Trader UploadedDocument record created for OrderHistory {order_history.id}")
            except Exception as e:
                logger.error(f"S3 upload or UploadedDocument for trader receipt failed for OrderHistory {order_history.id}: {e}", exc_info=True)
        
        order_history.status = "completed"
        # Potentially update other fields, e.g., confirmed_by_trader_at
        
        await self.session.flush()
        
        await log_event_async(
            session=self.session,
            user_id=actor_id,
            action="confirm_order_by_trader",
            target_entity="OrderHistory",
            target_id=order_history.id,
            details={"receipt_url": receipt_url_db, "new_status": "completed"}
        )

        # Trigger balance update (ensure balance_manager is async or called appropriately)
        # await update_balances_for_completed_order_async(self.session, order_history.id)
        # For now, assuming this might be handled by a worker task elsewhere or a subsequent call.
        logger.info(f"OrderHistory {order_history.id} status updated to 'completed' by trader {actor_id}.") 
        # Consider if balance update should be enqueued here via Celery task if it's lengthy.
        # For example: update_balances_task.delay(order_history.id)

        return order_history

    @handle_service_exceptions(logger, "OrderStatusManager", "Cancelling Order")
    async def cancel_order(
        self, 
        order_history_id: int, 
        actor_id: int, 
        actor_role: str, # e.g. "merchant", "trader", "admin", "support"
        reason: str
    ) -> OrderHistory:
        """Cancels an order with permission checks."""
        logger.info(f"Actor {actor_id} (role: {actor_role}) attempting to cancel OrderHistory ID: {order_history_id} for reason: {reason}")
        
        # Use with_for_update for pessimistic locking if needed, ensure db_ops supports it for async
        order_history = await get_entity_by_id_logged_async(
            self.session, OrderHistory, order_history_id, logger, "OrderHistory for cancellation",
            options=[joinedload(OrderHistory.merchant), joinedload(OrderHistory.trader)] # Load for permission checks
        )
        if not order_history:
            raise ObjectNotFoundError(f"OrderHistory with ID {order_history_id} not found for cancellation.")

        # --- Permission Checks (Simplified Example) ---
        can_cancel = False
        if actor_role == "admin" or actor_role == "support": # Admins/Support can cancel (almost) any order
            can_cancel = True
        elif actor_role == "merchant":
            if order_history.merchant and order_history.merchant.user_id == actor_id:
                can_cancel = True
        elif actor_role == "trader":
            if order_history.trader and order_history.trader.user_id == actor_id:
                can_cancel = True
        
        if not can_cancel:
            logger.warning(f"Actor {actor_id} (role: {actor_role}) unauthorized to cancel OrderHistory {order_history.id}")
            raise AuthorizationError("You are not authorized to cancel this order.")

        # --- Status Check ---
        # Define statuses from which an order can be cancelled
        VALID_STATUSES_FOR_CANCEL = ["new", "pending_assignment", "pending_client_confirmation", "pending_trader_confirmation", "awaiting_payout_proof"] # Example
        if order_history.status not in VALID_STATUSES_FOR_CANCEL:
            logger.warning(f"OrderHistory {order_history.id} in status '{order_history.status}' cannot be cancelled.")
            raise InvalidOrderStatus(f"Order {order_history.id} cannot be cancelled from its current status ({order_history.status}).")

        update_data = {"status": "canceled", "cancellation_reason": reason}
        updated_order_history = await update_object_db_async(self.session, order_history, update_data)
        
        await log_event_async(
            session=self.session,
            user_id=actor_id,
            action="cancel_order",
            target_entity="OrderHistory",
            target_id=updated_order_history.id,
            details={"reason": reason, "cancelled_by_role": actor_role, "previous_status": order_history.status}
        )
        logger.info(f"OrderHistory {updated_order_history.id} cancelled by actor {actor_id}. Reason: {reason}")
        return updated_order_history

    @handle_service_exceptions(logger, "OrderStatusManager", "Disputing Order")
    async def dispute_order(
        self,
        order_history_id: int,
        actor_id: int,
        actor_role: str, # e.g., "support", "admin", "merchant", "trader"
        reason: str
    ) -> OrderHistory:
        """Marks an order as disputed, with permission checks."""
        logger.info(f"Actor {actor_id} (role: {actor_role}) attempting to dispute OrderHistory ID: {order_history_id} for reason: {reason}")
        
        order_history = await get_entity_by_id_logged_async(
            self.session, OrderHistory, order_history_id, logger, "OrderHistory for dispute",
            options=[joinedload(OrderHistory.merchant), joinedload(OrderHistory.trader)]
        )
        if not order_history:
            raise ObjectNotFoundError(f"OrderHistory with ID {order_history_id} not found for dispute.")

        # --- Permission Checks (Simplified Example) ---
        # Typically, any involved party (merchant, trader) or support/admin can raise a dispute.
        can_dispute = False
        if actor_role in ["admin", "support"]:
            can_dispute = True
        elif actor_role == "merchant" and order_history.merchant and order_history.merchant.user_id == actor_id:
            can_dispute = True
        elif actor_role == "trader" and order_history.trader and order_history.trader.user_id == actor_id:
            can_dispute = True
        
        if not can_dispute:
            logger.warning(f"Actor {actor_id} (role: {actor_role}) unauthorized to dispute OrderHistory {order_history.id}")
            raise AuthorizationError("You are not authorized to dispute this order.")

        # --- Status Check ---
        # Orders usually can be disputed unless they are already finalized (canceled, failed, or already disputed).
        INVALID_STATUSES_FOR_DISPUTE = ["canceled", "failed", "disputed"]
        if order_history.status in INVALID_STATUSES_FOR_DISPUTE or order_history.status == "completed": # Completed might be disputable for a short period
            logger.warning(f"OrderHistory {order_history.id} in status '{order_history.status}' cannot be disputed.")
            raise InvalidOrderStatus(f"Order {order_history.id} cannot be disputed from its current status ({order_history.status}).")

        update_data = {"status": "disputed", "cancellation_reason": order_history.cancellation_reason + f" | DISPUTE: {reason}" if order_history.cancellation_reason else f"DISPUTE: {reason}"}
        updated_order_history = await update_object_db_async(self.session, order_history, update_data)
        
        await log_event_async(
            session=self.session,
            user_id=actor_id,
            action="dispute_order",
            target_entity="OrderHistory",
            target_id=updated_order_history.id,
            details={"reason": reason, "disputed_by_role": actor_role, "previous_status": order_history.status}
        )
        logger.info(f"OrderHistory {updated_order_history.id} disputed by actor {actor_id}. Reason: {reason}")
        return updated_order_history

    @handle_service_exceptions(logger, "OrderStatusManager", "Resolving Dispute")
    async def resolve_dispute(
        self,
        order_history_id: int,
        actor_id: int, # Typically admin or support
        actor_role: str,
        resolution_details: str,
        final_status: str # e.g., "completed", "canceled_by_admin"
    ) -> OrderHistory:
        """Resolves a disputed order, setting a final status."""
        logger.info(f"Actor {actor_id} (role: {actor_role}) attempting to resolve dispute for OrderHistory ID: {order_history_id} with final status: {final_status}")
        
        order_history = await get_entity_by_id_logged_async(
            self.session, OrderHistory, order_history_id, logger, "OrderHistory for dispute resolution"
        )
        if not order_history:
            raise ObjectNotFoundError(f"OrderHistory with ID {order_history_id} not found for dispute resolution.")

        # --- Permission Check ---
        if actor_role not in ["admin", "support"]:
            logger.warning(f"Actor {actor_id} (role: {actor_role}) unauthorized to resolve dispute for OrderHistory {order_history.id}")
            raise AuthorizationError("Only admin or support can resolve disputes.")

        # --- Status Check ---
        if order_history.status != "disputed":
            logger.warning(f"OrderHistory {order_history.id} is not in 'disputed' status. Current status: {order_history.status}")
            raise InvalidOrderStatus("Order is not currently disputed.")
        
        VALID_FINAL_STATUSES = ["completed", "canceled", "failed"] # Define valid resolution statuses
        if final_status not in VALID_FINAL_STATUSES:
            logger.error(f"Invalid final_status '{final_status}' for dispute resolution of order {order_history.id}.")
            raise InvalidInputError(f"Invalid final status for resolution: {final_status}. Must be one of {VALID_FINAL_STATUSES}.")

        update_data = {
            "status": final_status,
            "cancellation_reason": order_history.cancellation_reason + f" | RESOLUTION: {resolution_details}" if order_history.cancellation_reason else f"RESOLUTION: {resolution_details}"
        }
        updated_order_history = await update_object_db_async(self.session, order_history, update_data)
        
        await log_event_async(
            session=self.session,
            user_id=actor_id,
            action="resolve_dispute_order",
            target_entity="OrderHistory",
            target_id=updated_order_history.id,
            details={
                "resolution_details": resolution_details, 
                "final_status": final_status, 
                "resolved_by_role": actor_role
            }
        )
        logger.info(f"Dispute for OrderHistory {updated_order_history.id} resolved by actor {actor_id}. New status: {final_status}")
        return updated_order_history

    @handle_service_exceptions(logger, "OrderStatusManager", "Failing Order")
    async def fail_order(
        self,
        order_history_id: int,
        actor_id: Optional[int], # Can be system (None) or a user
        actor_role: Optional[str], # e.g., "system", "admin"
        reason: str
    ) -> OrderHistory:
        """Marks an order as failed, typically due to system issues or admin intervention."""
        logger.info(f"Actor {actor_id or 'System'} (role: {actor_role or 'N/A'}) attempting to fail OrderHistory ID: {order_history_id} for reason: {reason}")
        
        order_history = await get_entity_by_id_logged_async(
            self.session, OrderHistory, order_history_id, logger, "OrderHistory for failing"
        )
        if not order_history:
            raise ObjectNotFoundError(f"OrderHistory with ID {order_history_id} not found for failing.")

        # --- Status Check ---
        # Order can be failed unless it's already in a terminal success/failure state.
        NON_FAILABLE_STATUSES = ["completed", "failed", "canceled"]
        if order_history.status in NON_FAILABLE_STATUSES:
            logger.warning(f"OrderHistory {order_history.id} in status '{order_history.status}' cannot be marked as failed.")
            raise InvalidOrderStatus(f"Order {order_history.id} cannot be failed from its current status ({order_history.status}).")

        update_data = {"status": "failed", "cancellation_reason": reason}
        updated_order_history = await update_object_db_async(self.session, order_history, update_data)
        
        await log_event_async(
            session=self.session,
            user_id=actor_id,
            action="fail_order",
            target_entity="OrderHistory",
            target_id=updated_order_history.id,
            details={"reason": reason, "failed_by_role": actor_role, "previous_status": order_history.status}
        )
        logger.info(f"OrderHistory {updated_order_history.id} marked as FAILED by actor {actor_id or 'System'}. Reason: {reason}")
        return updated_order_history

# Synchronous functions below are marked for deprecation/refactoring.
# Their direct usage should be phased out in favor of the async OrderStatusManager class methods.

# ... (existing synchronous functions can be left here, commented out, or removed if no longer needed at all) ...