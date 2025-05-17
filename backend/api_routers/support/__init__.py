from fastapi import APIRouter

from .auth import router as auth_router
from .router import router as support_data_router # The new router we created

support_api_router = APIRouter()

support_api_router.include_router(auth_router, prefix="/auth", tags=["Support Authentication"])
support_api_router.include_router(support_data_router) # Mounts at /support (prefix from its own definition) 