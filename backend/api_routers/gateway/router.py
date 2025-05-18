"""API Router for the public-facing Payment Gateway endpoints."""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Path, Body, Request, UploadFile, File, status, HTTPException, Header, Form
from sqlalchemy.ext.asyncio import AsyncSession
import io

from backend.database.db_ops import get_async_db_session
from backend.config.logger import get_logger
from backend.schemas_enums.gateway import (
    PaymentSessionInitRequest,
    PaymentSessionInitResponse,
    PaymentSessionDetails,
    GatewayIncomingOrderStatusResponse,
    PaymentPageConfirmationResponse
)
from backend.schemas_enums.order import IncomingOrderCreate, IncomingOrderRead
from backend.services.gateway_service import handle_init_request, get_order_status, handle_client_confirmation, GatewayService
from backend.services.order_status_manager import OrderStatusManager
from backend.utils.s3_client import upload_file_async
from backend.config.settings import settings
from backend.exceptions.custom_exceptions import JivaPayException, ObjectNotFoundError, PermissionDeniedError, InvalidInputError, AuthenticationError

logger = get_logger(__name__)

router = APIRouter(prefix="/gateway", tags=["Payment Gateway"])

# --- Dependency for GatewayService --- #
async def get_gateway_service(session: AsyncSession = Depends(get_async_db_session)) -> GatewayService:
    order_status_manager = OrderStatusManager(session)
    return GatewayService(session, order_status_manager)

# --- Gateway v2 Endpoints (New flow with Payment Sessions) --- #

