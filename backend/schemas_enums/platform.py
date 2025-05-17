from pydantic import BaseModel
from decimal import Decimal
from typing import Union, List

class PlatformBalanceItemSchema(BaseModel):
    currency_code: str
    currency_name: str
    total_balance: Decimal

    class Config:
        from_attributes = True

class PlatformBalanceResponseSchema(BaseModel):
    items: List[PlatformBalanceItemSchema] 