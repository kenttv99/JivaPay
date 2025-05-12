"""Authentication endpoints for Admin users."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel

from backend.database.utils import get_db_session
from backend.database.db import Admin, User
from backend.config.crypto import verify_password
from backend.config.logger import get_logger
from backend.security import create_access_token
from backend.config.settings import settings

router = APIRouter()
logger = get_logger("admin_auth")


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/auth/token", response_model=Token, summary="Admin login for access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    """Authenticate admin via email/password and return JWT Bearer token."""
    # Admins are linked to User via admin_profile relationship
    user: User | None = db.query(User).options(selectinload(User.admin_profile)).filter(User.email == form_data.username).first()
    if not user or not user.admin_profile:
        logger.warning("Failed admin login attempt (user not admin?): %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        logger.warning("Failed admin login (bad password): %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info("Admin logged in: %s", user.email)
    return {"access_token": access_token, "token_type": "bearer"} 