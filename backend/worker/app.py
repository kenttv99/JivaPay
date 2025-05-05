"""Celery application configuration for the JivaPay worker."""

import os
import logging
from celery import Celery
from kombu import Queue

logger = logging.getLogger(__name__)

# Read Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    logger.error("REDIS_URL environment variable not set. Celery cannot connect.")
    # Option 1: Raise an error to prevent worker start
    raise RuntimeError("REDIS_URL is required for Celery worker operation.")
    # Option 2: Set broker_url/result_backend to None or a dummy value, Celery might fail later
    # broker_url = None
    # result_backend = None
else:
    broker_url = REDIS_URL
    result_backend = REDIS_URL

# Define the Celery application instance
# The first argument is the conventional name of the main module
# We use 'backend.worker' as the base for task auto-discovery
celery_app = Celery(
    'backend.worker',
    broker=broker_url,
    backend=result_backend,
    include=['backend.worker.tasks'] # List of modules to import when the worker starts
)

# --- Celery Configuration --- #
# Using a dictionary for configuration settings
# See Celery docs for all available options: https://docs.celeryq.dev/en/stable/userguide/configuration.html
celery_app.conf.update(
    # --- Basic Settings --- #
    task_serializer='json',         # Use JSON for task serialization
    result_serializer='json',       # Use JSON for result serialization
    accept_content=['json'],        # Accept only JSON content
    timezone='UTC',                 # Use UTC timezone
    enable_utc=True,
    worker_concurrency=int(os.getenv('CELERY_WORKER_CONCURRENCY', '4')), # Default concurrency
    worker_prefetch_multiplier=int(os.getenv('CELERY_PREFETCH_MULTIPLIER', '1')), # Prefetch 1 task per worker process by default

    # --- Task Routing and Queues (Example) --- #
    # Define queues explicitly for better organization
    task_queues=(
        Queue('default', routing_key='task.default'),
        Queue('order_processing', routing_key='task.order_processing'),
        # Add other queues if needed (e.g., 'notifications', 'balance_updates')
    ),
    task_default_queue='default',
    task_default_exchange='tasks',
    task_default_routing_key='task.default',
    # Route specific tasks to specific queues
    task_routes=({
        'backend.worker.tasks.process_order_task': {
            'queue': 'order_processing',
            'routing_key': 'task.order_processing',
        },
        # Add routes for other tasks
        # 'backend.worker.tasks.update_balances_task': {
        #     'queue': 'balance_updates',
        #     'routing_key': 'task.balance_updates',
        # },
    }),

    # --- Reliability Settings --- #
    # Task execution settings
    task_acks_late=True,            # Acknowledge tasks *after* execution (requires idempotent tasks)
    task_reject_on_worker_lost=True,# Reject tasks if worker process crashes
    task_track_started=True,        # Track task start times

    # --- Broker Settings (Redis specific) --- #
    broker_transport_options={
        'visibility_timeout': 3600,  # Default: 1 hour. Time task is invisible after pickup
        # Consider adjusting based on expected max task duration + buffer
        'max_connections': int(os.getenv('CELERY_BROKER_MAX_CONNECTIONS', '10')),
        'socket_timeout': int(os.getenv('CELERY_BROKER_SOCKET_TIMEOUT', '10')),
        'socket_connect_timeout': int(os.getenv('CELERY_BROKER_CONNECT_TIMEOUT', '10')),
    },

    # --- Result Backend Settings --- #
    result_expires=int(os.getenv('CELERY_RESULT_EXPIRES', '3600')), # Keep results for 1 hour by default

    # --- Beat (Scheduler) Settings --- #
    # (Configuration for Celery Beat if used directly in this app)
    # beat_schedule = {
    #     'poll-new-orders': {
    #         'task': 'backend.worker.tasks.poll_new_orders_task', # Task defined in tasks.py
    #         'schedule': 60.0, # Run every 60 seconds
    #         'options': {'queue' : 'default'} # Run scheduler task on default queue
    #     },
    # }
)

logger.info("Celery application configured.")
logger.info(f"Broker URL: {celery_app.conf.broker_url}")
logger.info(f"Include tasks from: {celery_app.conf.include}")

# Optional: Autodiscover tasks from installed apps (if using Django structure)
# celery_app.autodiscover_tasks()

if __name__ == '__main__':
    # This allows running the worker directly using:
    # python -m backend.worker.app worker --loglevel=info
    celery_app.start() 