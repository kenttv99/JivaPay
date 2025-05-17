from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from .common_enums import DirectionEnum # Assuming DirectionEnum is in common_enums.py


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
        from_attributes= True


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
        from_attributes= True

# --- Schemas for Online Requisites Statistics --- #

class RequisiteOnlineInfoSchema(BaseModel):
    id: int
    trader_id: int
    trader_username: Optional[str] = None # Assuming username is on the trader's user model
    trader_email: Optional[EmailStr] = None # Assuming email is on the trader's user model
    payment_method_name: Optional[str] = None
    bank_name: Optional[str] = None
    # Consider adding currency_code if not implicitly part of payment_method or bank
    # currency_code: Optional[str] = None 
    status: str # e.g. 'approve', 'active'
    pay_in_enabled: bool
    pay_out_enabled: bool
    lower_limit: Optional[Decimal] = None
    upper_limit: Optional[Decimal] = None
    # active_hours might be relevant if defined elsewhere, but removed from FullRequisitesSettings

    class Config:
        from_attributes = True

class RequisiteOnlineStatsResponseSchema(BaseModel):
    total_online_count: int
    # Optional: if the API should return a list of online requisites
    # items: List[RequisiteOnlineInfoSchema] 
    # page: Optional[int] = None
    # per_page: Optional[int] = None

# Schema for detailed list if stats endpoint provides more than just count
class PaginatedRequisitesOnlineResponseSchema(BaseModel):
    total_count: int
    page: int
    per_page: int
    items: List[RequisiteOnlineInfoSchema]

# --- Schemas for Admin/Support/TeamLead Requisite Management (Example) --- #
# These are placeholders and can be expanded based on specific actions in ADDITIONAL_FEATURES_AND_COMPONENTS.md

class RequisiteStatusUpdateSchema(BaseModel):
    status: str # e.g. 'approve', 'block', 'archive'
    reason: Optional[str] = None

class RequisiteLimitsUpdateSchema(BaseModel):
    lower_limit: Optional[Decimal] = Field(None, gt=0)
    upper_limit: Optional[Decimal] = Field(None, gt=0)
    total_limit: Optional[Decimal] = Field(None, gt=0)
    turnover_limit_minutes: Optional[int] = Field(None, gt=0)
    turnover_day_max: Optional[Decimal] = Field(None, ge=0)
    pay_in: Optional[bool] = None
    pay_out: Optional[bool] = None 