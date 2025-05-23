from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class MerchantRegister(BaseModel):
    email: EmailStr = Field(..., description="Merchant email for login")
    password: str = Field(..., min_length=6, description="Password for merchant account")
    first_name: Optional[str] = Field(None, description="Merchant's first name")
    last_name: Optional[str] = Field(None, description="Merchant's last name")

class SupportRegister(BaseModel):
    email: EmailStr = Field(..., description="Support's email for login")
    password: str = Field(..., min_length=6, description="Password for support account")
    access_to: Optional[str] = Field(None, description="Permissions or roles for support user, as comma-separated list or JSON") 