from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.utils.exceptions import JivaPayException


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""
    @app.exception_handler(JivaPayException)
    async def handle_jivapay_exception(request: Request, exc: JivaPayException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        ) 