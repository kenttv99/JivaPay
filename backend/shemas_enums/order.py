"""Pydantic schemas related to orders."""

from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal
from datetime import datetime
from typing import Optional, Any # Any for potential Enums initially

# --- Base Schemas (if needed) --- #
class OrderBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Order amount")
    currency_id: int = Field(..., description="ID of the order currency")
    payment_method_id: int = Field(..., description="ID of the payment method")
    # Assuming direction is an Enum later
    direction: Any = Field(..., description="Order direction (e.g., PAYIN, PAYOUT)")
    customer_id: Optional[str] = Field(None, max_length=255, description="Customer identifier from merchant system")
    return_url: Optional[str] = Field(None, max_length=1024, description="URL to redirect user after completion (optional)")
    callback_url: Optional[str] = Field(None, max_length=1024, description="URL for server-to-server notification (optional)")

# --- Incoming Order Schemas --- #
class IncomingOrderCreate(OrderBase):
    """Schema for creating a new incoming order (e.g., from Gateway API)."""
    # Fields required for creation, merchant_store_id likely identified via API key/auth
    pass # Inherits all fields from OrderBase

class IncomingOrderRead(OrderBase):
    """Schema for reading/returning an incoming order."""
    id: int
    merchant_store_id: int
    # Assuming status is an Enum later
    status: Any = Field(..., description="Current status of the incoming order")
    assigned_order_id: Optional[int] = Field(None, description="ID of the assigned OrderHistory, if any")
    failure_reason: Optional[str] = Field(None, description="Reason for the last processing failure")
    retry_count: int = Field(default=0, description="Number of processing attempts")
    created_at: datetime
    last_attempt_at: Optional[datetime] = None

    class Config:
        orm_mode = True # Enable reading data from ORM models
        # For Pydantic v2: from_attributes = True

# --- Order History Schemas --- #
class OrderHistoryRead(IncomingOrderRead): # Inherits many fields
    """Schema for reading/returning the main order history record."""
    requisite_id: int
    trader_id: int
    store_commission: Optional[Decimal] = None
    trader_commission: Optional[Decimal] = None
    fixed_exchange_rate: Optional[Decimal] = None
    # Add other relevant fields like completed_at, canceled_at, etc.

    class Config:
        orm_mode = True
        # For Pydantic v2: from_attributes = True

# --- Schemas for Status Updates --- #
class OrderConfirmPayload(BaseModel):
    # Example payload for confirming an order
    uploaded_document_url: Optional[str] = Field(None, max_length=1024, description="URL of the uploaded supporting document")

class OrderCancelPayload(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for cancellation")


# Add other schemas as needed (e.g., for filters, specific update operations) 