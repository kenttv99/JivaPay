"""API Router for TeamLead operations (manage traders)."""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Union

from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_teamlead
from backend.api_routers.common.teamlead_traders import router as common_teamlead_traders_router
from backend.database.utils import get_db_session
from backend.security import get_current_active_teamlead as security_get_current_active_teamlead
from backend.database.db import User, Trader
from backend.services import teamlead_service, requisite_service
from backend.services.permission_service import PermissionService
from backend.utils.exceptions import AuthorizationError, NotFoundError, OperationForbiddenError
import logging

# Import Pydantic schemas
from backend.schemas_enums.teamlead_schemas import (
    TeamLeadTraderBasicInfoSchema, 
    TraderTrafficStatusResponse,
    TeamOverallStatsSchema as TeamStatisticsSchema
)
from backend.schemas_enums.requisite import RequisiteOnlineStatsResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter(
    dependencies=[Depends(permission_required("teamlead"))]
)

# Mount common teamlead traders router under /traders
router.include_router(
    common_teamlead_traders_router,
    prefix="/traders",
    tags=["TeamLead Traders"]
)

@router.get("/managed-traders", response_model=List[TeamLeadTraderBasicInfoSchema])
async def list_managed_traders(
    db: Session = Depends(get_db_session),
    current_teamlead: User = Depends(security_get_current_active_teamlead)
):
    """
    Retrieves a list of traders managed by the current teamlead.
    Requires team:view:members_list permission.
    """
    try:
        return teamlead_service.get_managed_traders(session=db, current_teamlead_user=current_teamlead)
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in teamlead list_managed_traders: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving managed traders.")

@router.post("/managed-traders/{trader_id}/traffic", response_model=TraderTrafficStatusResponse)
async def set_trader_traffic_status(
    trader_id: int,
    enable: bool = Query(..., description="Set to true to enable traffic, false to disable"),
    db: Session = Depends(get_db_session),
    current_teamlead: User = Depends(security_get_current_active_teamlead),
):
    """
    Allows a TeamLead to enable or disable the 'is_traffic_enabled_by_teamlead' flag for a trader in their team.
    Requires team:manage:trader_traffic permission.
    """
    try:
        updated_trader = teamlead_service.set_trader_traffic_status_by_teamlead(
            session=db, 
            trader_id_to_manage=trader_id, 
            enable_traffic=enable, 
            current_teamlead_user=current_teamlead
        )
        return updated_trader
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OperationForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in teamlead set_trader_traffic_status: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating trader traffic status.")

@router.get("/requisites/online-stats", response_model=RequisiteOnlineStatsResponseSchema)
async def get_teamlead_online_requisites_stats(
    sort_by: Optional[str] = Query(None),
    sort_direction: Optional[str] = Query("asc"),
    trader_filter: Optional[Union[int, str]] = Query(None, description="Filter by Trader ID, email, or username from own team"),
    payment_method_id: Optional[int] = Query(None),
    bank_id: Optional[int] = Query(None),
    requisite_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_teamlead: User = Depends(security_get_current_active_teamlead)
):
    """
    Retrieves online requisites statistics for the current teamlead's team.
    Requires team:view:requisite_stats permission (checked in service layer based on role).
    """
    try:
        stats_data = requisite_service.get_online_requisites_stats(
            session=db,
            current_user=current_teamlead,
            sort_by=sort_by,
            sort_direction=sort_direction,
            trader_filter=trader_filter,
            payment_method_id=payment_method_id,
            bank_id=bank_id,
            requisite_type=requisite_type,
            page=page,
            per_page=per_page
        )
        return stats_data
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in teamlead get_online_requisites_stats: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving team requisite stats.")

@router.get("/team/statistics", response_model=TeamStatisticsSchema)
async def get_my_team_statistics(
    db: Session = Depends(get_db_session),
    current_teamlead: User = Depends(security_get_current_active_teamlead)
):
    """
    Retrieves aggregated statistics for the current teamlead's own team.
    Requires team:view:own_statistics permission.
    """
    try:
        return teamlead_service.get_team_statistics(session=db, current_teamlead_user=current_teamlead)
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in teamlead get_my_team_statistics: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving team statistics.")

# Import and include the auth router for teamlead login
from backend.api_routers.teamlead.auth import router as auth_teamlead_router
router.include_router(auth_teamlead_router, prefix="/auth", tags=["TeamLead - Authentication"]) 