"""
Utilities for building and executing SQLAlchemy queries,
including pagination, sorting, and common filters.
"""
import logging
from typing import Optional, List, Dict, Any, Tuple, Type
from sqlalchemy.orm import Session, Query
from sqlalchemy import func, desc, asc, Column
from datetime import datetime

from backend.config.logger import get_logger
from backend.utils.exceptions import DatabaseError

logger = get_logger(__name__)

def apply_pagination(query: Query, page: int, per_page: int) -> Query:
    """Applies pagination to a SQLAlchemy query."""
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20 # Default to 20 if invalid
    return query.offset((page - 1) * per_page).limit(per_page)

def apply_sorting(
    query: Query,
    sort_by: Optional[str],
    sort_direction: Optional[str],
    sort_field_map: Dict[str, Any], # Maps string key to Model.attribute or labeled column string
    default_sort_column: Optional[Any] = None # Model.attribute or string for default sort
) -> Query:
    """Applies sorting to a SQLAlchemy query based on a sort_field_map."""
    sort_column = None
    if sort_by and sort_by in sort_field_map:
        sort_column = sort_field_map[sort_by]
    elif default_sort_column is not None:
        sort_column = default_sort_column
        # If default_sort_column is a string from sort_field_map keys, resolve it
        if isinstance(default_sort_column, str) and default_sort_column in sort_field_map:
            sort_column = sort_field_map[default_sort_column]


    if sort_column is not None:
        direction = desc if sort_direction and sort_direction.lower() == "desc" else asc
        # If sort_column is a string (e.g., for a labeled column from a subquery),
        # it's applied directly. If it's a Column object, it's also applied directly.
        if isinstance(sort_column, (str, Column)):
            query = query.order_by(direction(sort_column))
        else: # Assuming it's a SQLAlchemy InstrumentedAttribute (Model.column)
            query = query.order_by(direction(sort_column))
    return query

def apply_user_status_filter(
    query: Query,
    user_model_alias: Type[Any], # SQLAlchemy alias of the User model
    status_filter: Optional[str] # 'active', 'inactive', or None/other for all
) -> Query:
    """Applies a filter based on User.is_active status."""
    if hasattr(user_model_alias, 'is_active'):
        if status_filter == 'active':
            query = query.filter(user_model_alias.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(user_model_alias.is_active == False)
    else:
        logger.warning(f"User model/alias {user_model_alias} does not have 'is_active' attribute for status filter.")
    return query

def apply_date_range_filter(
    query: Query,
    date_column: Any, # Model.attribute representing the date/datetime column
    start_time: Optional[datetime],
    end_time: Optional[datetime]
) -> Query:
    """Applies a date range filter to a query."""
    if start_time:
        query = query.filter(date_column >= start_time)
    if end_time:
        query = query.filter(date_column <= end_time)
    return query

def get_paginated_results_and_count(
    base_query: Query, # The query for fetching items, before pagination
    count_query: Query, # A separate query for counting total items, with filters applied
    page: int,
    per_page: int
) -> Tuple[List[Any], int]:
    """
    Applies pagination to the base_query, executes it,
    and executes the count_query to get the total number of items.

    Args:
        base_query: SQLAlchemy query object for fetching the list of items.
                    Sorting should be applied to this query before passing it here.
        count_query: SQLAlchemy query object for fetching the total count.
                     Filters should be applied to this query before passing it here.
        page: The current page number (1-indexed).
        per_page: The number of items per page.

    Returns:
        A tuple containing the list of items for the current page and the total count.
    """
    try:
        total_count = count_query.scalar() or 0
    except Exception as e:
        logger.error(f"Error executing count query: {e}", exc_info=True)
        # Decide on fallback: raise error or return 0/empty
        # For now, let's assume a failed count means we can't proceed reliably
        raise DatabaseError("Failed to count items for pagination.") from e

    if total_count == 0:
        return [], 0

    paginated_query = apply_pagination(base_query, page, per_page)
    
    try:
        results = paginated_query.all()
    except Exception as e:
        logger.error(f"Error executing paginated query: {e}", exc_info=True)
        raise DatabaseError("Failed to retrieve paginated items.") from e
        
    return results, total_count

# Example (Illustrative - not for direct execution here)
if __name__ == '__main__':
    # --- Illustration of how these functions might be used ---
    # from sqlalchemy.orm import Session, aliased
    # from sqlalchemy import create_engine
    # from backend.database.db import Base, User, Admin # Assuming these are defined

    # # Mock DB setup
    # engine = create_engine('sqlite:///:memory:')
    # Base.metadata.create_all(engine)
    # MockSession = Session(engine)
    
    # # --- Example usage for get_administrators_statistics from user_service.py ---
    # current_admin_user_mock = MockSession.query(User).first() # Placeholder
    # page_param = 1
    # per_page_param = 10
    # availability_filter_param = 'active'
    
    # # 1. Initial Query Setup (from user_service)
    # UserAlias = aliased(User, name="admin_user_alias")
    # base_items_query = MockSession.query(UserAlias).join(Admin, UserAlias.id == Admin.user_id)
    # count_query_base = MockSession.query(func.count(UserAlias.id)).join(Admin, UserAlias.id == Admin.user_id)

    # # 2. Apply Filters (from user_service + query_utils)
    # base_items_query = apply_user_status_filter(base_items_query, UserAlias, availability_filter_param)
    # count_query_base = apply_user_status_filter(count_query_base, UserAlias, availability_filter_param)
    
    # # 3. Apply Sorting (from query_utils)
    # sort_map_admins = {"email": UserAlias.email, "id": UserAlias.id, "created_at": UserAlias.created_at}
    # base_items_query = apply_sorting(base_items_query, "created_at", "desc", sort_map_admins, UserAlias.created_at)

    # # 4. Get Paginated Results and Count (from query_utils)
    # # try:
    # #     admins_list, total_admins = get_paginated_results_and_count(
    # #         base_query=base_items_query,
    # #         count_query=count_query_base,
    # #         page=page_param,
    # #         per_page=per_page_param
    # #     )
    # #     print(f"Total Admins: {total_admins}, Admins on page: {len(admins_list)}")
    # #     # result_dict = {"total_count": total_admins, "page": page_param, "per_page": per_page_param, "admins": admins_list}
    # # except DatabaseError as e:
    # #     print(f"Error: {e}")
    # #     # Handle error appropriately in service
    # MockSession.close()
    pass 