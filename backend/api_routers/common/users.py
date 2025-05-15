from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from backend.database.utils import get_db_session, create_object, update_object_db, get_object_or_none
from backend.database.db import User
from backend.schemas_enums.user import UserCreate, UserRead
from backend.common.permissions import permission_required
from backend.security import get_current_active_user

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

router = APIRouter()

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required("users:create"))]
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new user."""
    # Check email uniqueness
    if db.query(User).filter_by(email=user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    data = user_data.dict()
    obj = create_object(db, User, data)
    db.commit()
    return obj

@router.get(
    "/",
    response_model=List[UserRead],
    dependencies=[Depends(permission_required("users:read"))]
)
def list_users(
    db: Session = Depends(get_db_session)
):
    """List all users."""
    return db.query(User).all()

@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(permission_required("users:read"))]
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db_session)
):
    """Get details of a user by ID."""
    user = get_object_or_none(db, User, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(permission_required("users:update"))]
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db_session)
):
    """Update user attributes."""
    user = get_object_or_none(db, User, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = user_update.dict(exclude_unset=True)
    updated = update_object_db(db, user, update_data)
    db.commit()
    return updated

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(permission_required("users:delete"))]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db_session)
):
    """Delete a user by ID."""
    user = get_object_or_none(db, User, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit() 