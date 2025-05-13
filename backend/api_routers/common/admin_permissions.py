from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.database.utils import get_db_session, get_object_or_none, update_object_db
from backend.database.db import Admin, User
from backend.common.permissions import permission_required

# Schemas for admin permissions
class AdminPermissionsRead(BaseModel):
    id: int
    user_id: int
    can_manage_other_admins: bool
    can_manage_supports: bool
    can_manage_merchants: bool
    can_manage_traders: bool
    can_edit_system_settings: bool
    can_edit_limits: bool
    can_view_full_logs: bool
    can_handle_appeals: bool

    class Config:
        from_attributes = True

class AdminPermissionsUpdate(BaseModel):
    can_manage_other_admins: Optional[bool] = None
    can_manage_supports: Optional[bool] = None
    can_manage_merchants: Optional[bool] = None
    can_manage_traders: Optional[bool] = None
    can_edit_system_settings: Optional[bool] = None
    can_edit_limits: Optional[bool] = None
    can_view_full_logs: Optional[bool] = None
    can_handle_appeals: Optional[bool] = None

router = APIRouter()

@router.get(
    "/",
    response_model=List[AdminPermissionsRead],
    dependencies=[Depends(permission_required("permissions:read"))]
)
def list_admin_permissions(
    db: Session = Depends(get_db_session)
):
    """List permissions of all admin profiles."""
    return db.query(Admin).all()

@router.get(
    "/{admin_id}",
    response_model=AdminPermissionsRead,
    dependencies=[Depends(permission_required("permissions:read"))]
)
def get_admin_permissions(
    admin_id: int,
    db: Session = Depends(get_db_session)
):
    """Get permissions for a specific admin by ID."""
    admin = db.query(Admin).filter_by(id=admin_id).one_or_none()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin

@router.patch(
    "/{admin_id}",
    response_model=AdminPermissionsRead,
    dependencies=[Depends(permission_required("permissions:update"))]
)
def update_admin_permissions(
    admin_id: int,
    data: AdminPermissionsUpdate,
    db: Session = Depends(get_db_session)
):
    """Update permissions flags for a specific admin."""
    admin = db.query(Admin).filter_by(id=admin_id).one_or_none()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    update_data = data.dict(exclude_unset=True)
    updated = update_object_db(db, admin, update_data)
    db.commit()
    return updated 