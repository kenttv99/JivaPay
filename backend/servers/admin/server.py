from fastapi import FastAPI
from backend.api_routers.admin import register
from backend.config.logger import get_logger

app = FastAPI(title="Admin API")
logger = get_logger("admin_server")

app.include_router(register.router, prefix="/admin", tags=["admin"]) 