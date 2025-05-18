#!/usr/bin/env python3
"""
Service for managing users and roles in JivaPay.
Provides functions for creating users, retrieving users by email, authenticating users,
and managing user profiles and statistics for Admin, Support, TeamLead roles.
"""

import logging
from typing import Optional, List, Dict, Any, Union, Callable
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, or_

from backend.config.crypto import hash_password, verify_password
from backend.config.logger import get_logger
from backend.database.db import User, Role, Admin, Support, TeamLead, Trader, Merchant
from backend.utils.exceptions import AuthenticationError, AuthorizationError, DatabaseError, NotFoundError
from backend.services.permission_service import PermissionService
from backend.services.audit_logger import log_event
from backend.utils import query_utils
from backend.utils.decorators import handle_service_exceptions

logger = get_logger(__name__)
SERVICE_NAME = "user_service" # Для использования в декораторе

def get_user_by_email(session: Session, email: str) -> User | None:
    """Retrieve a user by email or return None if not found."""
    try:
        return session.query(User).filter_by(email=email).options(joinedload(User.admin_profile), joinedload(User.support_profile), joinedload(User.teamlead_profile)).one_or_none()
    except Exception as e:
        logger.error(f"Error retrieving user by email {email}: {e}", exc_info=True)
        raise DatabaseError(f"Error retrieving user by email {email}: {e}") from e

def get_user_by_id(session: Session, user_id: int) -> User | None:
    """Retrieve a user by ID or return None if not found."""
    try:
        return session.query(User).filter_by(id=user_id).options(joinedload(User.admin_profile), joinedload(User.support_profile), joinedload(User.teamlead_profile)).one_or_none()
    except Exception as e:
        logger.error(f"Error retrieving user by ID {user_id}: {e}", exc_info=True)
        raise DatabaseError(f"Error retrieving user by ID {user_id}: {e}") from e

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def create_user(
    db_session: Session,
    email: str,
    password: str,
    role_name: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    permissions: Optional[List[str]] = None,
    is_active: bool = True,
    profile_data: Optional[Dict[str, Any]] = None
) -> User:
    """Creates a new user with a specified role and profile.

    Handles password hashing and profile creation based on role.
    Raises DatabaseError on failure.
    """
    logger.info(f"Attempting to create user with email: {email}, role: {role_name}")
    # Check if user already exists
    existing_user = db_session.query(User).filter(User.email == email).first()
    if existing_user:
        raise DatabaseError(f"User with email {email} already exists.")

    # Get role or create if it doesn't exist (simple role handling)
    role = db_session.query(Role).filter(Role.name == role_name).first()
    if not role:
        # This part might need more robust role creation/management logic
        logger.warning(f"Role '{role_name}' not found, creating it.")
        role = Role(name=role_name, description=f"{role_name.capitalize()} role")
        db_session.add(role)
        # Flush to get role.id if needed immediately, but commit will handle it
        # db_session.flush() # Consider if role.id is needed before user creation

    hashed_pass = hash_password(password)
    new_user = User(
        email=email,
        hashed_password=hashed_pass,
        role_id=role.id, # Будет установлено после создания роли, если ее не было
        is_active=is_active,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        phone_number=phone_number,
        # permissions=permissions # Permissions are usually tied to roles or profiles
    )
    db_session.add(new_user)
    db_session.flush() # To get new_user.id for profile creation

    # Create profile based on role
    if profile_data is None:
        profile_data = {}
    
    profile_data['user_id'] = new_user.id # Ensure user_id is in profile_data

    if role_name == "admin":
        # Admin profile specific fields can be added here from profile_data
        admin_profile = Admin(**profile_data)
        db_session.add(admin_profile)
    elif role_name == "support":
        support_profile = Support(**profile_data)
        db_session.add(support_profile)
    elif role_name == "teamlead":
        teamlead_profile = TeamLead(**profile_data)
        db_session.add(teamlead_profile)
    elif role_name == "trader":
        trader_profile = Trader(**profile_data) # Add trader specific fields
        db_session.add(trader_profile)
    elif role_name == "merchant":
        merchant_profile = Merchant(**profile_data) # Add merchant specific fields
        db_session.add(merchant_profile)
    else:
        logger.warning(f"No specific profile creation logic for role: {role_name}")

    db_session.commit()
    db_session.refresh(new_user)
    # db_session.refresh(role) # If role was newly created and needs to be used with refreshed data

    # Load related profile for the returned user object
    if role_name == "admin":
        db_session.refresh(new_user.admin_profile)
    elif role_name == "support":
        db_session.refresh(new_user.support_profile)
    # ... and so on for other roles as needed

    logger.info(f"User {email} (ID: {new_user.id}) created successfully with role {role_name}.")
    return new_user

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def authenticate_user(db_session: Session, email: str, password: str) -> Optional[User]:
    """Authenticates a user by email and password.

    Returns the User object on success, None on failure.
    Raises AuthenticationError for invalid credentials or inactive user.
    """
    user = db_session.query(User).options(joinedload(User.role)).filter(User.email == email).one_or_none()

    if not user:
        logger.warning(f"Authentication failed: User not found for email {email}.")
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        logger.warning(f"Authentication failed: User {email} is inactive.")
        raise AuthenticationError("User account is inactive.")

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password for user {email}.")
        raise AuthenticationError("Invalid email or password.")

    # Load profile relationships based on role name after successful authentication
    # This ensures that when the user object is returned, its profile attribute is populated.
    # This is crucial for PermissionService or other services that rely on accessing user.admin_profile, user.support_profile etc.
    role_name = user.role.name
    if role_name == 'admin':
        db_session.query(Admin).filter_by(user_id=user.id).one_or_none() # Loads relation
    elif role_name == 'support':
        db_session.query(Support).filter_by(user_id=user.id).one_or_none() # Loads relation
    elif role_name == 'teamlead':
        db_session.query(TeamLead).filter_by(user_id=user.id).one_or_none() # Loads relation
    elif role_name == 'trader':
        db_session.query(Trader).filter_by(user_id=user.id).one_or_none() # Loads relation
    elif role_name == 'merchant':
        db_session.query(Merchant).filter_by(user_id=user.id).one_or_none() # Loads relation

    logger.info(f"User {email} authenticated successfully.")
    return user

