from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.database.utils import get_db_session, get_object_or_none, update_object_db, create_object
from backend.database.db import ConfigurationSetting
from backend.common.permissions import permission_required

# Pydantic schemas for configuration settings
class ConfigSettingBase(BaseModel):
    value: str
    description: Optional[str] = None

class ConfigSettingCreate(ConfigSettingBase):
    key: str

class ConfigSettingRead(ConfigSettingCreate):
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

class ConfigSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

router = APIRouter()

@router.post(
    "/",
    response_model=ConfigSettingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required("settings:create"))]
)
def create_setting(
    data: ConfigSettingCreate,
    db: Session = Depends(get_db_session)
):
    existing = db.get(ConfigurationSetting, data.key)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Setting key already exists")
    obj = ConfigurationSetting(
        key=data.key,
        value=data.value,
        description=data.description
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get(
    "/",
    response_model=List[ConfigSettingRead],
    dependencies=[Depends(permission_required("settings:read"))]
)
def list_settings(
    db: Session = Depends(get_db_session)
):
    return db.query(ConfigurationSetting).all()

@router.get(
    "/{key}",
    response_model=ConfigSettingRead,
    dependencies=[Depends(permission_required("settings:read"))]
)
def get_setting(
    key: str,
    db: Session = Depends(get_db_session)
):
    obj = db.get(ConfigurationSetting, key)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return obj

@router.patch(
    "/{key}",
    response_model=ConfigSettingRead,
    dependencies=[Depends(permission_required("settings:update"))]
)
def update_setting(
    key: str,
    data: ConfigSettingUpdate,
    db: Session = Depends(get_db_session)
):
    obj = db.get(ConfigurationSetting, key)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    update_data = data.dict(exclude_unset=True)
    updated = update_object_db(db, obj, update_data)
    db.commit()
    return updated

@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(permission_required("settings:delete"))]
)
def delete_setting(
    key: str,
    db: Session = Depends(get_db_session)
):
    obj = db.get(ConfigurationSetting, key)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    db.delete(obj)
    db.commit() 