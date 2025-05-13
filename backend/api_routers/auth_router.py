from fastapi import APIRouter

from backend.api_routers.merchant.auth import router as merchant_auth
from backend.api_routers.trader.auth import router as trader_auth
from backend.api_routers.support.auth import router as support_auth
from backend.api_routers.teamlead.auth import router as teamlead_auth
from backend.api_routers.admin.register import router as admin_register

# Unified Auth Router
router = APIRouter()

# Include individual auth routers
router.include_router(merchant_auth, prefix="/merchant", tags=["merchant"])
router.include_router(trader_auth, prefix="/trader", tags=["trader"])
router.include_router(support_auth, prefix="/support", tags=["support"])
router.include_router(teamlead_auth, prefix="/teamlead", tags=["teamlead"])
router.include_router(admin_register, prefix="/admin", tags=["admin"]) 