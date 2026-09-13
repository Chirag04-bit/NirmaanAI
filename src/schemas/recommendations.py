"""
NirmaanAI Operational Recommendation Schemas (Pydantic v2)
Covers Phase 15 prescriptive recommendation engine.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationResponse(BaseModel):
    """
    Evidence-grounded operational recommendation.
    Preserves closed 26-action taxonomy, priority/urgency matrix, and evidence references.
    """
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: str
    machine_id: str
    category: str = Field(description="PREVENTIVE_MAINTENANCE, PROCESS_OPTIMIZATION, INVENTORY_REPLENISHMENT, QUALITY_CONTROL, ENERGY_MANAGEMENT.")
    action: str = Field(description="Action from the closed 26-action taxonomy (e.g. INSPECT_SPINDLE_BEARING).")
    priority: str = Field(description="CRITICAL, HIGH, MEDIUM, LOW.")
    urgency: str = Field(description="IMMEDIATE, SCHEDULED, DEFERRED.")
    evidence_strength: str = Field(description="HIGH, MEDIUM, LOW.")
    rationale: str
    evidence_references: Optional[str] = None
    status: str = "PENDING"
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: str = Field(default="RULE_DERIVED")
    created_at: Optional[datetime] = None
