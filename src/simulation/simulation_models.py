"""
NirmaanAI Digital-Twin-Inspired What-If Simulation Models
Phase 16: What-If / Digital-Twin-Inspired Simulation Engine

Defines strongly typed, validated Pydantic v2 schemas and enumerations supporting:
1. Closed approved intervention catalog (strictly 15 approved actions from Phase 15 taxonomy).
2. KPI state vectors covering mechanical, flow, inventory, and financial dimensions.
3. Explicit separation of:
   - Observed Baseline State
   - Hypothetical Scenario
   - Projected Outcome & Delta
4. Epistemic provenance preservation per metric and scenario.
5. Strict "NOT_PROJECTABLE" fallback when empirical or analytical evidence is insufficient.
6. Categorical uncertainty labels (HIGH_EVIDENCE, MODERATE_EVIDENCE, LOW_EVIDENCE, ASSUMPTION_DEPENDENT, NOT_PROJECTABLE).
7. Sensitivity analysis modeling (LOW, BASE, HIGH).

DECISION SUPPORT GOVERNANCE:
- This is a decision-support what-if simulation layer.
- NOT a physical digital twin, NOT a physics-validated simulator (no CFD/FEM).
- NOT an autonomous controller.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

from src.decision.loss_models import EpistemicClassification
from src.decision.recommendation_models import RecommendationAction, RecommendationCategory
from src.health.health_models import HealthState


class SimulationInterventionType(str, Enum):
    """
    Approved Phase 16 What-If Intervention Catalog.
    Strictly restricted to 15 actions supported by NirmaanAI's recommendation taxonomy.
    """
    # MAINTENANCE (5)
    INSPECT_SPINDLE_BEARING = "INSPECT_SPINDLE_BEARING"
    INSPECT_LUBRICATION = "INSPECT_LUBRICATION"
    REPLACE_WORN_COMPONENT = "REPLACE_WORN_COMPONENT"
    REPLACE_TOOLING = "REPLACE_TOOLING"
    SCHEDULE_PREVENTIVE_MAINTENANCE = "SCHEDULE_PREVENTIVE_MAINTENANCE"

    # PRODUCTION (5)
    REDUCE_MACHINE_FEED_RATE = "REDUCE_MACHINE_FEED_RATE"
    RESCHEDULE_PENDING_JOBS = "RESCHEDULE_PENDING_JOBS"
    REBALANCE_LINE_WORKLOAD = "REBALANCE_LINE_WORKLOAD"
    BUFFER_DOWNSTREAM_INVENTORY = "BUFFER_DOWNSTREAM_INVENTORY"
    PAUSE_NEW_JOB_RELEASE = "PAUSE_NEW_JOB_RELEASE"

    # INVENTORY (3)
    EXPEDITE_CRITICAL_SPARE = "EXPEDITE_CRITICAL_SPARE"
    TRIGGER_STANDARD_REORDER = "TRIGGER_STANDARD_REORDER"
    INCREASE_SAFETY_STOCK_BUFFER = "INCREASE_SAFETY_STOCK_BUFFER"

    # ENERGY (2)
    SHIFT_HIGH_LOAD_OFF_PEAK = "SHIFT_HIGH_LOAD_OFF_PEAK"
    INVESTIGATE_POWER_EXCURSION = "INVESTIGATE_POWER_EXCURSION"


class ProjectionConfidence(str, Enum):
    """
    Categorical projection confidence / uncertainty taxonomy.
    Statistical confidence intervals are NOT fabricated where uncalibrated.
    """
    HIGH_EVIDENCE = "HIGH_EVIDENCE"                    # Corroborated by observed historical transitions
    MODERATE_EVIDENCE = "MODERATE_EVIDENCE"            # Dual-phase analytical extrapolation
    LOW_EVIDENCE = "LOW_EVIDENCE"                      # Single-phase indicator with unmodeled dynamics
    ASSUMPTION_DEPENDENT = "ASSUMPTION_DEPENDENT"      # Driven by configured MSME scenario assumptions
    NOT_PROJECTABLE = "NOT_PROJECTABLE"                # Insufficient evidence; number NOT invented


class SensitivityTier(str, Enum):
    """Configured sensitivity tier for scenario assumption stress-testing."""
    LOW = "LOW"      # Conservative / pessimistic parameter assumptions
    BASE = "BASE"    # Nominal / expected parameter assumptions
    HIGH = "HIGH"    # Aggressive / optimistic parameter assumptions


class OperationalKPIVector(BaseModel):
    """
    Multidimensional operational state vector capturing mechanical, flow,
    inventory, and financial status.
    Supports 'NOT_PROJECTABLE' when a KPI cannot be rigorously estimated.
    """
    model_config = ConfigDict(frozen=True)

    # Mechanical & Health
    failure_probability: Union[float, str] = Field(description="P(fail) in [0, 1] or 'NOT_PROJECTABLE'")
    anomaly_score: Union[float, str] = Field(description="Normalized anomaly score in [0, 1] or 'NOT_PROJECTABLE'")
    health_score: Union[float, str] = Field(description="Factory Health Score in [0, 100] or 'NOT_PROJECTABLE'")
    health_state: Union[HealthState, str] = Field(description="Health band or 'NOT_PROJECTABLE'")

    # Production Flow
    cycle_ratio: Union[float, str] = Field(description="Actual / Design cycle time ratio or 'NOT_PROJECTABLE'")
    delayed_throughput_units: Union[float, str] = Field(description="Delayed production units or 'NOT_PROJECTABLE'")
    is_bottleneck: Union[bool, str] = Field(description="Bottleneck flag or 'NOT_PROJECTABLE'")

    # Downtime & Physical Quality
    unplanned_downtime_minutes: Union[float, str] = Field(description="Unplanned failure stoppage minutes")
    planned_downtime_minutes: Union[float, str] = Field(description="Scheduled maintenance stoppage minutes")
    scrap_units: Union[float, str] = Field(description="Defective scrap units produced")
    rework_hours: Union[float, str] = Field(description="Technician salvage rework hours")

    # Inventory
    observed_current_stock: Union[float, str] = Field(description="Physical on-hand inventory units")
    safety_stock: Union[float, str] = Field(description="Configured safety stock threshold")
    reorder_point: Union[float, str] = Field(description="Configured reorder point threshold")
    projected_post_action_stock: Union[float, str] = Field(description="Projected on-hand stock after action")
    is_safety_stock_breached: Union[bool, str] = Field(description="True if stock < safety stock")

    # Financial Exposure (Phase 14 accounting standards)
    realized_operational_loss_inr: Union[float, str] = Field(description="Realized loss from historical disruption")
    projected_opportunity_cost_inr: Union[float, str] = Field(description="Unearned margin from bottleneck delay")
    gross_financial_exposure_inr: Union[float, str] = Field(description="Realized loss + projected opportunity cost")
    projected_avoided_loss_inr: Union[float, str] = Field(description="Projected avoided financial loss from intervention")


class KPIDeltaVector(BaseModel):
    """
    Represents delta = Projected State - Baseline State.
    Values can be numeric differences or explicit categorical status changes.
    """
    model_config = ConfigDict(frozen=True)

    failure_probability_delta: Union[float, str]
    anomaly_score_delta: Union[float, str]
    health_score_delta: Union[float, str]
    health_state_change: str  # e.g. "CRITICAL -> HEALTHY" or "UNCHANGED"
    cycle_ratio_delta: Union[float, str]
    delayed_units_delta: Union[float, str]
    unplanned_downtime_delta_minutes: Union[float, str]
    planned_downtime_delta_minutes: Union[float, str]
    scrap_units_delta: Union[float, str]
    rework_hours_delta: Union[float, str]
    stock_delta_units: Union[float, str]
    projected_avoided_loss_inr: float
    gross_exposure_delta_inr: float


class ScenarioAssumption(BaseModel):
    """Documented assumption underpinning a scenario projection."""
    model_config = ConfigDict(frozen=True)

    assumption_id: str
    parameter_name: str
    configured_value: Any
    unit: Optional[str] = None
    rationale: str
    epistemic_classification: EpistemicClassification = EpistemicClassification.CONFIGURED_ASSUMPTION


class WhatIfScenario(BaseModel):
    """
    Immutable representation of a What-If simulation scenario.
    """
    model_config = ConfigDict(frozen=True)

    scenario_id: str = Field(description="Scenario identifier, e.g. SCEN_M2_A_BASELINE")
    scenario_name: str = Field(description="Descriptive name")
    machine_id: str = Field(description="Target machine asset ID (M1-M5)")
    as_of_timestamp: datetime = Field(description="Decision cutoff timestamp (no lookahead)")
    interventions: List[SimulationInterventionType] = Field(description="Hypothetical operational actions applied")
    baseline_state: OperationalKPIVector = Field(description="Observed/derived state at decision timestamp")
    assumptions: List[ScenarioAssumption] = Field(description="Explicit scenario assumptions")
    projected_state: OperationalKPIVector = Field(description="Simulated state resulting from intervention")
    delta: KPIDeltaVector = Field(description="Projected state - Baseline state")
    confidence: ProjectionConfidence = Field(description="Confidence / uncertainty category")
    epistemic_classification: EpistemicClassification = Field(description="Scenario provenance classification")
    evidence_basis: List[str] = Field(description="Upstream phases & records supporting transition")
    limitations: List[str] = Field(description="Explicit physical or mathematical limitations")


class ScenarioComparisonReport(BaseModel):
    """
    Comparative portfolio evaluation across multiple What-If scenarios.
    """
    model_config = ConfigDict(frozen=True)

    comparison_id: str
    generated_at: datetime
    machine_id: str
    baseline_as_of: datetime
    scenarios: List[WhatIfScenario]
    ranking_narrative: str = Field(description="Policy-based comparative narrative (no fake global optimality)")
    recommended_scenario_id: str
    governance_notice: str
