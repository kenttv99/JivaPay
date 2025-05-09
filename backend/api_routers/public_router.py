"""API Router for public reference data."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.utils import get_db_session
from backend.services.reference_data import get_bank_details, get_payment_method_details, get_exchange_rate
from backend.shemas_enums.reference import BankDetails, PaymentMethodDetails, ExchangeRateDetails
from backend.utils.exceptions import JivaPayException

# Router for public reference data
router = APIRouter(prefix="/reference", tags=["reference"])

@router.get("/banks/{bank_id}", response_model=BankDetails)
def read_bank_details(bank_id: int, db: Session = Depends(get_db_session)):
    """Get bank details by ID."""
    try:
        bank = get_bank_details(bank_id, db)
        if not bank:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank not found")
        return bank
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/payment-methods/{method_id}", response_model=PaymentMethodDetails)
def read_payment_method_details(method_id: int, db: Session = Depends(get_db_session)):
    """Get payment method details by ID."""
    try:
        method = get_payment_method_details(method_id, db)
        if not method:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
        return method
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/exchange-rates/{crypto_id}/{fiat_id}", response_model=ExchangeRateDetails)
def read_exchange_rate(crypto_id: str, fiat_id: str, db: Session = Depends(get_db_session)):
    """Get current exchange rate between crypto and fiat currency."""
    try:
        rate = get_exchange_rate(crypto_id, fiat_id, db)
        if not rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found")
        return rate
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
