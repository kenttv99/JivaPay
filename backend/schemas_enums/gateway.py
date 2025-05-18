from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

# --- Schemas for Gateway v2: Payment Session ---

class PaymentSessionInitRequest(BaseModel):
    order_type: str # e.g., "pay_in"
    amount_fiat: Decimal
    fiat_currency_id: int # Or code, e.g., "RUB" - depends on how merchant_store defines it
    
    # merchant_store_id will be derived from X-API-KEY
    # crypto_currency_id might also be derived from merchant_store settings for pay_in

    target_method_id: Optional[int] = None # For pay_in, if merchant wants to suggest a method
    
    customer_id: Optional[str] = None
    external_order_id: Optional[str] = None # Merchant's internal order ID
    
    return_url: Optional[HttpUrl] = None # URL to redirect client after payment attempt on payment page
    callback_url_for_merchant: Optional[HttpUrl] = None # Callback for final order status to merchant server

    # Any other specific params merchant might send for this payment
    additional_params: Optional[Dict[str, Any]] = None


class PaymentSessionInitResponse(BaseModel):
    payment_url: HttpUrl
    incoming_order_id: int # ID of the created IncomingOrder
    payment_token: str # The unique token for this payment session
    expires_at: datetime


class PaymentSessionDetails(BaseModel):
    # Details to be shown on the payment page itself
    incoming_order_id: int
    payment_token: str
    
    amount_fiat_snapshot: Decimal
    fiat_currency_code_snapshot: str # e.g. "RUB", "USD"
    
    merchant_store_name: Optional[str] = None # For display on payment page
    
    expires_at: datetime
    # Could include payment_methods available for this session/order if selection happens on our page

    class Config:
        orm_mode = True


class PaymentPageConfirmationRequest(BaseModel):
    # This schema might not be directly used if it's a multipart/form-data request for file upload
    # However, it represents the data fields expected along with the file.
    # The actual file will be handled by FastAPI's UploadFile
    notes: Optional[str] = None # Any notes from the client during payment
    # payment_method_chosen_on_page: Optional[str] = None # If client chooses a method on our page

# Potentially, a response for payment page confirmation
class PaymentPageConfirmationResponse(BaseModel):
    status: str # e.g., "confirmation_received", "processing"
    message: Optional[str] = None
    order_history_id: Optional[int] = None # If OrderHistory is created/updated synchronously

# Schema for gateway to get status of an incoming order (existing or slightly adapted)
class GatewayIncomingOrderStatusResponse(BaseModel):
    incoming_order_id: int
    external_order_id: Optional[str] = None
    status: str # Status of IncomingOrder (e.g., new, processing, assigned, failed, expired)
    # Could also include OrderHistory status if available
    order_history_status: Optional[str] = None
    
    payment_url: Optional[HttpUrl] = None # If session is still active and payment page is relevant
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 