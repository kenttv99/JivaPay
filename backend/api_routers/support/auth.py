from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import Support
from backend.config.crypto import verify_password
from backend.config.logger import get_logger
from backend.shemas_enums import support_schemas

router = APIRouter()
logger = get_logger("support_auth")

def get_db():
    from backend.database.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/login")
def login_support(data: support_schemas.SupportLogin, db: Session = Depends(get_db)):
    user = db.query(Support).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        logger.warning(f"Неудачная попытка входа саппорта: {data.email}")
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    logger.info(f"Саппорт вошел: {user.email}")
    return {"id": user.id, "email": user.email} 