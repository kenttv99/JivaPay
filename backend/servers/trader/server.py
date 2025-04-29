from fastapi import FastAPI
from backend.api_routers.trader import auth
from backend.config.logger import get_logger

app = FastAPI(title="Trader API")
logger = get_logger("trader_server")

app.include_router(auth.router, prefix="/trader", tags=["trader"]) 