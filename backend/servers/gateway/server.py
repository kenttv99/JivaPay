from fastapi import FastAPI
from backend.api_routers.gateway.router import router as gateway_router
from backend.api_routers.public_router import router as public_router
from backend.config.logger import get_logger
from backend.middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(title="Gateway API")
logger = get_logger("gateway_server")

# Mount gateway endpoints
app.include_router(gateway_router, prefix="/gateway", tags=["gateway"])
# Mount reference data endpoints
app.include_router(public_router, prefix="/reference", tags=["reference"])

app.state.limiter = get_limiter()
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
app.add_middleware(SlowAPIMiddleware)

logger.info("Gateway API server configured.") 