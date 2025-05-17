"""
Service for managing and retrieving trader-related information, 
including statistics and detailed profiles, with permission checks.
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload, selectinload, aliased
from sqlalchemy import func, or_, and_, desc, asc, String, cast
from datetime import datetime
from decimal import Decimal

from backend.database.db import (
    Trader, User, OrderHistory, ReqTrader, 
    BalanceTraderFiatHistory, BalanceTraderCryptoHistory, FullRequisitesSettings,
    PaymentMethod
)
from backend.services.permission_service import PermissionService
from backend.utils.exceptions import AuthorizationError, DatabaseError, NotFoundError
from backend.utils import query_utils # Added import
# from backend.schemas_enums.trader import TraderStatsSchema, TraderFullDetailsSchema # For response formatting

logger = logging.getLogger(__name__)

def get_traders_statistics(
    session: Session,
    current_user: User, # User performing the action
    status_filter: Optional[str] = 'active', # "all", "active", "inactive" (User.is_active)
    online_status: Optional[str] = None, # "online" (in_work=True), "offline" (in_work=False), "all"
    turnover_period_start: Optional[datetime] = None,
    turnover_period_end: Optional[datetime] = None,
    sort_by: Optional[str] = None, # e.g., "turnover", "requisite_count", "registration_date", "order_count", "user_status", "username", "trader_id"
    sort_direction: Optional[str] = "asc",
    fiat_currency_id: Optional[int] = None, 
    payment_method_id: Optional[int] = None, 
    search_query: Optional[str] = None, 
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Retrieves paginated statistics for traders with filtering, sorting, and permission checks.
    """
    perm_service = PermissionService(session)
    if not perm_service.check_permission(current_user.id, current_user.role.name, "traders:view:list_statistics"):
        raise AuthorizationError("Not authorized to view trader statistics.")

    TraderUser = aliased(User, name="trader_user_for_stats")

    # Base query for items (Trader and selected User fields)
    items_query = session.query(
        Trader,
        TraderUser.email.label("user_email"), 
        TraderUser.is_active.label("user_is_active"),
        TraderUser.created_at.label("user_created_at")
    ).join(TraderUser, Trader.user_id == TraderUser.id)

    # Base query for count (counting distinct Trader.id)
    # The distinct on Trader.id is important if other joins might create duplicates (e.g. PaymentMethod join)
    count_query = session.query(func.count(func.distinct(Trader.id))).join(TraderUser, Trader.user_id == TraderUser.id)

    # --- Common Filter Application Function ---
    def _apply_common_filters(query_obj: query_utils.Query, is_count_query: bool = False) -> query_utils.Query:
        # User status filter (is_active)
        query_obj = query_utils.apply_user_status_filter(query_obj, TraderUser, status_filter)

        # Trader online status filter (in_work)
        if online_status == 'online':
            query_obj = query_obj.filter(Trader.in_work == True)
        elif online_status == 'offline':
            query_obj = query_obj.filter(Trader.in_work == False)
        
        if fiat_currency_id:
            query_obj = query_obj.filter(Trader.preferred_fiat_currency_id == fiat_currency_id)

        if search_query:
            search_term = f"%{search_query.lower()}%"
            query_obj = query_obj.filter(
                or_(
                    TraderUser.email.ilike(search_term),
                    cast(Trader.id, String).ilike(search_term),
                    # Add other searchable Trader fields if needed, e.g., Trader.username.ilike(search_term)
                )
            )
        return query_obj

    # Apply common filters to both queries
    items_query = _apply_common_filters(items_query)
    count_query = _apply_common_filters(count_query, is_count_query=True)

    # --- Payment Method Filter (applied after common filters, affects distinctness) ---
    # This needs to be applied to both queries carefully, especially the count query.
    # The join should be outer if we don't want to exclude traders with no requisites/matching PMs
    # but if we filter by PM ID, it effectively becomes an inner join requirement for those who match.

    if payment_method_id:
        # For items_query, distinct is handled by its initial distinct(Trader.id) if needed.
        # If items_query selects full Trader objects, subsequent joins for filtering are fine.
        # The main distinct for count_query is func.count(func.distinct(Trader.id))
        items_query = items_query.join(ReqTrader, Trader.id == ReqTrader.trader_id)\
                                 .join(PaymentMethod, ReqTrader.method_id == PaymentMethod.id)\
                                 .filter(PaymentMethod.id == payment_method_id)\
                                 .filter(ReqTrader.status == 'approve')
        
        count_query = count_query.join(ReqTrader, Trader.id == ReqTrader.trader_id)\
                                 .join(PaymentMethod, ReqTrader.method_id == PaymentMethod.id)\
                                 .filter(PaymentMethod.id == payment_method_id)\
                                 .filter(ReqTrader.status == 'approve')
    
    # --- Granular permission filtering for Support ---
    allowed_pm_ids_for_support_view = None
    if current_user.role.name == "support":
        can_view_all = perm_service.check_permission(current_user.id, "support", "traders:view:list_statistics_all")
        can_view_limited = perm_service.check_permission(current_user.id, "support", "traders:view:list_statistics_limited")

        if not can_view_all:
            if not can_view_limited:
                logger.info(f"Support user {current_user.id} has no permission for trader statistics. Returning empty.")
                return {"total_count": 0, "page": page, "per_page": per_page, "data": [], "statistics_columns": []}
            
            # Determine allowed Payment Method IDs for this support user
            # This is an example, actual permission strings might differ.
            allowed_pm_ids_for_support_view = []
            # Suppose permissions are like 'traders:view:allowed_pm_X'
            # This part would iterate through relevant PMs or check specific permissions
            user_perms = perm_service.get_user_permissions(current_user.id, "support")
            for perm in user_perms:
                if perm.startswith("traders:view:allowed_pm_"):
                    try:
                        pm_id = int(perm.split('_')[-1])
                        allowed_pm_ids_for_support_view.append(pm_id)
                    except ValueError:
                        logger.warning(f"Malformed PM permission for support {current_user.id}: {perm}")
            
            if not allowed_pm_ids_for_support_view and not payment_method_id:
                # If limited view, but no specific PMs granted by perms, AND no PM filter in request, they see nothing.
                logger.info(f"Support user {current_user.id} has limited view but no specific PMs allowed or requested. Returning empty.")
                return {"total_count": 0, "page": page, "per_page": per_page, "data": [], "statistics_columns": []}

            if allowed_pm_ids_for_support_view:
                # If a payment_method_id filter is already applied, the support user should only see results
                # if that payment_method_id is ALSO in their allowed_pm_ids_for_support_view.
                if payment_method_id and payment_method_id not in allowed_pm_ids_for_support_view:
                    logger.info(f"Support user {current_user.id} requested PM {payment_method_id} but not in their allowed list. Returning empty.")
                    return {"total_count": 0, "page": page, "per_page": per_page, "data": [], "statistics_columns": []}
                
                # Apply the PM ID intersection to the queries
                # The joins for ReqTrader and PaymentMethod might already exist if payment_method_id was set.
                # We need to ensure this filter is ANDed correctly.
                # A simple way is to add the filter again if it's not already implied.
                # This assumes the joins are already in place if payment_method_id was specified.
                if not payment_method_id: # If PM joins were not added yet for a direct PM filter
                    items_query = items_query.join(ReqTrader, Trader.id == ReqTrader.trader_id, isouter=True)\
                                         .join(PaymentMethod, ReqTrader.method_id == PaymentMethod.id, isouter=True)
                    count_query = count_query.join(ReqTrader, Trader.id == ReqTrader.trader_id, isouter=True)\
                                         .join(PaymentMethod, ReqTrader.method_id == PaymentMethod.id, isouter=True)
                
                items_query = items_query.filter(PaymentMethod.id.in_(allowed_pm_ids_for_support_view))
                count_query = count_query.filter(PaymentMethod.id.in_(allowed_pm_ids_for_support_view))
                # Ensure ReqTrader is active for this filter context
                items_query = items_query.filter(ReqTrader.status == 'approve') 
                count_query = count_query.filter(ReqTrader.status == 'approve')

    # --- Subqueries for aggregated data (turnover, order_count, requisite_count) ---
    # These will be added as columns to the items_query. They do not affect the count_query.
    turnover_sq_col = None
    order_count_sq_col = None
    req_count_sq_col = None

    if True: # Always calculate for now, can be made conditional if complex
        turnover_subquery = session.query(
            OrderHistory.trader_id,
            func.sum(OrderHistory.amount_fiat).label("total_turnover")
        ).filter(OrderHistory.order_type == 'pay_in')
        if turnover_period_start: turnover_subquery = turnover_subquery.filter(OrderHistory.created_at >= turnover_period_start)
        if turnover_period_end: turnover_subquery = turnover_subquery.filter(OrderHistory.created_at <= turnover_period_end)
        turnover_subquery = turnover_subquery.group_by(OrderHistory.trader_id).subquery('turnover_sq')
        items_query = items_query.outerjoin(turnover_subquery, Trader.id == turnover_subquery.c.trader_id)
        turnover_sq_col = func.coalesce(turnover_subquery.c.total_turnover, Decimal('0.0'))
        items_query = items_query.add_columns(turnover_sq_col.label("calculated_turnover"))

        order_count_subquery = session.query(
            OrderHistory.trader_id,
            func.count(OrderHistory.id).label("total_orders")
        ).group_by(OrderHistory.trader_id).subquery('order_count_sq')
        items_query = items_query.outerjoin(order_count_subquery, Trader.id == order_count_subquery.c.trader_id)
        order_count_sq_col = func.coalesce(order_count_subquery.c.total_orders, 0)
        items_query = items_query.add_columns(order_count_sq_col.label("calculated_order_count"))

        requisite_count_subquery = session.query(
            ReqTrader.trader_id,
            func.count(ReqTrader.id).label("total_requisites")
        ).filter(ReqTrader.status == 'approve').group_by(ReqTrader.trader_id).subquery('req_count_sq')
        items_query = items_query.outerjoin(requisite_count_subquery, Trader.id == requisite_count_subquery.c.trader_id)
        req_count_sq_col = func.coalesce(requisite_count_subquery.c.total_requisites, 0)
        items_query = items_query.add_columns(req_count_sq_col.label("calculated_requisite_count"))
    
    statistics_columns = [
        {"key": "calculated_turnover", "label": "Turnover"},
        {"key": "calculated_order_count", "label": "Order Count"},
        {"key": "calculated_requisite_count", "label": "Requisite Count"}
    ]

    # --- Sorting ---
    sort_field_map = {
        "trader_id": Trader.id,
        "username": TraderUser.email, # Assuming username is email for sorting
        "registration_date": TraderUser.created_at,
        "user_status": TraderUser.is_active,
        "online_status": Trader.in_work,
        "turnover": "calculated_turnover", # Use string for columns added via add_columns
        "order_count": "calculated_order_count",
        "requisite_count": "calculated_requisite_count"
    }
    items_query = query_utils.apply_sorting(items_query, sort_by, sort_direction, sort_field_map, default_sort_column=TraderUser.created_at)

    # --- Pagination and Execution ---
    try:
        results, total_count = query_utils.get_paginated_results_and_count(
            base_query=items_query,
            count_query=count_query, # This count_query already has filters applied
            page=page,
            per_page=per_page
        )
    except DatabaseError as e:
        logger.error(f"Database error in get_traders_statistics: {e}", exc_info=True)
        raise

    # Process results into a list of dicts or Pydantic models
    # The 'results' will be a list of Tuples: (Trader_obj, user_email, user_is_active, user_created_at, calc_turnover, calc_orders, calc_reqs)
    data = []
    for row in results:
        trader_obj = row[0]
        item_data = {
            "id": trader_obj.id,
            "user_id": trader_obj.user_id,
            "user_email": row.user_email, # from items_query selection
            "user_is_active": row.user_is_active,
            "user_created_at": row.user_created_at,
            "in_work": trader_obj.in_work,
            "is_traffic_enabled_by_teamlead": trader_obj.is_traffic_enabled_by_teamlead,
            "preferred_fiat_currency_id": trader_obj.preferred_fiat_currency_id,
            "teamlead_id": trader_obj.teamlead_id,
            # Add other Trader fields as needed from trader_obj
            "calculated_turnover": row.calculated_turnover if hasattr(row, 'calculated_turnover') else Decimal('0.0'),
            "calculated_order_count": row.calculated_order_count if hasattr(row, 'calculated_order_count') else 0,
            "calculated_requisite_count": row.calculated_requisite_count if hasattr(row, 'calculated_requisite_count') else 0,
        }
        data.append(item_data)

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "data": data,
        "statistics_columns": statistics_columns # For dynamic table rendering on frontend
    }

