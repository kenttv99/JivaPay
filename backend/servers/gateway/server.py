from fastapi import FastAPI
from backend.api_routers.gateway.router import router as gateway_router
from backend.api_routers.public_router import router as public_router
from backend.config.logger import get_logger
from backend.middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers

app = FastAPI(title="Gateway API")
register_exception_handlers(app)
logger = get_logger("gateway_server")

# Mount gateway endpoints
app.include_router(gateway_router, prefix="/gateway", tags=["gateway"])
# Mount reference data endpoints
app.include_router(public_router, prefix="/reference", tags=["reference"])

app.state.limiter = get_limiter()
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
# Log each request
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)

# Standard /health endpoint
add_health_endpoint(app)

logger.info("Gateway API server configured.") 