from fastapi import FastAPI
from backend.api_routers.admin import register
from backend.config.logger import get_logger
from backend.utils.health import add_health_endpoint
from backend.api_routers.admin.auth import router as admin_auth_router
from backend.api_routers.admin.debug import router as admin_debug_router
from backend.api_routers.admin.users import router as admin_users_router

app = FastAPI(title="Admin API")
logger = get_logger("admin_server")

app.include_router(register.router, prefix="/admin", tags=["admin"]) 
app.include_router(admin_auth_router, prefix="/admin", tags=["admin"])
app.include_router(admin_debug_router, prefix="/admin", tags=["debug"])
app.include_router(admin_users_router, prefix="/admin", tags=["admin"])

# Standard /health endpoint
add_health_endpoint(app) 