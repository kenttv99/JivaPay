"""Custom exceptions for the JivaPay application."""

class JivaPayException(Exception):
    """Base class for all custom exceptions in JivaPay."""
    def __init__(self, message: str = "An unspecified error occurred in JivaPay.", status_code: int = 500):
        self.message = message
        self.status_code = status_code # For potential mapping to HTTP status codes
        super().__init__(self.message)

# --- Database Related Exceptions --- #
class DatabaseError(JivaPayException):
    """Indicates an error during database operations."""
    def __init__(self, message: str = "A database error occurred.", original_exception: Exception | None = None):
        super().__init__(message, status_code=500)
        self.original_exception = original_exception

class RequisiteNotFound(DatabaseError):
    """Raised when a suitable requisite cannot be found."""
    def __init__(self, message: str = "No suitable requisite found for the order."):
        super().__init__(message, status_code=404) # Or maybe 400 Bad Request?

# --- Configuration Related Exceptions --- #
class ConfigurationError(JivaPayException):
    """Raised for configuration-related issues."""
    def __init__(self, message: str = "Configuration error detected."):
        super().__init__(message, status_code=500)

# --- Order Processing Exceptions --- #
class OrderProcessingError(JivaPayException):
    """Base class for errors during order processing stages."""
    def __init__(self, message: str = "An error occurred during order processing.", order_id: int | str | None = None):
        super().__init__(message, status_code=500)
        self.order_id = order_id

class LimitExceeded(OrderProcessingError):
    """Raised when an operation would exceed a defined limit (e.g., daily/monthly volume)."""
    def __init__(self, message: str = "Operation limit exceeded.", limit_type: str | None = None, order_id: int | str | None = None):
        super().__init__(message, order_id=order_id)
        self.limit_type = limit_type
        # Consider status_code 400 or 429 depending on context?

class InsufficientBalance(OrderProcessingError):
    """Raised when an operation cannot be completed due to insufficient funds."""
    def __init__(self, message: str = "Insufficient balance for the operation.", account_id: int | str | None = None, order_id: int | str | None = None):
        super().__init__(message, order_id=order_id)
        self.account_id = account_id
        self.status_code = 400 # Usually a client error

class InvalidOrderStatus(OrderProcessingError):
    """Raised when an operation is attempted on an order with an incompatible status."""
    def __init__(self, message: str = "Invalid order status for this operation.", order_id: int | str | None = None, current_status: str | None = None):
        super().__init__(message, order_id=order_id)
        self.current_status = current_status
        self.status_code = 409 # Conflict

# --- External Service Exceptions --- #
class NotificationError(JivaPayException):
    """Raised when sending a notification (e.g., Sentry) fails."""
    def __init__(self, message: str = "Failed to send notification.", original_exception: Exception | None = None):
        super().__init__(message, status_code=500)
        self.original_exception = original_exception

class CacheError(JivaPayException):
    """Raised for errors interacting with the cache (e.g., Redis)."""
    def __init__(self, message: str = "Cache interaction failed.", original_exception: Exception | None = None):
        super().__init__(message, status_code=500)
        self.original_exception = original_exception

class S3Error(JivaPayException):
    """Raised for errors interacting with S3 storage."""
    def __init__(self, message: str = "S3 storage interaction failed.", original_exception: Exception | None = None):
        super().__init__(message, status_code=500)
        self.original_exception = original_exception

# --- Authentication/Authorization Exceptions --- #
class AuthenticationError(JivaPayException):
    """Raised for authentication failures (e.g., invalid credentials, bad token)."""
    def __init__(self, message: str = "Authentication failed."):
        super().__init__(message, status_code=401)

class AuthorizationError(JivaPayException):
    """Raised when an authenticated user lacks permission for an action."""
    def __init__(self, message: str = "Permission denied."):
        super().__init__(message, status_code=403)

# --- Fraud Detection Exceptions --- #
class FraudDetectedError(OrderProcessingError):
    """Raised when a potential fraud is detected."""
    def __init__(self, message: str = "Potential fraud detected.", reason: str | None = None, order_id: int | str | None = None):
        super().__init__(message, order_id=order_id)
        self.reason = reason
        self.status_code = 400 # Or perhaps a specific code? 