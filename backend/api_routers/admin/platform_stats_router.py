"""
API Router for Admin - Platform Statistics
"""
from typing import List, Dict, Union
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.utils import get_db_session
from backend.services.platform_service import PlatformService
from backend.security import get_current_active_admin # Specific admin dependency
from backend.database.db import User # For type hinting current_user
from backend.schemas_enums.platform import PlatformBalanceResponseSchema # Added import
# from backend.schemas_enums.platform import PlatformBalanceItemSchema # TODO: Create and use this schema

router = APIRouter(
    prefix="/platform",
    tags=["Admin - Platform Statistics"],
)

@router.get("/balance", response_model=PlatformBalanceResponseSchema) # Changed from List[Dict[...]]
async def get_platform_balance_stats(
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieves the aggregated balance of the platform across all currencies.
    
    Requires admin authentication and permission: `platform:view:balance` (checked by service or decorator later).
    """
    # Permission check should ideally be here or as a separate dependency
    # For now, assuming get_current_active_admin is a basic check and service might do more, 
    # or a decorator-based permission system will be added.
    # Example if PermissionService is used directly here:
    # perm_service = PermissionService(db)
    # if not perm_service.check_permission(current_admin.id, "admin", "platform:view:balance"):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    platform_service = PlatformService(db_session=db)
    balances = platform_service.get_platform_balances()
    return balances 