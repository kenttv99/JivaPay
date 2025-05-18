from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.utils import get_db_session
from backend.database.db import MerchantStore, Merchant, User
from backend.schemas_enums.merchant import MerchantStoreCreate, MerchantStoreRead, MerchantStoreUpdate
from backend.common.permissions import permission_required
from backend.common.dependencies import get_current_active_merchant
from backend.services import merchant_service
from backend.utils.exceptions import DatabaseError, NotFoundError, AuthorizationError
import logging

logger = logging.getLogger(__name__)
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
    """Create a new store for the current merchant by calling the service layer."""
    try:
        new_store = merchant_service.create_merchant_store(
            session=db, 
            current_merchant_user=current_merchant,
            store_data=store_data
        )
        return new_store
    except (DatabaseError, AuthorizationError) as e:
        logger.error(f"Error creating store for merchant {current_merchant.id if current_merchant else 'Unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Could not create store.")
    except Exception as e:
        logger.error(f"Unexpected error creating store for merchant {current_merchant.id if current_merchant else 'Unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while creating the store.")

@router.get(
    "",
    response_model=List[MerchantStoreRead]
)
def list_stores(
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """List stores for the current merchant by calling the service layer."""
    try:
        stores = merchant_service.get_stores_for_merchant(session=db, current_merchant_user=current_merchant)
        return stores
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing stores for merchant {current_merchant.id if current_merchant else 'Unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing stores.")

@router.get(
    "/{store_id}",
    response_model=MerchantStoreRead
)
def get_store(
    store_id: int,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Get details of a specific store by calling the service layer."""
    try:
        store = merchant_service.get_merchant_store_details(session=db, current_merchant_user=current_merchant, store_id=store_id)
        return store
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting store {store_id} for merchant {current_merchant.id if current_merchant else 'Unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting store details.")

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
    """Update settings of an existing store by calling the service layer."""
    try:
        updated_store = merchant_service.update_merchant_store(
            session=db, 
            current_merchant_user=current_merchant, 
            store_id=store_id, 
            store_update_data=store_update
        )
        return updated_store
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Could not update store.")
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating store {store_id} for merchant {current_merchant.id if current_merchant else 'Unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating store.")

@router.delete(
    "/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db_session),
    current_merchant: Merchant = Depends(get_current_active_merchant)
):
    """Delete a store for the current merchant by calling the service layer."""
    try:
        merchant_service.delete_merchant_store(session=db, current_merchant_user=current_merchant, store_id=store_id)
        return
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Could not delete store.")
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting store {store_id} for merchant {current_merchant.id if current_merchant else 'Unknown'}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting store.") 