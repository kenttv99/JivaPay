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
def get_orders_for_trader(session: Session, current_trader: Trader, skip: int = 0, limit: int = 100) -> List[OrderHistory]:
    """
    Retrieves a list of orders assigned to the current trader.
    The `current_trader` argument is expected to be an instance of the Trader model.
    """
    # Проверка current_trader.trader_profile больше не нужна, так как current_trader УЖЕ является объектом Trader
    # if not current_trader_user.trader_profile: ... (удалено)
    
    # trader_id = current_trader_user.trader_profile.id (старая логика, если бы передавался User)
    # Теперь current_trader.id это и есть trader_id

    logger.info(f"Trader ID: {current_trader.id} (User ID: {current_trader.user_id if hasattr(current_trader, 'user_id') else 'N/A'}) fetching their orders. Skip: {skip}, Limit: {limit}.")
    orders = (
        session.query(OrderHistory)
        .filter(OrderHistory.trader_id == current_trader.id)
        .order_by(desc(OrderHistory.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders 

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_orders_for_merchant(session: Session, current_merchant: Merchant, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[OrderHistory]:
    """
    Retrieves a list of orders associated with the current merchant.
    The `current_merchant` argument is expected to be an instance of the Merchant model.
    """
    # Проверка current_merchant.merchant_profile больше не нужна, так как current_merchant УЖЕ является объектом Merchant
    # if not current_merchant_user.merchant_profile: ... (удалено)

    # merchant_id теперь это current_merchant.id
    merchant_id = current_merchant.id

    logger.info(f"Merchant ID: {merchant_id} (User ID: {current_merchant.user_id if hasattr(current_merchant, 'user_id') else 'N/A'}) fetching their orders. Skip: {skip}, Limit: {limit}, Status: {status_filter}.")

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