@handle_service_exceptions(logger, service_name=SERVICE_NAME)
def get_all_users_basic(db_session: Session, current_admin_user: User) -> List[User]:
    """
    Retrieves a basic list of all users with their core profiles.
    Requires 'users:view:all_basic' permission or superuser.
    """
    permission_service = PermissionService(db_session)
    # Check if current_admin_user has an admin profile before checking permissions
    # This assumes that current_admin_user is indeed an admin, 
    # which should be guaranteed by get_current_active_admin dependency in the router.
    # However, a direct check here can be an additional safeguard if the service is called from elsewhere.
    admin_profile = db_session.query(Admin).filter(Admin.user_id == current_admin_user.id).first()
    if not admin_profile:
        # This case should ideally not be reached if called from an admin-protected endpoint.
        logger.error(f"User {current_admin_user.id} attempting to call get_all_users_basic does not have an admin profile.")
        raise AuthorizationError("Action requires an admin profile.")

    can_view_all_basic = permission_service.check_permission(
        current_admin_user.id, "admin", "users:view:all_basic"
    )
    is_superuser = permission_service.check_permission(
        current_admin_user.id, "admin", "superuser"
    )

    if not (can_view_all_basic or is_superuser):
        logger.warning(f"Admin {current_admin_user.email} (ID: {current_admin_user.id}) failed to fetch basic list of all users due to insufficient permissions.")
        raise AuthorizationError("Not authorized to view a basic list of all users.")

    logger.info(f"Admin {current_admin_user.email} (ID: {current_admin_user.id}) fetching basic list of all users.")
    users = (
        db_session.query(User)
        .options(
            selectinload(User.admin_profile),
            selectinload(User.support_profile),
            selectinload(User.teamlead_profile),
            joinedload(User.role) # Eager load the role
        )
        .all()
    )
    return users

