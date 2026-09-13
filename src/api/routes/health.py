"""
NirmaanAI Health & Diagnostics API Routes
"""

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.dependencies import get_db

router = APIRouter(tags=["System & Health"])


class SystemHealthResponse(BaseModel):
    status: str = Field(description="OVERALL service status: HEALTHY, DEGRADED, or UNAVAILABLE.")
    application: str = Field(description="FastAPI service status.")
    database: str = Field(description="Database connection status: CONNECTED or UNAVAILABLE.")
    database_dialect: str = Field(default="unknown", description="Database dialect (e.g. postgresql, sqlite).")
    postgresql_verified: bool = Field(default=False, description="True ONLY if connected to a live PostgreSQL instance.")
    version: str = Field(default="0.18.0", description="API software version.")


@router.get("/health", response_model=SystemHealthResponse, summary="System Health Check")
def get_system_health(response: Response, db: Session = Depends(get_db)):
    """
    Evaluates application and database health.
    Returns HTTP 200 when connected, or HTTP 503 when database is unreachable.
    Accurately identifies database dialect and never claims PostgreSQL is verified unless dialect is postgresql.
    """
    app_status = "HEALTHY"
    db_status = "CONNECTED"
    overall_status = "HEALTHY"
    dialect_name = "unknown"
    is_postgres_verified = False

    try:
        if db.bind is not None:
            dialect_name = db.bind.dialect.name
        db.execute(text("SELECT 1")).scalar()
        is_postgres_verified = (dialect_name == "postgresql")
    except Exception:
        db_status = "UNAVAILABLE"
        overall_status = "UNAVAILABLE"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return SystemHealthResponse(
        status=overall_status,
        application=app_status,
        database=db_status,
        database_dialect=dialect_name,
        postgresql_verified=is_postgres_verified,
        version="0.18.0",
    )


@router.get("/api/v1/health", response_model=SystemHealthResponse, summary="API v1 Health Check")
def get_api_v1_health(response: Response, db: Session = Depends(get_db)):
    """Versioned health endpoint."""
    return get_system_health(response=response, db=db)
