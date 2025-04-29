from fastapi import FastAPI
from backend.api_routers.support import auth
from backend.config.logger import get_logger

app = FastAPI(title="Support API")
logger = get_logger("support_server")

app.include_router(auth.router, prefix="/support", tags=["support"]) 