"""Pydantic schemas related to orders."""

from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal
from datetime import datetime
from typing import Optional
from .common_enums import DirectionEnum, OrderStatusEnum

# --- Base Schemas (if needed) --- #
class OrderBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Order amount")
    currency_id: int = Field(..., description="ID of the order currency")
    payment_method_id: int = Field(..., description="ID of the payment method")
    direction: DirectionEnum = Field(..., description="Order direction (PAY_IN or PAY_OUT)")
    customer_id: Optional[str] = Field(None, max_length=255, description="Customer identifier from merchant system")
    return_url: Optional[str] = Field(None, max_length=1024, description="URL to redirect user after completion (optional)")
    callback_url: Optional[str] = Field(None, max_length=1024, description="URL for server-to-server notification (optional)")

# --- Incoming Order Schemas --- #
class IncomingOrderCreate(OrderBase):
    """Schema for creating a new incoming order (e.g., from Gateway API)."""
    # Inherits all fields from OrderBase, merchant and store inferred from API key
    pass

class IncomingOrderRead(OrderBase):
    """Schema for reading/returning an incoming order."""
    id: int
    merchant_store_id: int
    status: OrderStatusEnum = Field(..., description="Current status of the incoming order")
    assigned_order_id: Optional[int] = Field(None, description="ID of the assigned OrderHistory, if any")
    failure_reason: Optional[str] = Field(None, description="Reason for the last processing failure")
    retry_count: int = Field(default=0, description="Number of processing attempts")
    created_at: datetime
    last_attempt_at: Optional[datetime] = None

    class Config:
        from_attributes= True # Enable reading data from ORM models
        # For Pydantic v2: from_attributes = True

# --- Order History Schemas --- #
class OrderHistoryRead(IncomingOrderRead):
    """Schema for reading/returning the main order history record."""
    requisite_id: int
    trader_id: int
    store_commission: Optional[Decimal] = None
    trader_commission: Optional[Decimal] = None
    exchange_rate: Optional[Decimal] = None
    amount_fiat: Optional[Decimal] = None
    amount_crypto: Optional[Decimal] = None
    receipt_url: Optional[str] = None
    trader_receipt_url: Optional[str] = None
    cancellation_reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    disputed_at: Optional[datetime] = None

    class Config:
        from_attributes= True
        # For Pydantic v2: from_attributes = True

# --- Schemas for Status Updates --- #
class OrderConfirmPayload(BaseModel):
    uploaded_document_url: Optional[str] = Field(None, max_length=1024, description="URL of the uploaded supporting document")

class OrderCancelPayload(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for cancellation")

# Additional schemas for filters and list responses can be added here 