from fastapi import FastAPI
# from backend.api_routers.admin import register # No longer needed directly if part of admin_api_router
from backend.config.logger import get_logger
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers

# Import the main admin router
from backend.api_routers.admin import admin_api_router

app = FastAPI(title="Admin API")
register_exception_handlers(app)
logger = get_logger("admin_server")

# Mount the consolidated admin_api_router
# The prefixes defined within admin_api_router and its included routers will apply
app.include_router(admin_api_router, prefix="/api/admin") # Main prefix for all admin routes

# Standard /health endpoint
add_health_endpoint(app) 