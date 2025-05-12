"""API Router for TeamLead operations (manage traders)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, selectinload

from backend.database.utils import get_db_session
from backend.database.db import Trader, TeamLead
from backend.utils.exceptions import JivaPayException
from backend.config.logger import get_logger
from backend.security import get_current_active_user

router = APIRouter()
logger = get_logger("teamlead_router")


def get_current_active_teamlead(current_user=Depends(get_current_active_user), db: Session = Depends(get_db_session)) -> TeamLead:
    teamlead = db.query(TeamLead).filter_by(user_id=current_user.id).one_or_none()
    if not teamlead:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a teamlead")
    return teamlead


@router.get("/traders", summary="List traders under teamlead", response_model=List[int])
def list_traders(
    db: Session = Depends(get_db_session),
    current_teamlead: TeamLead = Depends(get_current_active_teamlead)
):
    traders = db.query(Trader).filter_by(team_lead_id=current_teamlead.id).all()
    return [t.id for t in traders]


@router.get("/traders/{trader_id}/stats", summary="Get trader stats placeholder")
def trader_stats(
    trader_id: int,
    db: Session = Depends(get_db_session),
    current_teamlead: TeamLead = Depends(get_current_active_teamlead)
):
    trader = db.query(Trader).options(selectinload(Trader.user)).filter_by(id=trader_id, team_lead_id=current_teamlead.id).one_or_none()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    # TODO: implement statistics gathering (orders, turnover, etc.)
    return {"id": trader.id, "email": trader.user.email if trader.user else None, "in_work": trader.in_work}


@router.patch("/traders/{trader_id}/traffic", summary="Enable/disable trader traffic")
def toggle_trader_traffic(
    trader_id: int,
    in_work: bool = Body(..., embed=True),
    db: Session = Depends(get_db_session),
    current_teamlead: TeamLead = Depends(get_current_active_teamlead)
):
    trader = db.query(Trader).filter_by(id=trader_id, team_lead_id=current_teamlead.id).one_or_none()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    trader.in_work = in_work
    db.commit()
    logger.info("TeamLead %s set trader %s in_work=%s", current_teamlead.id, trader.id, in_work)
    return {"trader_id": trader.id, "in_work": trader.in_work} 