"""API Router for TeamLead operations (manage traders)."""

from fastapi import APIRouter, Depends
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_teamlead
from backend.api_routers.common.teamlead_traders import router as common_teamlead_traders_router

router = APIRouter(
    dependencies=[Depends(permission_required("teamlead"))]
)

# Mount common teamlead traders router under /traders
router.include_router(
    common_teamlead_traders_router,
    prefix="/traders",
    tags=["TeamLead Traders"]
) 