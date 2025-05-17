"""
API Router for Admin - Order Management and Statistics
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.utils import get_db_session
from backend.services.order_service import get_orders_history, get_orders_count
from backend.security import get_current_active_admin
from backend.database.db import User
from backend.services.permission_service import PermissionService # For explicit permission checks
from backend.schemas_enums.order import OrderHistoryAdminResponseSchema, OrderCountResponseSchema # Added import
# TODO: Define Pydantic schemas for request query params and response models in schemas_enums/order.py
# from backend.schemas_enums.order import OrderHistoryAdminResponseSchema, OrderCountResponseSchema, OrdersHistoryQueryAdminSchema

router = APIRouter(
    prefix="/orders",
    tags=["Admin - Order Management"],
)

# Dependency for Pydantic query parameters (example, define properly in schemas)
# class OrdersHistoryQueryParams(BaseModel):
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] = None
#     status: Optional[str] = None
#     amount: Optional[Decimal] = None
#     trader_id: Optional[int] = None
#     store_id: Optional[int] = None
#     requisite_identifier: Optional[str] = None
#     user_query: Optional[str] = None
#     page: int = Query(1, ge=1)
#     per_page: int = Query(20, ge=1, le=100)

@router.get("/history", response_model=OrderHistoryAdminResponseSchema) # Changed from Dict[str, Any]
async def get_admin_orders_history(
    # params: OrdersHistoryQueryParams = Depends(), # Use Pydantic model for query params
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
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieves a paginated history of all orders with advanced filtering for administrators.
    Requires admin authentication and appropriate permissions (e.g., orders:view:any_list).
    """
    # Explicit permission check (can also be a separate dependency)
    # perm_service = PermissionService(db)
    # if not perm_service.check_permission(current_admin.id, "admin", "orders:view:any_list"):
    #     raise HTTPException(status_code=403, detail="Not enough permissions to view order history")

    # Pass current_admin to the service layer for any further permission-based filtering within the service
    history_data = get_orders_history(
        session=db, 
        current_user=current_admin, 
        start_time=start_time, #params.start_time,
        end_time=end_time, #params.end_time,
        status=status, #params.status,
        amount=amount, #params.amount,
        trader_id=trader_id, #params.trader_id,
        store_id=store_id, #params.store_id,
        requisite_identifier=requisite_identifier, #params.requisite_identifier,
        user_query=user_query, #params.user_query,
        page=page, #params.page,
        per_page=per_page #params.per_page
    )
    return history_data

@router.get("/count", response_model=OrderCountResponseSchema) # Changed from Dict[str, int]
async def get_admin_orders_count(
    status: Optional[str] = Query(None),
    date_start: Optional[datetime] = Query(None),
    date_end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieves the total count of orders, filterable by status and date range for administrators.
    Requires admin authentication and appropriate permissions (e.g., orders:view:count_total).
    """
    # perm_service = PermissionService(db)
    # if not perm_service.check_permission(current_admin.id, "admin", "orders:view:count_total"):
    #     raise HTTPException(status_code=403, detail="Not enough permissions to count orders")

    count = get_orders_count(
        session=db, 
        current_user=current_admin,
        status=status, 
        date_start=date_start, 
        date_end=date_end
    )
    return {"total_orders_count": count} 