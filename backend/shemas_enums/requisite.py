from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional


class RequisiteBase(BaseModel):
    fiat_id: int
    trader_id: int
    method_id: int
    bank_id: int
    status: str = Field(..., description="Current status of requisite (approve/blocked)")
    distribution_weight: Decimal = Field(..., gt=0, description="Weight in round-robin distribution")


class RequisiteRead(RequisiteBase):
    id: int
    owner_of_requisites_id: int
    last_used_at: Optional[datetime] = None
    is_excluded_from_distribution: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FullRequisiteSettingsRead(BaseModel):
    id: int
    requisite_id: int
    pay_in: bool
    pay_out: bool
    lower_limit: Decimal
    upper_limit: Decimal
    total_limit: Decimal
    turnover_limit_minutes: int
    turnover_day_max: Decimal

    class Config:
        orm_mode = True 