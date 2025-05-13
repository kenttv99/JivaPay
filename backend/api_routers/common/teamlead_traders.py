from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database.utils import get_db_session
from backend.database.db import Trader, TeamLead
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_teamlead
from backend.database.db import Trader as TraderModel

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/",
    response_model=List[int],
    dependencies=[Depends(permission_required("teamlead_traders:read"))]
)
def list_traders(
    db: Session = Depends(get_db_session),
    current_teamlead: TeamLead = Depends(get_current_active_teamlead)
):
    """List traders under current teamlead."""
    traders = db.query(Trader).filter_by(team_lead_id=current_teamlead.id).all()
    return [t.id for t in traders]

@router.patch(
    "/{trader_id}/traffic",
    response_model=dict,
    dependencies=[Depends(permission_required("teamlead_traders:update"))]
)
def toggle_trader_traffic(
    trader_id: int,
    in_work: bool = Body(..., embed=True),
    db: Session = Depends(get_db_session),
    current_teamlead: TeamLead = Depends(get_current_active_teamlead)
):
    """Enable/disable trader traffic under current teamlead."""
    trader = db.query(Trader).filter_by(id=trader_id, team_lead_id=current_teamlead.id).one_or_none()
    if not trader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trader not found")
    trader.in_work = in_work
    db.commit()
    logger.info("TeamLead %s set trader %s in_work=%s", current_teamlead.id, trader.id, in_work)
    return {"trader_id": trader.id, "in_work": trader.in_work} 