"""Debug and maintenance endpoints for administrators (non-production)."""

from fastapi import APIRouter, Depends
from celery.result import AsyncResult

from backend.worker.app import celery_app

router = APIRouter()

@router.post("/debug/celery/ping", tags=["debug"], summary="Ping Celery worker and return pong")
def celery_ping():
    """Send built-in Celery ping to workers and return their response."""
    res = celery_app.control.ping(timeout=5.0)  # Returns list of dicts
    return {"workers": res or [], "status": "pong"} 