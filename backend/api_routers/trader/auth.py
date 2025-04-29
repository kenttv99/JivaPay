from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import Trader
from backend.config.crypto import verify_password
from backend.config.logger import get_logger
from backend.shemas_enums import trader_schemas

router = APIRouter()
logger = get_logger("trader_auth")

def get_db():
    from backend.database.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/login")
def login_trader(data: trader_schemas.TraderLogin, db: Session = Depends(get_db)):
    user = db.query(Trader).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        logger.warning(f"Неудачная попытка входа трейдера: {data.email}")
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    logger.info(f"Трейдер вошел: {user.email}")
    return {"id": user.id, "email": user.email} 