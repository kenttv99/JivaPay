"""
API Router for Admin - Requisite Management and Statistics
"""
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.utils import get_db_session
from backend.services.requisite_service import get_online_requisites_stats
from backend.security import get_current_active_admin
from backend.database.db import User
from backend.services.permission_service import PermissionService
from backend.schemas_enums.requisite import RequisiteOnlineStatsResponseSchema
# TODO: Define Pydantic schemas (e.g., RequisiteOnlineStatsAdminResponseSchema) in schemas_enums/requisite.py

router = APIRouter(
    prefix="/requisites",
    tags=["Admin - Requisite Management"],
)

@router.get("/online-stats", response_model=RequisiteOnlineStatsResponseSchema)
async def get_admin_online_requisites_stats(
    sort_by: Optional[str] = Query(None, description="Sort by: limits_min, limits_max, direction"),
    sort_direction: Optional[str] = Query("asc", description="Sort direction: asc, desc"),
    trader_filter: Optional[Union[int, str]] = Query(None, description="Filter by Trader ID, email, or username"),
    payment_method_id: Optional[int] = Query(None),
    bank_id: Optional[int] = Query(None),
    requisite_type: Optional[str] = Query(None, description="Filter by type: pay_in or pay_out"),
    team_lead_id_filter: Optional[int] = Query(None, description="Filter by TeamLead ID (for admins)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieves statistics and a list of online requisites with advanced filtering and sorting options.
    Requires admin authentication and appropriate permissions (e.g., requisites:view:online_stats_all).
    """
    # perm_service = PermissionService(db)
    # if not perm_service.check_permission(current_admin.id, "admin", "requisites:view:online_stats_all"):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    stats_data = get_online_requisites_stats(
        session=db,
        current_user=current_admin,
        sort_by=sort_by,
        sort_direction=sort_direction,
        trader_filter=trader_filter,
        payment_method_id=payment_method_id,
        bank_id=bank_id,
        requisite_type=requisite_type,
        team_lead_id_filter=team_lead_id_filter, # Admin can use this to filter by a specific teamlead
        page=page,
        per_page=per_page
    )
    return stats_data

# TODO: Add endpoints for approving/rejecting requisites by admin if not covered elsewhere
# Example:
# @router.post("/{requisite_id}/approve", status_code=status.HTTP_200_OK)
# async def approve_requisite_admin(...):
# ... uses requisite_service.set_requisite_status(..., status="approve") ...

# @router.post("/{requisite_id}/reject", status_code=status.HTTP_200_OK)
# async def reject_requisite_admin(...):
# ... uses requisite_service.set_requisite_status(..., status="rejected") ... 