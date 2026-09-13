"""
NirmaanAI FastAPI Dependencies
Provides request-scoped database sessions and standard parameter validators.
"""

from datetime import datetime
from typing import Generator, Optional
from fastapi import HTTPException, Query, status
from sqlalchemy.orm import Session

from src.db.session import get_session_factory
from src.schemas.common import PaginationParams
from src.schemas.sensors import TelemetryQueryParams


def get_db() -> Generator[Session, None, None]:
    """
    Yields a request-scoped database session.
    Can be easily overridden in tests via app.dependency_overrides[get_db].
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def get_pagination(
    page: int = Query(1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(50, ge=1, le=100, description="Items per page (1-100)."),
) -> PaginationParams:
    """Extracts and validates pagination query parameters."""
    return PaginationParams(page=page, page_size=page_size)


def get_telemetry_params(
    start: Optional[datetime] = Query(None, description="Start timestamp (UTC)."),
    end: Optional[datetime] = Query(None, description="End timestamp (UTC)."),
    limit: int = Query(100, ge=1, le=1000, description="Max telemetry records (1-1000)."),
) -> TelemetryQueryParams:
    """Extracts and validates bounded telemetry query parameters."""
    if start and end and start > end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query parameter 'start' must be earlier than or equal to 'end'."
        )
    return TelemetryQueryParams(start=start, end=end, limit=limit)
