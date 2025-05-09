from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class TraderBase(BaseModel):
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    verification_level: str
    pay_in: bool
    pay_out: bool
    in_work: bool


class TraderRead(TraderBase):
    id: int
    trafic_priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TraderCommissionRead(BaseModel):
    id: int
    trader_id: int
    commission_payin: float
    commission_payout: float
    updated_at: datetime

    class Config:
        orm_mode = True 