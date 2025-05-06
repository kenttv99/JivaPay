"""Celery tasks for the JivaPay worker."""

import logging
from celery.exceptions import Reject
from datetime import datetime, timedelta

# Attempt to import Celery app, services, utils, exceptions
try:
    from backend.worker.app import celery_app
    from backend.services import order_processor
    from backend.database.utils import get_db_session # Needed for config_loader
    from backend.utils.exceptions import DatabaseError, CacheError, OrderProcessingError # Add specific retryable errors
    from backend.utils.config_loader import get_typed_config_value
    from backend.utils.notifications import report_critical_error
    from backend.database.db import IncomingOrder
    from backend.services.balance_manager import update_balances_for_completed_order
except ImportError as e:
    raise ImportError(f"Could not import required modules for Celery tasks: {e}")

logger = logging.getLogger(__name__)

# --- Task Definitions --- #

@celery_app.task(
    name="backend.worker.tasks.process_order_task",
    bind=True, # Allows access to task instance (self)
    acks_late=True, # Acknowledged after task completes (requires idempotent tasks)
    # --- Retry Logic --- #
    # Celery's automatic retry mechanism
    # It's often better to handle retries within the task for more control,
    # especially regarding database transactions and status updates.
    # However, autoretry_for can handle transient infra errors well.
    # autoretry_for=(DatabaseError, CacheError, ConnectionError), # Specify exceptions that trigger auto-retry
    # retry_backoff=True,       # Enable exponential backoff
    # retry_backoff_max=600,    # Max delay in seconds (10 minutes)
    # retry_jitter=True,        # Add random jitter to delays
    # max_retries=None          # Retry indefinitely for specified exceptions (or set a limit)
    # --- Custom Retry/Error Handling is often preferred for business logic --- #
)
def process_order_task(self, incoming_order_id: int):
    """Celery task to process an incoming order using the order_processor service.

    Handles retries based on configuration and specific exceptions.

    Args:
        self: The task instance (automatically passed with bind=True).
        incoming_order_id: The ID of the IncomingOrder to process.
    """
    logger.info(f"[Task ID: {self.request.id}] Received task to process IncomingOrder ID: {incoming_order_id}")

    # --- Get Retry Configuration from DB --- #
    # This requires a DB session *outside* the main order processing logic's transaction
    max_retries = 3 # Default
    retry_delay_base = 60 # Default delay in seconds (e.g., 1 minute)
    try:
        with get_db_session() as db_config:
            max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db_config, int, default=3)
            # We'll use Celery's countdown for delay, backoff factor is implicit in increasing countdown
            retry_delay_base = get_typed_config_value("RETRY_DELAY_SECONDS", db_config, int, default=60)
            logger.debug(f"[Task ID: {self.request.id}] Retry config: max_retries={max_retries}, retry_delay_base={retry_delay_base}s")
    except Exception as config_err:
        # Log error but proceed with defaults, maybe report?
        logger.error(f"[Task ID: {self.request.id}] Failed to load retry config from DB: {config_err}. Using defaults.", exc_info=True)
        # report_critical_error(config_err, context_message="Failed to load retry config in Celery task")

    try:
        # Call the main order processing logic
        # This function handles its own transactions and status updates on failure
        order_processor.process_incoming_order(incoming_order_id)

        logger.info(f"[Task ID: {self.request.id}] Successfully processed IncomingOrder ID: {incoming_order_id}")
        # Task completes successfully, ack is sent (due to acks_late=True)

    except (DatabaseError, CacheError) as e:
        # --- Handle Retryable Infrastructure Errors --- #
        logger.warning(f"[Task ID: {self.request.id}] Infrastructure error processing order {incoming_order_id}: {e}. Attempting retry ({self.request.retries + 1}/{max_retries}).")
        try:
            # Calculate delay with exponential backoff (manual approach)
            # backoff_factor read from config is not directly used here, Celery's `countdown` handles delay.
            # Use retry_delay_base * 2^retries as a simple backoff.
            delay = retry_delay_base * (2 ** self.request.retries)
            logger.info(f"[Task ID: {self.request.id}] Retrying task in {delay} seconds.")
            # self.retry() raises Retry exception, preventing ack
            self.retry(exc=e, countdown=delay, max_retries=max_retries)
        except Exception as retry_exc:
            # Log if retry mechanism itself fails (e.g., exceeded max_retries internally)
            logger.error(f"[Task ID: {self.request.id}] Celery retry failed for order {incoming_order_id}: {retry_exc}", exc_info=True)
            # Report critical failure if retries exhausted or retry call failed
            report_critical_error(e, context_message="Order processing failed after infra error retries", incoming_order_id=incoming_order_id, task_id=self.request.id)
            # Explicitly reject if retry fails to prevent ack
            raise Reject(f"Retry failed: {retry_exc}", requeue=False)

    except OrderProcessingError as e:
        # --- Handle Non-Retryable Business Logic Errors --- #
        # These errors should have been handled by process_incoming_order, resulting in a 'failed' or 'retrying' status update.
        # The task itself succeeded in triggering the logic, even if the logic failed.
        logger.error(f"[Task ID: {self.request.id}] OrderProcessingError for order {incoming_order_id}: {e}. Status should be updated by processor. Task will be acknowledged.", exc_info=True)
        # We might report these if they are unexpected, but generally, the processor handles the state.
        # report_critical_error(e, context_message="OrderProcessingError caught in Celery task", incoming_order_id=incoming_order_id, task_id=self.request.id)
        # Acknowledge the task as the error is handled at the business logic level.
        pass # Task completes, ack is sent

    except Exception as e:
        # --- Handle Unexpected Errors --- #
        logger.critical(f"[Task ID: {self.request.id}] UNEXPECTED error processing order {incoming_order_id}: {e}", exc_info=True)
        # Report critical unexpected errors
        report_critical_error(e, context_message="Unexpected error in Celery task", incoming_order_id=incoming_order_id, task_id=self.request.id)
        # Reject the task without requeueing to avoid infinite loops for unknown errors
        # The order status might be stuck unless manually corrected.
        raise Reject(f"Unexpected error: {e}", requeue=False)

