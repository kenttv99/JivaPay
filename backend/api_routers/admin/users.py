from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from backend.database.utils import get_db_session
from backend.common.permissions import permission_required
from backend.database.db import User
from backend.schemas_enums.user import UserRead

router = APIRouter(
    dependencies=[Depends(permission_required("admin"))]
)

@router.get("/users", response_model=List[UserRead], summary="List all users for admin")
def list_users(
    db: Session = Depends(get_db_session),
    current_user=Depends(permission_required("admin"))
) -> List[UserRead]:
    """Retrieve a list of all users; accessible to admins only."""
    users = db.query(User).options(selectinload(User.admin_profile)).all()
    return users 