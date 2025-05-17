from fastapi import APIRouter

from .auth import router as auth_router
from .router import router as teamlead_data_router # The updated router

teamlead_api_router = APIRouter()

teamlead_api_router.include_router(auth_router, prefix="/auth", tags=["TeamLead Authentication"])
teamlead_api_router.include_router(teamlead_data_router) # Mounts at /teamlead (prefix from its own definition) 