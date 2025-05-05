"""Main FastAPI application entry point for JivaPay backend."""

import logging
import logging.config
import os

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

# --- Import Utilities and Routers --- #
# (Add imports for your routers as they are created)
# from backend.api_routers import auth_router, merchant_router, trader_router, admin_router, gateway_router
try:
    from backend.utils.notifications import initialize_sentry, report_critical_error
    from backend.utils.exceptions import JivaPayException
    from backend.middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded, SlowAPIMiddleware
except ImportError:
    # Adjust paths if needed
    from .utils.notifications import initialize_sentry, report_critical_error
    from .utils.exceptions import JivaPayException
    from .middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded, SlowAPIMiddleware

# --- Basic Logging Configuration --- #
# TODO: Enhance logging configuration (e.g., read from file, structured logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Initialize Sentry (Call early) --- #
initialize_sentry()

# --- Create FastAPI App --- #
app = FastAPI(
    title="JivaPay API",
    description="Backend API for the JivaPay Payment System",
    version="0.1.0",
    # Add other FastAPI options like docs_url, redoc_url if needed
)

# --- Configure Rate Limiting --- #
limiter = get_limiter()
app.state.limiter = limiter # Make limiter accessible in dependencies/routers if needed
# Add the custom handler for RateLimitExceeded BEFORE the generic Exception handler
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
# Add the SlowAPIMiddleware
app.add_middleware(SlowAPIMiddleware)

# --- Global Exception Handlers --- #

@app.exception_handler(JivaPayException)
async def jiva_pay_exception_handler(request: Request, exc: JivaPayException):
    """Handles custom application exceptions."""
    logger.warning(f"Handled JivaPayException: {exc.message} (Status: {exc.status_code}) Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error": exc.__class__.__name__},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors for incoming requests."""
    # Log the detailed validation errors
    logger.warning(f"Request validation failed: {exc.errors()} Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": exc.errors()},
    )

@app.exception_handler(ValidationError) # Catch Pydantic validation errors not tied to requests (e.g., in responses)
async def generic_validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Generic validation error: {exc.errors()} Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal validation error occurred.", "error": "ValidationError"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handles any other unhandled exceptions."""
    # Log the error and report to Sentry
    logger.error(f"Unhandled exception occurred: {exc} Path: {request.url.path}", exc_info=True)
    report_critical_error(exc, context_message="Unhandled exception in generic handler", request_path=str(request.url.path))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred.", "error": "InternalServerError"},
    )

# --- Health Check Endpoint --- #

@app.get("/health", tags=["Health"], summary="Perform a Health Check")
def health_check():
    """Returns a simple health check response."""
    return {"status": "OK"}

# --- Include API Routers --- #
# (Uncomment and add routers as they are created)
# app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(merchant_router.router, prefix="/api/merchant", tags=["Merchant"])
# app.include_router(trader_router.router, prefix="/api/trader", tags=["Trader"])
# app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])
# app.include_router(gateway_router.router, prefix="/api/gateway", tags=["Gateway"])

# --- Application Startup Logic (Example) --- #
# @app.on_event("startup")
# async def startup_event():
#     logger.info("Application startup...")
#     # Connect to database, load resources, etc.
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     logger.info("Application shutdown...")
#     # Disconnect from database, release resources, etc.
#     pass

logger.info("FastAPI application configured.")

# To run the app (using uvicorn):
# uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 