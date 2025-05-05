from pydantic import BaseModel, EmailStr, Field

class SupportLogin(BaseModel):
    password: str = Field(..., min_length=6, description="Password for support account") 