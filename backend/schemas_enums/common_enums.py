from enum import Enum

class DirectionEnum(str, Enum):
    PAY_IN = 'pay_in'
    PAY_OUT = 'pay_out'

class OrderStatusEnum(str, Enum):
    NEW = 'new'
    PROCESSING = 'processing'
    ASSIGNED = 'assigned'
    RETRYING = 'retrying'
    FAILED = 'failed'
    PENDING_CLIENT_CONFIRMATION = 'pending_trader_confirmation'
    PENDING_TRADER_CONFIRMATION = 'pending_client_confirmation'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    DISPUTED = 'disputed' 