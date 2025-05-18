"""
Service for managing and retrieving merchant-related information, 
including statistics and detailed profiles, with permission checks.
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload, selectinload, aliased
from sqlalchemy import func, or_, and_, desc, asc, String, cast
from datetime import datetime
from decimal import Decimal

from backend.database.db import (
    Merchant, User, MerchantStore, OrderHistory, BalanceStoreHistory
)
from backend.services.permission_service import PermissionService
from backend.utils.exceptions import AuthorizationError, DatabaseError, NotFoundError
from backend.utils import query_utils
from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions

logger = get_logger(__name__)
SERVICE_NAME = "merchant_service"

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_merchants_statistics(
    session: Session,
    current_user: User, 
    status_filter: Optional[str] = 'active', 
    turnover_period_start: Optional[datetime] = None,
    turnover_period_end: Optional[datetime] = None,
    sort_by: Optional[str] = None, 
    sort_direction: Optional[str] = "asc",
    search_query: Optional[str] = None, 
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Retrieves paginated statistics for merchants with filtering, sorting, and permission checks.
    """
    perm_service = PermissionService(session)
    # Initial broad permission check
    can_view_full_stats = perm_service.check_permission(current_user.id, current_user.role.name, "merchants:view:list_statistics")
    can_view_limited_stats_for_support = False
    if current_user.role.name == "support":
        can_view_limited_stats_for_support = perm_service.check_permission(current_user.id, "support", "merchants:view:list_statistics_limited")

    if not (can_view_full_stats or can_view_limited_stats_for_support):
        logger.warning(f"User {current_user.id} ({current_user.role.name}) lacks permission to view merchant statistics.")
        raise AuthorizationError("Not authorized to view merchant statistics.")

    MerchantUser = aliased(User, name="merchant_user_for_stats")

    items_query = session.query(
        Merchant,
        MerchantUser.email.label("user_email"),
        MerchantUser.is_active.label("user_is_active"),
        MerchantUser.created_at.label("user_created_at")
    ).join(MerchantUser, Merchant.user_id == MerchantUser.id)

    count_query = session.query(func.count(func.distinct(Merchant.id)))\
                         .join(MerchantUser, Merchant.user_id == MerchantUser.id)

    def _apply_merchant_filters(query_obj: query_utils.Query) -> query_utils.Query:
        query_obj = query_utils.apply_user_status_filter(query_obj, MerchantUser, status_filter)
        
        if search_query:
            search_term = f"%{search_query.lower()}%"
            # Subquery to find merchant_ids that have stores matching the name
            # This ensures we are filtering Merchants, not MerchantStores directly in the main query's FROM clause
            store_owner_merchant_ids_sq = session.query(MerchantStore.merchant_id)\
                .filter(MerchantStore.store_name.ilike(search_term)).distinct().subquery()
            
            query_obj = query_obj.filter(
                or_(
                    MerchantUser.email.ilike(search_term),
                    cast(Merchant.id, String).ilike(search_term),
                    Merchant.id.in_(session.query(store_owner_merchant_ids_sq.c.merchant_id))
                )
            )
        return query_obj

    items_query = _apply_merchant_filters(items_query)
    count_query = _apply_merchant_filters(count_query)

    # --- Granular permission filtering for Support (Conceptual) ---
    # If can_view_limited_stats_for_support is True but can_view_full_stats is False,
    # specific filters for support could be applied here. Since they are not defined,
    # the current behavior is that they see data based on common filters.
    if current_user.role.name == "support" and can_view_limited_stats_for_support and not can_view_full_stats:
        logger.info(f"Support user {current_user.id} has limited view for merchant stats. No specific granular filters yet defined.")
        # Placeholder: If specific support filters were added, apply them to items_query and count_query here.
        # e.g., query = query.filter(Merchant.category_id.in_(support_user_allowed_categories))
        pass 

    # --- Subqueries for aggregated data ---
    turnover_sq_col, order_count_sq_col, store_count_sq_col = None, None, None

    turnover_subquery = session.query(
        OrderHistory.merchant_id,
        func.sum(OrderHistory.amount_fiat).label("total_turnover")
    ).filter(OrderHistory.order_type == 'pay_in')
    if turnover_period_start: turnover_subquery = turnover_subquery.filter(OrderHistory.created_at >= turnover_period_start)
    if turnover_period_end: turnover_subquery = turnover_subquery.filter(OrderHistory.created_at <= turnover_period_end)
    turnover_subquery = turnover_subquery.group_by(OrderHistory.merchant_id).subquery('merchant_turnover_sq')
    items_query = items_query.outerjoin(turnover_subquery, Merchant.id == turnover_subquery.c.merchant_id)
    turnover_sq_col = func.coalesce(turnover_subquery.c.total_turnover, Decimal('0.0'))
    items_query = items_query.add_columns(turnover_sq_col.label("calculated_turnover"))

    order_count_subquery = session.query(
        OrderHistory.merchant_id,
        func.count(OrderHistory.id).label("total_orders")
    ).group_by(OrderHistory.merchant_id).subquery('merchant_order_count_sq')
    items_query = items_query.outerjoin(order_count_subquery, Merchant.id == order_count_subquery.c.merchant_id)
    order_count_sq_col = func.coalesce(order_count_subquery.c.total_orders, 0)
    items_query = items_query.add_columns(order_count_sq_col.label("calculated_order_count"))

    store_count_subquery = session.query(
        MerchantStore.merchant_id,
        func.count(MerchantStore.id).label("total_stores")
    ).filter(MerchantStore.access == True).group_by(MerchantStore.merchant_id).subquery('merchant_store_count_sq')
    items_query = items_query.outerjoin(store_count_subquery, Merchant.id == store_count_subquery.c.merchant_id)
    store_count_sq_col = func.coalesce(store_count_subquery.c.total_stores, 0)
    items_query = items_query.add_columns(store_count_sq_col.label("calculated_store_count"))

    statistics_columns_def = [
        {"key": "calculated_turnover", "label": "Turnover"},
        {"key": "calculated_order_count", "label": "Order Count"},
        {"key": "calculated_store_count", "label": "Store Count"}
    ]

    # --- Sorting ---
    sort_field_map = {
        "merchant_id": Merchant.id,
        "email": MerchantUser.email,
        "registration_date": MerchantUser.created_at,
        "user_status": MerchantUser.is_active,
        "turnover": "calculated_turnover",
        "order_count": "calculated_order_count",
        "store_count": "calculated_store_count"
    }
    items_query = query_utils.apply_sorting(items_query, sort_by, sort_direction, sort_field_map, default_sort_column=MerchantUser.created_at)

    results, total_count = query_utils.get_paginated_results_and_count(
        base_query=items_query,
        count_query=count_query,
        page=page,
        per_page=per_page
    )

    data = []
    for row in results:
        merchant_obj = row[0]
        item_data = {
            "id": merchant_obj.id,
            "user_id": merchant_obj.user_id,
            "user_email": row.user_email,
            "user_is_active": row.user_is_active,
            "user_created_at": row.user_created_at,
            # Add other Merchant fields from merchant_obj as needed
            "calculated_turnover": row.calculated_turnover if hasattr(row, 'calculated_turnover') else Decimal('0.0'),
            "calculated_order_count": row.calculated_order_count if hasattr(row, 'calculated_order_count') else 0,
            "calculated_store_count": row.calculated_store_count if hasattr(row, 'calculated_store_count') else 0,
        }
        data.append(item_data)

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "data": data,
        "statistics_columns": statistics_columns_def
    }

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_merchant_full_details(
    session: Session, 
    merchant_id_to_view: int, 
    current_user: User # Admin performing the action
) -> Dict[str, Any]:
    """
    Retrieves full details for a specific merchant, for admin view.
    Includes profile, user info, stores with settings, balance histories, order histories.
    """
    perm_service = PermissionService(session)
    can_view_specific = perm_service.check_permission(current_user.id, current_user.role.name, f"merchant:view:full_details:{merchant_id_to_view}")
    can_view_any = perm_service.check_permission(current_user.id, current_user.role.name, "merchant:view:any_full_details")
    # For support roles, there might be a more limited version of full_details view
    can_view_limited_details_for_support = False
    if current_user.role.name == "support":
        can_view_limited_details_for_support = perm_service.check_permission(current_user.id, "support", f"merchant:view:limited_details:{merchant_id_to_view}") or \
                                               perm_service.check_permission(current_user.id, "support", "merchant:view:any_limited_details")

    if not (can_view_specific or can_view_any or can_view_limited_details_for_support):
        logger.warning(f"User {current_user.id} ({current_user.role.name}) lacks permission to view full details for merchant ID {merchant_id_to_view}.")
        raise AuthorizationError(f"Not authorized to view full details for merchant ID {merchant_id_to_view}.")

    # Note: If can_view_limited_details_for_support is True but others are False,
    # the response data might need to be shaped differently (e.g., masking sensitive fields).
    # This service function currently returns all data; masking/shaping should occur at the API router level based on resolved permissions.

    merchant = session.query(Merchant).filter(Merchant.id == merchant_id_to_view)\
        .options(
            joinedload(Merchant.user),
            selectinload(Merchant.stores).selectinload(MerchantStore.store_commissions),
            selectinload(Merchant.stores).selectinload(MerchantStore.store_gateways),
            selectinload(Merchant.stores).selectinload(MerchantStore.balance_stores),
            selectinload(Merchant.order_histories).order_by(desc(OrderHistory.created_at)).limit(50) # Limit history
        ).one_or_none()

    if not merchant:
        raise NotFoundError(f"Merchant with ID {merchant_id_to_view} not found.")

    # Fetch balance histories for each store separately if not easily loaded above
    store_balance_histories = {}
    for store_item in merchant.stores:
        history = session.query(BalanceStoreHistory)\
            .filter(BalanceStoreHistory.store_id == store_item.id)\
            .order_by(desc(BalanceStoreHistory.created_at))\
            .limit(20).all() # Example limit
        store_balance_histories[store_item.id] = history

    response_data = {
        "profile": merchant,
        "user": merchant.user,
        "stores": [
            {
                "store_info": store, 
                "balance_history": store_balance_histories.get(store.id, [])
            } for store in merchant.stores
        ],
        "order_history_for_merchant": merchant.order_histories 
        # Note: order_history_for_merchant contains orders where merchant_id = merchant.id
        # If you need orders related to specific stores, you'd query OrderHistory.store_id.in_([...])
    }
    return response_data 