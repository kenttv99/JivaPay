"""API Router for the public-facing Payment Gateway endpoints."""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Path, Body, Request, UploadFile, File, status, HTTPException
from sqlalchemy.orm import Session
import io

from backend.database.utils import get_db_session
from backend.schemas_enums.order import IncomingOrderCreate, IncomingOrderRead
from backend.services.gateway_service import handle_init_request, get_order_status, handle_client_confirmation
from backend.utils.s3_client import upload_file_async
from backend.config.settings import settings
from backend.services import gateway_service
from backend.utils.exceptions import OrderProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Pay-In Endpoints --- #

@router.post(
    "/payin/init",
    # response_model=GatewayInitResponse, # Define specific response? Maybe redirect URL or just order ID?
    response_model=IncomingOrderRead, # Example: return created order details
    summary="Initialize a Pay-In Transaction",
    tags=["Gateway Pay-In"]
)
def initialize_payin(
    request_data: IncomingOrderCreate, # Reuse for now
    request: Request, # To get merchant identifier (e.g., API key from header)
    db: Session = Depends(get_db_session)
):
    """Receives initial Pay-In request from merchant site, creates IncomingOrder."""
    merchant_api_key = request.headers.get("X-API-KEY") # Example: Get key from header
    logger.info(f"Gateway: Received Pay-In init request. Key: {merchant_api_key}. Data: {request_data.dict()}")

    created_order = handle_init_request(
        api_key=merchant_api_key,
        request_data=request_data,
        direction="PAYIN",
        db=db
    )
    return created_order

@router.get(
    "/payin/status/{order_identifier}",
    # response_model=GatewayStatusResponse, # Define specific status response
    response_model=IncomingOrderRead, # Example
    summary="Get Pay-In Order Status",
    tags=["Gateway Pay-In"]
)
def get_payin_status(
    order_identifier: str = Path(..., description="Unique identifier for the order (e.g., ID)"),
    db: Session = Depends(get_db_session)
):
    """Allows merchant/client to check the status of a Pay-In order."""
    logger.info(f"Gateway: Received status request for Pay-In order: {order_identifier}")
    return get_order_status(order_identifier, db)

@router.post(
    "/payin/confirm/{order_identifier}",
    # response_model=GatewayConfirmResponse, # Define response
    status_code=status.HTTP_202_ACCEPTED, # Or 200 OK if returning final status
    summary="Confirm Pay-In Payment (Client Action)",
    tags=["Gateway Pay-In"]
)
async def confirm_payin_payment(
    order_identifier: str = Path(..., description="Unique identifier for the order (e.g., ID)"),
    receipt_file: Optional[UploadFile] = File(None, description="Optional payment receipt upload"),
    db: Session = Depends(get_db_session)
):
    """Endpoint for the end-client to confirm they have made the payment (e.g., uploaded receipt)."""
    logger.info(f"Gateway: Received payment confirmation for Pay-In order: {order_identifier}. File provided: {receipt_file is not None}")
    
    receipt_content_bytes: Optional[bytes] = None
    original_filename: Optional[str] = None

    if receipt_file:
        receipt_content_bytes = await receipt_file.read()
        original_filename = receipt_file.filename
        # No S3 upload logic here anymore, it's in order_status_manager via gateway_service

    try:
        updated_order = gateway_service.handle_client_confirmation(
            order_identifier=order_identifier, 
            receipt_content=receipt_content_bytes, 
            receipt_filename=original_filename, 
            db=db
        )
        # Depending on what handle_client_confirmation returns (e.g. OrderHistory),
        # a response_model might be useful here if not just 202 Accepted.
        # For now, let's assume it might return the updated order for consistency with other endpoints.
        return updated_order # Or a specific response schema
    except OrderProcessingError as e:
        logger.error(f"Error during client confirmation for order {order_identifier}: {e.detail}", exc_info=True)
        raise HTTPException(status_code=e.status_code if hasattr(e, 'status_code') else 400, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error during client confirmation for order {order_identifier}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during payment confirmation.")

# --- Pay-Out Endpoints --- #

@router.post(
    "/payout/init",
    # response_model=GatewayInitResponse, # Define specific response
    response_model=IncomingOrderRead, # Example
    summary="Initialize a Pay-Out Transaction",
    tags=["Gateway Pay-Out"]
)
def initialize_payout(
    # request_data: GatewayPayoutRequest, # Define specific input schema
    request_data: IncomingOrderCreate, # Reuse for now
    request: Request,
    db: Session = Depends(get_db_session)
):
    """Receives initial Pay-Out request from merchant site, creates IncomingOrder."""
    merchant_api_key = request.headers.get("X-API-KEY") # Example
    logger.info(f"Gateway: Received Pay-Out init request. Key: {merchant_api_key}. Data: {request_data.dict()}")
    created_order = handle_init_request(
        api_key=merchant_api_key,
        request_data=request_data,
        direction="PAYOUT",
        db=db
    )
    return created_order

@router.get(
    "/payout/status/{order_identifier}",
    # response_model=GatewayStatusResponse, # Define specific status response
    response_model=IncomingOrderRead, # Example
    summary="Get Pay-Out Order Status",
    tags=["Gateway Pay-Out"]
)
def get_payout_status(
    order_identifier: str = Path(..., description="Unique identifier for the order (e.g., ID)"),
    db: Session = Depends(get_db_session)
):
    """Allows merchant/client to check the status of a Pay-Out order."""
    logger.info(f"Gateway: Received status request for Pay-Out order: {order_identifier}")
    return get_order_status(order_identifier, db) 