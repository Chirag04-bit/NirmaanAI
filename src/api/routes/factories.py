"""
NirmaanAI Factory API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.factories import FactoryOverviewResponse, FactoryResponse
from src.services.api.factory_service import FactoryApiService

router = APIRouter(prefix="/factories", tags=["Factories"])


@router.get("", response_model=PaginatedResponse[FactoryResponse], summary="List Factories")
def list_factories(
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = FactoryApiService.list_factories(db, page=pagination.page, page_size=pagination.page_size)
    total_pages = (total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/{factory_id}", response_model=FactoryResponse, summary="Get Factory Details")
def get_factory(factory_id: str, db: Session = Depends(get_db)):
    factory = FactoryApiService.get_factory(db, factory_id=factory_id)
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory '{factory_id}' not found."
        )
    return factory


@router.get("/{factory_id}/overview", response_model=FactoryOverviewResponse, summary="Get Factory Overview")
def get_factory_overview(factory_id: str, db: Session = Depends(get_db)):
    overview = FactoryApiService.get_factory_overview(db, factory_id=factory_id)
    if not overview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory '{factory_id}' not found."
        )
    return overview
