from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from backend.config.settings import settings
from backend.database.utils import get_db_session
from backend.database.db import User, Role, Admin, Support, TeamLead

# OAuth2 scheme for bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Token creation parameters
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Retrieve user from DB and eager load role and specific profiles
    user = db.query(User).filter(User.email == username)\
        .options(
            joinedload(User.role),
            joinedload(User.admin_profile),
            joinedload(User.support_profile),
            joinedload(User.teamlead_profile),
            joinedload(User.merchant_profile),
            joinedload(User.trader_profile)
        ).one_or_none()
        
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is active and return the session-bound instance."""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# --- Role-specific active user dependencies ---

def get_current_active_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.admin_profile or current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an active admin or does not have an admin profile."
        )
    return current_user

def get_current_active_support(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.support_profile or current_user.role.name != "support":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an active support agent or does not have a support profile."
        )
    return current_user

def get_current_active_teamlead(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.teamlead_profile or current_user.role.name != "teamlead":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an active teamlead or does not have a teamlead profile."
        )
    return current_user

def get_current_active_merchant(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.merchant_profile or current_user.role.name != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an active merchant or does not have a merchant profile."
        )
    return current_user

def get_current_active_trader(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.trader_profile or current_user.role.name != "trader":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an active trader or does not have a trader profile."
        )
    return current_user 