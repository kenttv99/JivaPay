from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="User password")

class UserRead(UserBase):
    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes= True 