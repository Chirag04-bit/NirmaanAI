"""
NirmaanAI Machine API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.machines import MachineOverviewResponse, MachineResponse
from src.services.api.machine_service import MachineApiService

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.get("", response_model=PaginatedResponse[MachineResponse], summary="List Machines")
def list_machines(
    factory_id: Optional[str] = Query(None, description="Filter by parent factory ID."),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by operational status."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = MachineApiService.list_machines(
        db,
        factory_id=factory_id,
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


@router.get("/{machine_id}", response_model=MachineResponse, summary="Get Machine Details")
def get_machine(machine_id: str, db: Session = Depends(get_db)):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )
    return machine


@router.get("/{machine_id}/overview", response_model=MachineOverviewResponse, summary="Get Machine Overview")
def get_machine_overview(machine_id: str, db: Session = Depends(get_db)):
    overview = MachineApiService.get_machine_overview(db, machine_id=machine_id)
    if not overview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )
    return overview
