"""
NirmaanAI Maintenance Schemas (Pydantic v2)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MaintenanceRecordResponse(BaseModel):
    """
    Maintenance event record.
    Strictly preserves temporal causality:
    - is_decision_input = True: Event occurred <= DECISION_CUTOFF (2026-01-21T12:00:00Z).
    - is_decision_input = False: Post-cutoff retrospective synthetic ground truth (e.g. MAINT_0003).
    """
    model_config = ConfigDict(from_attributes=True)

    maintenance_id: str
    machine_id: str
    maintenance_type: str
    failure_mode: str = "NONE"
    timestamp: datetime
    duration_minutes: float
    reason: str = ""
    technician: str = "TECH_01"
    status: str = "COMPLETED"
    notes: Optional[str] = None
    is_decision_input: bool = Field(description="True if event is valid prospective decision evidence (<= cutoff).")
    epistemic_status: str = Field(description="Epistemic classification: OBSERVED_HISTORICAL vs RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.")
    created_at: Optional[datetime] = None
