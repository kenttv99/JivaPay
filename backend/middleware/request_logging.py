import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.config.logger import get_logger

logger = get_logger("request_logger")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log details of each HTTP request and its response time."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        response: Response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        logger.info(
            f"Completed request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.2f}ms"
        )
        return response 