from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Any, Dict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="User password")
    role_name: str
    username: Optional[str] = None
    granted_permissions: Optional[List[str]] = []
    role_description: Optional[str] = None
    additional_profile_data: Optional[Dict[str, Any]] = None

class UserRead(UserBase):
    id: int
    role_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminProfileSchema(BaseModel):
    id: int
    user_id: int
    username: str
    granted_permissions: Optional[List[str]] = []

    class Config:
        from_attributes = True

class SupportProfileSchema(BaseModel):
    id: int
    user_id: int
    username: str
    role_description: Optional[str] = None
    granted_permissions: Optional[List[str]] = []

    class Config:
        from_attributes = True

class TeamLeadProfileSchema(BaseModel):
    id: int
    user_id: int
    username: str
    granted_permissions: Optional[List[str]] = []

    class Config:
        from_attributes = True

class UserReadWithAdminProfile(UserRead):
    admin_profile: Optional[AdminProfileSchema] = None

class UserReadWithSupportProfile(UserRead):
    support_profile: Optional[SupportProfileSchema] = None

class UserReadWithTeamLeadProfile(UserRead):
    teamlead_profile: Optional[TeamLeadProfileSchema] = None

class AdminProfileUpdateSchema(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None

class SupportProfileUpdateSchema(BaseModel):
    username: Optional[str] = None
    role_description: Optional[str] = None
    is_active: Optional[bool] = None

class TeamLeadProfileUpdateSchema(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None

class UserPermissionsUpdateSchema(BaseModel):
    granted_permissions: List[str]

class UserStatisticsItem(UserRead):
    username: Optional[str] = None

class UserStatisticsResponse(BaseModel):
    total_count: int
    page: int
    per_page: int
    items: List[Any]

class AdminUserStatItem(UserRead):
    username: str

class AdminStatisticsResponse(BaseModel):
    total_count: int
    page: int
    per_page: int
    admins: List[AdminUserStatItem]

# TODO: Define similar specific stat items and responses for Support and TeamLead if needed

class SupportUserStatItem(UserRead):
    username: str # From SupportProfile
    role_description: Optional[str] = None # From SupportProfile
    # Add other relevant fields for support statistics list item

class SupportStatisticsResponse(BaseModel):
    total_count: int
    page: int
    per_page: int
    supports: List[SupportUserStatItem]

class TeamLeadUserStatItem(UserRead):
    username: str # From TeamLeadProfile
    # Add other relevant fields for team lead statistics list item (e.g., number of traders in team)
    # trader_count: Optional[int] = None 

class TeamLeadStatisticsResponse(BaseModel):
    total_count: int
    page: int
    per_page: int
    teamleads: List[TeamLeadUserStatItem] 