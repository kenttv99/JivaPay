"""
API Router for Support Users
"""
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from backend.database.utils import get_db_session
from backend.services import order_service, requisite_service, trader_service # Import relevant services
from backend.security import get_current_active_support # Specific support dependency
from backend.database.db import User
from backend.services.permission_service import PermissionService
from backend.schemas_enums.order import OrderHistoryAdminResponseSchema
from backend.schemas_enums.requisite import RequisiteOnlineStatsResponseSchema
from backend.schemas_enums.trader import TraderStatisticsResponseSchema
from backend.utils.exceptions import AuthorizationError
# TODO: Define Pydantic schemas for responses in schemas_enums/support.py or reuse from admin if identical structure

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/support", # Prefix for all support routes
    tags=["Support"],
    dependencies=[Depends(get_current_active_support)] # Ensures user is an active support agent
)

@router.get("/orders/history", response_model=OrderHistoryAdminResponseSchema)
async def get_support_orders_history(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    amount: Optional[Decimal] = Query(None),
    trader_id: Optional[int] = Query(None),
    store_id: Optional[int] = Query(None),
    requisite_identifier: Optional[str] = Query(None),
    user_query: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_support_user: User = Depends(get_current_active_support)
):
    """
    Retrieves order history for support agents.
    The data returned is filtered based on the support agent's specific permissions.
    """
    # PermissionService.check_permission for "orders:view:limited_list" or similar is done 
    # by get_orders_history service internally based on current_support_user's role and permissions.
    try:
        history_data = order_service.get_orders_history(
            session=db, 
            current_user=current_support_user, # Crucial for permission-based filtering in the service
            start_time=start_time,
            end_time=end_time,
            status=status,
            amount=amount,
            trader_id=trader_id,
            store_id=store_id,
            requisite_identifier=requisite_identifier,
            user_query=user_query,
            page=page,
            per_page=per_page
        )
        return history_data
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in support get_orders_history: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving order history.")

@router.get("/requisites/online-stats", response_model=RequisiteOnlineStatsResponseSchema)
async def get_support_online_requisites_stats(
    sort_by: Optional[str] = Query(None),
    sort_direction: Optional[str] = Query("asc"),
    trader_filter: Optional[Union[int, str]] = Query(None),
    payment_method_id: Optional[int] = Query(None),
    bank_id: Optional[int] = Query(None),
    requisite_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_support_user: User = Depends(get_current_active_support)
):
    """
    Retrieves online requisites statistics for support agents, if permitted.
    """
    # PermissionService.check_permission for "requisites:view:online_stats_limited" or similar
    # is handled by get_online_requisites_stats service internally.
    try:
        stats_data = requisite_service.get_online_requisites_stats(
            session=db,
            current_user=current_support_user,
            sort_by=sort_by,
            sort_direction=sort_direction,
            trader_filter=trader_filter,
            payment_method_id=payment_method_id,
            bank_id=bank_id,
            requisite_type=requisite_type,
            page=page,
            per_page=per_page
            # team_lead_id_filter is not typically for support unless specifically granted
        )
        return stats_data
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in support get_online_requisites_stats: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving requisite stats.")

@router.get("/traders/stats", response_model=TraderStatisticsResponseSchema)
async def get_support_traders_statistics(
    status_filter: Optional[str] = Query('active'),
    online_status: Optional[str] = Query(None),
    # Support users might have limited access to turnover or other sensitive stats
    # turnover_period_start: Optional[datetime] = Query(None),
    # turnover_period_end: Optional[datetime] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_direction: Optional[str] = Query("asc"),
    search_query: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_support_user: User = Depends(get_current_active_support)
):
    """
    Retrieves trader statistics for support agents, if permitted (potentially limited view).
    """
    # PermissionService.check_permission for "traders:view:limited_stats" or similar
    # is handled by get_traders_statistics service internally.
    try:
        stats_data = trader_service.get_traders_statistics(
            session=db,
            current_user=current_support_user,
            status_filter=status_filter,
            online_status=online_status,
            # Pass None for params support might not have access to, let service handle defaults or raise error
            turnover_period_start=None, 
            turnover_period_end=None,
            sort_by=sort_by,
            sort_direction=sort_direction,
            search_query=search_query,
            page=page,
            per_page=per_page
        )
        return stats_data
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in support get_traders_statistics: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving trader stats.")

# TODO: Add endpoints for viewing specific order details, user details (read-only)
# These will also need to pass current_support_user to service layer for permission checks.
# Example: 
# @router.get("/orders/{order_id}", response_model=OrderDetailsSchema)
# async def get_support_order_details(order_id: int, ...):
#    return order_service.get_order_details_for_support(session, current_support_user, order_id) 