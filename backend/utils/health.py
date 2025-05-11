"""Utility helpers to attach standard health/ready endpoints to FastAPI apps.

Usage:
    from backend.utils.health import add_health_endpoint
    add_health_endpoint(app)

This will register a simple GET /health route returning {"status": "ok"} so that
external monitoring systems and test scripts can quickly verify that the service
is alive and responsive.
"""
from fastapi import FastAPI

__all__ = ["add_health_endpoint"]


def add_health_endpoint(app: FastAPI) -> None:  # pragma: no cover
    """Register a standard health check endpoint on the given FastAPI app.

    The endpoint is mounted at GET /health and always returns the JSON
    {"status": "ok"}. It has the tag "misc" so that it appears in the OpenAPI
    docs but does not clutter domain-specific sections.

    Calling this function multiple times for the same *app* is harmless – the
    route will only be added once because FastAPI ignores duplicates with the
    same path+method signature.
    """

    # Check if already registered
    existing = [r for r in app.router.routes if getattr(r, "path", None) == "/health" and "GET" in getattr(r, "methods", set())]
    if existing:
        return

    @app.get("/health", tags=["misc"], summary="Health check")
    async def _health() -> dict[str, str]:  # noqa: D401
        """Return a simple OK status used for liveness probes."""
        return {"status": "ok"} 