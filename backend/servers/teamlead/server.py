from fastapi import FastAPI
from backend.api_routers.teamlead.auth import router as auth_router
from backend.api_routers.teamlead.router import router as teamlead_router
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.config.logger import get_logger
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers

app = FastAPI(title="TeamLead API")
register_exception_handlers(app)
logger = get_logger("teamlead_server")

app.add_middleware(RequestLoggingMiddleware)

# Standard /health
add_health_endpoint(app)

# Mount routers
app.include_router(auth_router, prefix="/teamlead", tags=["teamlead"])
app.include_router(teamlead_router, prefix="/teamlead", tags=["teamlead"])

logger.info("TeamLead API server configured.") 