@router.post(
    "/v2/payin/initiate_session",
    response_model=PaymentSessionInitResponse,
    summary="[V2] Initialize a Pay-In Transaction and Get Payment Session URL",
    tags=["Gateway V2 Pay-In"]
)
async def v2_initiate_payin_session(
    request_data: PaymentSessionInitRequest,
    x_api_key: str = Header(..., description="Merchant's Public API Key"),
    service: GatewayService = Depends(get_gateway_service)
):
    """
    Receives initial Pay-In request from merchant, creates an IncomingOrder 
    and a PaymentSession, then returns a URL to the dedicated payment page.
    """
    try:
        logger.info(f"Gateway V2: Received Pay-In session initiation. Key: {x_api_key[:10]}... Data: {request_data.model_dump_json(indent=2)}")
        response = await service.initiate_payment_session(request_data, x_api_key)
        return response
    except (ObjectNotFoundError, PermissionDeniedError, InvalidInputError, AuthenticationError) as e:
        logger.warning(f"Gateway V2 Pay-In init error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except JivaPayException as e:
        logger.error(f"Gateway V2 Pay-In init JivaPayException: {e.detail}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error in V2 Pay-In init: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during payment session initiation.")

@router.get(
    "/v2/payment/session/{payment_token}",
    response_model=PaymentSessionDetails,
    summary="[V2] Get Payment Session Details (for Payment Page)",
    tags=["Gateway V2 Pay-In"]
)
async def v2_get_payment_session_details(
    payment_token: str = Path(..., description="Unique token for the payment session"),
    service: GatewayService = Depends(get_gateway_service)
):
    """
    Endpoint for the payment page frontend to fetch details about the session 
    (e.g., amount, currency, expiry time).
    """
    try:
        logger.info(f"Gateway V2: Requesting payment session details for token: {payment_token}")
        details = await service.get_payment_session_details(payment_token)
        return details
    except ObjectNotFoundError as e:
        logger.warning(f"Gateway V2 session details: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except PermissionDeniedError as e:
        logger.warning(f"Gateway V2 session details permission error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except JivaPayException as e:
        logger.error(f"Gateway V2 session details JivaPayException: {e.detail}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error in V2 payment session details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching payment session details.")

@router.post(
    "/v2/payment/confirm/{payment_token}",
    response_model=PaymentPageConfirmationResponse, 
    summary="[V2] Confirm Payment from Payment Page (Client Action)",
    tags=["Gateway V2 Pay-In"]
)
async def v2_confirm_payment_from_page(
    payment_token: str = Path(..., description="Unique token for the payment session"),
    receipt_file: Optional[UploadFile] = File(None, description="Payment receipt upload"),
    notes: Optional[str] = Form(None, description="Optional notes from the client during payment"),
    service: GatewayService = Depends(get_gateway_service)
):
    """
    Endpoint for the dedicated payment page to submit payment confirmation, 
    including an optional receipt and notes.
    """
    logger.info(f"Gateway V2: Received payment page confirmation for token: {payment_token}. File: {receipt_file.filename if receipt_file else 'No'}, Notes: {notes}")
    
    receipt_content_bytes: Optional[bytes] = None
    original_filename: Optional[str] = None

    if receipt_file:
        try:
            receipt_content_bytes = await receipt_file.read()
            original_filename = receipt_file.filename
        except Exception as e:
            logger.error(f"Error reading uploaded file for token {payment_token}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail="Error processing uploaded receipt file.")
        finally:
            if hasattr(receipt_file, 'close'):
                 await receipt_file.close()

    try:
        response = await service.handle_payment_page_confirmation(
            payment_token=payment_token,
            receipt_content=receipt_content_bytes,
            receipt_filename=original_filename,
            notes=notes
        )
        return response
    except (ObjectNotFoundError, PermissionDeniedError, InvalidInputError) as e:
        logger.warning(f"Gateway V2 payment page confirmation error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except JivaPayException as e:
        logger.error(f"Gateway V2 payment page confirmation JivaPayException: {e.detail}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error in V2 payment page confirmation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during payment confirmation.")

@router.get(
    "/v2/payin/status",
    response_model=GatewayIncomingOrderStatusResponse,
    summary="[V2] Get Pay-In Order Status by ID or Payment Token",
    tags=["Gateway V2 Pay-In"]
)
async def v2_get_payin_status(
    incoming_order_id: Optional[int] = None,
    payment_token: Optional[str] = None,
    x_api_key: Optional[str] = Header(None, description="Merchant's Public API Key for ownership verification"),
    service: GatewayService = Depends(get_gateway_service)
):
    """
    Allows merchant/client to check the status of a Pay-In order using its ID or payment token.
    If X-API-KEY is provided, ownership is verified (typically for merchant calls).
    If only payment_token is provided, it can be used by client from redirect/payment page context.
    """
    if not incoming_order_id and not payment_token:
        raise HTTPException(status_code=400, detail="Either incoming_order_id or payment_token query parameter must be provided.")
    
    logger.info(f"Gateway V2: Status request. OrderID: {incoming_order_id}, Token: {payment_token}, APIKey: {x_api_key[:10] if x_api_key else 'N/A'}")
    try:
        status_response = await service.get_incoming_order_status(
            incoming_order_id=incoming_order_id, 
            payment_token=payment_token, 
            api_key=x_api_key
        )
        return status_response
    except (ObjectNotFoundError, PermissionDeniedError, InvalidInputError, AuthenticationError) as e:
        logger.warning(f"Gateway V2 status check error: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except JivaPayException as e:
        logger.error(f"Gateway V2 status check JivaPayException: {e.detail}", exc_info=True)
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error in V2 status check: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching order status.")

# --- Legacy Endpoints (To be reviewed/deprecated) --- #
# The following endpoints are from the older implementation and might need
# to be adapted, deprecated, or removed based on the new V2 flow.

@router.post(
    "/payin/init",
    response_model=IncomingOrderRead, 
    summary="(Legacy) Initialize a Pay-In Transaction",
    tags=["Gateway Legacy Pay-In"],
    deprecated=True
)
async def legacy_initialize_payin(
    request_data: IncomingOrderCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db_session),
    service: GatewayService = Depends(get_gateway_service)
):
    """(Legacy) Receives initial Pay-In request from merchant site, creates IncomingOrder."""
    merchant_api_key = request.headers.get("X-API-KEY")
    logger.warning(f"Gateway: LEGACY Pay-In init request. Key: {merchant_api_key}. Data: {request_data.model_dump_json(indent=2)}")
    try:
        created_order_model = await service.handle_init_request(
            api_key=merchant_api_key,
            request_data=request_data.model_dump(),
        )
        return IncomingOrderRead.from_orm(created_order_model)
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Legacy Pay-In init error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error in legacy pay-in initiation.")

@router.post(
    "/payin/confirm/{order_identifier}",
    status_code=202, 
    summary="(Legacy) Confirm Pay-In Payment (Client Action)",
    tags=["Gateway Legacy Pay-In"],
    deprecated=True
)
async def legacy_confirm_payin_payment(
    order_identifier: str = Path(..., description="Unique identifier for the order (e.g., ID)"),
    receipt_file: Optional[UploadFile] = File(None, description="Optional payment receipt upload"),
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY", description="Merchant's Public API Key"),
    service: GatewayService = Depends(get_gateway_service)
):
    """(Legacy) Endpoint for the end-client/merchant to confirm payment has been made."""
    logger.warning(f"Gateway: LEGACY payment confirmation for Pay-In order: {order_identifier}. File: {receipt_file is not None}")
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-KEY header is required for this operation.")

    receipt_content_bytes: Optional[bytes] = None
    original_filename: Optional[str] = None
    if receipt_file:
        try:
            receipt_content_bytes = await receipt_file.read()
            original_filename = receipt_file.filename
        except Exception as e:
            logger.error(f"Error reading legacy uploaded file for order {order_identifier}: {str(e)}")
            raise HTTPException(status_code=400, detail="Error processing uploaded receipt file.")
        finally:
            if hasattr(receipt_file, 'close'):
                 await receipt_file.close()
    try:
        await service.handle_client_confirmation_api(
            api_key=x_api_key,
            incoming_order_id=int(order_identifier),
            receipt_content=receipt_content_bytes,
            receipt_filename=original_filename
        )
        return {"message": "Confirmation received and is being processed."}
    except (ObjectNotFoundError, PermissionDeniedError, InvalidInputError, AuthenticationError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Legacy confirm payment error for {order_identifier}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during legacy payment confirmation.")

# --- Pay-Out Endpoints (Legacy - Review and Update to V2 if needed) --- #

@router.post(
    "/payout/init",
    response_model=IncomingOrderRead, 
    summary="(Legacy) Initialize a Pay-Out Transaction",
    tags=["Gateway Legacy Pay-Out"],
    deprecated=True
)
async def legacy_initialize_payout(
    request_data: IncomingOrderCreate,
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY", description="Merchant's Public API Key"),
    service: GatewayService = Depends(get_gateway_service)
):
    """(Legacy) Receives initial Pay-Out request from merchant site, creates IncomingOrder."""
    logger.warning(f"Gateway: LEGACY Pay-Out init request. Key: {x_api_key}. Data: {request_data.model_dump_json(indent=2)}")
    try:
        created_order_model = await service.handle_init_request(
            api_key=x_api_key,
            request_data=request_data.model_dump(),
        )
        return IncomingOrderRead.from_orm(created_order_model)
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Legacy Pay-Out init error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error in legacy pay-out initiation.")

@router.get(
    "/payout/status/{order_identifier}",
    response_model=GatewayIncomingOrderStatusResponse,
    summary="(Legacy) Get Pay-Out Order Status",
    tags=["Gateway Legacy Pay-Out"],
    deprecated=True
)
async def legacy_get_payout_status(
    order_identifier: str = Path(..., description="Unique identifier for the order (e.g., ID)"),
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY", description="Merchant's Public API Key"),
    service: GatewayService = Depends(get_gateway_service)
):
    """(Legacy) Allows merchant/client to check the status of a Pay-Out order."""
    logger.warning(f"Gateway: LEGACY status request for Pay-Out order: {order_identifier}")
    if not x_api_key:
         raise HTTPException(status_code=401, detail="X-API-KEY header is required for this operation.")
    try:
        return await service.get_incoming_order_status(incoming_order_id=int(order_identifier), api_key=x_api_key)
    except (ObjectNotFoundError, PermissionDeniedError, InvalidInputError, AuthenticationError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except JivaPayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Legacy get payout status error for {order_identifier}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching legacy payout status.") 