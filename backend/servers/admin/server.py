from fastapi import FastAPI
from backend.api_routers.admin import register
from backend.config.logger import get_logger
from backend.utils.health import add_health_endpoint
from backend.utils.exception_handlers import register_exception_handlers
from backend.api_routers.admin.auth import router as admin_auth_router
from backend.api_routers.admin.debug import router as admin_debug_router
from backend.api_routers.common.users import router as common_users_router
from backend.api_routers.common.requisites import router as common_requisites_router
from backend.api_routers.common.support_orders import router as common_support_orders_router
from backend.api_routers.common.configuration_router import router as common_settings_router
from backend.api_routers.common.admin_permissions import router as common_admin_permissions_router

app = FastAPI(title="Admin API")
register_exception_handlers(app)
logger = get_logger("admin_server")

app.include_router(register.router, prefix="/admin", tags=["admin"]) 
app.include_router(admin_auth_router, prefix="/admin", tags=["admin"])
app.include_router(admin_debug_router, prefix="/admin", tags=["debug"])
app.include_router(common_users_router, prefix="/admin/users", tags=["admin"])
app.include_router(common_requisites_router, prefix="/admin/requisites", tags=["admin"])
app.include_router(common_support_orders_router, prefix="/admin/support-orders", tags=["admin"])
app.include_router(common_settings_router, prefix="/admin/settings", tags=["admin"])
app.include_router(common_admin_permissions_router, prefix="/admin/permissions", tags=["admin"])

# Standard /health endpoint
add_health_endpoint(app) 