"""Service handling the logic for Gateway API requests."""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid
from datetime import datetime, timedelta, timezone

from backend.database.db import OrderHistory
from backend.config.logger import get_logger
from backend.config.settings import settings
from backend.database.db import MerchantStore, IncomingOrder, FiatCurrency, CryptoCurrency, PaymentSession # Added PaymentSession, FiatCurrency, CryptoCurrency
from backend.database.db_ops import get_entity_by_field, get_entity_by_id_logged
from backend.exceptions.custom_exceptions import (
    GatewayProcessingError,
    JivaPayException,
    ObjectNotFoundError,
    PermissionDeniedError,
    RateLimitExceededError, # Not directly used here, but good to be aware of for API layer
    AuthenticationError,
    InvalidInputError
)
from backend.schemas_enums.custom_types import OrderType
# Updated imports for Gateway v2
from backend.schemas_enums.gateway import (
    GatewayIncomingOrderStatusResponse,
    PaymentSessionInitRequest,
    PaymentSessionInitResponse,
    PaymentSessionDetails,
    PaymentPageConfirmationResponse # Added for confirmation response
)
from backend.services.base_service import BaseService
from backend.services.order_status_manager import OrderStatusManager # Assuming this will be updated
from backend.utils.decorators import handle_service_exceptions
from backend.utils.security import verify_api_key_hash # Assuming this exists for API key check
# Import the new order finalization function
from backend.services.order_processor import finalize_order_after_client_confirmation_async

# Attempt imports
try:
    # !! Models needed: MerchantStore, IncomingOrder !!
    from backend.database.db import MerchantStore, IncomingOrder
    from backend.database.utils import get_object_or_none, create_object
    # !! Need Schemas !!
    # from backend.sсhemas_enums.gateway import GatewayInitRequest # Specific schemas?
    from backend.schemas_enums.order import IncomingOrderCreate, DirectionEnum
    # !! Need Order Service (or create order directly here) !!
    # from backend.services import order_service
    # !! Need Order Status Manager !!
    from backend.services import order_status_manager
    # !! Need S3 client !!
    # from backend.utils.s3_client import upload_file
    from backend.utils.exceptions import (
        AuthenticationError, AuthorizationError, ConfigurationError, 
        OrderProcessingError, DatabaseError, JivaPayException, S3Error
    )
    from backend.worker.tasks import process_order_task
except ImportError as e:
    raise ImportError(f"Could not import required modules for GatewayService: {e}")

# Добавляем импорт декоратора и определяем SERVICE_NAME
from backend.utils.decorators import handle_service_exceptions
logger = get_logger(__name__)
SERVICE_NAME = "gateway_service"

