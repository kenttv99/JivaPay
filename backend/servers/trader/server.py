from fastapi import FastAPI
from backend.api_routers.trader.auth import router as auth_router
from backend.api_routers.trader.router import router as trader_router
from backend.config.logger import get_logger
from backend.middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers

app = FastAPI(title="Trader API")
register_exception_handlers(app)
logger = get_logger("trader_server")

app.include_router(auth_router, prefix="/trader", tags=["trader"])
app.include_router(trader_router, prefix="/trader", tags=["trader"])

app.state.limiter = get_limiter()
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
# Log each request
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)

# Standard /health endpoint
add_health_endpoint(app) 