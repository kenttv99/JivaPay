from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional


class BalanceStoreRead(BaseModel):
    id: int
    store_id: int
    crypto_currency_id: int
    balance: Decimal = Field(..., description="Current cryptocurrency balance of the store")
    updated_at: datetime

    class Config:
        orm_mode = True


class BalanceTraderRead(BaseModel):
    id: int
    trader_id: int
    fiat_currency_id: int
    balance: Decimal = Field(..., description="Current fiat balance of the trader")
    updated_at: datetime

    class Config:
        orm_mode = True


class BalanceStoreHistoryRead(BaseModel):
    id: int
    store_id: int
    crypto_currency_id: int
    order_id: Optional[int] = None
    balance_change: Decimal
    new_balance: Decimal
    operation_type: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class BalanceTraderFiatHistoryRead(BaseModel):
    id: int
    trader_id: int
    fiat_id: int
    order_id: Optional[int] = None
    operation_type: str
    network: Optional[str]
    balance_change: Decimal
    new_balance: Decimal
    description: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class BalanceTraderCryptoHistoryRead(BaseModel):
    id: int
    trader_id: int
    crypto_currency_id: int
    order_id: Optional[int] = None
    operation_type: str
    network: str
    balance_change: Decimal
    new_balance: Decimal
    description: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True 