def get_administrators_statistics(
    session: Session, 
    current_admin_user: User, 
    availability_filter: Optional[str] = 'available', 
    page: int = 1, 
    per_page: int = 20
) -> Dict[str, Any]:
    permission_service = PermissionService(session)
    if not permission_service.check_permission(current_admin_user.id, "admin", "users:view:admins_list"):
        raise AuthorizationError("Not authorized to view administrators statistics.")

    # Define User alias for clarity in joins, if needed more broadly
    # For this simple case, direct User might be fine, but aliasing is good practice
    AdminUser = User # Using User directly as it's clear here

    # Base query for fetching admin users
    items_query = session.query(AdminUser).join(Admin, AdminUser.id == Admin.user_id)
    
    # Base query for counting
    count_query = session.query(func.count(AdminUser.id)).join(Admin, AdminUser.id == Admin.user_id)

    # Apply common filters to both queries
    items_query = query_utils.apply_user_status_filter(items_query, AdminUser, availability_filter)
    count_query = query_utils.apply_user_status_filter(count_query, AdminUser, availability_filter)
    
    # TODO: Apply sorting - Define sort_map and use query_utils.apply_sorting
    # Example sort_map (assuming User model has these, adjust AdminUser if it's an alias)
    sort_map_admins = {
        "email": AdminUser.email,
        "id": AdminUser.id,
        "created_at": AdminUser.created_at 
        # Add other sortable fields as needed
    }
    # Default sort or pass from parameters
    items_query = query_utils.apply_sorting(items_query, None, None, sort_map_admins, default_sort_column=AdminUser.created_at)


    try:
        admins_list, total_count = query_utils.get_paginated_results_and_count(
            base_query=items_query,
            count_query=count_query,
            page=page,
            per_page=per_page
        )
    except DatabaseError: # Catch specific error from query_utils
        # Log or handle as appropriate for the service layer
        # For now, re-raising is fine, or return a standard error response
        raise # Or transform into a service-specific error/response

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "admins": admins_list # Consider returning Pydantic schemas
    }

def get_administrator_details(
    session: Session, 
    admin_id_to_view: int, 
    current_admin_user: User
) -> Admin:
    permission_service = PermissionService(session)
    # Check if current_admin can view any admin or specific admin
    can_view_specific = permission_service.check_permission(current_admin_user.id, "admin", f"admin:view:profile:{admin_id_to_view}")
    can_view_any = permission_service.check_permission(current_admin_user.id, "admin", "admin:view:any_profile")
    
    if not (can_view_specific or can_view_any):
        raise AuthorizationError("Not authorized to view administrator details.")

    admin_profile = session.query(Admin).filter(Admin.user_id == admin_id_to_view).options(joinedload(Admin.user)).one_or_none()
    if not admin_profile:
        raise NotFoundError(f"Administrator profile with user ID {admin_id_to_view} not found.")
    return admin_profile

# Helper function for specific profile updates, to be defined or passed as callbacks
def _update_admin_specific_fields(admin_profile: Admin, data: Dict[str, Any]):
    # Admins currently only have 'username' managed by generic, no extra specific fields yet
    pass

def _update_support_specific_fields(support_profile: Support, data: Dict[str, Any]):
    if "role_description" in data:
        support_profile.role_description = data["role_description"]

def _update_teamlead_specific_fields(teamlead_profile: TeamLead, data: Dict[str, Any]):
    # TeamLeads currently only have 'username' managed by generic, no extra specific fields yet
    pass

