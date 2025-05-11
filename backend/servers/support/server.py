from fastapi import FastAPI
from backend.api_routers.support import auth
from backend.config.logger import get_logger
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.utils.health import add_health_endpoint

app = FastAPI(title="Support API")
logger = get_logger("support_server")

app.add_middleware(RequestLoggingMiddleware)
app.include_router(auth.router, prefix="/support", tags=["support"])

# Standard /health endpoint
add_health_endpoint(app) 