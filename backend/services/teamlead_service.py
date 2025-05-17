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
# from backend.schemas_enums.teamlead import TeamLeadFullDetailsSchema, TeamStatsSchema # For response formatting
# from backend.schemas_enums.trader import TraderBasicInfoSchema # For managed traders list
from backend.services.audit_logger import log_event
from backend.utils.query_filters import get_active_trader_and_requisite_filters # Added import

logger = logging.getLogger(__name__)

def get_managed_traders(
    session: Session, 
    current_teamlead_user: User
) -> List[Dict[str, Any]]: # Consider returning List[TraderBasicInfoSchema]
    """
    Retrieves a list of traders managed by the current teamlead.
    Requires teamlead role and appropriate permission.
    """
    perm_service = PermissionService(session)
    if not current_teamlead_user.teamlead_profile:
        raise AuthorizationError("User is not a TeamLead.")
    
    # Example permission for viewing own team members
    if not perm_service.check_permission(current_teamlead_user.id, "teamlead", "team:view:members_list"):
        raise AuthorizationError("Not authorized to view managed traders.")

    team_lead_id = current_teamlead_user.teamlead_profile.id
    
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

def set_trader_traffic_status_by_teamlead(
    session: Session, 
    trader_id_to_manage: int, 
    enable_traffic: bool, 
    current_teamlead_user: User,
    ip_address: Optional[str] = None # For audit logging
) -> Trader:
    """
    Allows a TeamLead to enable or disable traffic for a trader in their team.
    Updates Trader.is_traffic_enabled_by_teamlead.
    """
    perm_service = PermissionService(session)
    if not current_teamlead_user.teamlead_profile:
        raise AuthorizationError("User is not a TeamLead.")

    if not perm_service.check_permission(current_teamlead_user.id, "teamlead", "team:manage:trader_traffic"): # General permission
        # Or more specific: team:manage:trader_traffic:{trader_id_to_manage} if team structure is complex
        raise AuthorizationError("Not authorized to manage trader traffic.")

    trader = session.query(Trader).filter(Trader.id == trader_id_to_manage).one_or_none()

    if not trader:
        raise NotFoundError(f"Trader with ID {trader_id_to_manage} not found.")
    
    if trader.team_lead_id != current_teamlead_user.teamlead_profile.id:
        raise OperationForbiddenError("This trader does not belong to your team.")

    trader.is_traffic_enabled_by_teamlead = enable_traffic
    try:
        session.commit()
        session.refresh(trader)
        logger.info(f"TeamLead {current_teamlead_user.email} set traffic for Trader ID {trader_id_to_manage} to {enable_traffic}")
        # Audit log for this action
        log_event(
            user_id=current_teamlead_user.id,
            action="TRADER_TRAFFIC_STATUS_CHANGED_BY_TEAMLEAD",
            target_entity="Trader",
            target_id=trader_id_to_manage,
            details={
                "teamlead_user_id": current_teamlead_user.id,
                "teamlead_email": current_teamlead_user.email, # Assuming User model has email
                "trader_user_id": trader.user_id, # Assuming Trader model has user_id
                "new_status": enable_traffic
            },
            level="INFO",
            ip_address=ip_address
        )
        return trader
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting traffic status for Trader ID {trader_id_to_manage} by TeamLead {current_teamlead_user.email}: {e}")
        # Log failed attempt if necessary, though primary failure is DB related here.
        log_event(
            user_id=current_teamlead_user.id,
            action="SET_TRADER_TRAFFIC_STATUS_FAILED_DB",
            target_entity="Trader",
            target_id=trader_id_to_manage,
            details={
                "teamlead_user_id": current_teamlead_user.id,
                "attempted_status": enable_traffic,
                "error": str(e)
            },
            level="ERROR",
            ip_address=ip_address
        )
        raise DatabaseError("Failed to set trader traffic status.") from e

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
    team_stats = {"total_traders": len(team_trader_ids), "total_turnover": Decimal("0.0"), "total_orders": 0, "active_requisites":0}
    if team_trader_ids:
        turnover = session.query(func.sum(OrderHistory.amount_fiat))\
            .filter(OrderHistory.trader_id.in_(team_trader_ids), OrderHistory.order_type == 'pay_in')\
            .scalar() or Decimal("0.0")
        team_stats["total_turnover"] = turnover

        orders_count = session.query(func.count(OrderHistory.id))\
            .filter(OrderHistory.trader_id.in_(team_trader_ids))\
            .scalar() or 0
        team_stats["total_orders"] = orders_count
        
        active_reqs_query = session.query(func.count(ReqTrader.id))\
            .join(FullRequisitesSettings, ReqTrader.id == FullRequisitesSettings.requisite_id)\
            .join(Trader, ReqTrader.trader_id == Trader.id)\
            .join(User, Trader.user_id == User.id)\
            .filter(ReqTrader.trader_id.in_(team_trader_ids))\
            .filter(*get_active_trader_and_requisite_filters())\
            .filter(or_(FullRequisitesSettings.pay_in == True, FullRequisitesSettings.pay_out == True))\
            .scalar() or 0
        team_stats["active_requisites"] = active_reqs_query

    response_data = {
        "profile": teamlead, 
        "user": teamlead.user,   
        "granted_permissions": teamlead.granted_permissions, 
        "managed_traders": managed_traders_info,
        "team_statistics": team_stats
    }
    return response_data

def get_team_statistics(
    session: Session, 
    current_teamlead_user: User
) -> Dict[str, Any]: # Consider TeamStatsSchema
    """
    Retrieves aggregated statistics for the current teamlead's team.
    """
    perm_service = PermissionService(session)
    if not current_teamlead_user.teamlead_profile:
        raise AuthorizationError("User is not a TeamLead.")
    
    if not perm_service.check_permission(current_teamlead_user.id, "teamlead", "team:view:own_statistics"):
        raise AuthorizationError("Not authorized to view team statistics.")

    team_lead_id = current_teamlead_user.teamlead_profile.id
    
    team_trader_ids_query = session.query(Trader.id).filter(Trader.team_lead_id == team_lead_id)
    team_trader_ids = [id_tuple[0] for id_tuple in team_trader_ids_query.all()]

    team_stats_data = {"total_traders": len(team_trader_ids), "total_turnover": Decimal("0.0"), "total_orders": 0, "active_requisites":0}
    if team_trader_ids:
        turnover = session.query(func.sum(OrderHistory.amount_fiat))\
            .filter(OrderHistory.trader_id.in_(team_trader_ids), OrderHistory.order_type == 'pay_in')\
            .scalar() or Decimal("0.0")
        team_stats_data["total_turnover"] = turnover

        orders_count = session.query(func.count(OrderHistory.id))\
            .filter(OrderHistory.trader_id.in_(team_trader_ids))\
            .scalar() or 0
        team_stats_data["total_orders"] = orders_count
        
        active_reqs_query_team_stats = session.query(func.count(ReqTrader.id))\
            .join(FullRequisitesSettings, ReqTrader.id == FullRequisitesSettings.requisite_id)\
            .join(Trader, ReqTrader.trader_id == Trader.id)\
            .join(User, Trader.user_id == User.id)\
            .filter(ReqTrader.trader_id.in_(team_trader_ids))\
            .filter(*get_active_trader_and_requisite_filters())\
            .filter(or_(FullRequisitesSettings.pay_in == True, FullRequisitesSettings.pay_out == True))\
            .scalar() or 0
        team_stats_data["active_requisites"] = active_reqs_query_team_stats

    return team_stats_data 