def _update_user_and_profile_generic(
    session: Session,
    user_id_to_update: int,
    profile_data: Dict[str, Any],
    current_user_performing_action: User,
    profile_model_class: type,
    role_name_for_permissions: str,
    audit_action_name: str,
    ip_address: Optional[str],
    profile_specific_update_callback: Optional[Callable[[Any, Dict[str, Any]], None]] = None,
) -> Any: # Returns the updated profile
    """Generic function to update user and associated profile."""
    perm_service = PermissionService(session)

    profile = (
        session.query(profile_model_class)
        .filter(profile_model_class.user_id == user_id_to_update)
        .options(joinedload(profile_model_class.user)) # type: ignore
        .one_or_none()
    )

    if not profile or not profile.user:
        raise NotFoundError(
            f"{role_name_for_permissions.capitalize()} profile with user ID {user_id_to_update} not found."
        )
    
    user_to_update = profile.user
    original_profile_data_for_audit = {col.name: getattr(profile, col.name) for col in profile.__table__.columns if hasattr(profile, col.name)}
    original_user_data_for_audit = {"is_active": user_to_update.is_active, "email": user_to_update.email}


    # Check permission to manage the profile
    perm_service.check_specific_or_any_permission(
        user_id=current_user_performing_action.id,
        user_role=current_user_performing_action.role.name,
        action_verb="manage",
        target_entity_type="profile",
        permission_template_base=role_name_for_permissions,
        specific_target_id=user_id_to_update,
        raise_exception_on_fail=True
    )

    changes_made = {}

    # Update common profile fields like username
    if "username" in profile_data and hasattr(profile, "username"):
        if profile.username != profile_data["username"]:
            profile.username = profile_data["username"]
            changes_made["username"] = profile.username

    # Call specific callback for unique profile fields
    if profile_specific_update_callback:
        # To capture changes made by callback, we'd need a more complex mechanism
        # For now, we assume callback modifies 'profile' in place and audit will log new state
        profile_specific_update_callback(profile, profile_data)
        # A simple way to track if callback potentially made changes for audit detail:
        # Check if any of its target fields changed, if known.
        # For 'role_description' in Support:
        if role_name_for_permissions == "support" and "role_description" in profile_data and \
           original_profile_data_for_audit.get("role_description") != profile_data["role_description"]:
            changes_made["role_description"] = profile_data["role_description"]


    # Update User.is_active if provided and permitted
    if "is_active" in profile_data:
        if user_to_update.is_active != profile_data["is_active"]:
            perm_service.check_specific_or_any_permission(
                user_id=current_user_performing_action.id,
                user_role=current_user_performing_action.role.name,
                action_verb="manage",
                target_entity_type="status",
                permission_template_base=role_name_for_permissions,
                specific_target_id=user_id_to_update,
                raise_exception_on_fail=True
            )
            user_to_update.is_active = profile_data["is_active"]
            changes_made["is_active"] = user_to_update.is_active
    
    # Update User.email if provided and permitted (more complex, usually separate flow)
    # For now, not including email change in this generic profile update.

    if not changes_made:
        logger.info(f"No actual changes requested for {role_name_for_permissions} {user_id_to_update}. Skipping commit and audit.")
        return profile # Return profile without commit if no changes detected

    try:
        session.commit()
        session.refresh(profile)
        session.refresh(user_to_update)

        log_event(
            user_id=current_user_performing_action.id,
            action=audit_action_name,
            target_entity=profile_model_class.__name__,
            target_id=profile.id if hasattr(profile, 'id') else user_id_to_update, # Use profile ID if exists
            details={
                "profile_user_id": user_id_to_update,
                "admin_user_id": current_user_performing_action.id,
                "changes": changes_made,
                "original_user_data": original_user_data_for_audit, # For context
                # "original_profile_data": original_profile_data_for_audit # Can be too verbose
            },
            level="INFO",
            ip_address=ip_address,
        )
        return profile
    except Exception as e:
        session.rollback()
        logger.error(
            f"Error updating {role_name_for_permissions} profile for user ID {user_id_to_update}: {e}", exc_info=True
        )
        log_event(
            user_id=current_user_performing_action.id,
            action=f"{audit_action_name}_FAILED",
            target_entity=profile_model_class.__name__,
            target_id=profile.id if hasattr(profile, 'id') else user_id_to_update,
            details={"error": str(e), "profile_user_id": user_id_to_update, "requested_changes": profile_data},
            level="ERROR",
            ip_address=ip_address,
        )
        raise DatabaseError(
            f"Failed to update {role_name_for_permissions} profile."
        ) from e

def update_administrator_profile(
    session: Session,
    admin_id_to_update: int,
    profile_data: Dict[str, Any],
    current_admin_user: User,
    ip_address: Optional[str] = None,
) -> Admin:
    return _update_user_and_profile_generic(
        session=session,
        user_id_to_update=admin_id_to_update,
        profile_data=profile_data,
        current_user_performing_action=current_admin_user,
        profile_model_class=Admin,
        role_name_for_permissions="admin",
        audit_action_name="ADMIN_PROFILE_UPDATED",
        ip_address=ip_address,
        profile_specific_update_callback=_update_admin_specific_fields # or None if no specific fields
    )

