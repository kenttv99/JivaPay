"""API Router for the public-facing Payment Gateway endpoints."""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Path, Body, Request, Response, UploadFile, File
from sqlalchemy.orm import Session
import io

# Attempt imports (adjusting paths based on new location)
try:
    from backend.database.utils import get_db_session
    # !! Need Gateway specific Schemas (e.g., GatewayInitRequest, GatewayStatusResponse) !!
    # from backend.shemas_enums.gateway import GatewayInitRequest, GatewayStatusResponse, GatewayConfirmPayload
    from backend.shemas_enums.order import IncomingOrderCreate, IncomingOrderRead # Reuse or adapt
    # !! Need Gateway Service !!
    from backend.services.gateway_service import handle_init_request, get_order_status, handle_client_confirmation
    from backend.utils.s3_client import upload_fileobj
    from backend.config.settings import settings
    from backend.utils.exceptions import JivaPayException, OrderProcessingError
except ImportError as e:
    raise ImportError(f"Could not import required modules for gateway router (in api_routers/gateway/router.py): {e}")

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
    # request_data: GatewayInitRequest, # Define specific input schema
    request_data: IncomingOrderCreate, # Reuse for now
    request: Request, # To get merchant identifier (e.g., API key from header)
    db: Session = Depends(get_db_session)
):
    """Receives initial Pay-In request from merchant site, creates IncomingOrder."""
    # TODO: Identify merchant (API key, domain?)
    merchant_api_key = request.headers.get("X-API-KEY") # Example: Get key from header
    logger.info(f"Gateway: Received Pay-In init request. Key: {merchant_api_key}. Data: {request_data.dict()}")

    try:
        created_order = handle_init_request(
            api_key=merchant_api_key,
            request_data=request_data,
            direction="PAYIN",
            db=db
        )
        return created_order

    except JivaPayException as e:
        logger.warning(f"Gateway Pay-In init failed: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Gateway Pay-In init: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gateway processing error.")

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
    try:
        order = get_order_status(order_identifier, db)
        return order

    except OrderProcessingError as e:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JivaPayException as e:
        logger.warning(f"Gateway Pay-In status check failed for {order_identifier}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Gateway Pay-In status: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gateway processing error.")

@router.post(
    "/payin/confirm/{order_identifier}",
    # response_model=GatewayConfirmResponse, # Define response
    status_code=status.HTTP_202_ACCEPTED, # Or 200 OK if returning final status
    summary="Confirm Pay-In Payment (Client Action)",
    tags=["Gateway Pay-In"]
)
async def confirm_payin_payment(
    order_identifier: str = Path(..., description="Unique identifier for the order (e.g., ID)"),
    # Define payload: GatewayConfirmPayload? Or handle form data?
    # payload: GatewayConfirmPayload = Body(None), # Example with JSON body
    receipt_file: Optional[UploadFile] = File(None, description="Optional payment receipt upload"),
    db: Session = Depends(get_db_session)
):
    """Endpoint for the end-client to confirm they have made the payment (e.g., uploaded receipt)."""
    logger.info(f"Gateway: Received payment confirmation for Pay-In order: {order_identifier}. File provided: {receipt_file is not None}")
    try:
        uploaded_url = None
        if receipt_file:
            content = await receipt_file.read()
            buffer = io.BytesIO(content)
            key = f"receipts/{order_identifier}/{receipt_file.filename}"
            uploaded_url = upload_fileobj(buffer, settings.S3_BUCKET_NAME, key)
        updated = handle_client_confirmation(order_identifier, uploaded_url, db)
        return updated

    except JivaPayException as e:
        logger.warning(f"Gateway Pay-In confirmation failed for {order_identifier}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Gateway Pay-In confirmation: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gateway processing error.")

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
    try:
        created_order = handle_init_request(
            api_key=merchant_api_key,
            request_data=request_data,
            direction="PAYOUT",
            db=db
        )
        return created_order

    except JivaPayException as e:
        logger.warning(f"Gateway Pay-Out init failed: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Gateway Pay-Out init: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gateway processing error.")

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
    try:
        order = get_order_status(order_identifier, db)
        return order

    except OrderProcessingError as e:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JivaPayException as e:
        logger.warning(f"Gateway Pay-Out status check failed for {order_identifier}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Gateway Pay-Out status: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gateway processing error.") 