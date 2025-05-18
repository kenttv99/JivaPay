from fastapi import APIRouter

from .auth import router as auth_router
from .register import router as register_router # Assuming register.py contains an APIRouter named router
from .users import router as users_router # Assuming users.py contains an APIRouter named router
from .debug import router as debug_router # Assuming debug.py contains an APIRouter named router

# Import new routers
from .platform_stats_router import router as platform_stats_router
from .order_management_router import router as order_management_router
from .requisite_management_router import router as requisite_management_router
from .business_entity_stats_router import router as business_entity_stats_router
# TODO: Add system_logs_router when created

admin_api_router = APIRouter()

admin_api_router.include_router(auth_router, prefix="/auth", tags=["Admin Authentication"])
admin_api_router.include_router(register_router, prefix="/register", tags=["Admin Registration"])
admin_api_router.include_router(users_router, prefix="/users-management", tags=["Admin User Management"]) # Changed prefix for clarity
admin_api_router.include_router(debug_router, prefix="/debug", tags=["Admin Debug"])

admin_api_router.include_router(platform_stats_router, prefix="/stats", tags=["Admin Platform Statistics"]) # Mounted under /stats/platform
admin_api_router.include_router(order_management_router, prefix="/orders", tags=["Admin Order Management"]) # Mounted under /orders
admin_api_router.include_router(requisite_management_router, prefix="/requisites", tags=["Admin Requisite Management"]) # Mounted under /requisites
admin_api_router.include_router(business_entity_stats_router, tags=["Admin Business Entity Statistics"])

# Example for a potential system logs router
# from .system_logs_router import router as system_logs_router
# admin_api_router.include_router(system_logs_router, prefix="/logs", tags=["Admin System Logs"]) 