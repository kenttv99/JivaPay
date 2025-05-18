from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database.utils import get_db_session
from backend.database.db import TeamLead, Trader as TraderModel
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_teamlead
from backend.services import teamlead_service
from backend.database.db import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/",
    response_model=List[int],
    dependencies=[Depends(permission_required("teamlead_traders:read"))]
)
def list_traders(
    db: Session = Depends(get_db_session),
    current_teamlead: User = Depends(get_current_active_teamlead)
):
    """List traders under current teamlead by calling the service layer."""
    try:
        traders = teamlead_service.list_traders_for_teamlead(session=db, current_teamlead_user=current_teamlead)
        return [t.id for t in traders]
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in common list_traders: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing traders.")

@router.patch(
    "/{trader_id}/traffic",
    response_model=dict,
    dependencies=[Depends(permission_required("teamlead_traders:update"))]
)
def toggle_trader_traffic(
    trader_id: int,
    in_work: bool = Body(..., embed=True),
    db: Session = Depends(get_db_session),
    current_teamlead: User = Depends(get_current_active_teamlead)
):
    """Enable/disable trader in_work status under current teamlead by calling the service layer."""
    try:
        updated_trader = teamlead_service.set_trader_in_work_status_by_teamlead(
            session=db,
            trader_id_to_manage=trader_id,
            in_work_status=in_work,
            current_teamlead_user=current_teamlead
        )
        return {"trader_id": updated_trader.id, "in_work": updated_trader.in_work}
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OperationForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in common toggle_trader_traffic: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating trader in_work status.") 