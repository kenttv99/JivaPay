from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


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
        from_attributes= True


class TraderCommissionRead(BaseModel):
    id: int
    trader_id: int
    commission_payin: float
    commission_payout: float
    updated_at: datetime

    class Config:
        from_attributes= True


# --- Trader Statistics Schemas --- #
class TraderStatisticsItemSchema(TraderRead):
    username: Optional[str] = None
    is_online: Optional[bool] = None
    total_turnover: Optional[Decimal] = Field(None, description="Total turnover for the selected period")
    requisite_count: Optional[int] = Field(None, description="Number of active requisites")
    order_count: Optional[int] = Field(None, description="Number of orders for the selected period")
    account_status: Optional[str] = Field(None, description="e.g., active, blocked")

    class Config:
        from_attributes = True


class TraderStatisticsResponseSchema(BaseModel):
    total_count: int
    page: int
    per_page: int
    items: List[TraderStatisticsItemSchema] 