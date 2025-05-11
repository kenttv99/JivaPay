"""Authentication endpoints for TeamLead users."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.utils import get_db_session
from backend.database.db import TeamLead, User
from backend.config.crypto import verify_password
from backend.config.logger import get_logger
from backend.security import create_access_token
from backend.config.settings import settings

router = APIRouter()
logger = get_logger("teamlead_auth")


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/auth/token", response_model=Token, summary="TeamLead login for access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    """Authenticate teamlead and return JWT token."""
    user: User | None = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.teamlead_profile:
        logger.warning("Failed teamlead login attempt (not teamlead): %s", form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if not verify_password(form_data.password, user.password_hash):
        logger.warning("Failed teamlead login (bad password): %s", form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    logger.info("TeamLead logged in: %s", user.email)
    return {"access_token": access_token, "token_type": "bearer"} 