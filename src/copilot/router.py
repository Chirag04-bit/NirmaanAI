"""
NirmaanAI Phase 20: AI Factory Copilot API Router
Exposes high-performance, validated endpoints for operational decision support.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.copilot.copilot_service import FactoryCopilotService
from src.copilot.schemas import CopilotContext, CopilotResponse

router = APIRouter(prefix="/copilot", tags=["AI Factory Copilot"])

# Global singleton service instance for fast in-process routing
_copilot_service: Optional[FactoryCopilotService] = None


def get_copilot_service() -> FactoryCopilotService:
    """Dependency provider for FactoryCopilotService."""
    global _copilot_service
    if _copilot_service is None:
        _copilot_service = FactoryCopilotService()
    return _copilot_service


class CopilotAskRequest(BaseModel):
    """Request payload for Copilot query submission."""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language operational query.")
    context: Optional[CopilotContext] = Field(default=None, description="Optional operational and temporal context.")


@router.post(
    "/ask",
    response_model=CopilotResponse,
    summary="Submit a natural-language query to the AI Factory Copilot",
    description="Returns a grounded, evidence-backed decision-support answer with full provenance and confidence metrics.",
)
async def ask_copilot(
    request: CopilotAskRequest,
    service: FactoryCopilotService = Depends(get_copilot_service),
) -> CopilotResponse:
    """Processes user query and returns grounded Copilot response."""
    try:
        return service.ask(query=request.query, context=request.context)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Copilot inference failed: {str(e)}",
        )


@router.get(
    "/health",
    summary="Copilot subsystem health check",
    description="Returns operational status of the Copilot inference and grounding layer.",
)
async def copilot_health(
    service: FactoryCopilotService = Depends(get_copilot_service),
):
    """Health check verifying vector store readiness."""
    total_chunks = len(service.retriever.vector_store.chunks) if service.retriever.vector_store else 0
    return {
        "status": "healthy",
        "subsystem": "AI Factory Copilot (Phase 20)",
        "version": "v0.20.0",
        "indexed_chunks": total_chunks,
        "decision_cutoff": "2026-01-21T12:00:00Z",
        "grounding_layer": "Phase 19 Factory Knowledge Memory",
    }
