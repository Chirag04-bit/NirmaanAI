"""
NirmaanAI Sensor & Telemetry API Routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_telemetry_params
from src.schemas.sensors import TelemetryQueryParams, TelemetrySnapshotResponse
from src.services.api.machine_service import MachineApiService
from src.services.api.telemetry_service import TelemetryApiService

router = APIRouter(tags=["Telemetry & Sensors"])


@router.get(
    "/machines/{machine_id}/telemetry",
    response_model=List[TelemetrySnapshotResponse],
    summary="Get Machine Telemetry Time-Series",
)
def get_machine_telemetry(
    machine_id: str,
    params: TelemetryQueryParams = Depends(get_telemetry_params),
    db: Session = Depends(get_db),
):
    """
    Returns bounded historical telemetry snapshots for a machine.
    Enforces max limit = 1000 and valid start <= end timestamps.
    """
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    return TelemetryApiService.get_machine_telemetry(
        db,
        machine_id=machine_id,
        start=params.start,
        end=params.end,
        limit=params.limit,
    )
