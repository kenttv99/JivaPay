from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.utils import get_db_session
from backend.database.db import User
from backend.config.crypto import verify_password
from backend.config.logger import get_logger
from backend.shemas_enums import support_schemas

router = APIRouter()
logger = get_logger("support_auth")

@router.post("/auth/login")
def login_support(data: support_schemas.SupportLogin, db: Session = Depends(get_db_session)):
    user = db.query(User).filter_by(email=data.email).one_or_none()
    if not user or not user.support_profile or not verify_password(data.password, user.password_hash):
        logger.warning(f"Неудачная попытка входа саппорта: {data.email}")
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    support_profile = user.support_profile
    logger.info(f"Саппорт вошел: {user.email}")
    return {"id": support_profile.id, "email": user.email} 