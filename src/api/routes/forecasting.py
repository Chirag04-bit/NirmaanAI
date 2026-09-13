"""
NirmaanAI Production & Energy Forecasting API Routes (Phase 9)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.ai_outputs import ForecastingResponse
from src.services.api.ai_output_service import AiOutputApiService

router = APIRouter(tags=["AI Subsystems: Forecasting"])


@router.get(
    "/ai/forecasts",
    response_model=PaginatedResponse[ForecastingResponse],
    summary="List Production & Energy Forecasts",
)
def list_forecasts(
    target_series: Optional[str] = Query(
        None,
        description="Filter by target: production_volume, power_consumption_kw, electricity_cost_inr."
    ),
    horizon_hours: Optional[int] = Query(None, description="Forecast horizon in hours (e.g. 24)."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = AiOutputApiService.get_forecasts(
        db,
        target_series=target_series,
        horizon_hours=horizon_hours,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    total_pages = (total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )
