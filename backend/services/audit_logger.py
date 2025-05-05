#!/usr/bin/env python3
"""
Service for recording audit logs to the AuditLog table.
"""

import logging
from typing import Optional, Dict, Any

from backend.database.db import AuditLog
from backend.database.utils import create_object, get_db_session
from backend.utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)

def log_event(
    user_id: Optional[int],
    action: str,
    target_entity: str,
    target_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
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
    """
    try:
        with get_db_session() as session:
            create_object(session, AuditLog, {
                'user_id': user_id,
                'action': action,
                'target_entity': target_entity,
                'target_id': target_id,
                'ip_address': ip_address,
                'details': details or {}
            })
        logger.info(f"Audit event recorded: {action} on {target_entity}({target_id}) by user {user_id}")
    except Exception as e:
        logger.error(f"Failed to record audit event '{action}': {e}", exc_info=True)
        raise DatabaseError(f"Audit log error: {e}") from e 