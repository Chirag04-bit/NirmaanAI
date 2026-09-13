"""
NirmaanAI Production Jobs API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.production import ProductionJobResponse
from src.services.api.machine_service import MachineApiService
from src.services.api.production_service import ProductionApiService

router = APIRouter(tags=["Production"])


@router.get("/production/jobs", response_model=PaginatedResponse[ProductionJobResponse], summary="List Production Jobs")
def list_production_jobs(
    machine_id: Optional[str] = Query(None, description="Filter jobs by machine ID."),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by job status."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = ProductionApiService.list_jobs(
        db,
        machine_id=machine_id,
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


@router.get("/production/jobs/{job_id}", response_model=ProductionJobResponse, summary="Get Production Job Details")
def get_production_job(job_id: str, db: Session = Depends(get_db)):
    job = ProductionApiService.get_job(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production job '{job_id}' not found."
        )
    return job


@router.get("/machines/{machine_id}/production", response_model=PaginatedResponse[ProductionJobResponse], summary="Get Machine Production Jobs")
def get_machine_production(
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

    items, total = ProductionApiService.list_jobs(
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
