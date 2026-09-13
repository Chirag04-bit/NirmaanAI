"""
NirmaanAI Maintenance API Routes
Preserves temporal causality and separates retrospective ground truth.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.maintenance import MaintenanceRecordResponse
from src.services.api.machine_service import MachineApiService
from src.services.api.maintenance_service import MaintenanceApiService

router = APIRouter(tags=["Maintenance"])


@router.get("/maintenance/records", response_model=PaginatedResponse[MaintenanceRecordResponse], summary="List Maintenance Records")
def list_maintenance_records(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    include_retrospective: bool = Query(
        False,
        description="Set True to include post-cutoff retrospective ground-truth events (e.g. MAINT_0003). Default False prevents decision leakage."
    ),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = MaintenanceApiService.list_maintenance(
        db,
        machine_id=machine_id,
        include_retrospective=include_retrospective,
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


@router.get("/machines/{machine_id}/maintenance", response_model=PaginatedResponse[MaintenanceRecordResponse], summary="Get Machine Maintenance History")
def get_machine_maintenance(
    machine_id: str,
    include_retrospective: bool = Query(False, description="Include post-cutoff retrospective records."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    items, total = MaintenanceApiService.list_maintenance(
        db,
        machine_id=machine_id,
        include_retrospective=include_retrospective,
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


@router.get("/maintenance/{maintenance_id}", response_model=MaintenanceRecordResponse, summary="Get Maintenance Record Details")
def get_maintenance_record(maintenance_id: str, db: Session = Depends(get_db)):
    rec = MaintenanceApiService.get_maintenance_record(db, maintenance_id=maintenance_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record '{maintenance_id}' not found."
        )
    return rec
