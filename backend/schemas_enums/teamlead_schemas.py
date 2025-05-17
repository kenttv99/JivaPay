from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

# Assuming imports from other schema files if needed, e.g.:
# from .user import UserRead # Base user info
# from .requisite import RequisiteOnlineInfoSchema
# from .order import OrderHistoryRead
# from .trader import TraderRead # Base trader info

class TeamLeadTraderBasicInfoSchema(BaseModel):
    id: int # Trader's User ID or Trader Profile ID
    username: Optional[str] = None
    email: EmailStr
    is_active: bool # User.is_active
    in_work: bool # Trader.in_work
    is_traffic_enabled_by_teamlead: bool # Trader.is_traffic_enabled_by_teamlead
    requisite_count: Optional[int] = None
    online_requisite_count: Optional[int] = None

    class Config:
        from_attributes = True

class TeamLeadTraderListResponseSchema(BaseModel):
    items: List[TeamLeadTraderBasicInfoSchema]
    total_count: int
    page: int # if paginated
    per_page: int # if paginated


class TeamLeadTraderDetailSchema(TeamLeadTraderBasicInfoSchema): # Inherits and can add more
    # Detailed stats for a specific trader, e.g.
    total_turnover_period: Optional[Decimal] = None
    order_count_period: Optional[int] = None
    # List of requisites or recent orders could be sub-models or separate endpoints
    # requisites: Optional[List[RequisiteOnlineInfoSchema]] = None
    created_at: datetime # Trader profile creation
    
    # Fields from TraderRead / UserRead if not covered by TeamLeadTraderBasicInfoSchema
    verification_level: Optional[str] = None
    
    class Config:
        from_attributes = True

class TraderTrafficTogglePayloadSchema(BaseModel):
    enable_traffic: bool

# New schema for the response of setting trader traffic status
class TraderTrafficStatusResponse(BaseModel):
    id: int # Trader ID (Trader.id)
    is_traffic_enabled_by_teamlead: bool

    class Config:
        from_attributes = True

class TeamOverallStatsSchema(BaseModel):
    total_traders_in_team: int
    active_traders_count: int
    total_turnover_team_period: Optional[Decimal] = None
    total_orders_team_period: Optional[int] = None
    # Could add breakdown by currency or other metrics
    period_start_date: Optional[datetime] = None
    period_end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeamRequisiteListResponseSchema(BaseModel):
    items: List[Any] # Should be List[RequisiteOnlineInfoSchema] or similar
    total_count: int
    page: int
    per_page: int

    class Config:
        from_attributes = True 