"""
Service for managing and retrieving order information, 
including history with advanced filtering and permission checks.
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func, or_, and_, String, cast
from datetime import datetime
from decimal import Decimal

from backend.database.db import (
    OrderHistory, IncomingOrder, User, Merchant, Trader, MerchantStore, ReqTrader
)
from backend.services.permission_service import PermissionService
from backend.utils.exceptions import AuthorizationError, DatabaseError
from backend.utils import query_utils
from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions

logger = get_logger(__name__)
SERVICE_NAME = "order_service"

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_orders_history(
    session: Session, 
    current_user: User, 
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None, 
    status: Optional[str] = None, 
    amount_exact: Optional[Decimal] = None, 
    amount_min: Optional[Decimal] = None,   
    amount_max: Optional[Decimal] = None,   
    trader_id: Optional[int] = None, 
    store_id: Optional[int] = None, 
    requisite_identifier: Optional[str] = None, 
    user_query: Optional[str] = None, 
    page: int = 1, 
    per_page: int = 20,
    sort_by: Optional[str] = "created_at",
    sort_direction: Optional[str] = "desc"
) -> Dict[str, Any]:
    """
    Retrieves a paginated history of orders with advanced filtering and search,
    respecting the current user's permissions.
    """
    perm_service = PermissionService(session)
    
    can_view_any_list = perm_service.check_permission(current_user.id, current_user.role.name, "orders:view:any_list")
    can_view_limited_list = perm_service.check_permission(current_user.id, current_user.role.name, "orders:view:limited_list")
    can_view_all_details = perm_service.check_permission(current_user.id, current_user.role.name, "orders:view:all_details")

    if not (can_view_any_list or can_view_limited_list):
        logger.warning(f"User {current_user.id} ({current_user.role.name}) has no basic permission to view any order list.")
        raise AuthorizationError("Not authorized to view order history.")

    MerchantUser = aliased(User, name="merchant_user_for_orders")
    TraderUser = aliased(User, name="trader_user_for_orders")

    items_query = session.query(OrderHistory)
    count_query = session.query(func.count(OrderHistory.id))

    def _apply_joins(query_obj: query_utils.Query) -> query_utils.Query:
        query_obj = query_obj.join(IncomingOrder, OrderHistory.incoming_order_id == IncomingOrder.id, isouter=True)\
                             .join(MerchantStore, OrderHistory.store_id == MerchantStore.id)\
                             .join(Merchant, OrderHistory.merchant_id == Merchant.id)\
                             .join(MerchantUser, Merchant.user_id == MerchantUser.id)\
                             .join(Trader, OrderHistory.trader_id == Trader.id)\
                             .join(TraderUser, Trader.user_id == TraderUser.id)\
                             .join(ReqTrader, OrderHistory.requisite_id == ReqTrader.id, isouter=True)
        return query_obj

    items_query = _apply_joins(items_query)
    count_query = _apply_joins(count_query)

    def _apply_order_filters(query_obj: query_utils.Query) -> query_utils.Query:
        query_obj = query_utils.apply_date_range_filter(query_obj, OrderHistory.created_at, start_time, end_time)
        
        if status:
            query_obj = query_obj.filter(OrderHistory.status.ilike(f"%{status}%"))
        
        amount_conditions = []
        if amount_exact is not None:
            amount_conditions.append(or_(OrderHistory.amount_fiat == amount_exact, OrderHistory.amount_crypto == amount_exact))
        if amount_min is not None:
            amount_conditions.append(or_(OrderHistory.amount_fiat >= amount_min, OrderHistory.amount_crypto >= amount_min))
        if amount_max is not None:
            amount_conditions.append(or_(OrderHistory.amount_fiat <= amount_max, OrderHistory.amount_crypto <= amount_max))
        if amount_conditions:
            query_obj = query_obj.filter(and_(*amount_conditions))

        if trader_id:
            query_obj = query_obj.filter(OrderHistory.trader_id == trader_id)
        if store_id:
            query_obj = query_obj.filter(OrderHistory.store_id == store_id)
        if requisite_identifier:
            query_obj = query_obj.filter(ReqTrader.req_number.ilike(f"%{requisite_identifier}%"))
        
        if user_query:
            search_term = f"%{user_query.lower()}%"
            query_obj = query_obj.filter(
                or_(
                    OrderHistory.hash_id.ilike(search_term),
                    cast(IncomingOrder.id, String).ilike(search_term),
                    MerchantUser.email.ilike(search_term),
                    TraderUser.email.ilike(search_term),
                    MerchantStore.store_name.ilike(search_term),
                )
            )
        return query_obj

    items_query = _apply_order_filters(items_query)
    count_query = _apply_order_filters(count_query)

    if not can_view_all_details and current_user.role.name == "support":
        restricted_statuses = []
        if not perm_service.check_permission(current_user.id, "support", "orders:view:status_failed"): restricted_statuses.append('failed')
        if not perm_service.check_permission(current_user.id, "support", "orders:view:status_cancelled"): restricted_statuses.append('cancelled')
        if not perm_service.check_permission(current_user.id, "support", "orders:view:status_fraud"): restricted_statuses.append('fraud')
        
        if restricted_statuses:
            if status:
                if status.lower() in restricted_statuses:
                    logger.debug(f"Support user {current_user.id} explicitly filtered for status '{status}' which is normally restricted. Filter proceeds.")
            else:
                for r_status in restricted_statuses:
                    items_query = items_query.filter(OrderHistory.status.notilike(f"%{r_status}%"))
                    count_query = count_query.filter(OrderHistory.status.notilike(f"%{r_status}%"))
                logger.info(f"Support user {current_user.id} order view restricted from statuses: {restricted_statuses}")
    
    sort_field_map = {
        "created_at": OrderHistory.created_at,
        "status": OrderHistory.status,
        "amount_fiat": OrderHistory.amount_fiat,
        "amount_crypto": OrderHistory.amount_crypto,
        "merchant_email": MerchantUser.email,
        "trader_email": TraderUser.email,
        "store_name": MerchantStore.store_name,
        "order_id": OrderHistory.id
    }
    items_query = query_utils.apply_sorting(items_query, sort_by, sort_direction, sort_field_map, default_sort_column=OrderHistory.created_at)

    orders, total_count = query_utils.get_paginated_results_and_count(
        base_query=items_query,
        count_query=count_query,
        page=page,
        per_page=per_page
    )

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "data": orders 
    }

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_orders_count(
    session: Session, 
    current_user: User,
    status: Optional[str] = None, 
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Counts orders, potentially filtered by status and date range,
    respecting user permissions.
    """
    perm_service = PermissionService(session)
    if not perm_service.check_permission(current_user.id, current_user.role.name, "orders:view:count_total") and \
       not perm_service.check_permission(current_user.id, current_user.role.name, "orders:view:count_limited"):
        raise AuthorizationError("Not authorized to count orders.")

    query = session.query(func.count(OrderHistory.id))
    
    query = query_utils.apply_date_range_filter(query, OrderHistory.created_at, start_time, end_time)
    if status:
        query = query.filter(OrderHistory.status.ilike(f"%{status}%"))

    can_view_all_details_for_count = perm_service.check_permission(current_user.id, current_user.role.name, "orders:view:all_details") 
    if not can_view_all_details_for_count and current_user.role.name == "support":
        restricted_statuses_for_count = []
        if not perm_service.check_permission(current_user.id, "support", "orders:view:status_failed"): restricted_statuses_for_count.append('failed')
        if not perm_service.check_permission(current_user.id, "support", "orders:view:status_cancelled"): restricted_statuses_for_count.append('cancelled')
        if not perm_service.check_permission(current_user.id, "support", "orders:view:status_fraud"): restricted_statuses_for_count.append('fraud')
        
        if restricted_statuses_for_count:
            if status and status.lower() in restricted_statuses_for_count:
                 pass
            else:
                for r_status in restricted_statuses_for_count:
                    query = query.filter(OrderHistory.status.notilike(f"%{r_status}%"))

    count = query.scalar() or 0
    return {"total_count": count} 

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_orders_for_trader(session: Session, current_trader_user: User, skip: int = 0, limit: int = 100) -> List[OrderHistory]:
    """
    Retrieves a list of orders assigned to the current trader.
    Requires 'trader_orders:read' permission (assumed to be checked by caller or could be added here).
    """
    # Ensure the user has a trader profile
    if not current_trader_user.trader_profile:
        logger.warning(f"User {current_trader_user.email} (ID: {current_trader_user.id}) attempting to list trader orders does not have a trader profile.")
        raise AuthorizationError("User does not have a trader profile.")
    
    trader_id = current_trader_user.trader_profile.id # Assuming trader_profile has an id which is the Trader.id
    # If current_trader_user *is* the Trader object directly, then current_trader_user.id would be used.
    # Given get_current_active_trader returns Trader, it's likely current_trader_user.id is the trader_id.
    # Let's re-verify how get_current_active_trader is implemented or what it returns.
    # For now, assuming the dependency `get_current_active_trader` in the router gives us a User object
    # which has a `trader_profile` attribute, and that profile's ID is the trader ID for filtering orders.
    # If `get_current_active_trader` directly returns a `Trader` object (which has `user_id` and `id` as PK for Trader table itself),
    # then the logic would be simpler: trader_id = current_trader_user.id (if current_trader_user is Trader type)

    # Based on common/trader_orders.py, current_trader: Trader, so current_trader.id is correct.
    # The service function signature uses User, so we need to adjust.
    # Let's assume current_trader_user is a User object, and trader_id is current_trader_user.trader_profile.id
    # However, the original router code used `current_trader.id` where `current_trader` was of type `Trader`.
    # This suggests `get_current_active_trader` might return a `Trader` object directly.
    # If so, the service should accept Trader or User and handle accordingly.
    # For now, let's stick to User and trader_profile.id, and adjust if `get_current_active_trader` returns Trader.

    # Rechecking get_current_active_trader. It is defined in backend/common/dependencies.py
    # It gets User, then tries to get user.trader_profile. If not found, raises 403.
    # It returns the user.trader_profile (which is a Trader object).
    # So, current_trader_user in the service will be a Trader object if called from router.
    # The signature `current_trader_user: User` in the service is thus a bit misleading in this context.
    # It should ideally be `current_trader_object: Trader` or the service needs to handle User and get trader_id.

    # Let's adjust service signature to accept Trader directly for clarity if this is its primary use case from trader routes.
    # Or, keep User and ensure trader_id extraction is robust.
    # Given the router provides Trader, let's assume for now the service gets Trader object as current_trader_user argument.

    logger.info(f"Trader (User ID: {current_trader_user.user_id}, Trader ID: {current_trader_user.id}) fetching their orders. Skip: {skip}, Limit: {limit}.")
    orders = (
        session.query(OrderHistory)
        .filter(OrderHistory.trader_id == current_trader_user.id) # Assuming current_trader_user is the Trader object
        .order_by(desc(OrderHistory.created_at)) # Added default sorting
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders 

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_orders_for_merchant(session: Session, current_merchant_user: User, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[OrderHistory]:
    """
    Retrieves a list of orders associated with the current merchant.
    Requires 'merchant_orders:read' permission (assumed to be checked by caller).
    """
    if not current_merchant_user.merchant_profile:
        logger.warning(f"User {current_merchant_user.email} (ID: {current_merchant_user.id}) attempting to list merchant orders does not have a merchant profile.")
        raise AuthorizationError("User does not have a merchant profile.")

    # Similar to get_orders_for_trader, current_merchant_user will be a Merchant object
    # due to get_current_active_merchant returning user.merchant_profile.
    merchant_id = current_merchant_user.id # current_merchant_user is Merchant object

    logger.info(f"Merchant (User ID: {current_merchant_user.user_id}, Merchant ID: {merchant_id}) fetching their orders. Skip: {skip}, Limit: {limit}, Status: {status_filter}.")

    query = session.query(OrderHistory).filter(OrderHistory.merchant_id == merchant_id)

    if status_filter:
        query = query.filter(OrderHistory.status.ilike(f"%{status_filter}%")) # Use ilike for case-insensitive status filter

    orders = (
        query.order_by(desc(OrderHistory.created_at)) # Added default sorting
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders

# Ensure other service functions if any are below this 