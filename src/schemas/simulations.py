"""
NirmaanAI Simulation Schemas (Pydantic v2)
Covers Phase 16 what-if digital-twin-inspired counterfactual engine.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SimulationScenarioResponse(BaseModel):
    """
    Phase 16 Counterfactual What-If Scenario.
    Preserves:
    - Normalized baseline state
    - Operational execution parameters
    - Normalized financial benefit (₹7,030 net benefit)
    - Strictly non-projectable diagnostic KPIs ("NOT_PROJECTABLE")
    """
    model_config = ConfigDict(from_attributes=True)

    scenario_id: str
    machine_id: str
    scenario_name: str
    decision_cutoff: datetime

    # 1. Baseline State at Decision Cutoff
    baseline_downtime_minutes: float
    baseline_failure_probability: float
    baseline_anomaly_score: float
    baseline_health_score: float
    baseline_realized_loss_inr: float
    baseline_gross_exposure_inr: float

    # 2. Operational Intervention Execution
    planned_service_downtime_minutes: float
    net_avoided_downtime_minutes: float

    # 3. Normalized Financial Projections
    avoided_downtime_loss_inr: float
    avoided_emergency_labor_inr: float
    projected_avoided_breakdown_loss_inr: float
    planned_service_cost_inr: float
    net_counterfactual_benefit_inr: float
    remaining_gross_exposure_inr: float

    # 4. Diagnostic KPI Governance (NOT_PROJECTABLE)
    projected_failure_probability: str = Field(
        default="NOT_PROJECTABLE",
        description="Diagnostic failure risk under intervention (NOT_PROJECTABLE without physics simulator)."
    )
    projected_anomaly_score: str = Field(
        default="NOT_PROJECTABLE",
        description="PCA anomaly score under intervention (NOT_PROJECTABLE)."
    )
    projected_health_score: str = Field(
        default="NOT_PROJECTABLE",
        description="Composite health score under intervention (NOT_PROJECTABLE)."
    )
    projected_health_state: str = Field(
        default="NOT_PROJECTABLE",
        description="Health band under intervention (NOT_PROJECTABLE)."
    )

    # 5. Metadata & Semantics
    temporal_semantics: str = "COUNTERFACTUAL_EVALUATION"
    epistemic_status: str = "HYPOTHETICAL_COUNTERFACTUAL"
    diagnostic_kpi_status: str = "NOT_PROJECTABLE"
    provenance: str = "COUNTERFACTUAL_PROJECTION"
    intervention_list: str
    configured_assumptions: str
    created_at: Optional[datetime] = None
