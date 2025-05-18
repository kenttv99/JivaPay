"""
Service for managing and retrieving requisite information, 
including online statistics with filtering and permission checks.
"""
import logging
from typing import Optional, List, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func, or_, and_, desc, asc, case, String, cast
from datetime import datetime
from decimal import Decimal

from backend.database.db import (
    ReqTrader, FullRequisitesSettings, Trader, User, PaymentMethod, BanksTrader as Bank # Renamed BanksTrader to Bank for clarity in this service
)
from backend.services.permission_service import PermissionService
from backend.utils.exceptions import AuthorizationError, DatabaseError, NotFoundError
from backend.services.audit_service import log_event
from backend.utils.query_filters import get_active_trader_filters, get_active_requisite_filters # Added imports
from backend.utils import query_utils # Added import
from backend.config.logger import get_logger # Added import
from backend.utils.decorators import handle_service_exceptions
# from backend.schemas_enums.requisite import RequisiteOnlineStatsSchema # For response formatting

logger = get_logger(__name__)
SERVICE_NAME = "requisite_service" # Для использования в декораторе

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_online_requisites_stats(
    session: Session,
    current_user: User, # User performing the action
    sort_by: Optional[str] = None, # e.g., "limits_min", "limits_max", "direction"
    sort_direction: Optional[str] = "asc", # "asc" or "desc"
    trader_filter: Optional[Union[int, str]] = None, # Trader ID, email, or username
    payment_method_id: Optional[int] = None,
    bank_id: Optional[int] = None,
    requisite_type: Optional[str] = None, # "pay_in" or "pay_out"
    team_lead_id_filter: Optional[int] = None, # For admin to filter by teamlead, or for teamlead themselves
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Retrieves statistics and a list of online requisites with filtering, sorting,
    and permission checks.
    "Online" definition: 
    - Trader's user account is active (User.is_active == True).
    - Trader has self-enabled work (Trader.in_work == True).
    - Trader's traffic is enabled by TeamLead (Trader.is_traffic_enabled_by_teamlead == True).
    - Requisite status is active/approved (ReqTrader.status == 'approve').
    - Requisite is enabled for the specified direction (FullRequisitesSettings.pay_in or .pay_out == True).
    """
    perm_service = PermissionService(session)
    user_permissions = perm_service.get_user_permissions(current_user.id, current_user.role.name)

    # Basic permission check
    can_view_any = perm_service.check_permission(current_user.id, current_user.role.name, "requisites:view:online_stats_all")
    can_view_own_team = perm_service.check_permission(current_user.id, current_user.role.name, "requisites:view:online_stats_own_team")
    can_view_limited = perm_service.check_permission(current_user.id, current_user.role.name, "requisites:view:online_stats_limited")

    if not (can_view_any or can_view_own_team or can_view_limited):
        raise AuthorizationError("Not authorized to view online requisites statistics.")

    TraderUser = aliased(User, name="trader_user_for_req_stats")

    # Base query for fetching items (ReqTrader and related data)
    # Select individual columns or full objects as needed for the response
    items_query = session.query(
        ReqTrader, 
        FullRequisitesSettings, 
        Trader, 
        TraderUser,
        PaymentMethod, # Добавляем для доступа к имени
        Bank           # Добавляем для доступа к имени
    )
    # Base query for counting distinct ReqTrader.id
    count_query = session.query(func.count(ReqTrader.id))

    def _apply_common_joins(query_obj: query_utils.Query) -> query_utils.Query:
        query_obj = query_obj.join(FullRequisitesSettings, ReqTrader.id == FullRequisitesSettings.requisite_id)\
                             .join(Trader, ReqTrader.trader_id == Trader.id)\
                             .join(TraderUser, Trader.user_id == TraderUser.id)\
                             .outerjoin(PaymentMethod, ReqTrader.method_id == PaymentMethod.id)\
                             .outerjoin(Bank, ReqTrader.bank_id == Bank.id)
        return query_obj

    items_query = _apply_common_joins(items_query)
    count_query = _apply_common_joins(count_query)

    # Apply core "online" filters
    items_query = items_query.filter(*get_active_trader_filters(user_alias=TraderUser))
    count_query = count_query.filter(*get_active_trader_filters(user_alias=TraderUser))

    items_query = items_query.filter(*get_active_requisite_filters())
    count_query = count_query.filter(*get_active_requisite_filters())

    # --- Helper to apply other filters ---
    def _apply_additional_filters(query_obj: query_utils.Query, is_count_query: bool = False) -> query_utils.Query:
        if requisite_type == "pay_in":
            query_obj = query_obj.filter(FullRequisitesSettings.pay_in == True)
        elif requisite_type == "pay_out":
            query_obj = query_obj.filter(FullRequisitesSettings.pay_out == True)
        elif requisite_type is not None:
            logger.warning(f"Invalid requisite_type provided: {requisite_type}, will return empty.")
            return query_obj.filter(False) # Ensure no results for invalid type
        else: 
            query_obj = query_obj.filter(or_(FullRequisitesSettings.pay_in == True, FullRequisitesSettings.pay_out == True))

        if trader_filter is not None:
            if isinstance(trader_filter, int):
                query_obj = query_obj.filter(Trader.id == trader_filter)
            elif isinstance(trader_filter, str):
                query_obj = query_obj.filter(or_(
                    TraderUser.email.ilike(f"%{trader_filter}%"),
                    # Add Trader.username if it exists and is searchable
                ))
        
        # Условные join'ы для PaymentMethod и Bank больше не нужны здесь,
        # так как они добавлены в _apply_common_joins с outerjoin.
        # Фильтры будут применяться к уже присоединенным таблицам.

        if payment_method_id:
            query_obj = query_obj.filter(PaymentMethod.id == payment_method_id)
        
        if bank_id:
            query_obj = query_obj.filter(Bank.id == bank_id)

        # TeamLead specific filtering
        if current_user.role.name == "teamlead" and not can_view_any:
            if current_user.teamlead_profile:
                query_obj = query_obj.filter(Trader.team_lead_id == current_user.teamlead_profile.id)
            else: 
                return query_obj.filter(False) # Teamlead role without profile, invalid state
        elif team_lead_id_filter and can_view_any: 
            query_obj = query_obj.filter(Trader.team_lead_id == team_lead_id_filter)

        # Support specific granular filtering
        if current_user.role.name == "support" and not can_view_any:
            allowed_pm_ids_for_support = [] 
            user_perms_list = perm_service.get_user_permissions(current_user.id, "support")
            for perm_str in user_perms_list:
                if perm_str.startswith("requisites:view:pm_"):
                    try: allowed_pm_ids_for_support.append(int(perm_str.split('_')[-1]))
                    except ValueError: pass
            
            if allowed_pm_ids_for_support:
                if not payment_method_id: # If PM filter not already applied
                    # PaymentMethod уже присоединен через outerjoin в _apply_common_joins
                    pass # query_obj = query_obj.join(PaymentMethod, ReqTrader.method_id == PaymentMethod.id, isouter=True if is_count_query else False)
                query_obj = query_obj.filter(ReqTrader.method_id.in_(allowed_pm_ids_for_support))
            elif not can_view_limited: # No specific PMs and no general limited view
                return query_obj.filter(False)
        return query_obj

    items_query = _apply_additional_filters(items_query)
    count_query = _apply_additional_filters(count_query, is_count_query=True)
    
    # Handle invalid requisite_type early if it resulted in query.filter(False)
    # This check is a bit indirect. A more direct flag from _apply_additional_filters might be cleaner.
    if requisite_type and requisite_type not in ["pay_in", "pay_out"]:
         return {"total_online": 0, "page": page, "per_page": per_page, "data": []}
    if current_user.role.name == "teamlead" and not can_view_any and not current_user.teamlead_profile:
         return {"total_online": 0, "page": page, "per_page": per_page, "data": []}

    # --- Sorting ---
    sort_field_map = {
        "limits_min": FullRequisitesSettings.lower_limit,
        "limits_max": FullRequisitesSettings.upper_limit,
        "direction": case([(FullRequisitesSettings.pay_in == True, 0)], else_=1),
        "trader_priority": Trader.trafic_priority,
        "last_used": ReqTrader.last_used_at,
        "trader_email": TraderUser.email
    }
    default_sort = [asc(Trader.trafic_priority), asc(ReqTrader.last_used_at).nullsfirst()]
    items_query = query_utils.apply_sorting(items_query, sort_by, sort_direction, sort_field_map, default_sort_column=default_sort)

    results, total_count = query_utils.get_paginated_results_and_count(
        base_query=items_query,
        count_query=count_query,
        page=page,
        per_page=per_page
    )

    requisites_data = []
    for row_items in results: # results is a list of Tuples (ReqTrader, FullRequisitesSettings, Trader, TraderUser, PaymentMethod, Bank)
        req, frs, trader, t_user, pm, bank = row_items # Обновляем распаковку
        requisites_data.append({
            "requisite_id": req.id,
            "req_number": req.req_number, 
            "status": req.status,
            "trader_id": trader.id,
            "trader_email": t_user.email,
            "trader_in_work": trader.in_work,
            "trader_is_active": t_user.is_active,
            "trader_traffic_enabled_by_teamlead": trader.is_traffic_enabled_by_teamlead,
            "pay_in_enabled": frs.pay_in,
            "pay_out_enabled": frs.pay_out,
            "lower_limit": frs.lower_limit,
            "upper_limit": frs.upper_limit,
            "method_id": req.method_id,
            "payment_method_name": pm.public_name or pm.method_name if pm else None, # Добавляем имя метода
            "bank_id": req.bank_id,
            "bank_name": bank.public_name or bank.bank_name if bank else None, # Добавляем имя банка
        })

    return {
        "total_online": total_count,
        "page": page,
        "per_page": per_page,
        "data": requisites_data 
    }

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_requisite_details_for_moderation(
    session: Session,
    requisite_id: int,
    admin_user: User # The admin performing this action
) -> ReqTrader:
    """
    Retrieves detailed information for a specific requisite for moderation purposes.
    Includes associated Trader, User (for trader), PaymentMethod, and Bank information.
    Requires admin privileges.
    """
    perm_service = PermissionService(session)
    # Check if the admin_user has permission to view these details
    # Example permissions: "requisites:view:details_for_moderation", "requisites:moderate:view_details", or a general "requisites:view:any_details"
    if not perm_service.check_permission(admin_user.id, "admin", "requisites:view:details_for_moderation") and \
       not perm_service.check_permission(admin_user.id, "admin", "requisites:view:any_details"): # Fallback to a more general permission
        logger.warning(f"Admin user {admin_user.id} lacks permission to view requisite {requisite_id} details for moderation.")
        raise AuthorizationError("Not authorized to view requisite details for moderation.")

    requisite = session.query(ReqTrader)\
        .filter(ReqTrader.id == requisite_id)\
        .options(
            joinedload(ReqTrader.trader).joinedload(Trader.user), # Trader and their User details
            joinedload(ReqTrader.payment_method),
            joinedload(ReqTrader.bank),
            joinedload(ReqTrader.full_settings) # Assuming FullRequisitesSettings is related as 'full_settings'
        ).one_or_none()

    if not requisite:
        raise NotFoundError(f"Requisite with ID {requisite_id} not found.")
    
    logger.info(f"Admin user {admin_user.id} accessed requisite {requisite_id} details for moderation.")
    return requisite

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def set_requisite_status(
    session: Session,
    requisite_id: int,
    new_status: str, # e.g., "approved", "rejected", "blocked", "pending_review"
    admin_user: User, # The admin performing this action
    reason: Optional[str] = None, # Optional reason for the status change
    ip_address: Optional[str] = None # For audit logging
) -> ReqTrader:
    """
    Allows an administrator to set the status of a specific requisite.
    Logs the action to the audit log.
    Requires admin privileges for moderation.
    """
    perm_service = PermissionService(session)
    # Example permissions: "requisites:manage:status", "requisites:moderate:set_status"
    if not perm_service.check_permission(admin_user.id, "admin", "requisites:manage:status") and \
       not perm_service.check_permission(admin_user.id, "admin", "requisites:moderate"): # Broader moderation permission
        logger.warning(f"Admin user {admin_user.id} lacks permission to set status for requisite {requisite_id}.")
        # Log denied attempt to audit log
        log_event(
            user_id=admin_user.id,
            action="SET_REQUISITE_STATUS_DENIED",
            target_entity="ReqTrader",
            target_id=requisite_id,
            details={"new_status": new_status, "reason": "Insufficient permissions"},
            level="WARNING",
            ip_address=ip_address
        )
        raise AuthorizationError("Not authorized to set requisite status.")

    # Validate new_status (optional, but good practice)
    valid_statuses = ["approved", "rejected", "blocked", "pending_review", "active"] # Extend as needed, active might be same as approved
    if new_status.lower() not in valid_statuses:
        logger.error(f"Admin user {admin_user.id} attempted to set invalid status '{new_status}' for requisite {requisite_id}.")
        # Log error attempt to audit log
        log_event(
            user_id=admin_user.id,
            action="SET_REQUISITE_STATUS_INVALID",
            target_entity="ReqTrader",
            target_id=requisite_id,
            details={"invalid_status": new_status, "valid_statuses": valid_statuses},
            level="ERROR",
            ip_address=ip_address
        )
        raise ValueError(f"Invalid status: '{new_status}'. Valid statuses are: {valid_statuses}")

    requisite = session.query(ReqTrader).filter(ReqTrader.id == requisite_id).one_or_none()
    if not requisite:
        # Log attempt on non-existing requisite
        log_event(
            user_id=admin_user.id,
            action="SET_REQUISITE_STATUS_NOT_FOUND",
            target_entity="ReqTrader",
            target_id=requisite_id,
            details={"new_status": new_status},
            level="ERROR",
            ip_address=ip_address
        )
        raise NotFoundError(f"Requisite with ID {requisite_id} not found.")

    old_status = requisite.status
    if old_status == new_status.lower():
        logger.info(f"Requisite {requisite_id} already has status '{new_status}'. No change made by admin {admin_user.id}.")
        return requisite # No change, no audit for actual change needed

    requisite.status = new_status.lower()
    session.commit()
    session.refresh(requisite)
    logger.info(f"Admin user {admin_user.id} successfully set status of requisite {requisite_id} from '{old_status}' to '{new_status}'. Reason: {reason or 'N/A'}")
    # Log successful status change to audit log
    log_event(
        user_id=admin_user.id,
        action="REQUISITE_STATUS_CHANGED_SUCCESS",
        target_entity="ReqTrader",
        target_id=requisite_id,
        details={"old_status": old_status, "new_status": new_status, "reason": reason},
        level="INFO",
        ip_address=ip_address
    )
    return requisite

# Next: trader_service.py and merchant_service.py 