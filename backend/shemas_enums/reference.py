from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime

class BankDetails(BaseModel):
    id: int
    name: str = Field(..., description="Bank public or official name")
    fiat_currency_id: int = Field(..., description="ID of the associated fiat currency")
    currency_code: Optional[str] = Field(None, description="Currency code (e.g., USD)")
    access: bool = Field(..., description="Is the bank available for transactions?")

    class Config:
        orm_mode = True

class PaymentMethodDetails(BaseModel):
    id: int
    method_name: str = Field(..., description="Internal name of the payment method")
    public_name: Optional[str] = Field(None, description="User-friendly display name")
    access: bool = Field(..., description="Is the payment method active?")

    class Config:
        orm_mode = True

class ExchangeRateDetails(BaseModel):
    id: int
    currency: str = Field(..., description="Crypto currency code")
    fiat: str = Field(..., description="Fiat currency code")
    buy_rate: Decimal = Field(..., description="Rate for buying crypto")
    sell_rate: Decimal = Field(..., description="Rate for selling crypto")
    median_rate: Decimal = Field(..., description="Median rate used for calculations")
    source: str = Field(..., description="Source of the rate data")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last update")

    class Config:
        orm_mode = True 