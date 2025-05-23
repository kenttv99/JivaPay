from fastapi import FastAPI
from backend.api_routers.merchant.auth import router as auth_router
from backend.api_routers.merchant.router import router as merchant_router
from backend.config.logger import get_logger
from backend.middleware.rate_limiting import get_limiter, get_rate_limit_exceeded_handler, RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware

app = FastAPI(title="Merchant API")
logger = get_logger("merchant_server")

app.state.limiter = get_limiter()
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router, prefix="/merchant", tags=["merchant"])
app.include_router(merchant_router, prefix="/merchant", tags=["merchant"]) 