from fastapi import FastAPI
# from backend.api_routers.support import auth # No longer needed directly if part of support_api_router
from backend.config.logger import get_logger
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers

# Import the main support router
from backend.api_routers.support import support_api_router

app = FastAPI(title="Support API")
register_exception_handlers(app)
logger = get_logger("support_server")

app.add_middleware(RequestLoggingMiddleware)

# Mount the consolidated support_api_router
# The prefixes defined within support_api_router and its included routers will apply
# The prefix for support_data_router itself is already /support
app.include_router(support_api_router, prefix="/api") # Main prefix /api, then /support from router itself

# Standard /health endpoint
add_health_endpoint(app) 