def get_supports_statistics(
    session: Session, 
    current_admin_user: User, 
    status_filter: Optional[str] = 'active', 
    role_description: Optional[str] = None,
    page: int = 1, 
    per_page: int = 20,
    sort_by: Optional[str] = None, # Added for sorting
    sort_direction: Optional[str] = "asc" # Added for sorting
) -> Dict[str, Any]:
    permission_service = PermissionService(session)
    if not permission_service.check_permission(current_admin_user.id, "admin", "users:view:supports_list"):
        raise AuthorizationError("Not authorized to view support statistics.")

    SupportUser = User # Alias for User model linked to Support profile

    items_query = session.query(SupportUser).join(Support, SupportUser.id == Support.user_id)\
                         .options(joinedload(SupportUser.support_profile)) # Eager load profile
    count_query = session.query(func.count(SupportUser.id)).join(Support, SupportUser.id == Support.user_id)

    # Apply status filter
    items_query = query_utils.apply_user_status_filter(items_query, SupportUser, status_filter)
    count_query = query_utils.apply_user_status_filter(count_query, SupportUser, status_filter)

    # Apply role_description filter (specific to this function)
    if role_description:
        # Assuming Support model is already joined via SupportUser.id == Support.user_id
        # and items_query selects SupportUser. To filter on Support.role_description, we need to ensure Support is accessible.
        # The join is already there. We filter on the Support model's attribute.
        items_query = items_query.filter(Support.role_description.ilike(f"%{role_description}%"))
        count_query = count_query.filter(Support.role_description.ilike(f"%{role_description}%"))
        
    sort_map_supports = {
        "email": SupportUser.email,
        "id": SupportUser.id,
        "created_at": SupportUser.created_at,
        "role_description": Support.role_description # Sorting by a field in the joined Support table
    }
    items_query = query_utils.apply_sorting(items_query, sort_by, sort_direction, sort_map_supports, SupportUser.created_at)

    try:
        supports_list, total_count = query_utils.get_paginated_results_and_count(
            base_query=items_query,
            count_query=count_query,
            page=page,
            per_page=per_page
        )
    except DatabaseError:
        raise

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "supports": supports_list
    }

def get_support_details(
    session: Session, 
    support_id_to_view: int, # This is user_id of the support
    current_user: User # User performing the action (e.g. an Admin)
) -> Support:
    permission_service = PermissionService(session)
    # Check permissions: current_user (admin) needs rights to view support profiles
    # Example perms: "support:view:profile:{id}", "support:view:any_profile", "users:view:support:any"
    # For simplicity, assuming current_user is an admin for now.
    # The role of current_user should be passed or inferred to check_permission correctly.
    # Inferring role or making it explicit:
    performing_user_role = "admin" # Default to admin, adjust if current_user can be other roles
    if current_user.support_profile: performing_user_role = "support" 
    if current_user.teamlead_profile: performing_user_role = "teamlead"
    
    can_view_specific = permission_service.check_permission(current_user.id, performing_user_role, f"support:view:profile:{support_id_to_view}")
    can_view_any = permission_service.check_permission(current_user.id, performing_user_role, "support:view:any_profile")

    if not (can_view_specific or can_view_any):
        logger.warning(f"User {current_user.id} ({performing_user_role}) denied access to view support profile {support_id_to_view}")
        raise AuthorizationError("Not authorized to view support details.")

    support_profile = session.query(Support).filter(Support.user_id == support_id_to_view).options(joinedload(Support.user)).one_or_none()
    if not support_profile:
        raise NotFoundError(f"Support profile with user ID {support_id_to_view} not found.")
    
    logger.info(f"User {current_user.id} ({performing_user_role}) accessed support profile {support_id_to_view}")
    return support_profile

def update_support_profile(
    session: Session,
    support_id_to_update: int, # This is user_id of the support
    profile_data: Dict[str, Any], # e.g. {"username": "new_name", "role_description": "L2 Support", "is_active": False}
    current_user: User, # User performing the action (e.g. an Admin)
    ip_address: Optional[str] = None,
) -> Support:
    # Performing user role check should be ideally done by the permission service or earlier
    # For now, we assume current_user.role.name is correctly populated.
    
    # old audit log code removed, will be handled by generic function
    # ...

    return _update_user_and_profile_generic(
        session=session,
        user_id_to_update=support_id_to_update,
        profile_data=profile_data,
        current_user_performing_action=current_user,
        profile_model_class=Support,
        role_name_for_permissions="support",
        audit_action_name="SUPPORT_PROFILE_UPDATED",
        ip_address=ip_address,
        profile_specific_update_callback=_update_support_specific_fields
    )

