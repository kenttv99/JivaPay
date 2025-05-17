"""Pydantic schemas related to orders."""

from pydantic import BaseModel, Field, EmailStr, model_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from .common_enums import DirectionEnum, OrderStatusEnum

# --- Base Schemas (if needed) --- #
class OrderBase(BaseModel):
    order_type: DirectionEnum = Field(..., description="Order type (pay_in or pay_out)")

    amount_fiat: Optional[Decimal] = Field(None, gt=0, description="Order amount in fiat currency (for pay_in)")
    fiat_currency_id: Optional[int] = Field(None, description="ID of the fiat currency (for pay_in)")

    amount_crypto: Optional[Decimal] = Field(None, gt=0, description="Order amount in crypto currency (for pay_out)")
    crypto_currency_id: Optional[int] = Field(None, description="ID of the crypto currency (for pay_out)")
    
    target_method_id: int = Field(..., description="ID of the payment method (maps to target_method_id in DB)")
    
    customer_id: Optional[str] = Field(None, max_length=255, description="Customer identifier from merchant system")
    return_url: Optional[str] = Field(None, max_length=1024, description="URL to redirect user after completion (optional)")
    callback_url: Optional[str] = Field(None, max_length=1024, description="URL for server-to-server notification (optional)")

    @model_validator(mode='after')
    def check_conditional_fields(self) -> 'OrderBase':
        if self.order_type == DirectionEnum.PAY_IN:
            if self.amount_fiat is None or self.fiat_currency_id is None:
                raise ValueError("For PAY_IN, amount_fiat and fiat_currency_id are required.")
            # Ensure crypto fields are not set for PAY_IN if they were somehow provided
            self.amount_crypto = None
            self.crypto_currency_id = None
        elif self.order_type == DirectionEnum.PAY_OUT:
            if self.amount_crypto is None or self.crypto_currency_id is None:
                raise ValueError("For PAY_OUT, amount_crypto and crypto_currency_id are required.")
            # Ensure fiat fields are not set for PAY_OUT
            self.amount_fiat = None
            self.fiat_currency_id = None
        return self

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

# --- Admin Specific Schemas for Order History and Count ---

class OrderHistoryAdminItemSchema(OrderHistoryRead):
    """Detailed order information for admin, could include more sensitive fields or related objects."""
    # Example: Add trader and merchant email directly if needed for quick view
    trader_email: Optional[EmailStr] = None 
    merchant_email: Optional[EmailStr] = None
    store_name: Optional[str] = None
    requisite_number_partial: Optional[str] = None # e.g., last 4 digits for display

    # TODO: Populate these fields in the service layer when constructing the response

    class Config:
        from_attributes = True

class OrderHistoryAdminResponseSchema(BaseModel):
    total_count: int
    page: int
    per_page: int
    orders: List[OrderHistoryAdminItemSchema]

class OrderCountResponseSchema(BaseModel):
    total_orders_count: int

# Potentially a Pydantic model for query parameters if using Depends(QuerySchema)
# class OrdersHistoryQueryAdminSchema(BaseModel):
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] = None
#     status: Optional[str] = None
#     amount: Optional[Decimal] = None
#     trader_id: Optional[int] = None
#     store_id: Optional[int] = None
#     requisite_identifier: Optional[str] = None
#     user_query: Optional[str] = None
#     page: int = Query(1, ge=1)
#     per_page: int = Query(20, ge=1, le=100)

# Additional schemas for filters and list responses can be added here 