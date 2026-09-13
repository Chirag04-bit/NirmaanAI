"""
NirmaanAI Financial & Operational Loss Analysis Models
Phase 14: Operational & Financial Loss Analysis (INR)

Defines strongly typed Pydantic v2 schemas and enumerations supporting:
1. Strict epistemic categorization (OBSERVED, DERIVED_FROM_OBSERVED, CONFIGURED_ASSUMPTION,
   PROJECTED_OPPORTUNITY_COST, CONTROLLED_SYNTHETIC).
2. Loss category taxonomy (Unplanned Downtime, Routine Maintenance, Energy Cost,
   Energy Inefficiency, Scrap Material, Production Rework, Emergency Maintenance Labor,
   Bottleneck Opportunity Cost).
3. Explicit separation between Unplanned Downtime and Scheduled Maintenance.
4. Explicit accounting treatment of Emergency Maintenance Overhaul Labor (₹420).
5. Disaggregated machine loss rollups and plant-wide summary representations.
6. Mathematical accounting identities for Realized Loss and Gross Exposure.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EpistemicClassification(str, Enum):
    """
    Epistemic provenance classification for operational and financial figures.
    Mandates transparent distinction between directly observed, derived physical,
    simulation assumptions, and projected opportunity metrics.
    """
    OBSERVED = "OBSERVED"
    DERIVED_FROM_OBSERVED = "DERIVED_FROM_OBSERVED"
    CONFIGURED_ASSUMPTION = "CONFIGURED_ASSUMPTION"
    PROJECTED_OPPORTUNITY_COST = "PROJECTED_OPPORTUNITY_COST"
    CONTROLLED_SYNTHETIC = "CONTROLLED_SYNTHETIC"


class LossCategory(str, Enum):
    """
    Standardized operational disruption and loss categories for manufacturing MSMEs.
    """
    UNPLANNED_DOWNTIME = "UNPLANNED_DOWNTIME"
    ROUTINE_MAINTENANCE = "ROUTINE_MAINTENANCE"
    ENERGY_COST = "ENERGY_COST"
    ENERGY_INEFFICIENCY = "ENERGY_INEFFICIENCY"
    SCRAP_MATERIAL = "SCRAP_MATERIAL"
    PRODUCTION_REWORK = "PRODUCTION_REWORK"
    EMERGENCY_MAINTENANCE_LABOR = "EMERGENCY_MAINTENANCE_LABOR"
    BOTTLENECK_OPPORTUNITY_COST = "BOTTLENECK_OPPORTUNITY_COST"


class LossItem(BaseModel):
    """
    Atomic operational loss line item with full epistemic provenance.
    """
    model_config = ConfigDict(frozen=True)

    loss_id: str = Field(description="Unique identifier for the loss event/record")
    machine_id: str = Field(description="Asset identifier (e.g. M1 to M5)")
    timestamp: datetime = Field(description="UTC timestamp of the disruption or event")
    category: LossCategory = Field(description="Operational loss category")
    epistemic_type: EpistemicClassification = Field(description="Epistemic provenance classification")
    quantity: float = Field(ge=0.0, description="Underlying physical quantity (hours, kWh, kg, units)")
    unit: str = Field(description="Physical unit of measurement")
    rate_inr: float = Field(ge=0.0, description="Configured unit financial rate in INR")
    amount_inr: float = Field(ge=0.0, description="Calculated financial impact in INR (rounded to 2 decimal places)")
    description: str = Field(description="Human-readable event narrative")
    context: Dict[str, Any] = Field(default_factory=dict, description="Operational metadata and context tags")


class MachineLossBreakdown(BaseModel):
    """
    Disaggregated financial and operational loss assessment for a single machine asset.
    Maintains clean, mathematically verified separation between:
    - Unplanned downtime loss (failure halts)
    - Routine maintenance planned cost (scheduled service)
    - Scrap material replacement loss
    - Production rework labor overhead (parts recovery)
    - Emergency maintenance overhaul labor (technician service)
    - Energy inefficiency loss (excess above rated power)
    - Projected opportunity cost (delayed throughput margin)
    """
    model_config = ConfigDict(frozen=True)

    machine_id: str

    # 1. Downtime Breakdown (Strict separation between unplanned failure and scheduled maintenance)
    observed_unplanned_downtime_hours: float = Field(default=0.0, ge=0.0)
    observed_unplanned_downtime_loss_inr: float = Field(default=0.0, ge=0.0)
    observed_routine_maintenance_hours: float = Field(default=0.0, ge=0.0)
    observed_routine_maintenance_cost_inr: float = Field(default=0.0, ge=0.0)
    total_maintenance_downtime_hours: float = Field(default=0.0, ge=0.0)
    total_maintenance_downtime_cost_inr: float = Field(default=0.0, ge=0.0)
    observed_downtime_hours: float = Field(default=0.0, ge=0.0)
    observed_downtime_loss_inr: float = Field(default=0.0, ge=0.0)

    # 2. Scrap Breakdown
    scrap_quantity_units: int = Field(default=0, ge=0)
    scrap_mass_kg: float = Field(default=0.0, ge=0.0)
    scrap_loss_inr: float = Field(default=0.0, ge=0.0)

    # 3. Labor Breakdown (Strict separation between production part rework and emergency technician labor)
    production_rework_hours: float = Field(default=0.0, ge=0.0)
    production_rework_loss_inr: float = Field(default=0.0, ge=0.0)
    emergency_maintenance_labor_hours: float = Field(default=0.0, ge=0.0)
    emergency_maintenance_labor_cost_inr: float = Field(default=0.0, ge=0.0)
    total_rework_and_labor_hours: float = Field(default=0.0, ge=0.0)
    total_rework_and_labor_loss_inr: float = Field(default=0.0, ge=0.0)

    # 4. Energy Breakdown
    total_energy_kwh: float = Field(default=0.0, ge=0.0)
    total_energy_cost_inr: float = Field(default=0.0, ge=0.0)
    base_energy_cost_inr: float = Field(default=0.0, ge=0.0)
    peak_energy_cost_inr: float = Field(default=0.0, ge=0.0)
    energy_inefficiency_kwh: float = Field(default=0.0, ge=0.0)
    energy_inefficiency_loss_inr: float = Field(default=0.0, ge=0.0)

    # 5. Bottleneck Opportunity Cost
    delayed_throughput_units: float = Field(default=0.0, ge=0.0)
    projected_opportunity_cost_inr: float = Field(default=0.0, ge=0.0)

    # 6. Formal Accounting Identities
    # Realized Operational Loss = Unplanned Downtime + Scrap + Production Rework + Emergency Overhaul Labor + Energy Inefficiency
    realized_operational_loss_inr: float = Field(default=0.0, ge=0.0)
    # Gross Financial Exposure = Realized Operational Loss + Projected Opportunity Cost
    gross_financial_exposure_inr: float = Field(default=0.0, ge=0.0)
    # Non-overlapping Exposure (deduplicated against concurrency)
    non_overlapping_financial_exposure_inr: float = Field(default=0.0, ge=0.0)

    items_count: int = Field(default=0, ge=0)
    epistemic_summary: Dict[str, float] = Field(default_factory=dict)


class FactoryLossSummary(BaseModel):
    """
    Aggregated plant-wide financial loss evaluation across all production assets.
    """
    model_config = ConfigDict(frozen=True)

    timestamp: datetime = Field(description="Evaluation generation timestamp")
    evaluation_window_start: Optional[datetime] = None
    evaluation_window_end: Optional[datetime] = None
    machine_breakdowns: Dict[str, MachineLossBreakdown] = Field(default_factory=dict)

    # Plant-wide component sums
    total_unplanned_downtime_hours: float = Field(default=0.0, ge=0.0)
    total_unplanned_downtime_loss_inr: float = Field(default=0.0, ge=0.0)
    total_routine_maintenance_hours: float = Field(default=0.0, ge=0.0)
    total_routine_maintenance_cost_inr: float = Field(default=0.0, ge=0.0)
    total_maintenance_downtime_hours: float = Field(default=0.0, ge=0.0)
    total_maintenance_downtime_cost_inr: float = Field(default=0.0, ge=0.0)

    total_scrap_loss_inr: float = Field(default=0.0, ge=0.0)
    total_production_rework_loss_inr: float = Field(default=0.0, ge=0.0)
    total_emergency_maintenance_labor_cost_inr: float = Field(default=0.0, ge=0.0)
    total_energy_inefficiency_loss_inr: float = Field(default=0.0, ge=0.0)
    total_energy_cost_inr: float = Field(default=0.0, ge=0.0)
    total_projected_opportunity_cost_inr: float = Field(default=0.0, ge=0.0)

    # Formal Plant Accounting Identities
    total_realized_loss_inr: float = Field(default=0.0, ge=0.0)
    gross_financial_exposure_inr: float = Field(default=0.0, ge=0.0)
    non_overlapping_financial_exposure_inr: float = Field(default=0.0, ge=0.0)

    by_category: Dict[str, float] = Field(default_factory=dict)
    by_epistemic_type: Dict[str, float] = Field(default_factory=dict)

    audit_safeguards_applied: List[str] = Field(default_factory=list)
    research_integrity_statement: str = Field(
        default="Financial parameters are configured simulation assumptions unless independently measured. "
                "Projected opportunity cost is an operational capacity model and not equivalent to realized accounting loss."
    )
