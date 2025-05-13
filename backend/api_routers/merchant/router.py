import logging
from fastapi import APIRouter, Depends
from backend.common.permissions import permission_required
from backend.api_routers.common.merchant_orders import router as common_merchant_orders_router
from backend.api_routers.common.stores import router as common_stores_router

logger = logging.getLogger(__name__)

router = APIRouter(
    dependencies=[Depends(permission_required("merchant"))]
)

# Mount common merchant orders router under /orders
router.include_router(common_merchant_orders_router, prefix="/orders", tags=["merchant_orders"])

# Mount common stores router under /stores
router.include_router(common_stores_router, prefix="/stores", tags=["merchant_stores"]) 