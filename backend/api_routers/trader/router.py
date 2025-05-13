from fastapi import APIRouter, Depends
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_trader
from backend.api_routers.common.trader_orders import router as common_trader_orders_router

router = APIRouter(
    prefix="/trader",
    tags=["Trader Orders"],
    dependencies=[Depends(permission_required("trader"))]
)

# Mount common trader orders router under /orders
router.include_router(common_trader_orders_router, prefix="/orders", tags=["Trader Orders"]) 