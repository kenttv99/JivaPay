from sqlalchemy.orm import Session
from typing import Optional, Type, TypeVar
import logging

# Attempt to import the model, handle potential circular imports if structure changes
try:
    from backend.database.models import ConfigurationSetting
except ImportError:
    # This path might be needed if called from scripts outside the main app structure
    # Or handle potential restructuring later
    from ..database.models import ConfigurationSetting # Adjust relative path if needed

logger = logging.getLogger(__name__) # Use standard logging

T = TypeVar('T')

def get_config_value(key: str, db: Session, default: Optional[str] = None) -> Optional[str]:
    """Fetches a configuration value (as string) from the database.

    Args:
        key: The unique key of the configuration setting.
        db: The SQLAlchemy session to use for querying.
        default: The default value to return if the key is not found or an error occurs.

    Returns:
        The configuration value as a string, or the default value.
    """
    # TODO: Implement caching (e.g., TTLCache or Redis) to avoid frequent DB queries.
    try:
        setting = db.query(ConfigurationSetting).filter(ConfigurationSetting.key == key).one_or_none()
        if setting:
            logger.debug(f"Retrieved config key '{key}' from DB: '{setting.value}'")
            return setting.value
        else:
            logger.warning(f"Configuration key '{key}' not found in database. Returning default value: {default}")
            return default
    except Exception as e:
        logger.error(f"Error fetching configuration key '{key}' from database: {e}", exc_info=True)
        # Fallback to default value on any DB error during lookup
        return default

def get_typed_config_value(key: str, db: Session, expected_type: Type[T], default: Optional[T] = None) -> Optional[T]:
    """Fetches a configuration value from the database and attempts to cast it to the expected type.

    Args:
        key: The unique key of the configuration setting.
        db: The SQLAlchemy session to use for querying.
        expected_type: The Python type to cast the value to (e.g., int, float, bool).
        default: The default value of the expected type to return on failure.

    Returns:
        The configuration value cast to the expected type, or the default value.
    """
    value_str = get_config_value(key, db)

    if value_str is None:
        return default # Return default if key not found or error in get_config_value

    try:
        if expected_type == bool:
            # Handle boolean conversion flexibly (e.g., 'true', '1', 'yes')
            lower_val = value_str.lower()
            if lower_val in ['true', '1', 'yes', 'on']:
                return True
            elif lower_val in ['false', '0', 'no', 'off']:
                return False
            else:
                logger.warning(f"Could not convert config value '{value_str}' for key '{key}' to bool. Returning default.")
                return default
        else:
            # Attempt direct type casting
            return expected_type(value_str)
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to cast config value '{value_str}' for key '{key}' to type {expected_type.__name__}: {e}. Returning default.")
        return default

# Example Usage (within a context that has a db session):
# max_retries = get_typed_config_value("MAX_ORDER_RETRIES", db_session, int, default=5)
# use_feature_x = get_typed_config_value("USE_FEATURE_X", db_session, bool, default=False) 