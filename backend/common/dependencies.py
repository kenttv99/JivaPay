from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.security import get_current_active_user
from backend.database.utils import get_db_session
from backend.database.db import Merchant, Trader, TeamLead, Admin, Support


def get_current_active_merchant(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Merchant:
    """Retrieve the Merchant profile for the currently authenticated user."""
    merchant = db.query(Merchant).filter_by(user_id=current_user.id).one_or_none()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a merchant")
    return merchant


def get_current_active_trader(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Trader:
    """Retrieve the Trader profile for the currently authenticated user."""
    trader = db.query(Trader).filter_by(user_id=current_user.id).one_or_none()
    if not trader:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a trader")
    return trader


def get_current_active_teamlead(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> TeamLead:
    """Retrieve the TeamLead profile for the currently authenticated user."""
    teamlead = db.query(TeamLead).filter_by(user_id=current_user.id).one_or_none()
    if not teamlead:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a teamlead")
    return teamlead


def get_current_active_admin(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Admin:
    """Retrieve the Admin profile for the currently authenticated user."""
    admin = db.query(Admin).filter_by(user_id=current_user.id).one_or_none()
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an admin")
    return admin


def get_current_active_support(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
) -> Support:
    """Retrieve the Support profile for the currently authenticated user."""
    support = db.query(Support).filter_by(user_id=current_user.id).one_or_none()
    if not support:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not support")
    return support 