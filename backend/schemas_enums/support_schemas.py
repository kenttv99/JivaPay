from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

# Assuming these are imported from their respective files if not defined here
# from .trader import TraderRead, TraderStatisticsItemSchema # Example
# from .order import OrderHistoryRead # Example
# from .requisite import RequisiteOnlineInfoSchema # Example

class SupportLogin(BaseModel):
    email: EmailStr = Field(..., description="Support's email for login")
    password: str = Field(..., min_length=6, description="Password for support account")

    class Config:
        from_attributes= True 

# --- Schemas for Support Interactions --- #

class SupportTraderDetailsSchema(BaseModel): # Placeholder, adapt from trader.py or UserReadWithProfile
    id: int
    user_id: int
    email: EmailStr
    username: Optional[str] = None
    is_active: bool
    # Add other fields relevant for support when viewing a trader
    # e.g., from TraderRead or specific profile information
    verification_level: Optional[str] = None
    in_work: Optional[bool] = None
    is_traffic_enabled_by_teamlead: Optional[bool] = None
    # Consider adding a list of recent orders or requisites here or as separate calls
    created_at: datetime

    class Config:
        from_attributes = True

class SupportMerchantDetailsSchema(BaseModel): # Placeholder
    id: int
    user_id: int
    email: EmailStr
    company_name: Optional[str] = None
    is_active: bool
    # created_at: datetime
    # stores: List[Any] # Or a specific Store schema

    class Config:
        from_attributes = True

class SupportStoreDetailsSchema(BaseModel): # Placeholder
    id: int
    merchant_id: int
    name: str
    is_active: bool
    # api_key: Optional[str] # May be sensitive
    # callback_url: Optional[str]

    class Config:
        from_attributes = True

class SupportOrderActionPayloadSchema(BaseModel):
    action: str = Field(..., description="Specific action to perform, e.g., 'request_document', 'change_status'")
    new_status: Optional[str] = None # If action is 'change_status'
    comment: Optional[str] = Field(None, description="Comment or reason for the action")
    # Add other fields depending on the action

class SupportActionResponseSchema(BaseModel):
    success: bool
    message: Optional[str] = None
    details: Optional[Any] = None # e.g., updated order details 