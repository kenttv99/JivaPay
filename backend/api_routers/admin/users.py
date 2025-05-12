from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from backend.database.utils import get_db_session
from backend.security import get_current_active_user
from backend.database.db import User
from backend.shemas_enums.user import UserRead

router = APIRouter()

@router.get("/users", response_model=List[UserRead], summary="List all users for admin")
def list_users(
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_active_user)
) -> List[UserRead]:
    """Retrieve a list of all users; accessible to admins only."""
    # Ensure the current user has an admin profile
    if not getattr(current_user, 'admin_profile', None):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")
    users = db.query(User).options(selectinload(User.admin_profile)).all()
    return users 