from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db import Admin, Merchant, Support
from backend.config.crypto import hash_password
from backend.config.logger import get_logger
from backend.database.db import Base
from backend.shemas_enums import admin_schemas
from backend.database import db

router = APIRouter()
logger = get_logger("admin_register")

# Dependency для получения сессии БД

def get_db():
    from backend.database.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register/merchant", status_code=201)
def register_merchant(data: admin_schemas.MerchantRegister, db: Session = Depends(get_db)):
    if db.query(Merchant).filter_by(email=data.email).first():
        logger.warning(f"Попытка регистрации мерчанта с существующим email: {data.email}")
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    merchant = Merchant(email=data.email, password_hash=hash_password(data.password))
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    logger.info(f"Мерчант зарегистрирован: {merchant.email}")
    return {"id": merchant.id, "email": merchant.email}

@router.post("/register/support", status_code=201)
def register_support(data: admin_schemas.SupportRegister, db: Session = Depends(get_db)):
    if db.query(Support).filter_by(email=data.email).first():
        logger.warning(f"Попытка регистрации саппорта с существующим email: {data.email}")
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    support = Support(email=data.email, password_hash=hash_password(data.password), access_to=data.access_to)
    db.add(support)
    db.commit()
    db.refresh(support)
    logger.info(f"Саппорт зарегистрирован: {support.email}")
    return {"id": support.id, "email": support.email} 