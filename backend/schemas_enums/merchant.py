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
        from_attributes= True


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
        from_attributes= True


class MerchantStoreCreate(MerchantStoreBase):
    """Schema for creating a new merchant store."""
    pass


class MerchantStoreUpdate(BaseModel):
    """Schema for updating an existing merchant store."""
    store_name: Optional[str] = None
    crypto_currency_id: Optional[int] = None
    fiat_currency_id: Optional[int] = None
    lower_limit: Optional[Decimal] = None
    upper_limit: Optional[Decimal] = None
    callback_url: Optional[AnyUrl] = None
    pay_in_enabled: Optional[bool] = None
    pay_out_enabled: Optional[bool] = None
    trafic_access: Optional[bool] = None
    access: Optional[bool] = None

    class Config:
        from_attributes = True 