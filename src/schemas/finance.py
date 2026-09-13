"""
NirmaanAI Financial Loss & Exposure Schemas (Pydantic v2)
Covers Phase 14 first-principles loss accounting.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FinancialLossResponse(BaseModel):
    """Individual financial loss record with cost-pool decomposition."""
    model_config = ConfigDict(from_attributes=True)

    loss_id: int
    machine_id: str
    timestamp: datetime
    loss_type: str = Field(description="REALIZED_LOSS, PROJECTED_OPPORTUNITY_COST, GROSS_EXPOSURE, AVOIDED_OPPORTUNITY_COST.")
    downtime_minutes: float
    downtime_loss_inr: float
    scrap_loss_inr: float
    rework_loss_inr: float
    emergency_labor_loss_inr: float
    energy_loss_inr: float
    opportunity_cost_inr: float
    total_loss_inr: float
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: str = Field(description="OBSERVED_HISTORICAL, PROJECTED_OPPORTUNITY_COST, AGGREGATE_BOUND, etc.")


class MachineFinancialSummaryResponse(BaseModel):
    """
    Segregated financial breakdown for a machine.
    Prevents collapsing realized costs into projected opportunity bounds.
    """
    model_config = ConfigDict(from_attributes=True)

    machine_id: str
    as_of_timestamp: datetime

    # 1. Realized Historical Loss (Observed downtime, scrap, rework, emergency labor, excess energy)
    realized_historical_loss_inr: float = Field(
        description="Historical accounting loss from completed events (e.g. M2: ₹73,062.28)."
    )
    realized_downtime_loss_inr: float = Field(default=0.0)
    realized_scrap_loss_inr: float = Field(default=0.0)
    realized_rework_loss_inr: float = Field(default=0.0)
    realized_emergency_labor_inr: float = Field(default=0.0)
    realized_energy_inefficiency_inr: float = Field(default=0.0)

    # 2. Baseline Projected Opportunity Cost
    baseline_projected_opportunity_cost_inr: float = Field(
        description="Bottleneck delay opportunity loss (e.g. M2: ₹24,320.00 for 76 units @ ₹320/unit)."
    )

    # 3. Total Baseline Gross Financial Exposure
    baseline_gross_financial_exposure_inr: float = Field(
        description="Realized loss + Baseline opportunity cost (e.g. M2: ₹97,382.28)."
    )

    # 4. Scenario-Specific Mitigation Bounds (Phase 16 Counterfactuals)
    counterfactual_avoided_opportunity_cost_inr: Optional[float] = Field(
        default=None,
        description="Opportunity loss avoided by throughput recovery (e.g. Scenario D: ₹19,520.00)."
    )
    counterfactual_remaining_gross_exposure_inr: Optional[float] = Field(
        default=None,
        description="Remaining exposure after counterfactual mitigation (e.g. ₹77,862.28)."
    )

    epistemic_status: str = Field(
        default="FINANCIAL_SUMMARY_SEGREGATED",
        description="Explicit notice that historical and counterfactual pools are distinct."
    )
