from pydantic import BaseModel, EmailStr, Field

class SupportLogin(BaseModel):
    email: EmailStr = Field(..., description="Support's email for login")
    password: str = Field(..., min_length=6, description="Password for support account")

    class Config:
        orm_mode = True 