# Task to update balances asynchronously
@celery_app.task(
    name="backend.worker.tasks.update_balance_task",
    bind=True,
    acks_late=True
)
def update_balance_task(self, order_id: int):
    """Async task to update balances for a completed order."""
    logger.info(f"[Task ID: {self.request.id}] Updating balances for order {order_id}")
    try:
        with get_db_session() as db:
            update_balances_for_completed_order(order_id, db)
            logger.info(f"[Task ID: {self.request.id}] Balances updated for order {order_id}")
    except Exception as e:
        logger.error(f"[Task ID: {self.request.id}] Error updating balances for order {order_id}: {e}", exc_info=True)
        # Retry the task with default retry policy
        raise self.retry(exc=e)

# Task to poll incoming orders and enqueue processing tasks
# @celery_app.task(name="backend.worker.tasks.poll_new_orders_task")
# def poll_new_orders_task():
#     """Polls for new or retrying orders and enqueues them for processing."""
#     logger.info("Polling for new or retrying orders...")
#     try:
#         with get_db_session() as db:
#             max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db, int, default=3)
#             retry_delay_base = get_typed_config_value("RETRY_DELAY_SECONDS", db, int, default=60)
#             now = datetime.utcnow()
#             # Fetch new orders
#             new_orders = db.query(IncomingOrder).filter(IncomingOrder.status == 'new').all()
#             # Fetch retrying orders ready for retry
#             retrying_orders = db.query(IncomingOrder).filter(IncomingOrder.status == 'retrying').all()
#             orders_to_process = []
#             orders_to_process.extend(new_orders)
#             for inc in retrying_orders:
#                 backoff = retry_delay_base * (2 ** (inc.retry_count or 0))
#                 if inc.last_attempt_at and inc.last_attempt_at + timedelta(seconds=backoff) <= now:
#                     orders_to_process.append(inc)
#             for order in orders_to_process:
#                 logger.info(f"Queueing order ID {order.id} for processing.")
#                 process_order_task.delay(order.id)
#     except Exception as e:
#         logger.error(f"Error polling and queuing orders: {e}", exc_info=True)
# 
# # TODO: Define task for polling new/retrying orders (scheduler task)
# # @celery_app.task(name="backend.worker.tasks.poll_new_orders_task")
# # def poll_new_orders_task():
# #    logger.info("Polling for new or retrying orders...")
# #    with get_db_session() as db:
# #        # Query IncomingOrder for status='new' OR (status='retrying' AND retry_count < MAX_RETRIES AND last_attempt_at < now - backoff_delay)
# #        # ... complex query needed ...
# #        order_ids_to_process = [...] # Get list of IDs
# #        for order_id in order_ids_to_process:
# #            logger.info(f"Queueing order ID {order_id} for processing.")
# #            process_order_task.delay(order_id) # Send to the processing queue 