def get_teamleads_statistics(
    session: Session, 
    current_admin_user: User, 
    status_filter: Optional[str] = 'active', 
    page: int = 1, 
    per_page: int = 20,
    sort_by: Optional[str] = None, # Added for sorting
    sort_direction: Optional[str] = "asc" # Added for sorting
) -> Dict[str, Any]:
    permission_service = PermissionService(session)
    if not permission_service.check_permission(current_admin_user.id, "admin", "users:view:teamleads_list"):
        raise AuthorizationError("Not authorized to view team lead statistics.")

    TeamLeadUser = User # Alias for User model linked to TeamLead profile

    items_query = session.query(TeamLeadUser).join(TeamLead, TeamLeadUser.id == TeamLead.user_id)\
                           .options(joinedload(TeamLeadUser.teamlead_profile)) # Eager load profile
    count_query = session.query(func.count(TeamLeadUser.id)).join(TeamLead, TeamLeadUser.id == TeamLead.user_id)

    items_query = query_utils.apply_user_status_filter(items_query, TeamLeadUser, status_filter)
    count_query = query_utils.apply_user_status_filter(count_query, TeamLeadUser, status_filter)
    
    sort_map_teamleads = {
        "email": TeamLeadUser.email,
        "id": TeamLeadUser.id,
        "created_at": TeamLeadUser.created_at
        # Add other sortable fields if needed (e.g., from TeamLead profile if joined and selected)
    }
    items_query = query_utils.apply_sorting(items_query, sort_by, sort_direction, sort_map_teamleads, TeamLeadUser.created_at)

    try:
        teamleads_list, total_count = query_utils.get_paginated_results_and_count(
            base_query=items_query,
            count_query=count_query,
            page=page,
            per_page=per_page
        )
    except DatabaseError:
        raise

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "teamleads": teamleads_list 
    }

def get_teamlead_details(
    session: Session, 
    teamlead_id_to_view: int, # This is user_id of the teamlead
    current_user: User # User performing the action
) -> TeamLead:
    permission_service = PermissionService(session)
    performing_user_role = "admin" # Default, determine actual role if not admin
    if current_user.support_profile: performing_user_role = "support"
    if current_user.teamlead_profile: performing_user_role = "teamlead"

    can_view_specific = permission_service.check_permission(current_user.id, performing_user_role, f"teamlead:view:profile:{teamlead_id_to_view}")
    can_view_any = permission_service.check_permission(current_user.id, performing_user_role, "teamlead:view:any_profile")

    if not (can_view_specific or can_view_any):
        logger.warning(f"User {current_user.id} ({performing_user_role}) denied access to view teamlead profile {teamlead_id_to_view}")
        raise AuthorizationError("Not authorized to view teamlead details.")

    teamlead_profile = session.query(TeamLead).filter(TeamLead.user_id == teamlead_id_to_view).options(joinedload(TeamLead.user), joinedload(TeamLead.traders)).one_or_none()
    if not teamlead_profile:
        raise NotFoundError(f"TeamLead profile with user ID {teamlead_id_to_view} not found.")
    
    logger.info(f"User {current_user.id} ({performing_user_role}) accessed teamlead profile {teamlead_id_to_view}")
    return teamlead_profile

def update_teamlead_profile(
    session: Session,
    teamlead_id_to_update: int, # This is user_id of the teamlead
    profile_data: Dict[str, Any], # e.g. {"username": "new_leader", "is_active": True}
    current_user: User, # User performing the action
    ip_address: Optional[str] = None,
) -> TeamLead:
    # Performing user role check... (similar to support)

    # old audit log code removed
    # ...

    return _update_user_and_profile_generic(
        session=session,
        user_id_to_update=teamlead_id_to_update,
        profile_data=profile_data,
        current_user_performing_action=current_user,
        profile_model_class=TeamLead,
        role_name_for_permissions="teamlead",
        audit_action_name="TEAMLEAD_PROFILE_UPDATED",
        ip_address=ip_address,
        profile_specific_update_callback=_update_teamlead_specific_fields # or None
    )

# TODO: Implement other user management functions if needed (e.g., deleting users, more complex searches)

# Consider adding functions for non-admin users to view/update their OWN profiles, e.g.:
# def get_my_profile(session: Session, current_user: User) -> Union[Admin, Support, TeamLead, Trader, Merchant]:
# def update_my_profile(session: Session, current_user: User, data: Dict[str, Any]) -> Union[Admin, Support, TeamLead, Trader, Merchant]: 