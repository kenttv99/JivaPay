from fastapi import Depends, HTTPException, status
from backend.security import get_current_active_user
from backend.database.db import User


def permission_required(role: str):
    """Dependency factory to enforce that current user has given role or is admin."""
    def verify_permission(current_user: User = Depends(get_current_active_user)) -> User:
        # Super-admin has access to everything
        if current_user.role.name == "admin":
            return current_user
        # Check if user's role matches required role
        if current_user.role.name != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges"
            )
        return current_user

    return verify_permission 