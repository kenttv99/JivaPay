#!/usr/bin/env python3
"""
Service for recording audit logs and retrieving specific log information.
(Consider renaming to audit_service.py for consistency)
"""

import logging
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy import desc # Added for ordering

from backend.database.db import AuditLog, User # Added User for type hint
from backend.database.utils import create_object, get_db_session_cm
from backend.utils.exceptions import DatabaseError, AuthorizationError
from backend.services.permission_service import PermissionService # For checking permissions

logger = logging.getLogger(__name__)

def log_event(
    user_id: Optional[int],
    action: str,
    target_entity: Optional[str] = None, # Made Optional
    target_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    level: str = "INFO" # Added level, e.g., INFO, WARNING, ERROR, CRITICAL
) -> None:
    """
    Records an audit log entry.

    Args:
        user_id: ID of the user performing the action, or None for system.
        action: Description of the action performed.
        target_entity: Name of the entity affected (e.g., 'OrderHistory').
        target_id: ID of the target entity instance.
        ip_address: IP address of the requester.
        details: Additional context data.
        level: Severity level of the log event (e.g., INFO, ERROR, CRITICAL).
    """
    if details is None:
        details = {}
    details["level"] = level # Store level in details

    try:
        with get_db_session_cm() as session:
            log_entry_data = {
                'user_id': user_id,
                'action': action,
                'target_entity': target_entity,
                'target_id': target_id,
                'ip_address': ip_address,
                'details': details
            }
            new_log = AuditLog(**log_entry_data)
            session.add(new_log)
            session.commit()

        log_message = f"Audit event recorded: [{level}] {action}"
        if target_entity:
            log_message += f" on {target_entity}({target_id if target_id is not None else 'N/A'})"
        if user_id:
            log_message += f" by user {user_id}"
        logger.info(log_message)

    except Exception as e:
        logger.error(f"Failed to record audit event '{action}': {e}", exc_info=True)

def get_critical_system_errors(
    session: Session, 
    current_user: User, # For permission check
    page: int = 1, 
    per_page: int = 20,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Retrieves a paginated list of critical system error logs.
    Requires appropriate admin permissions.
    """
    perm_service = PermissionService(session)
    if not perm_service.check_permission(current_user.id, current_user.role.name, "logs:view:critical_system_errors"):
        raise AuthorizationError("Not authorized to view critical system error logs.")

    query = session.query(AuditLog)\
        .filter(AuditLog.details["level"].astext == "CRITICAL")\
        .filter(AuditLog.user_id == None) 
    
    if filters:
        if "action_contains" in filters:
            query = query.filter(AuditLog.action.ilike(f"%{filters['action_contains']}%"))
        if "target_entity" in filters:
            query = query.filter(AuditLog.target_entity == filters["target_entity"])

    try:
        total_count = query.count()
        error_logs = query.order_by(desc(AuditLog.timestamp))\
                          .offset((page - 1) * per_page)\
                          .limit(per_page)\
                          .all()
    except Exception as e:
        logger.error(f"Error querying critical system error logs: {e}", exc_info=True)
        raise DatabaseError("Failed to retrieve critical system error logs.") from e

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "logs": error_logs
    } 