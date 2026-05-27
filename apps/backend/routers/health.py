import os
from fastapi import APIRouter
from db import engine
from schemas import HealthResponse

router = APIRouter()

GIT_SHA = os.getenv("GIT_SHA", "unknown")


@router.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_status = "degraded"
    return HealthResponse(status="ok", db=db_status, version=GIT_SHA)
