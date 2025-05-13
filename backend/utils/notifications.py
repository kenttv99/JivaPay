"""Utility for sending notifications, primarily for error reporting."""

import logging
import os
from typing import Dict, Any

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Attempt to import custom exceptions
from backend.utils.exceptions import JivaPayException

logger = logging.getLogger(__name__)

def initialize_sentry():
    """Initializes the Sentry SDK based on environment configuration."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development") # e.g., development, staging, production

    if not sentry_dsn:
        logger.warning("SENTRY_DSN environment variable not set. Sentry reporting is disabled.")
        return

    try:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                sentry_logging,
                FastApiIntegration(),
                SqlalchemyIntegration(),
                # Add other integrations like CeleryIntegration, RedisIntegration if needed
            ],
            environment=environment,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")), # Sample 10% by default
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions. Adjust in production.
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")), # Sample 10% by default
            send_default_pii=False # Do not send Personally Identifiable Information by default
        )
        logger.info(f"Sentry SDK initialized for environment: {environment}")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry SDK: {e}", exc_info=True)

def report_critical_error(exception: Exception, context_message: str = "", **kwargs: Any):
    """Sends an exception report to Sentry with optional context.

    Args:
        exception: The exception object to report.
        context_message: An additional message describing the context of the error.
        **kwargs: Additional key-value pairs to add as context (tags or extra data).
    """
    if not sentry_sdk.is_initialized():
        logger.warning(f"Sentry not initialized. Skipping error report for: {exception}")
        return

    try:
        with sentry_sdk.push_scope() as scope:
            if context_message:
                scope.set_extra("context_message", context_message)

            # Separate known JivaPay exceptions from unexpected ones
            if isinstance(exception, JivaPayException):
                scope.set_tag("error_type", "jiva_pay_handled")
                scope.set_level("warning") # Or keep as error depending on severity
            else:
                scope.set_tag("error_type", "unhandled")
                scope.set_level("error")

            # Add extra context provided in kwargs
            for key, value in kwargs.items():
                # Decide if it should be a tag (indexed, searchable) or extra (more details)
                if isinstance(value, (str, int, float, bool)) and len(str(value)) < 200: # Sentry tag value limit
                    scope.set_tag(key, value)
                else:
                    scope.set_extra(key, value)

            sentry_sdk.capture_exception(exception)
            logger.debug(f"Reported exception to Sentry: {exception}")

    except Exception as report_exc:
        # Log the failure to report, but don't let it crash the main flow
        logger.error(f"Failed to report exception to Sentry: {report_exc}", exc_info=True)
        # Also log the original exception that failed to report
        logger.error(f"Original exception that failed Sentry reporting: {exception}", exc_info=True)

# Call initialize_sentry() early in your application startup process
# For FastAPI, this could be in main.py before creating the app or using an event handler.
# Example: initialize_sentry()
