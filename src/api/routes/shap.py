"""
NirmaanAI SHAP Feature Attribution API Routes (Phase 11)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_db
from src.schemas.ai_outputs import ShapExplanationResponse
from src.services.api.ai_output_service import AiOutputApiService
from src.services.api.machine_service import MachineApiService

router = APIRouter(tags=["AI Subsystems: Explainability (SHAP)"])


@router.get(
    "/ai/shap/{machine_id}",
    response_model=List[ShapExplanationResponse],
    summary="Get Machine SHAP Feature Attributions",
)
def get_machine_shap(machine_id: str, db: Session = Depends(get_db)):
    machine = MachineApiService.get_machine(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine '{machine_id}' not found."
        )

    return AiOutputApiService.get_shap_explanations(db, machine_id=machine_id)
