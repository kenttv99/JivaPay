from fastapi import FastAPI
# from backend.api_routers.teamlead.auth import router as auth_router # No longer needed if part of teamlead_api_router
# from backend.api_routers.teamlead.router import router as teamlead_router # No longer needed if part of teamlead_api_router
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.config.logger import get_logger
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers

# Import the main teamlead router
from backend.api_routers.teamlead import teamlead_api_router

app = FastAPI(title="TeamLead API")
register_exception_handlers(app)
logger = get_logger("teamlead_server")

app.add_middleware(RequestLoggingMiddleware)

# Standard /health
add_health_endpoint(app)

# Mount the consolidated teamlead_api_router
# The prefixes defined within teamlead_api_router and its included routers will apply
# The prefix for teamlead_data_router itself is /teamlead
app.include_router(teamlead_api_router, prefix="/api") # Main prefix /api, then /teamlead from router itself

logger.info("TeamLead API server configured.") 