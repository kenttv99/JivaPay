from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from pydantic import BaseModel
from datetime import timedelta

from backend.database.db import User
from backend.config.crypto import verify_password
from backend.config.logger import get_logger
from backend.database.utils import get_async_db_session
from backend.security import create_access_token
from backend.config.settings import settings

router = APIRouter()
logger = get_logger("merchant_auth")


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db_session)
):
    query = (
        select(User)
        .options(selectinload(User.merchant_profile))
        .filter(User.email == form_data.username)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not user.merchant_profile or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Failed merchant login attempt: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"Merchant logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"} 