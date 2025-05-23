from pydantic import BaseModel, Field, EmailStr, AnyUrl
from datetime import datetime
from decimal import Decimal
from typing import Optional


class MerchantBase(BaseModel):
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    verification_level: Optional[str]


class MerchantRead(MerchantBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MerchantStoreBase(BaseModel):
    store_name: str
    crypto_currency_id: int
    fiat_currency_id: int
    lower_limit: Decimal
    upper_limit: Decimal
    callback_url: Optional[AnyUrl] = None
    pay_in_enabled: bool
    pay_out_enabled: bool


class MerchantStoreRead(MerchantStoreBase):
    id: int
    merchant_id: int
    public_api_key: str
    pay_in_enabled: bool
    pay_out_enabled: bool
    trafic_access: bool
    access: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 