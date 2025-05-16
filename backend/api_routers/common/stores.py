from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.utils import get_db_session, create_object, update_object_db
from backend.database.db import MerchantStore, Merchant
from backend.schemas_enums.merchant import MerchantStoreCreate, MerchantStoreRead, MerchantStoreUpdate
from backend.common.permissions import permission_required
from backend.security import get_current_active_user
from backend.common.dependencies import get_current_active_merchant
import secrets

router = APIRouter()

@router.post(
    "",
    response_model=MerchantStoreRead,
    status_code=status.HTTP_201_CREATED
)
def create_store(
    store_data: MerchantStoreCreate,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Create a new store for the current merchant."""
    public_key = secrets.token_urlsafe(32)
    private_key = secrets.token_urlsafe(64)
    data = store_data.dict()
    data.update({
        "merchant_id": current_merchant.id,
        "public_api_key": public_key,
        "private_api_key": private_key
    })
    new_store = create_object(db, MerchantStore, data)
    db.commit()
    return new_store

@router.get(
    "",
    response_model=List[MerchantStoreRead]
)
def list_stores(
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """List stores for the current merchant."""
    stores = db.query(MerchantStore).filter_by(merchant_id=current_merchant.id).all()
    return stores

@router.get(
    "/{store_id}",
    response_model=MerchantStoreRead
)
def get_store(
    store_id: int,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Get details of a specific store."""
    store = db.query(MerchantStore).filter_by(id=store_id, merchant_id=current_merchant.id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store

@router.patch(
    "/{store_id}",
    response_model=MerchantStoreRead
)
def update_store(
    store_id: int,
    store_update: MerchantStoreUpdate,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Update settings of an existing store."""
    store = db.query(MerchantStore).filter_by(id=store_id, merchant_id=current_merchant.id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    update_data = store_update.dict(exclude_unset=True)
    updated = update_object_db(db, store, update_data)
    db.commit()
    return updated

@router.delete(
    "/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Delete a store for the current merchant."""
    store = db.query(MerchantStore).filter_by(id=store_id, merchant_id=current_merchant.id).one_or_none()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    db.delete(store)
    db.commit() 