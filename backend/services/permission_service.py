"""
Service for managing and checking granular user permissions.

Permissions are stored as a list of strings in a JSON field
(e.g., Admin.granted_permissions).
"""
import logging
from typing import List, Optional, Union, Any # Added Any for details in audit log

from sqlalchemy.orm import Session
from backend.database.db import User, Admin, Support, TeamLead # Assuming Profile models are correctly named
# Import the log_event function directly
from backend.services.audit_logger import log_event 
from backend.config.logger import get_logger
# Добавляем импорт декоратора
from backend.utils.decorators import handle_service_exceptions

logger = get_logger(__name__)
SERVICE_NAME = "permission_service" # Для использования в декораторе

# Placeholder for actual Pydantic schemas if/when defined for permission updates
# from backend.schemas_enums.user import AdminPermissionsUpdate, SupportPermissionsUpdate, TeamLeadPermissionsUpdate

class PermissionService:
    def __init__(self, db_session: Session):
        self.db = db_session
        # No need to instantiate AuditLogger if using log_event directly

    def _get_user_profile(self, user_id: int, user_role: str) -> Optional[Union[Admin, Support, TeamLead]]:
        """Helper to get the specific profile model instance."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User with ID {user_id} not found when trying to get profile for role {user_role}.")
            return None
        
        profile: Optional[Union[Admin, Support, TeamLead]] = None
        # Assuming profile tables are named Admin, Support, TeamLead and have a user_id FK
        if user_role == "admin":
            profile = self.db.query(Admin).filter(Admin.user_id == user_id).first()
        elif user_role == "support":
            profile = self.db.query(Support).filter(Support.user_id == user_id).first()
        elif user_role == "teamlead":
            profile = self.db.query(TeamLead).filter(TeamLead.user_id == user_id).first()
        else:
            logger.error(f"Unknown user_role '{user_role}' provided for user_id {user_id}.")
            return None
        
        if not profile:
            # This warning might be normal if a user exists but doesn't have a profile for the specified role yet.
            logger.debug(f"Profile for user_id {user_id} with role '{user_role}' not found.")
            return None
        return profile

    def get_user_permissions(self, user_id: int, user_role: str) -> List[str]:
        """Retrieves the list of granted permission strings for a given user and role."""
        profile = self._get_user_profile(user_id, user_role)
        if profile and hasattr(profile, 'granted_permissions') and profile.granted_permissions is not None:
            if isinstance(profile.granted_permissions, list):
                return [str(p) for p in profile.granted_permissions] # Ensure all are strings
            else:
                logger.warning(f"granted_permissions for user {user_id} ({user_role}) is not a list, but {type(profile.granted_permissions)}. Returning empty list.")
                return []
        return []

    @handle_service_exceptions(logger, service_name=SERVICE_NAME) # Применяем к методу
    def update_user_permissions(
        self,
        target_user_id: int,
        target_user_role: str,
        permissions_to_set: List[str],
        current_admin_user: User,
        ip_address: Optional[str] = None # Added for audit logging
    ) -> bool:
        """Updates permissions. Requires admin rights. Logs action."""
        if not current_admin_user or not self.db.query(Admin).filter(Admin.user_id == current_admin_user.id).first(): # More robust admin check
            logger.error(f"Action denied: User {current_admin_user.id if current_admin_user else 'Unknown'} performing update is not a valid admin.")
            log_event(
                user_id=current_admin_user.id if current_admin_user else None,
                action="UPDATE_PERMISSIONS_DENIED",
                target_entity="USER_PROFILE_PERMISSIONS",
                target_id=target_user_id,
                details={"reason": "Performer is not a valid admin", "target_role": target_user_role, "attempted_permissions": permissions_to_set},
                level="WARNING",
                ip_address=ip_address
            )
            return False

        required_perm_manage = f"permissions:manage:{target_user_role}"
        can_manage_specific = self.check_permission(current_admin_user.id, "admin", required_perm_manage)
        can_manage_all = self.check_permission(current_admin_user.id, "admin", "permissions:manage:*")
        is_superuser = self.check_permission(current_admin_user.id, "admin", "superuser")

        if not (can_manage_specific or can_manage_all or is_superuser):
            logger.warning(
                f"Admin {current_admin_user.id} lacks permission ('{required_perm_manage}' or 'permissions:manage:*' or 'superuser') "
                f"to update permissions for user {target_user_id} (role '{target_user_role}')."
            )
            log_event(
                user_id=current_admin_user.id,
                action="UPDATE_PERMISSIONS_DENIED",
                target_entity="USER_PROFILE_PERMISSIONS",
                target_id=target_user_id,
                details={"reason": "Insufficient privileges to manage permissions", "target_role": target_user_role, "required": required_perm_manage, "attempted_set": permissions_to_set},
                level="WARNING",
                ip_address=ip_address
            )
            return False

        target_profile = self._get_user_profile(target_user_id, target_user_role)
        if not target_profile:
            logger.error(f"Target profile for user {target_user_id} (role {target_user_role}) not found during permission update.")
            # No audit log here as the target doesn't exist for an update attempt
            return False

        if hasattr(target_profile, 'granted_permissions'):
            old_permissions = self.get_user_permissions(target_user_id, target_user_role) # Use getter to ensure it's a list
            
            # Ensure uniqueness and sort for consistent storage/comparison
            new_permissions_list = sorted(list(set(str(p) for p in permissions_to_set))) 
            target_profile.granted_permissions = new_permissions_list
            
            try:
                self.db.commit()
                self.db.refresh(target_profile)
                logger.info(f"Successfully updated permissions for user {target_user_id} ({target_user_role}) to {new_permissions_list}")
                log_event(
                    user_id=current_admin_user.id,
                    action="PERMISSIONS_UPDATED_SUCCESS",
                    target_entity="USER_PROFILE_PERMISSIONS",
                    target_id=target_user_id,
                    details={"role": target_user_role, "old_permissions": old_permissions, "new_permissions": new_permissions_list},
                    level="INFO",
                    ip_address=ip_address
                )
                return True
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error updating permissions for user {target_user_id} ({target_user_role}): {e}", exc_info=True)
                log_event(
                    user_id=current_admin_user.id,
                    action="UPDATE_PERMISSIONS_FAILED",
                    target_entity="USER_PROFILE_PERMISSIONS",
                    target_id=target_user_id,
                    details={"error": str(e), "target_role": target_user_role, "attempted_set": new_permissions_list},
                    level="ERROR",
                    ip_address=ip_address
                )
                return False
        else:
            logger.error(f"Profile {target_user_role} for user {target_user_id} does not have 'granted_permissions' attribute.")
            # This case might indicate a programming error or inconsistent DB state.
            log_event(
                user_id=current_admin_user.id,
                action="UPDATE_PERMISSIONS_ERROR",
                target_entity="USER_PROFILE", # Target is the profile itself which is malformed
                target_id=target_user_id,
                details={"reason": f"Profile object for role {target_user_role} lacks 'granted_permissions' attribute.", "target_role": target_user_role},
                level="ERROR",
                ip_address=ip_address
            )
            return False

    def check_permission(
        self,
        user_id: Optional[int],
        user_role: Optional[str],
        required_permission_template: str,
        target_entity_id: Optional[Union[int, str]] = None,
        # context: Optional[Dict[str, Any]] = None # Future: for more complex ABAC-like checks
    ) -> bool:
        """Checks if a user has a specific permission, supporting wildcards and {id} placeholders."""
        if user_id is None or user_role is None:
            if user_role == "anonymous": # Explicitly allow checking for anonymous role if defined
                anon_permissions = self.get_anonymous_permissions() 
                return self._match_permission(anon_permissions, required_permission_template, target_entity_id, "anonymous", user_id)
            logger.debug(f"Permission check for '{required_permission_template}': No user_id or user_role provided.")
            return False

        user_permissions = self.get_user_permissions(user_id, user_role)
        if not user_permissions:
            logger.debug(f"Permission check for '{required_permission_template}': User {user_id} ({user_role}) has no permissions.")
            return False
        
        return self._match_permission(user_permissions, required_permission_template, target_entity_id, user_role, user_id)

    def _match_permission(
        self,
        granted_permissions: List[str],
        required_permission_template: str,
        target_entity_id: Optional[Union[int, str]],
        user_role_for_log: str, # For logging context
        user_id_for_log: Optional[int] # For logging context
    ) -> bool:
        """Internal logic to match required permission against a list of granted ones."""
        
        final_required_permission = required_permission_template
        if "{id}" in required_permission_template:
            if target_entity_id is None:
                logger.warning(f"User {user_id_for_log} ({user_role_for_log}): Permission template '{required_permission_template}' requires an entity ID, but none was provided.")
                return False
            final_required_permission = required_permission_template.format(id=str(target_entity_id))

        if final_required_permission in granted_permissions:
            logger.debug(f"User {user_id_for_log} ({user_role_for_log}): Direct match for permission '{final_required_permission}'. Access GRANTED.")
            return True

        required_parts = final_required_permission.split(':')
        for granted_perm_str in granted_permissions:
            if granted_perm_str == "*" or granted_perm_str == "superuser": # Global wildcard
                logger.debug(f"User {user_id_for_log} ({user_role_for_log}): Matched global wildcard '{granted_perm_str}' for required '{final_required_permission}'. Access GRANTED.")
                return True
            
            granted_parts = granted_perm_str.split(':')
            if len(granted_parts) > len(required_parts): # e.g. granted 'a:b:c', required 'a:b' -> no match unless wildcard
                if granted_parts[len(required_parts)-1] == "*" and all(granted_parts[i] == required_parts[i] for i in range(len(required_parts)-1)):
                     # e.g. granted 'a:b:*' should match required 'a:b' if we interpret 'a:b' as a prefix for 'a:b:anything'
                     # This interpretation is usually not how specific permissions work; typically 'a:b' is distinct from 'a:b:c'.
                     # For now, if granted is more specific, it doesn't match a less specific requirement unless the last part of required matches a wildcard.
                     pass # Let more specific checks handle it
                else:
                    continue
            
            is_match = True
            # Check segment by segment
            # Example: required = "orders:view:specific", granted = "orders:*:specific" -> match
            # Example: required = "orders:view:specific", granted = "orders:view:*" -> match
            # Example: required = "orders:view:specific", granted = "orders:edit:*" -> no match
            if len(required_parts) > len(granted_parts) and granted_parts[-1] != "*":
                # Required is more specific than granted, and granted doesn't end with a wildcard, so no match.
                # e.g., required="a:b:c", granted="a:b"
                continue

            for i in range(len(required_parts)):
                if i >= len(granted_parts):
                    # Required is more specific than granted, e.g. req='a:b:c', grant='a:b'
                    # This can only match if the last part of granted was a wildcard that consumed previous parts.
                    # This case should be covered if granted_parts[-1] == '*' and it's the segment-matching part.
                    if granted_parts[-1] == "*": # Check if the last granted part was a wildcard
                        # This implies the wildcard in granted_parts should cover the rest of required_parts
                        logger.debug(f"User {user_id_for_log} ({user_role_for_log}): Granted permission '{granted_perm_str}' with trailing wildcard matches more specific required '{final_required_permission}'. Access GRANTED.")
                        return True
                    is_match = False
                    break

                if granted_parts[i] == "*":
                    # This segment in granted is a wildcard. It matches this segment in required.
                    # If this wildcard is the last part of the granted permission, it matches all remaining parts of required_permission.
                    if i == len(granted_parts) - 1:
                        logger.debug(f"User {user_id_for_log} ({user_role_for_log}): Granted permission '{granted_perm_str}' (ends with wildcard) matches required '{final_required_permission}'. Access GRANTED.")
                        return True 
                    continue # Move to next segment of required_permission
                
                if granted_parts[i] != required_parts[i]:
                    is_match = False
                    break
            
            if is_match:
                # This is reachable if all parts matched, or if a wildcard in granted_parts[-1] covered remaining required_parts.
                # Also check if required_parts is shorter than or equal to granted_parts after matching
                if len(required_parts) <= len(granted_parts) or (len(granted_parts) > 0 and granted_parts[-1] == "*"):
                    logger.debug(f"User {user_id_for_log} ({user_role_for_log}): Matched granted '{granted_perm_str}' with required '{final_required_permission}'. Access GRANTED.")
                    return True
        
        logger.debug(f"User {user_id_for_log} ({user_role_for_log}): Permission '{final_required_permission}' NOT matched with granted {granted_permissions}. Access DENIED.")
        return False
    
    def get_anonymous_permissions(self) -> List[str]:
        # Placeholder: fetch permissions for an 'anonymous' role from config or DB.
        # For now, returning an empty list means anonymous users have no permissions by default.
        # Example: return ["public:view:articles"] 
        return []

    def check_specific_or_any_permission(
        self,
        user_id: int,
        user_role: str,
        action_verb: str, # e.g., "view", "manage", "edit"
        target_entity_type: str, # e.g., "profile", "status", "permissions" for specific sub-resource
        permission_template_base: str, # e.g., "admin", "support", "teamlead" (usually same as user_role being acted upon)
        specific_target_id: Optional[Union[int, str]] = None,
        raise_exception_on_fail: bool = True
    ) -> bool:
        """
        Checks for two patterns:
        1. specific_permission: f"{permission_template_base}:{action_verb}:{target_entity_type}:{specific_target_id}"
        2. any_permission: f"{permission_template_base}:{action_verb}:{target_entity_type}:*"
                           OR f"{permission_template_base}:{action_verb}:any_{target_entity_type}" (legacy or alternative)

        If specific_target_id is None, only the 'any' patterns are checked.

        Raises AuthorizationError if raise_exception_on_fail is True and check fails.
        Returns True if permission is granted, False otherwise (if raise_exception_on_fail is False).
        """
        has_permission = False
        
        # Try the more general "any" permission first if it covers the specific case
        any_permission_pattern_wildcard = f"{permission_template_base}:{action_verb}:{target_entity_type}:*"
        any_permission_pattern_legacy = f"{permission_template_base}:{action_verb}:any_{target_entity_type}" # Common alternative

        if self.check_permission(user_id, user_role, any_permission_pattern_wildcard):
            has_permission = True
        elif self.check_permission(user_id, user_role, any_permission_pattern_legacy):
            has_permission = True
        
        if not has_permission and specific_target_id is not None:
            specific_permission_pattern = f"{permission_template_base}:{action_verb}:{target_entity_type}:{{id}}"
            if self.check_permission(user_id, user_role, specific_permission_pattern, target_entity_id=specific_target_id):
                has_permission = True
        
        if not has_permission and raise_exception_on_fail:
            perm_details = f"either '{any_permission_pattern_wildcard}' OR '{any_permission_pattern_legacy}'"
            if specific_target_id is not None:
                perm_details += f" OR '{permission_template_base}:{action_verb}:{target_entity_type}:{specific_target_id}'"
            
            logger.warning(f"User {user_id} (role {user_role}) denied action '{action_verb}' on '{target_entity_type}' (target ID: {specific_target_id}). Required: {perm_details}")
            raise AuthorizationError(
                f"Not authorized to {action_verb} {target_entity_type}."
                f" Target ID: {specific_target_id if specific_target_id else 'any'}."
            )
        return has_permission

# Example Usage (conceptual, actual usage will be in API endpoints/dependencies)
if __name__ == '__main__':
    # This block is for conceptual illustration and won't run in FastAPI app
    # Requires a mock DB session and user objects to be testable
    
    # Mocking a DB Session and User for demonstration:
    class MockDB:
        def query(self, model): return self
        def filter(self, *args): return self
        def first(self): return None # Placeholder
        def commit(self): pass
        def refresh(self, obj): pass
        def rollback(self): pass

    class MockUser:
        def __init__(self, id, admin_profile=None, support_profile=None, teamlead_profile=None):
            self.id = id
            self.admin_profile = admin_profile
            self.support_profile = support_profile
            self.teamlead_profile = teamlead_profile
            
    class MockAdminProfile:
        def __init__(self, perms=None):
            self.granted_permissions = perms if perms is not None else []
            
    class MockSupportProfile:
        def __init__(self, perms=None):
            self.granted_permissions = perms if perms is not None else []

    mock_db_session = MockDB()
    
    # -- Admin creating/checking another admin's permissions --
    super_admin_user = MockUser(id=1, admin_profile=MockAdminProfile(perms=["admin:permissions:manage:admin"]))
    target_admin_user = MockUser(id=2, admin_profile=MockAdminProfile(perms=["orders:view:all"]))
    
    # Mocking _get_user_profile for the test
    def mock_get_profile_admin(user_id, user_role):
        if user_id == super_admin_user.id and user_role == "admin": return super_admin_user.admin_profile
        if user_id == target_admin_user.id and user_role == "admin": return target_admin_user.admin_profile
        return None

    perm_service = PermissionService(db_session=mock_db_session)
    perm_service._get_user_profile = mock_get_profile_admin # Override for test

    print(f"Super Admin's permissions: {perm_service.get_user_permissions(super_admin_user.id, 'admin')}")
    print(f"Target Admin's permissions before: {perm_service.get_user_permissions(target_admin_user.id, 'admin')}")

    # Simulate Super Admin trying to update Target Admin's permissions
    # First, let's assume the permission check for the super_admin itself is done externally or mocked
    # For this test, we'll mock the check for the super_admin having rights to update.
    # In a real scenario, this check would be robust.
    
    # To make update_user_permissions testable without full User model from DB:
    # We will assume the `current_admin_user` passed to `update_user_permissions` has already been validated
    # and its profile (like `current_admin_user.admin_profile`) is accessible.
    
    # For testing `update_user_permissions`, we also need `current_admin_user` to have an `admin_profile`.
    # And we need `_get_user_profile` to correctly return the `target_profile`.
    
    # Let's directly test check_permission first
    print(f"Target admin has 'orders:view:all': {perm_service.check_permission(target_admin_user.id, 'admin', 'orders:view:all')}")
    print(f"Target admin has 'orders:edit:all': {perm_service.check_permission(target_admin_user.id, 'admin', 'orders:edit:all')}")
    print(f"Target admin has 'orders:view:*': {perm_service.check_permission(target_admin_user.id, 'admin', 'orders:view:*')}")
    
    # Test entity-specific permission
    target_admin_user.admin_profile.granted_permissions.append("order:edit:123")
    print(f"Target admin has 'order:edit:123': {perm_service.check_permission(target_admin_user.id, 'admin', 'order:edit:{id}', target_entity_id=123)}")
    print(f"Target admin has 'order:edit:456': {perm_service.check_permission(target_admin_user.id, 'admin', 'order:edit:{id}', target_entity_id=456)}")


    # Test updating permissions (simplified admin check for this example)
    class MockSuperAdminUser(MockUser): # Simulate a User object that would be fetched for current_admin_user
        def __init__(self, id, admin_profile):
            super().__init__(id, admin_profile=admin_profile)
            # In a real scenario, this user would be loaded from DB by FastAPI's dependency injection

    mock_super_admin_object = MockSuperAdminUser(id=1, admin_profile=MockAdminProfile(perms=["admin:permissions:manage:admin"]))


    if perm_service.update_user_permissions(
        user_id=target_admin_user.id, 
        user_role="admin", 
        permissions_to_set=["orders:edit:all", "users:view:all"],
        current_admin_user=mock_super_admin_object # Pass the simulated User object
    ):
        print(f"Target Admin's permissions after update: {perm_service.get_user_permissions(target_admin_user.id, 'admin')}")
    else:
        print("Failed to update Target Admin's permissions.") 