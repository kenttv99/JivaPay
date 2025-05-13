from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.utils import get_db_session, create_object, update_object_db, get_object_or_none
from backend.database.db import ReqTrader
from backend.shemas_enums.requisite import RequisiteBase, RequisiteRead, FullRequisiteSettingsRead
from backend.common.permissions import permission_required
from pydantic import BaseModel

# Define create and update schemas
class RequisiteCreate(RequisiteBase):
    """Schema for creating a new trader requisite."""
    pass

class RequisiteUpdate(BaseModel):
    status: Optional[str] = None
    distribution_weight: Optional[float] = None

router = APIRouter()

@router.post(
    "/",
    response_model=RequisiteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required("requisites:create"))]
)
def create_requisite(
    data: RequisiteCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new trader requisite."""
    new_req = create_object(db, ReqTrader, data.dict())
    db.commit()
    return new_req

@router.get(
    "/",
    response_model=List[RequisiteRead],
    dependencies=[Depends(permission_required("requisites:read"))]
)
def list_requisites(
    db: Session = Depends(get_db_session)
):
    """List all requisites."""
    return db.query(ReqTrader).all()

@router.get(
    "/{req_id}",
    response_model=RequisiteRead,
    dependencies=[Depends(permission_required("requisites:read"))]
)
def get_requisite(
    req_id: int,
    db: Session = Depends(get_db_session)
):
    """Get requisite by ID."""
    req = get_object_or_none(db, ReqTrader, id=req_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisite not found")
    return req

@router.patch(
    "/{req_id}",
    response_model=RequisiteRead,
    dependencies=[Depends(permission_required("requisites:update"))]
)
def update_requisite(
    req_id: int,
    data: RequisiteUpdate,
    db: Session = Depends(get_db_session)
):
    """Update an existing requisite."""
    req = get_object_or_none(db, ReqTrader, id=req_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisite not found")
    update_data = data.dict(exclude_unset=True)
    updated = update_object_db(db, req, update_data)
    db.commit()
    return updated

@router.delete(
    "/{req_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(permission_required("requisites:delete"))]
)
def delete_requisite(
    req_id: int,
    db: Session = Depends(get_db_session)
):
    """Delete a requisite by ID."""
    req = get_object_or_none(db, ReqTrader, id=req_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requisite not found")
    db.delete(req)
    db.commit() 