def get_trader_full_details(
    session: Session, 
    trader_id_to_view: int, 
    current_user: User # Admin performing the action
) -> Dict[str, Any]:
    """
    Retrieves full details for a specific trader, for admin view.
    Includes profile, user info, requisites, balance histories, order histories.
    """
    perm_service = PermissionService(session)
    # Example permissions, adjust based on your defined permission strings
    can_view_specific = perm_service.check_permission(current_user.id, current_user.role.name, f"trader:view:full_details:{trader_id_to_view}")
    can_view_any = perm_service.check_permission(current_user.id, current_user.role.name, "trader:view:any_full_details")

    if not (can_view_specific or can_view_any):
        raise AuthorizationError(f"Not authorized to view full details for trader ID {trader_id_to_view}.")

    trader = session.query(Trader).filter(Trader.id == trader_id_to_view)\
        .options(
            joinedload(Trader.user),
            selectinload(Trader.req_traders).joinedload(ReqTrader.full_requisites_settings),
            selectinload(Trader.req_traders).joinedload(ReqTrader.method),
            selectinload(Trader.req_traders).joinedload(ReqTrader.bank),
            selectinload(Trader.balance_trader_fiat_history).order_by(desc(BalanceTraderFiatHistory.created_at)).limit(50), # Limit history for performance
            selectinload(Trader.balance_trader_crypto_history).order_by(desc(BalanceTraderCryptoHistory.created_at)).limit(50),
            selectinload(Trader.order_histories).order_by(desc(OrderHistory.created_at)).limit(50) # Limit history
        ).one_or_none()

    if not trader:
        raise NotFoundError(f"Trader with ID {trader_id_to_view} not found.")

    # Format the data (consider using Pydantic schemas for clean output)
    # This is a simplified representation
    response_data = {
        "profile": trader, # Contains Trader model fields
        "user": trader.user,   # Contains User model fields (email, is_active, created_at)
        "requisites": trader.req_traders,
        "fiat_balance_history": trader.balance_trader_fiat_history,
        "crypto_balance_history": trader.balance_trader_crypto_history,
        "order_history": trader.order_histories
    }
    return response_data 