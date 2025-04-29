from fastapi import FastAPI
from backend.api_routers.merchant import auth
from backend.config.logger import get_logger

app = FastAPI(title="Merchant API")
logger = get_logger("merchant_server")

app.include_router(auth.router, prefix="/merchant", tags=["merchant"]) 