"""API Router for public reference data."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.utils import get_db_session
from backend.services.reference_data import get_bank_details, get_payment_method_details, get_exchange_rate
from backend.schemas_enums.reference import BankDetails, PaymentMethodDetails, ExchangeRateDetails

# Router for public reference data
router = APIRouter(prefix="/reference", tags=["reference"])

@router.get("/banks/{bank_id}", response_model=BankDetails)
def read_bank_details(bank_id: int, db: Session = Depends(get_db_session)):
    """Get bank details by ID."""
    bank = get_bank_details(bank_id, db)
    if not bank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank not found")
    return bank

@router.get("/payment-methods/{method_id}", response_model=PaymentMethodDetails)
def read_payment_method_details(method_id: int, db: Session = Depends(get_db_session)):
    """Get payment method details by ID."""
    method = get_payment_method_details(method_id, db)
    if not method:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
    return method

@router.get("/exchange-rates/{crypto_id}/{fiat_id}", response_model=ExchangeRateDetails)
def read_exchange_rate(crypto_id: str, fiat_id: str, db: Session = Depends(get_db_session)):
    """Get current exchange rate between crypto and fiat currency."""
    rate = get_exchange_rate(crypto_id, fiat_id, db)
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found")
    return rate