class GatewayService(BaseService):
    """
    Service for handling gateway operations including PayIn/PayOut initiation,
    status checks, and client confirmations, now with Payment Session logic.
    """

    def __init__(self, session: AsyncSession, order_status_manager: OrderStatusManager):
        super().__init__(session)
        self.order_status_manager = order_status_manager

    async def _get_merchant_store_by_api_key(self, api_key: str) -> MerchantStore:
        """
        Retrieves and validates a merchant store using a public API key.
        Note: In a real scenario, API key hashing and secure comparison are crucial.
        This implementation assumes direct key comparison for simplicity during development.
        A more secure approach would involve hashing the input API key and comparing it
        against hashed keys in the database, or using a dedicated API key management service.
        """
        logger.debug(f"Attempting to find merchant store by API key (first 10 chars): {api_key[:10]}...")
        
        # This is a simplified lookup. In production, consider security implications:
        # 1. Hashing: Store hashed API keys, not plaintext. Compare hashes.
        # 2. Timing Attacks: Use constant-time comparison for hashes.
        # 3. API Key Rotation/Management: Have policies for key rotation and revocation.
        
        # For now, direct comparison (replace with secure method)
        stmt = select(MerchantStore).where(MerchantStore.public_api_key == api_key)
        result = await self.session.execute(stmt)
        store = result.scalars().first()

        if not store:
            logger.warning(f"Merchant store not found for API key (first 10 chars): {api_key[:10]}.")
            raise AuthenticationError("Invalid API Key.") # More specific than ObjectNotFoundError
        
        if not store.access or not store.trafic_access: # Assuming these flags control overall store access
            logger.warning(f"Access denied for store ID {store.id} linked to API key (first 10 chars): {api_key[:10]}. Store access: {store.access}, trafic_access: {store.trafic_access}")
            raise PermissionDeniedError(f"Store (ID: {store.id}) is currently disabled or traffic is not allowed.")

        logger.info(f"Merchant store ID {store.id} successfully retrieved for API key (first 10 chars): {api_key[:10]}.")
        return store

    @handle_service_exceptions(logger, "GatewayService", "Initiating Payment Session")
    async def initiate_payment_session(
        self, request_data: PaymentSessionInitRequest, api_key: str
    ) -> PaymentSessionInitResponse:
        """
        Initiates a new payment session for PayIn.
        Creates an IncomingOrder and a PaymentSession, returning a URL for the payment page.
        """
        merchant_store = await self._get_merchant_store_by_api_key(api_key)

        if request_data.order_type.lower() != OrderType.PAY_IN.value:
            raise InvalidInputError(f"Unsupported order_type '{request_data.order_type}'. Only 'pay_in' is supported for session initiation.")

        if not merchant_store.pay_in_enabled:
            raise PermissionDeniedError(f"Pay-in is disabled for store ID {merchant_store.id}.")

        # Validate amount against store limits
        if not (merchant_store.lower_limit <= request_data.amount_fiat <= merchant_store.upper_limit):
            raise InvalidInputError(
                f"Amount {request_data.amount_fiat} is outside the allowed limits for this store "
                f"({merchant_store.lower_limit} - {merchant_store.upper_limit})."
            )
        
        # TODO: Fetch actual exchange rate. For now, using a placeholder.
        # This should ideally come from a rate service or be calculated based on various factors.
        exchange_rate = Decimal("1.0") # Placeholder, ensure this is dynamic

        # Fetch FiatCurrency and CryptoCurrency to get codes for snapshot
        fiat_currency = await get_entity_by_id_logged(self.session, FiatCurrency, merchant_store.fiat_currency_id, logger, "FiatCurrency for store")
        crypto_currency = await get_entity_by_id_logged(self.session, CryptoCurrency, merchant_store.crypto_currency_id, logger, "CryptoCurrency for store")


        # Create IncomingOrder
        incoming_order = IncomingOrder(
            merchant_id=merchant_store.merchant_id,
            store_id=merchant_store.id,
            fiat_currency_id=merchant_store.fiat_currency_id,
            crypto_currency_id=merchant_store.crypto_currency_id, # Assuming pay_in implies store's crypto
            amount_fiat=request_data.amount_fiat,
            # amount_crypto will be calculated by order processor later or based on rate
            exchange_rate=exchange_rate, # Placeholder
            store_commission=Decimal("0.0"), # Placeholder, should be from store settings
            order_type=request_data.order_type,
            customer_id=request_data.customer_id,
            return_url=str(request_data.return_url) if request_data.return_url else None,
            callback_url=str(request_data.callback_url_for_merchant) if request_data.callback_url_for_merchant else None,
            status="new", # Initial status
            # client_id could be generated here or passed in request_data.additional_params if needed
        )
        self.session.add(incoming_order)
        await self.session.flush() # To get incoming_order.id

        # Create PaymentSession
        session_token = uuid.uuid4().hex
        payment_page_url = f"{settings.PAYMENT_GATEWAY_BASE_URL}/session/{session_token}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.PAYMENT_SESSION_TIMEOUT_SECONDS)

        payment_session = PaymentSession(
            incoming_order_id=incoming_order.id,
            token=session_token,
            payment_page_url=payment_page_url,
            status="active",
            expires_at=expires_at,
            amount_fiat_snapshot=incoming_order.amount_fiat,
            fiat_currency_code_snapshot=fiat_currency.currency_code # e.g. "RUB"
        )
        self.session.add(payment_session)
        await self.session.commit()
        logger.info(f"Payment session {payment_session.id} (token: {session_token}) created for IncomingOrder {incoming_order.id}")

        return PaymentSessionInitResponse(
            payment_url=payment_page_url,
            incoming_order_id=incoming_order.id,
            payment_token=session_token,
            expires_at=expires_at,
        )

    @handle_service_exceptions(logger, "GatewayService", "Getting Payment Session Details")
    async def get_payment_session_details(self, payment_token: str) -> PaymentSessionDetails:
        """
        Retrieves details for a payment session, intended for use by the payment page.
        """
        stmt = (
            select(PaymentSession)
            .options(joinedload(PaymentSession.incoming_order).joinedload(IncomingOrder.store))
            .where(PaymentSession.token == payment_token)
        )
        result = await self.session.execute(stmt)
        session = result.scalars().first()

        if not session:
            raise ObjectNotFoundError(f"Payment session with token '{payment_token}' not found.")
        
        if session.status != "active" or session.expires_at < datetime.now(timezone.utc):
            session.status = "expired" if session.status == "active" else session.status # Mark as expired if it was active
            await self.session.commit()
            logger.warning(f"Payment session {session.id} (token: {payment_token}) is not active or has expired. Status: {session.status}, Expires at: {session.expires_at}")
            raise PermissionDeniedError(f"Payment session is not active or has expired.")

        return PaymentSessionDetails(
            incoming_order_id=session.incoming_order_id,
            payment_token=session.token,
            amount_fiat_snapshot=session.amount_fiat_snapshot,
            fiat_currency_code_snapshot=session.fiat_currency_code_snapshot,
            merchant_store_name=session.incoming_order.store.store_name if session.incoming_order and session.incoming_order.store else "Merchant", # Fallback name
            expires_at=session.expires_at,
        )

    @handle_service_exceptions(logger, "GatewayService", "Handling Payment Page Confirmation")
    async def handle_payment_page_confirmation(
        self,
        payment_token: str,
        receipt_content: Optional[bytes],
        receipt_filename: Optional[str],
        notes: Optional[str] = None,
    ) -> PaymentPageConfirmationResponse:
        """
        Handles payment confirmation submitted from the dedicated payment page.
        This will find the IncomingOrder via PaymentSession, update its status via OrderStatusManager,
        and then trigger final processing (OrderHistory creation, receipt upload) via OrderProcessor.
        """
        logger.info(f"Handling payment page confirmation for token: {payment_token}")
        stmt = select(PaymentSession).where(PaymentSession.token == payment_token)
        result = await self.session.execute(stmt)
        payment_session = result.scalars().first() # Renamed from session to payment_session for clarity

        if not payment_session:
            raise ObjectNotFoundError(f"Payment session with token '{payment_token}' not found for confirmation.")
        
        if payment_session.status != "active":
            logger.warning(f"Payment confirmation attempt on non-active session. Token: {payment_token}, Status: {payment_session.status}")
            raise PermissionDeniedError(f"Payment session is not active. Current status: {payment_session.status}.")
            
        if payment_session.expires_at < datetime.now(timezone.utc):
            payment_session.status = "expired"
            await self.session.commit() # Commit early if session is expired
            logger.warning(f"Payment confirmation attempt on expired session. Token: {payment_token}")
            raise PermissionDeniedError("Payment session has expired.")

        incoming_order = await get_entity_by_id_logged(self.session, IncomingOrder, payment_session.incoming_order_id, logger, "IncomingOrder for payment confirmation")
        if not incoming_order: # Should not happen if session exists and points to a valid order
            # Update payment session status to reflect this inconsistency
            payment_session.status = "failed_consistency_error" 
            await self.session.commit()
            raise GatewayProcessingError(f"Consistency error: IncomingOrder ID {payment_session.incoming_order_id} linked to PaymentSession {payment_session.id} not found.")

        # Step 1: Confirm payment by client via OrderStatusManager
        # This updates IncomingOrder status to 'client_payment_confirmed' and other relevant fields.
        # It does NOT handle receipt upload or OrderHistory creation anymore.
        try:
            updated_incoming_order = await self.order_status_manager.confirm_payment_from_gateway_page(
                incoming_order_id=incoming_order.id,
                payment_details_text=notes, # Pass notes as payment_details_text
                # user_id=None, # Decide on user_id for audit, maybe from a system config or merchant
                # ip_address=None # If available from request
            )
            logger.info(f"IncomingOrder {incoming_order.id} status updated to '{updated_incoming_order.status}' by OrderStatusManager.")
        except JivaPayException as e:
            # If OrderStatusManager fails, update PaymentSession and re-raise
            payment_session.status = "failed_confirmation" # Custom status
            # Log details of what went wrong with OSM
            payment_session.failure_reason = f"OrderStatusManager error: {str(e.detail)[:200]}"
            await self.session.commit()
            logger.error(f"Error during OrderStatusManager.confirm_payment_from_gateway_page for IO {incoming_order.id}: {e.detail}")
            raise # Re-raise the original exception to be caught by decorator or router

        # Step 2: Finalize order processing (OrderHistory, receipt) via OrderProcessor
        # This is a critical step that was previously deferred.
        order_history_id: Optional[int] = None
        try:
            finalization_result = await finalize_order_after_client_confirmation_async(
                db=self.session,
                incoming_order_id=updated_incoming_order.id,
                receipt_content=receipt_content,
                receipt_filename=receipt_filename,
                payment_token=payment_token # For audit logging context
            )
            
            order_history_id = finalization_result.get("order_history_id")
            
            # Update PaymentSession based on finalization result
            # finalize_order_after_client_confirmation_async returns 'payment_session_status' which should be the new status
            payment_session.status = finalization_result.get("payment_session_status", "completed_with_issues") # Default if key missing
            if finalization_result.get("failure_reason"):
                payment_session.failure_reason = str(finalization_result.get("failure_reason"))[:255] # Ensure length constraint

            logger.info(f"Order finalization for IO {updated_incoming_order.id} completed. OH_ID: {order_history_id}, PS_Status: {payment_session.status}")
            
            # Note: IncomingOrder status is updated within finalize_order_after_client_confirmation_async
            # We trust it to set the final IO status (e.g., 'processed', 'failed').
            
        except InvalidInputError as iie: # Raised by finalize_order if IO status is not 'client_payment_confirmed'
            payment_session.status = "failed_invalid_state"
            payment_session.failure_reason = f"OrderProcessor InvalidInput: {str(iie.detail)[:200]}"
            await self.session.commit()
            logger.error(f"OrderProcessor.finalize_order_after_client_confirmation_async failed for IO {updated_incoming_order.id} due to invalid state: {iie.detail}")
            # This specific error from finalize_order implies a pre-condition was not met.
            # We return a specific error response.
            raise HTTPException(status_code=409, detail=f"Order processing cannot proceed: {iie.detail}")
        except Exception as proc_exc:
            # Catch any other exception from finalize_order_after_client_confirmation_async
            payment_session.status = "failed_processing" # Generic processing failure for PaymentSession
            payment_session.failure_reason = f"OrderProcessor error: {str(proc_exc)[:200]}"
            logger.error(f"Error during order_processor.finalize_order_after_client_confirmation_async for IO {updated_incoming_order.id}: {proc_exc}", exc_info=True)
            # The IncomingOrder status might have been set to 'failed' inside finalize_order.
            # We must commit the PaymentSession changes.
            # This exception will be caught by the main handler or decorator.
            # We raise a generic error to the client but log specifics.
            # No, let the decorator handle raising HTTP error after commit.
            # We need to ensure session is committed before raising or returning.
            await self.session.commit() # Commit PaymentSession changes
            raise GatewayProcessingError(detail=f"An error occurred during final order processing. Please check order status later.")


        # If we've reached here, both OSM and OrderProcessor (attempt) have run.
        # Commit all changes made to PaymentSession and potentially by OrderProcessor (if not self-committed)
        await self.session.commit()
        
        # Prepare response
        # The actual status of the order and history should be reflected from the finalization_result
        # or the updated_incoming_order if finalization had issues.
        
        final_io_status = finalization_result.get("status", updated_incoming_order.status) if 'finalization_result' in locals() else updated_incoming_order.status

        response_message = "Payment confirmed and processing initiated."
        if finalization_result.get("failure_reason") if 'finalization_result' in locals() else None:
            response_message = f"Payment confirmed, but processing encountered issues: {finalization_result.get('failure_reason')}"
        elif final_io_status != "processed": # Assuming 'processed' is the ideal final status from OrderProcessor
             response_message = f"Payment confirmed. Order status: {final_io_status}."


        return PaymentPageConfirmationResponse(
            status=final_io_status, # Reflects the final status of the IncomingOrder
            message=response_message,
            order_history_id=order_history_id # This now comes from the order_processor
        )


    @handle_service_exceptions(logger, "GatewayService", "Getting Incoming Order Status")
    async def get_incoming_order_status(
        self, incoming_order_id: Optional[int] = None, payment_token: Optional[str] = None, api_key: Optional[str] = None
    ) -> GatewayIncomingOrderStatusResponse:
        """
        Retrieves the status of an IncomingOrder, identified by its ID or payment token.
        If api_key is provided, it also verifies merchant ownership.
        """
        if not incoming_order_id and not payment_token:
            raise InvalidInputError("Either incoming_order_id or payment_token must be provided.")

        query = select(IncomingOrder).options(joinedload(IncomingOrder.payment_session))
        
        if payment_token:
            # Find IncomingOrder via PaymentSession token
            session_stmt = select(PaymentSession).where(PaymentSession.token == payment_token)
            session_res = await self.session.execute(session_stmt)
            payment_session_obj = session_res.scalars().first()
            if not payment_session_obj:
                raise ObjectNotFoundError(f"No payment session found for token {payment_token}")
            incoming_order_id = payment_session_obj.incoming_order_id
            # Now query will use this ID

        # At this point, incoming_order_id is set
        query = query.where(IncomingOrder.id == incoming_order_id)
        
        result = await self.session.execute(query)
        order = result.scalars().first()

        if not order:
            raise ObjectNotFoundError(f"Incoming order with ID {incoming_order_id} not found.")

        if api_key: # If called by merchant, verify ownership
            merchant_store = await self._get_merchant_store_by_api_key(api_key)
            if order.store_id != merchant_store.id:
                raise PermissionDeniedError(
                    f"Access denied. Merchant store {merchant_store.id} does not own incoming order {order.id}."
                )
        
        payment_url_response = None
        if order.payment_session and order.payment_session.status == "active" and order.payment_session.expires_at > datetime.now(timezone.utc):
            payment_url_response = order.payment_session.payment_page_url


        # Check for related OrderHistory status
        order_history_status = None
        if order.assigned_order_rel: # Assuming this is the link to OrderHistory
            order_history_status = order.assigned_order_rel.status
        else:
            # Try to find OrderHistory if not directly linked in the loaded object
            stmt_oh = select(OrderHistory.status).where(OrderHistory.incoming_order_id == order.id)
            res_oh = await self.session.execute(stmt_oh)
            order_history_status_val = res_oh.scalars().first()
            if order_history_status_val:
                order_history_status = order_history_status_val


        return GatewayIncomingOrderStatusResponse(
            incoming_order_id=order.id,
            external_order_id=getattr(order, 'external_order_id', None), # If this field exists
            status=order.status,
            order_history_status=order_history_status,
            payment_url=payment_url_response,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    # --- Existing methods to be reviewed/refactored or removed if obsolete ---

    @handle_service_exceptions(logger, "GatewayService", "Handling Init Request (Legacy/Payout)")
    async def handle_init_request(
        self, api_key: str, request_data: dict # schema.GatewayRequest - old schema?
    ) -> IncomingOrder: # Should return a schema, not a model
        """
        Handles the initialization of a payment (PayIn or PayOut).
        This might be primarily for PayOut now, or a generic internal entry point.
        PayIn is now handled by `initiate_payment_session`.
        """
        # This method needs careful review. If it's only for PayOut,
        # its logic will differ significantly from PayIn.
        # For now, assuming it might be a generic internal way or for PayOut.

        logger.info(f"Handling init request for API key: {api_key[:10]}...")
        merchant_store = await self._get_merchant_store_by_api_key(api_key)

        order_type_str = request_data.get("order_type")
        if not order_type_str or order_type_str.lower() not in [ot.value for ot in OrderType]:
             raise InvalidInputError(f"Invalid or missing order_type. Supported: {[ot.value for ot in OrderType]}")
        
        order_type_val = OrderType(order_type_str.lower())

        if order_type_val == OrderType.PAY_IN and not merchant_store.pay_in_enabled:
            raise PermissionDeniedError(f"Pay-in is disabled for store ID {merchant_store.id}.")
        if order_type_val == OrderType.PAY_OUT and not merchant_store.pay_out_enabled:
            raise PermissionDeniedError(f"Pay-out is disabled for store ID {merchant_store.id}.")

        # TODO: Add amount validation against store limits similar to initiate_payment_session
        # TODO: Determine exchange rate, commissions etc.

        # This is a very simplified creation, needs more business logic from original implementation
        # or from the Payout specific requirements.
        incoming_order = IncomingOrder(
            merchant_id=merchant_store.merchant_id,
            store_id=merchant_store.id,
            fiat_currency_id=merchant_store.fiat_currency_id, # Should be from request for Payout?
            crypto_currency_id=merchant_store.crypto_currency_id, # Should be from request for Payout?
            amount_fiat=request_data.get("amount_fiat"), # Or amount_crypto for payout
            # ... other fields based on request_data and Payout logic
            order_type=order_type_val.value,
            status="new",
            # ...
        )
        self.session.add(incoming_order)
        await self.session.commit()
        logger.info(f"IncomingOrder {incoming_order.id} created for store {merchant_store.id}, type: {order_type_val.value}.")
        return incoming_order # Return a Pydantic schema instead

    @handle_service_exceptions(logger, "GatewayService", "Handling Client Confirmation (Legacy/API)")
    async def handle_client_confirmation_api( # Renamed to avoid clash if old one is kept
        self,
        api_key: str, # Merchant API key
        incoming_order_id: int,
        receipt_content: Optional[bytes],
        receipt_filename: Optional[str],
    ) -> OrderHistory: # Should return a Pydantic schema
        """
        Handles payment confirmation by the client (e.g., merchant confirming on behalf of customer, or payout proof).
        This version is for API calls by the merchant.
        The payment page confirmation is handle_payment_page_confirmation.
        """
        logger.info(f"Handling client confirmation via API for order ID: {incoming_order_id} by API key {api_key[:10]}...")
        merchant_store = await self._get_merchant_store_by_api_key(api_key)
        
        incoming_order = await get_entity_by_id_logged(self.session, IncomingOrder, incoming_order_id, logger, "IncomingOrder for client confirmation")
        if not incoming_order:
            raise ObjectNotFoundError(f"Incoming order with ID {incoming_order_id} not found.")

        if incoming_order.store_id != merchant_store.id:
            raise PermissionDeniedError("Merchant does not own this order.")

        # Here, the OrderStatusManager would be called.
        # The actor would likely be the merchant user associated with the store/API key.
        # This needs to be resolved. For now, passing None or a system actor.
        # actor_id = await self._get_actor_id_for_merchant_store(merchant_store) # Placeholder
        
        order_history = await self.order_status_manager.confirm_payment_by_client(
            incoming_order_id=incoming_order.id,
            receipt_content=receipt_content,
            receipt_filename=receipt_filename,
            # actor_id=actor_id # Pass actual actor
        )
        
        # Update incoming_order status, e.g. to 'processing_confirmation' or similar
        incoming_order.status = "processing" # Or a more specific status
        incoming_order.payment_details_submitted = True
        await self.session.commit()
        logger.info(f"Client confirmation for order {incoming_order.id} (OrderHistory: {order_history.id if order_history else 'N/A'}) processed.")
        return order_history # Return a Pydantic schema instead
        
    # Placeholder for _get_actor_id_for_merchant_store
    # async def _get_actor_id_for_merchant_store(self, store: MerchantStore) -> Optional[int]:
    #     # This method would ideally find the User associated with the Merchant
    #     # who owns this store, to be used as the actor_id for audit logging.
    #     # For simplicity, returning None.
    #     # stmt = select(User.id).join(Merchant).where(Merchant.id == store.merchant_id)
    #     # user_id = await self.session.scalar(stmt)
    #     # return user_id
    #     return None

# Example of how OrderStatusManager might need to be structured or called (conceptual)
# class OrderStatusManager:
#     async def confirm_payment_by_client(self, incoming_order_id: int, receipt_content: Optional[bytes], receipt_filename: Optional[str], actor_id: Optional[int] = None, client_notes: Optional[str] = None) -> Optional[int]:
#         # ... logic to create/update OrderHistory
#         # ... logic to save receipt_content to S3 and create UploadedDocument linking to OrderHistory and actor_id
#         # ... update OrderHistory status to 'pending_trader_confirmation' for PayIn
#         # ... update IncomingOrder status if necessary
#         # Returns OrderHistory.id
#         pass

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def _get_merchant_store_by_api_key(api_key: Optional[str], db: Session) -> MerchantStore:
    """Authenticates and retrieves the merchant store based on API key."""
    if not api_key:
        raise AuthenticationError("API key is missing.")
    
    # Secure API key lookup using public_api_key field
    store = get_object_or_none(db, MerchantStore, public_api_key=api_key)
    
    if not store:
        raise AuthenticationError("Invalid API key.")
    if not store.access:
        raise AuthorizationError("Merchant store is inactive.")
    
    logger.debug(f"Authenticated merchant store ID: {store.id} using API key.")
    return store

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def handle_init_request(
    api_key: Optional[str],
    request_data: IncomingOrderCreate, # Or specific GatewayInitRequest schema
    direction: str, # "PAYIN" or "PAYOUT"
    db: Session
) -> IncomingOrder: # Return the created IncomingOrder object
    """Handles the initialization request from the gateway.

    - Identifies merchant.
    - Validates request against store settings.
    - Creates the IncomingOrder record.
    """
    # 1. Identify Merchant
    merchant_store = _get_merchant_store_by_api_key(api_key, db)
    logger.info(f"Handling {direction} init request for Store ID: {merchant_store.id}")

    # 2. Validate Request Data against Store Settings
    # TODO: Implement validation
    # - Check if merchant_store allows this direction (payin_enabled/payout_enabled)
    # - Check if request has required params based on store settings (gateway_require_customer_id, etc.)
    # - Check currency/payment method compatibility with store
    # - Raise ConfigurationError or OrderProcessingError (4xx) if validation fails
    if direction == "PAYIN" and not merchant_store.pay_in_enabled:
         raise AuthorizationError(f"Pay-In is not enabled for store {merchant_store.id}")
    if direction == "PAYOUT" and not merchant_store.pay_out_enabled:
         raise AuthorizationError(f"Pay-Out is not enabled for store {merchant_store.id}")
    # Example check for required param:
    # if merchant_store.gateway_require_customer_id and not request_data.customer_id:
    #     raise OrderProcessingError("Customer ID is required for this merchant.", status_code=400)
    logger.debug(f"Request validation passed (placeholder) for Store ID: {merchant_store.id}")

    # 3. Create IncomingOrder record
    try:
        # request_data is an instance of IncomingOrderCreate with new field names
        # and validated conditional fields (e.g., amount_fiat is present if order_type is PAY_IN)
        order_data_db = {}

        # Transfer validated and correctly named fields from Pydantic schema
        order_data_db['order_type'] = request_data.order_type.value # Get string value from enum

        if request_data.order_type == DirectionEnum.PAY_IN:
            order_data_db['amount_fiat'] = request_data.amount_fiat
            order_data_db['fiat_currency_id'] = request_data.fiat_currency_id
            # Derive the other required currency ID from the store
            order_data_db['crypto_currency_id'] = merchant_store.crypto_currency_id
        elif request_data.order_type == DirectionEnum.PAY_OUT:
            order_data_db['amount_crypto'] = request_data.amount_crypto
            order_data_db['crypto_currency_id'] = request_data.crypto_currency_id
            # Derive the other required currency ID from the store
            order_data_db['fiat_currency_id'] = merchant_store.fiat_currency_id
        
        order_data_db['target_method_id'] = request_data.target_method_id

        # Optional fields from Pydantic schema
        if request_data.customer_id is not None:
            order_data_db['customer_id'] = request_data.customer_id
        if request_data.return_url is not None:
            order_data_db['return_url'] = request_data.return_url
        if request_data.callback_url is not None:
            order_data_db['callback_url'] = request_data.callback_url
        
        # Add other necessary fields for IncomingOrder creation
        order_data_db.update({
            'merchant_id': merchant_store.merchant_id,
            'store_id': merchant_store.id,
            # 'gateway_id': merchant_store.id, # Placeholder, might need specific gateway logic
            'status': 'new',
            'retry_count': 0,
            # CRITICAL: exchange_rate and store_commission must be properly calculated/fetched.
            # These are required by the DB model but not part of IncomingOrderCreate schema.
            'exchange_rate': Decimal('1.0'), # Placeholder
            'store_commission': Decimal('0.0')  # Placeholder
        })

        created_order = create_object(db, IncomingOrder, order_data_db)
        logger.info(f"Created IncomingOrder ID {created_order.id} for Store ID {merchant_store.id}")
        # Immediately enqueue the order for processing to achieve real-time handling
        process_order_task.delay(created_order.id)
        return created_order
    except Exception as e:
        msg = f"Failed to create IncomingOrder for Store {merchant_store.id}: {e}"
        logger.error(msg, exc_info=True)
        if isinstance(e, DatabaseError):
            raise
        raise OrderProcessingError(msg) from e

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_order_status(order_identifier: str, db: Session) -> Any: # Return type depends on desired response schema
    """Retrieves the status details for a given order identifier."""
    logger.debug(f"Getting status for order identifier: {order_identifier}")
    # 1. Try to find in OrderHistory
    order = get_object_or_none(db, OrderHistory, hash_id=order_identifier)
    if order:
        return order
    # 2. Try to find in IncomingOrder by ID
    try:
        incoming_id = int(order_identifier)
        order = get_object_or_none(db, IncomingOrder, id=incoming_id)
        if order:
            return order
    except ValueError:
        pass
    raise OrderProcessingError(f"Order not found: {order_identifier}", status_code=404)

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def handle_client_confirmation(
    order_identifier: str, 
    receipt_content: Optional[bytes], 
    receipt_filename: Optional[str],
    db: Session
) -> OrderHistory:
    """Handles the client confirmation action from the gateway."""
    logger.info(f"Handling client confirmation for order identifier: {order_identifier}, file provided: {receipt_content is not None}")
    
    oh = get_object_or_none(db, OrderHistory, hash_id=order_identifier)
    if not oh:
        # Simplified error handling for now. Robust version would check IncomingOrder too.
        logger.warning(f"OrderHistory not found for hash_id: {order_identifier} during client confirmation.")
        raise OrderProcessingError(f"Order not found or not ready for confirmation: {order_identifier}", status_code=404)

    # order_status_manager.confirm_payment_by_client handles the S3 upload internally
    updated_order = order_status_manager.confirm_payment_by_client(
        order_id=oh.id,
        receipt=receipt_content, # Pass bytes directly
        filename=receipt_filename or "uploaded_receipt.bin", # Pass filename or a default
        db_session=db
    )
    
    logger.info(f"Client confirmation processed for order {order_identifier} (OH ID: {oh.id}). Status: {updated_order.status}")
    return updated_order 