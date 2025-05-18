"""
Service for TeamLead specific functionalities, including managing their team of traders,
viewing team statistics, and allowing admins to view full teamlead details.
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc, or_
from decimal import Decimal

from backend.database.db import (
    TeamLead, User, Trader, ReqTrader, OrderHistory, 
    FullRequisitesSettings, BalanceTraderFiatHistory, BalanceTraderCryptoHistory
)
from backend.services.permission_service import PermissionService
from backend.utils.exceptions import AuthorizationError, DatabaseError, NotFoundError, OperationForbiddenError
from backend.schemas_enums.teamlead_schemas import (
    TeamLeadTraderBasicInfoSchema, 
    TraderTrafficStatusResponse,
    TeamOverallStatsSchema
)
from backend.services.audit_service import log_event
from backend.utils.query_filters import get_active_trader_and_requisite_filters, get_active_trader_filters, get_active_requisite_filters
from backend.config.logger import get_logger
from backend.utils.decorators import handle_service_exceptions

logger = get_logger(__name__)
SERVICE_NAME = "teamlead_service" # Для использования в декораторе

# Вспомогательная функция для расчета статистики команды
def _calculate_team_stats(session: Session, team_trader_ids: List[int]) -> Dict[str, Any]:
    stats = {
        "total_traders": len(team_trader_ids), 
        "total_turnover_pay_in_fiat": Decimal("0.0"), 
        "total_orders": 0, 
        "active_requisites": 0
    }
    if not team_trader_ids:
        return stats

    # Общий оборот (PayIn Fiat)
    turnover = session.query(func.sum(OrderHistory.amount_fiat))\
        .filter(OrderHistory.trader_id.in_(team_trader_ids), OrderHistory.order_type == 'pay_in')\
        .scalar() or Decimal("0.0")
    stats["total_turnover_pay_in_fiat"] = turnover

    # Общее количество ордеров
    orders_count = session.query(func.count(OrderHistory.id))\
        .filter(OrderHistory.trader_id.in_(team_trader_ids))\
        .scalar() or 0
    stats["total_orders"] = orders_count
    
    # Количество активных реквизитов
    # Применяем фильтры активности для трейдеров и реквизитов
    # Важно: get_active_trader_filters может требовать alias для User, если он уже присоединен
    # Здесь Trader и User присоединяются внутри запроса, поэтому user_alias не обязателен,
    # но если бы User уже был в join'е основного запроса, потребовался бы alias.
    active_reqs_query = session.query(func.count(ReqTrader.id))\
        .join(FullRequisitesSettings, ReqTrader.id == FullRequisitesSettings.requisite_id)\
        .join(Trader, ReqTrader.trader_id == Trader.id)\
        .join(User, Trader.user_id == User.id) # User присоединяется здесь для get_active_trader_filters
    
    # Применение фильтров
    active_reqs_query = active_reqs_query.filter(ReqTrader.trader_id.in_(team_trader_ids))
    active_reqs_query = active_reqs_query.filter(*get_active_trader_filters()) # User уже присоединен
    active_reqs_query = active_reqs_query.filter(*get_active_requisite_filters())
    active_reqs_query = active_reqs_query.filter(or_(FullRequisitesSettings.pay_in == True, FullRequisitesSettings.pay_out == True))
    
    stats["active_requisites"] = active_reqs_query.scalar() or 0
    return stats

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_managed_traders(
    session: Session, 
    current_teamlead: TeamLead
) -> List[TeamLeadTraderBasicInfoSchema]:
    """
    Retrieves a list of traders managed by the current teamlead.
    Requires teamlead role and appropriate permission.
    """
    perm_service = PermissionService(session)
    if not current_teamlead.teamlead_profile:
        raise AuthorizationError("User is not a TeamLead.")
    
    # Example permission for viewing own team members
    if not perm_service.check_permission(current_teamlead.user_id, "teamlead", "team:view:members_list"):
        raise AuthorizationError("Not authorized to view managed traders.")

    team_lead_id = current_teamlead.id
    
    traders_query = session.query(Trader, User.email, User.is_active.label("user_is_active"))\
        .join(User, Trader.user_id == User.id)\
        .filter(Trader.team_lead_id == team_lead_id)\
        .all()

    managed_traders = []
    for trader, email, user_is_active in traders_query:
        managed_traders.append({
            "id": trader.id,
            "user_id": trader.user_id,
            "email": email,
            "user_is_active": user_is_active,
            "in_work": trader.in_work,
            "is_traffic_enabled_by_teamlead": trader.is_traffic_enabled_by_teamlead,
            "first_name": trader.first_name,
            "last_name": trader.last_name
            # Add other relevant fields from Trader as specified by TraderBasicInfoSchema
        })
    return managed_traders

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def list_traders_for_teamlead(session: Session, current_teamlead: TeamLead) -> List[Trader]:
    """
    Lists all traders directly managed by the current teamlead.
    Requires 'team:view:members_list' or a more specific 'teamlead_traders:read' type permission.
    The permission 'teamlead_traders:read' is assumed to be checked by the caller (router) for this specific function.
    Alternatively, it can be checked here if this function is intended to be more self-contained.
    """
    # Permission check example (can be adapted or made more specific)
    # perm_service = PermissionService(session)
    # if not perm_service.check_permission(current_teamlead_user.id, "teamlead", "team:view:members_list") and \\
    #    not perm_service.check_permission(current_teamlead_user.id, "teamlead", "teamlead_traders:read"):
    #     raise AuthorizationError("Not authorized to list managed traders.")

    logger.info(f"TeamLead (User ID: {current_teamlead.user_id}, TeamLeadProfileID: {current_teamlead.id}) fetching list of their traders.")
    
    traders = session.query(Trader).filter(Trader.team_lead_id == current_teamlead.id).all()
    return traders

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def set_trader_traffic_status_by_teamlead(
    session: Session, 
    trader_id_to_manage: int, 
    enable_traffic: bool, 
    current_teamlead: TeamLead,
    ip_address: Optional[str] = None # For audit logging
) -> Trader:
    """
    Allows a TeamLead to enable or disable traffic for a trader in their team.
    Updates Trader.is_traffic_enabled_by_teamlead.
    """
    perm_service = PermissionService(session)
    if not current_teamlead.teamlead_profile:
        raise AuthorizationError("User is not a TeamLead.")

    if not perm_service.check_permission(current_teamlead.user_id, "teamlead", "team:manage:trader_traffic"): # General permission
        # Or more specific: team:manage:trader_traffic:{trader_id_to_manage} if team structure is complex
        raise AuthorizationError("Not authorized to manage trader traffic.")

    trader = session.query(Trader).filter(Trader.id == trader_id_to_manage).one_or_none()

    if not trader:
        raise NotFoundError(f"Trader with ID {trader_id_to_manage} not found.")
    
    if trader.team_lead_id != current_teamlead.id:
        raise OperationForbiddenError("This trader does not belong to your team.")

    trader.is_traffic_enabled_by_teamlead = enable_traffic
    try:
        session.commit()
        session.refresh(trader)
        logger.info(f"TeamLead {current_teamlead.user.email} set traffic for Trader ID {trader_id_to_manage} to {enable_traffic}")
        # Audit log for this action
        log_event(
            user_id=current_teamlead.user_id,
            action="TRADER_TRAFFIC_STATUS_CHANGED_BY_TEAMLEAD",
            target_entity="Trader",
            target_id=trader_id_to_manage,
            details={
                "teamlead_user_id": current_teamlead.user_id,
                "teamlead_email": current_teamlead.user.email if hasattr(current_teamlead, 'user') and current_teamlead.user else 'N/A',
                "trader_user_id": trader.user_id,
                "new_status": enable_traffic
            },
            level="INFO",
            ip_address=ip_address
        )
        return trader
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting traffic status for Trader ID {trader_id_to_manage} by TeamLead {current_teamlead.user.email}: {e}")
        # Log failed attempt if necessary, though primary failure is DB related here.
        log_event(
            user_id=current_teamlead.user_id,
            action="SET_TRADER_TRAFFIC_STATUS_FAILED_DB",
            target_entity="Trader",
            target_id=trader_id_to_manage,
            details={
                "teamlead_user_id": current_teamlead.user_id,
                "attempted_status": enable_traffic,
                "error": str(e)
            },
            level="ERROR",
            ip_address=ip_address
        )
        raise DatabaseError("Failed to set trader traffic status.") from e

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_teamlead_full_details(
    session: Session, 
    teamlead_id_to_view: int, 
    current_admin_user: User
) -> Dict[str, Any]: # Consider TeamLeadFullDetailsSchema
    """
    Retrieves full details for a specific TeamLead, for admin view.
    Includes profile, user info, list of managed traders, and aggregated team stats.
    """
    perm_service = PermissionService(session)
    can_view_specific = perm_service.check_permission(current_admin_user.id, "admin", f"teamlead:view:full_details:{teamlead_id_to_view}")
    can_view_any = perm_service.check_permission(current_admin_user.id, "admin", "teamlead:view:any_full_details")

    if not (can_view_specific or can_view_any):
        raise AuthorizationError(f"Not authorized to view full details for TeamLead ID {teamlead_id_to_view}.")

    teamlead = session.query(TeamLead).filter(TeamLead.id == teamlead_id_to_view)\
        .options(
            joinedload(TeamLead.user),
            selectinload(TeamLead.traders).joinedload(Trader.user) # Load traders and their user info
        ).one_or_none()

    if not teamlead:
        raise NotFoundError(f"TeamLead with ID {teamlead_id_to_view} not found.")

    managed_traders_info = [
        {
            "id": t.id, "email": t.user.email, "is_active": t.user.is_active, 
            "in_work": t.in_work, "is_traffic_enabled_by_teamlead": t.is_traffic_enabled_by_teamlead
        } for t in teamlead.traders
    ]
    
    team_trader_ids = [t.id for t in teamlead.traders]
    team_stats = _calculate_team_stats(session, team_trader_ids)

    response_data = {
        "profile": teamlead, 
        "user": teamlead.user,   
        "granted_permissions": teamlead.granted_permissions, 
        "managed_traders": managed_traders_info,
        "team_statistics": team_stats
    }
    return response_data

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_team_statistics(
    session: Session, 
    current_teamlead: TeamLead
) -> Dict[str, Any]: # Consider TeamStatsSchema
    """
    Retrieves aggregated statistics for the current teamlead's team.
    """
    perm_service = PermissionService(session)
    if not current_teamlead.teamlead_profile:
        raise AuthorizationError("User is not a TeamLead.")
    
    if not perm_service.check_permission(current_teamlead.user_id, "teamlead", "team:view:own_statistics"):
        raise AuthorizationError("Not authorized to view team statistics.")

    team_lead_id = current_teamlead.id
    
    team_trader_ids_query = session.query(Trader.id).filter(Trader.team_lead_id == team_lead_id)
    team_trader_ids = [id_tuple[0] for id_tuple in team_trader_ids_query.all()]

    team_stats_data = _calculate_team_stats(session, team_trader_ids)
    
    return team_stats_data

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def set_trader_in_work_status_by_teamlead(
    session: Session, 
    trader_id_to_manage: int, 
    in_work_status: bool, 
    current_teamlead_user: User
) -> TraderModel:
    """
    Sets the 'in_work' status for a trader if managed by the current teamlead.
    Requires 'team:manage:trader_status' or similar permission (e.g. 'teamlead_traders:update').
    """
    perm_service = PermissionService(session)
    # Example specific permission check, can be adapted
    can_manage_status = perm_service.check_permission(current_teamlead_user.id, "teamlead", "team:manage:trader_status")
    can_update_common = perm_service.check_permission(current_teamlead_user.id, "teamlead", "teamlead_traders:update")

    if not (can_manage_status or can_update_common):
        log_event(
            user_id=current_teamlead_user.id,
            action="SET_TRADER_IN_WORK_DENIED",
            target_entity="TRADER",
            target_id=trader_id_to_manage,
            details={"reason": "Insufficient permissions", "attempted_status": in_work_status},
            level="WARNING"
        )
        raise AuthorizationError("Not authorized to set trader in_work status.")

    teamlead_profile = session.query(TeamLead).filter(TeamLead.user_id == current_teamlead_user.id).first()
    if not teamlead_profile:
        raise OperationForbiddenError("Action can only be performed by a teamlead with a valid profile.")

    trader_to_update = session.query(TraderModel).filter(
        TraderModel.id == trader_id_to_manage,
        TraderModel.team_lead_id == teamlead_profile.id
    ).first()

    if not trader_to_update:
        log_event(
            user_id=current_teamlead_user.id,
            action="SET_TRADER_IN_WORK_NOT_FOUND",
            target_entity="TRADER",
            target_id=trader_id_to_manage,
            details={"reason": "Trader not found or not in team", "attempted_status": in_work_status},
            level="WARNING"
        )
        raise NotFoundError(f"Trader with ID {trader_id_to_manage} not found in your team or does not exist.")

    # Check if status is actually changing to avoid unnecessary audit logs/commits
    if trader_to_update.in_work == in_work_status:
        logger.info(f"Trader {trader_id_to_manage} in_work status is already {in_work_status}. No change made by TeamLead {current_teamlead_user.id}.")
        return trader_to_update # Return the trader object as is

    old_status = trader_to_update.in_work
    trader_to_update.in_work = in_work_status
    session.commit()
    session.refresh(trader_to_update)

    log_event(
        user_id=current_teamlead_user.id,
        action="TRADER_IN_WORK_STATUS_UPDATED",
        target_entity="TRADER",
        target_id=trader_to_update.id,
        details={"old_status": old_status, "new_status": in_work_status, "teamlead_id": teamlead_profile.id},
        level="INFO"
    )
    logger.info(f"TeamLead {current_teamlead_user.email} (ID: {current_teamlead_user.id}) updated trader {trader_to_update.id} in_work status to {in_work_status}.")
    return trader_to_update 