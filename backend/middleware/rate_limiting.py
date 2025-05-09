"""Rate Limiting middleware using slowapi and Redis."""

import logging
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import RateLimitExceeded  # Re-export for clarity in main.py
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.database.utils import get_db_session
from backend.utils.config_loader import get_typed_config_value

logger = logging.getLogger(__name__)

# --- Limiter Configuration --- #

# Read Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    logger.warning("REDIS_URL environment variable not set. Rate limiting might not function correctly.")
    # Optionally, fallback to in-memory storage for development/testing, but Redis is preferred
    # limiter = Limiter(key_func=get_remote_address)
    # raise ConfigurationError("REDIS_URL is required for rate limiting") # Or raise error
    storage_uri = "memory://" # Fallback to memory if needed, but log warning
else:
    storage_uri = REDIS_URL

# Read default rate limit from DB configuration
def get_default_rate_limit() -> str:
    """Fetch the default rate limit from DB (RATE_LIMIT_DEFAULT key)."""
    with get_db_session() as db:
        # default format: "100/minute"
        limit = get_typed_config_value("RATE_LIMIT_DEFAULT", db, str, default="100/minute")
    return limit

# Configure limiter without default_limits, use get_limiter instead
# limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)

# --- Custom Exception Handler (Optional but Recommended) --- #

def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler to return a JSON response for 429 Too Many Requests."""
    logger.warning(f"Rate limit exceeded for {request.client.host} on {request.url.path}. Limit: {exc.detail}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "error": "Too Many Requests"
        }
    )

# --- Functions to be used in main.py --- #

def get_limiter() -> Limiter:
    """Returns a Limiter instance configured with default limits from DB."""
    default_limit = get_default_rate_limit()
    return Limiter(key_func=get_remote_address, storage_uri=storage_uri, default_limits=[default_limit])

def get_rate_limit_exceeded_handler():
    """Returns the custom rate limit exception handler."""
    return custom_rate_limit_exceeded_handler

# The SlowAPIMiddleware needs to be added in main.py
# Example in main.py:
# from backend.middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded
# app = FastAPI()
# app.state.limiter = get_limiter()
# app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
# app.add_middleware(SlowAPIMiddleware)

# Applying limits:
# 1. Globally (in main.py or here if desired, requires app instance):
#    app.state.limiter.limit("100/minute")(app) # Not recommended here
# 2. On Routers (in api_router files):
#    from fastapi import Depends
#    from backend.middleware.rate_limiting import get_limiter
#    limiter = get_limiter()
#    router = APIRouter(dependencies=[Depends(limiter.limit("50/minute"))])
# 3. On specific endpoints:
#    @router.post("/resource", dependencies=[Depends(limiter.limit("10/second"))])
#    async def create_resource(...):
#        ...

# TODO: Integrate reading default/specific limits from the database using config_loader
#       Instead of hardcoding "100/minute" etc., fetch keys like RATE_LIMIT_DEFAULT

# Applying limits:
# 1. Globally (in main.py or here if desired, requires app instance):
#    app.state.limiter.limit("100/minute")(app) # Not recommended here
# 2. On Routers (in api_router files):
#    from fastapi import Depends
#    from backend.middleware.rate_limiting import get_limiter
#    limiter = get_limiter()
#    router = APIRouter(dependencies=[Depends(limiter.limit("50/minute"))])
# 3. On specific endpoints:
#    @router.post("/resource", dependencies=[Depends(limiter.limit("10/second"))])
#    async def create_resource(...):
#        ...

# TODO: Integrate reading default/specific limits from the database using config_loader
#       Instead of hardcoding "100/minute" etc., fetch keys like RATE_LIMIT_DEFAULT 