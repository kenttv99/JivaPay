"""Authentication endpoints for TeamLead users."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.utils import get_db_session
from backend.database.db import User
from backend.config.logger import get_logger
from backend.security import create_access_token
from backend.config.settings import settings
from backend.services import user_service
from backend.utils.exceptions import AuthenticationError

router = APIRouter()
logger = get_logger("teamlead_auth")


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token, summary="TeamLead login for access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    """Authenticate teamlead and return JWT token."""
    try:
        user = user_service.authenticate_user(
            db_session=db,
            email=form_data.username,
            password=form_data.password
        )
    except AuthenticationError as e:
        logger.warning(f"TeamLead authentication failed for {form_data.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.teamlead_profile or user.role.name != "teamlead":
        logger.warning(f"Authenticated user {form_data.username} (Role: {user.role.name}) is not a TeamLead or does not have a teamlead profile.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized as a TeamLead",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": "teamlead"},
        expires_delta=access_token_expires
    )
    logger.info(f"TeamLead logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"} 