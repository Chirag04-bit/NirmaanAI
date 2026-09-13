"""
NirmaanAI Inventory API Routes
Preserves authoritative Phase 10 inventory contracts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.inventory import InventoryItemResponse
from src.services.api.inventory_service import InventoryApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["Inventory"])


@router.get("/inventory", response_model=PaginatedResponse[InventoryItemResponse], summary="List Inventory & Spares")
def list_inventory(
    factory_id: Optional[str] = Query(None, description="Filter by factory ID."),
    category: Optional[str] = Query(None, description="Filter by category (e.g. SPARE_PART, RAW_MATERIAL)."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = InventoryApiService.list_inventory(
        db,
        factory_id=factory_id,
        category=category,
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


@router.get("/inventory/{sku}", response_model=InventoryItemResponse, summary="Get Inventory Item by SKU")
def get_inventory_item(sku: str, db: Session = Depends(get_db)):
    item = InventoryApiService.get_by_sku(db, sku_id=sku)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with SKU '{sku}' not found."
        )
    return item


@router.get("/machines/{machine_id}/inventory", response_model=List[InventoryItemResponse], summary="Get Machine Critical Spares")
def get_machine_inventory(machine_id: str, db: Session = Depends(get_db)):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )
    return InventoryApiService.get_machine_inventory(db, machine_id=machine_id)
