"""
NirmaanAI Financial API Routes (Phase 14)
Preserves strict financial semantics:
- Realized loss: ₹73,062.28
- Baseline opportunity cost: ₹24,320.00
- Baseline gross exposure: ₹97,382.28
- Counterfactual avoided opportunity cost: ₹19,520.00
- Remaining exposure: ₹77,862.28
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.finance import FinancialLossResponse, MachineFinancialSummaryResponse
from src.services.api.factory_service import FactoryApiService
from src.services.api.finance_service import FinanceApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["Financial Loss & Exposure"])


@router.get(
    "/finance/losses",
    response_model=PaginatedResponse[FinancialLossResponse],
    summary="List Financial Loss Records",
)
def list_financial_losses(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    loss_type: Optional[str] = Query(
        None,
        description="Filter by loss type: REALIZED_LOSS, PROJECTED_OPPORTUNITY_COST, GROSS_EXPOSURE, AVOIDED_OPPORTUNITY_COST."
    ),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = FinanceApiService.list_losses(
        db,
        machine_id=machine_id,
        loss_type=loss_type,
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
    "/machines/{machine_id}/finance",
    response_model=MachineFinancialSummaryResponse,
    summary="Get Machine Financial Summary",
)
def get_machine_finance(machine_id: str, db: Session = Depends(get_db)):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    return FinanceApiService.get_machine_finance_summary(db, machine_id=machine_id)


@router.get(
    "/factories/{factory_id}/finance",
    response_model=PaginatedResponse[FinancialLossResponse],
    summary="Get Factory Financial Loss Records",
)
def get_factory_finance(
    factory_id: str,
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    factory = FactoryApiService.get_factory(db, factory_id=factory_id)
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory '{factory_id}' not found."
        )

    # Returns all financial loss records
    items, total = FinanceApiService.list_losses(
        db,
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
