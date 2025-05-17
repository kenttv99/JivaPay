from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session, selectinload, joinedload

from backend.database.utils import get_db_session
from backend.common.permissions import permission_required
from backend.database.db import User, Admin, Support, TeamLead
from backend.schemas_enums.user import UserRead
from backend.services import user_service
from backend.services.permission_service import PermissionService
from backend.security import get_current_active_admin

router = APIRouter(
    prefix="/users",
    tags=["Admin - User Management"],
    dependencies=[Depends(get_current_active_admin)]
)

# --- Statistics Endpoints ---
@router.get("/admins/stats", response_model=Dict[str, Any])
async def get_administrators_statistics_admin_panel(
    availability_filter: Optional[str] = Query('available', description="Filter by availability: available, unavailable, all"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    return user_service.get_administrators_statistics(db, current_admin, availability_filter, page, per_page)

@router.get("/supports/stats", response_model=Dict[str, Any])
async def get_supports_statistics_admin_panel(
    status_filter: Optional[str] = Query('active', description="Filter by status: active, inactive, all"),
    role_description: Optional[str] = Query(None, description="Filter by role description (contains)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    return user_service.get_supports_statistics(db, current_admin, status_filter, role_description, page, per_page)

@router.get("/teamleads/stats", response_model=Dict[str, Any])
async def get_teamleads_statistics_admin_panel(
    status_filter: Optional[str] = Query('active', description="Filter by status: active, inactive, all"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    return user_service.get_teamleads_statistics(db, current_admin, status_filter, page, per_page)

# --- User Detail Endpoints (Admin, Support, TeamLead) ---
@router.get("/admin/{admin_user_id}/details", response_model=Any)
async def get_administrator_details_admin_panel(
    admin_user_id: int,
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    return user_service.get_administrator_details(db, admin_id_to_view=admin_user_id, current_admin_user=current_admin)

@router.get("/", response_model=List[UserRead], summary="List all users for admin (Basic)")
async def list_all_users_basic(
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    """Retrieve a basic list of all users; primarily for admins.
       Consider using more specific statistics endpoints for detailed role-based lists.
    """
    users = db.query(User).options(selectinload(User.admin_profile), selectinload(User.support_profile), selectinload(User.teamlead_profile)).all()
    return users

# --- Profile Update Endpoints ---
@router.put("/admin/{admin_user_id}/profile", response_model=Any)
async def update_administrator_profile_admin_panel(
    admin_user_id: int,
    profile_data: Dict[str, Any],
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    return user_service.update_administrator_profile(db, admin_id_to_update=admin_user_id, profile_data=profile_data, current_admin_user=current_admin)

# --- Permissions Management Endpoints ---
@router.get("/permissions/{target_user_id}/{target_role}", response_model=List[str])
async def get_user_permissions_admin_panel(
    target_user_id: int,
    target_role: str,
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    if target_role not in ["admin", "support", "teamlead"]:
        raise HTTPException(status_code=400, detail="Invalid target role specified.")
    
    perm_service = PermissionService(db)
    return perm_service.get_user_permissions(user_id=target_user_id, user_role=target_role)

@router.put("/permissions/{target_user_id}/{target_role}", status_code=status.HTTP_200_OK)
async def update_user_permissions_admin_panel(
    target_user_id: int,
    target_role: str,
    permissions_to_set: List[str] = Body(...),
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    if target_role not in ["admin", "support", "teamlead"]:
        raise HTTPException(status_code=400, detail="Invalid target role specified.")

    perm_service = PermissionService(db)
    success = perm_service.update_user_permissions(
        user_id=target_user_id, 
        user_role=target_role, 
        permissions_to_set=permissions_to_set, 
        current_admin_user=current_admin
    )
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to update permissions for user {target_user_id} ({target_role}).")
    return {"message": f"Permissions updated successfully for user {target_user_id} ({target_role})."} 