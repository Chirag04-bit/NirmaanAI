"""
NirmaanAI Predictive Maintenance API Routes (Phase 6)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.ai_outputs import PredictiveMaintenanceResponse
from src.services.api.ai_output_service import AiOutputApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["AI Subsystems: Predictive Maintenance"])


@router.get(
    "/ai/predictive-maintenance",
    response_model=PaginatedResponse[PredictiveMaintenanceResponse],
    summary="List Predictive Maintenance Predictions",
)
def list_predictive_maintenance(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = AiOutputApiService.get_pdm_predictions(
        db,
        machine_id=machine_id,
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
    "/machines/{machine_id}/predictive-maintenance",
    response_model=PaginatedResponse[PredictiveMaintenanceResponse],
    summary="Get Machine Predictive Maintenance Predictions",
)
def get_machine_predictive_maintenance(
    machine_id: str,
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    items, total = AiOutputApiService.get_pdm_predictions(
        db,
        machine_id=machine_id,
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
