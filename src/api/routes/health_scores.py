"""
NirmaanAI Factory Health Score API Routes (Phase 13)
Preserves locked Phase 13 bands:
EXCELLENT (90-100), HEALTHY (75-89), WATCH (60-74), DEGRADED (40-59), CRITICAL (0-39).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.ai_outputs import FactoryHealthScoreResponse
from src.services.api.ai_output_service import AiOutputApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["AI Subsystems: Factory Health"])


@router.get(
    "/ai/health-scores",
    response_model=PaginatedResponse[FactoryHealthScoreResponse],
    summary="List Factory & Machine Health Scores",
)
def list_health_scores(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    factory_id: Optional[str] = Query(None, description="Filter by factory ID."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = AiOutputApiService.get_health_scores(
        db,
        machine_id=machine_id,
        factory_id=factory_id,
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


@router.get(
    "/machines/{machine_id}/health",
    response_model=FactoryHealthScoreResponse,
    summary="Get Machine Current Health Score",
)
def get_machine_health(machine_id: str, db: Session = Depends(get_db)):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    items, _ = AiOutputApiService.get_health_scores(db, machine_id=machine_id, page=1, page_size=1)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No health score found for machine '{machine_id}'."
        )
    return items[0]
