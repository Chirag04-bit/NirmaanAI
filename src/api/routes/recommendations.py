"""
NirmaanAI Operational Recommendations API Routes (Phase 15)
Preserves closed 26-action taxonomy and evidence-grounded prioritization.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.recommendations import RecommendationResponse
from src.services.api.machine_service import MachineApiService
from src.services.api.recommendation_service import RecommendationApiService

router = APIRouter(tags=["Recommendations"])


@router.get(
    "/recommendations",
    response_model=PaginatedResponse[RecommendationResponse],
    summary="List Operational Recommendations",
)
def list_recommendations(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    category: Optional[str] = Query(None, description="Filter by category (e.g. PREVENTIVE_MAINTENANCE)."),
    priority: Optional[str] = Query(None, description="Filter by priority (CRITICAL, HIGH, MEDIUM, LOW)."),
    urgency: Optional[str] = Query(None, description="Filter by urgency (IMMEDIATE, SCHEDULED, DEFERRED)."),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, ACCEPTED)."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = RecommendationApiService.list_recommendations(
        db,
        machine_id=machine_id,
        category=category,
        priority=priority,
        urgency=urgency,
        status=status_filter,
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
    "/machines/{machine_id}/recommendations",
    response_model=PaginatedResponse[RecommendationResponse],
    summary="Get Machine Recommendations",
)
def get_machine_recommendations(
    machine_id: str,
    priority: Optional[str] = Query(None, description="Filter by priority."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    items, total = RecommendationApiService.list_recommendations(
        db,
        machine_id=machine_id,
        priority=priority,
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
