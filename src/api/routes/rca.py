"""
NirmaanAI Root Cause Analysis API Routes (Phase 12)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.schemas.ai_outputs import RcaResultResponse
from src.services.api.ai_output_service import AiOutputApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["AI Subsystems: Root Cause Analysis"])


@router.get(
    "/ai/rca/{machine_id}",
    response_model=List[RcaResultResponse],
    summary="Get Machine Root Cause Analysis Results",
)
def get_machine_rca(machine_id: str, db: Session = Depends(get_db)):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    return AiOutputApiService.get_rca_results(db, machine_id=machine_id)
