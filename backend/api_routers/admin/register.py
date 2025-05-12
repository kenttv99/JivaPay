from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db import Admin, Merchant, Support, User, Role
from backend.config.crypto import hash_password
from backend.config.logger import get_logger
from backend.shemas_enums import admin_schemas
from backend.database.utils import get_db_session

router = APIRouter()
logger = get_logger("admin_register")

# Use standard DB session dependency

@router.post("/register/merchant", status_code=201)
def register_merchant(data: admin_schemas.MerchantRegister, db: Session = Depends(get_db_session)):
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
def register_support(data: admin_schemas.SupportRegister, db: Session = Depends(get_db_session)):
    # Ensure email is unique across users
    if db.query(User).filter_by(email=data.email).first():
        logger.warning(f"Попытка регистрации саппорта с существующим email: {data.email}")
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    # Find support role
    role = db.query(Role).filter_by(name='support').one_or_none()
    if not role:
        raise HTTPException(status_code=500, detail="Роль support не найдена")
    # Create User
    user = User(email=data.email, password_hash=hash_password(data.password), role_id=role.id)
    db.add(user)
    db.flush()  # to get user.id
    # Create Support profile
    support_profile = Support(user_id=user.id, username=data.email)
    db.add(support_profile)
    db.commit()
    db.refresh(support_profile)
    logger.info(f"Саппорт зарегистрирован: {data.email}")
    return {"id": support_profile.id, "email": data.email} 