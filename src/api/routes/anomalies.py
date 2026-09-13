"""
NirmaanAI Anomaly Detection API Routes (Phase 7)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.ai_outputs import AnomalyDetectionResponse
from src.services.api.ai_output_service import AiOutputApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["AI Subsystems: Anomaly Detection"])


@router.get(
    "/ai/anomalies",
    response_model=PaginatedResponse[AnomalyDetectionResponse],
    summary="List Anomaly Detection Results",
)
def list_anomalies(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = AiOutputApiService.get_anomaly_results(
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
    "/machines/{machine_id}/anomalies",
    response_model=PaginatedResponse[AnomalyDetectionResponse],
    summary="Get Machine Anomaly Results",
)
def get_machine_anomalies(
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

    items, total = AiOutputApiService.get_anomaly_results(
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
