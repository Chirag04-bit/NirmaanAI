"""
NirmaanAI What-If Digital Twin Simulation API Routes (Phase 16)
Preserves counterfactual semantics, net benefit calculations, and NOT_PROJECTABLE diagnostic KPIs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_pagination
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.simulations import SimulationScenarioResponse
from src.services.api.machine_service import MachineApiService
from src.services.api.simulation_service import SimulationApiService

router = APIRouter(tags=["Simulation & What-If"])


@router.get(
    "/simulations",
    response_model=PaginatedResponse[SimulationScenarioResponse],
    summary="List Simulation Scenarios",
)
def list_simulations(
    machine_id: Optional[str] = Query(None, description="Filter by machine ID."),
    pagination: PaginationParams = Depends(get_pagination),
    db: Session = Depends(get_db),
):
    items, total = SimulationApiService.list_scenarios(
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
    "/simulations/{scenario_id}",
    response_model=SimulationScenarioResponse,
    summary="Get Simulation Scenario Details",
)
def get_simulation_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = SimulationApiService.get_scenario(db, scenario_id=scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation scenario '{scenario_id}' not found."
        )
    return scenario


@router.get(
    "/machines/{machine_id}/simulations",
    response_model=PaginatedResponse[SimulationScenarioResponse],
    summary="Get Machine Simulation Scenarios",
)
def get_machine_simulations(
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

    items, total = SimulationApiService.list_scenarios(
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
