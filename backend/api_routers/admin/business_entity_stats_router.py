from typing import Dict, Any, Optional
from datetime import datetime # Добавлен импорт datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.utils import get_db_session
from backend.services import trader_service, merchant_service
from backend.security import get_current_active_admin
from backend.database.db import User # Required for current_admin type hint

router = APIRouter()

@router.get("/traders/stats", response_model=Dict[str, Any], summary="Get Traders Statistics for Admin Panel")
async def get_traders_statistics_admin_panel(
    status_filter: Optional[str] = Query(None, description="Filter by trader status (e.g., active, inactive)"), # Переименовано
    online_status: Optional[bool] = Query(None, description="Filter by online status"), # Переименовано is_online -> online_status, тип bool
    turnover_period_start: Optional[datetime] = Query(None, description="Start date for turnover period stats"), # Изменено
    turnover_period_end: Optional[datetime] = Query(None, description="End date for turnover period stats"),   # Изменено
    # currency_id: Optional[int] = Query(None, description="Filter by currency ID for turnover"), # Удалено, сервис не ожидает
    # payment_method_id: Optional[int] = Query(None, description="Filter by payment method ID"), # Удалено, сервис не ожидает
    search_query: Optional[str] = Query(None, description="Search by email, ID, telegram, phone"),
    sort_by: Optional[str] = Query(None, description="Sort by field (e.g., turnover, requisites_count)"),
    sort_direction: Optional[str] = Query("desc", description="Sort order (asc or desc)"), # Переименовано
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieve paginated and filtered statistics for traders.
    Admins can view comprehensive trader data.
    """
    return await trader_service.get_traders_statistics(
        session=db, # Параметр сессии в сервисе называется session
        current_user=current_admin,
        status_filter=status_filter,
        online_status=online_status,
        turnover_period_start=turnover_period_start,
        turnover_period_end=turnover_period_end,
        # currency_id and payment_method_id are not direct params for trader_service.get_traders_statistics
        # This service might handle them internally if search_query or other filters imply them,
        # or they might need to be added to the service function signature if required.
        # For now, they are removed from direct pass-through if not in service signature.
        search_query=search_query,
        sort_by=sort_by,
        sort_direction=sort_direction,
        page=page,
        per_page=per_page
    )

@router.get("/merchants/stats", response_model=Dict[str, Any], summary="Get Merchants Statistics for Admin Panel")
async def get_merchants_statistics_admin_panel(
    activity_status: Optional[str] = Query(None, description="Filter by merchant activity status (e.g., active, inactive)"),
    store_status: Optional[str] = Query(None, description="Filter by store status (e.g., active, inactive)"),
    search_query: Optional[str] = Query(None, description="Search by merchant name, email, store name"),
    sort_by: Optional[str] = Query(None, description="Sort by field (e.g., total_turnover, stores_count)"),
    sort_direction: Optional[str] = Query("desc", description="Sort order (asc or desc)"), # Переименовано sort_order
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieve paginated and filtered statistics for merchants and their stores.
    Admins can view comprehensive merchant data.
    """
    return await merchant_service.get_merchants_statistics(
        db=db, # В merchant_service тоже может быть session
        current_user=current_admin,
        activity_status=activity_status,
        store_status=store_status,
        search_query=search_query,
        sort_by=sort_by,
        sort_direction=sort_direction, # Переименовано
        page=page,
        per_page=per_page
    ) 