"""
NirmaanAI Operational Recommendation Models
Phase 15: Recommendation Engine

Defines strongly typed, validated Pydantic v2 schemas and enumerations supporting:
1. Closed recommendation action taxonomy (strictly 24 approved actions across 5 categories).
2. Priority and Urgency hierarchies grounded in operational reality.
3. Categorical evidence strength (STRONG, MODERATE, WEAK, INSUFFICIENT) based on 5 physical domains.
4. Epistemic provenance preservation per atomic EvidenceItem (OBSERVED, DERIVED, CONFIGURED, PROJECTED, etc.).
5. Strict distinction between observed current stock and projected post-action inventory.
6. Human-in-the-loop decision-support governance (requires_operator_verification = True).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

from src.health.health_models import HealthState


class EpistemicClassification(str, Enum):
    """
    Epistemic provenance classification for evidence and recommendations.
    Preserves transparent demarcation of physical observations vs configured policies vs projections.
    """
    OBSERVED = "OBSERVED"
    DERIVED_FROM_OBSERVED = "DERIVED_FROM_OBSERVED"
    CONFIGURED_ASSUMPTION = "CONFIGURED_ASSUMPTION"
    PROJECTED = "PROJECTED"
    PROJECTED_OPPORTUNITY_COST = "PROJECTED_OPPORTUNITY_COST"
    CONTROLLED_SYNTHETIC = "CONTROLLED_SYNTHETIC"


class RecommendationCategory(str, Enum):
    """Controlled operational recommendation categories."""
    MAINTENANCE = "MAINTENANCE"
    PRODUCTION_FLOW = "PRODUCTION_FLOW"
    INVENTORY = "INVENTORY"
    ENERGY = "ENERGY"
    MONITORING = "MONITORING"


class RecommendationAction(str, Enum):
    """
    Closed, controlled taxonomy of exactly 24 approved operational actions.
    Free-text or unapproved action strings are strictly prohibited.
    """
    # MAINTENANCE (7)
    INSPECT_SPINDLE_BEARING = "INSPECT_SPINDLE_BEARING"
    SCHEDULE_PREVENTIVE_MAINTENANCE = "SCHEDULE_PREVENTIVE_MAINTENANCE"
    REPLACE_WORN_COMPONENT = "REPLACE_WORN_COMPONENT"
    INSPECT_LUBRICATION = "INSPECT_LUBRICATION"
    REPLACE_TOOLING = "REPLACE_TOOLING"
    CALIBRATE_AXIS_ALIGNMENT = "CALIBRATE_AXIS_ALIGNMENT"
    OVERHAUL_ASSEMBLY = "OVERHAUL_ASSEMBLY"

    # PRODUCTION_FLOW (6)
    REDUCE_MACHINE_FEED_RATE = "REDUCE_MACHINE_FEED_RATE"
    RESCHEDULE_PENDING_JOBS = "RESCHEDULE_PENDING_JOBS"
    REBALANCE_LINE_WORKLOAD = "REBALANCE_LINE_WORKLOAD"
    BUFFER_DOWNSTREAM_INVENTORY = "BUFFER_DOWNSTREAM_INVENTORY"
    PAUSE_NEW_JOB_RELEASE = "PAUSE_NEW_JOB_RELEASE"
    BYPASS_TO_PARALLEL_LINE = "BYPASS_TO_PARALLEL_LINE"

    # INVENTORY (5)
    EXPEDITE_CRITICAL_SPARE = "EXPEDITE_CRITICAL_SPARE"
    TRIGGER_STANDARD_REORDER = "TRIGGER_STANDARD_REORDER"
    INCREASE_SAFETY_STOCK_BUFFER = "INCREASE_SAFETY_STOCK_BUFFER"
    MONITOR_SUPPLIER_LEAD_TIME = "MONITOR_SUPPLIER_LEAD_TIME"
    HOLD_UNNECESSARY_PROCUREMENT = "HOLD_UNNECESSARY_PROCUREMENT"

    # ENERGY (4)
    INVESTIGATE_POWER_EXCURSION = "INVESTIGATE_POWER_EXCURSION"
    SHIFT_HIGH_LOAD_OFF_PEAK = "SHIFT_HIGH_LOAD_OFF_PEAK"
    INSPECT_ELECTROMECHANICAL_DRIVE = "INSPECT_ELECTROMECHANICAL_DRIVE"
    MONITOR_IDLE_STANDBY_POWER = "MONITOR_IDLE_STANDBY_POWER"

    # MONITORING (4)
    CONTINUE_NOMINAL_MONITORING = "CONTINUE_NOMINAL_MONITORING"
    INCREASE_TELEMETRY_SAMPLING_FREQUENCY = "INCREASE_TELEMETRY_SAMPLING_FREQUENCY"
    MANDATE_OPERATOR_VISUAL_CHECK = "MANDATE_OPERATOR_VISUAL_CHECK"
    VERIFY_SENSOR_CALIBRATION = "VERIFY_SENSOR_CALIBRATION"


class RecommendationPriority(str, Enum):
    """
    Deterministic priority classification based on failure risk, health band, and operational impact.
    """
    CRITICAL = "CRITICAL"  # Severe degradation/failure evidence plus immediate operational consequence
    HIGH = "HIGH"          # Significant degradation, bottleneck, or material operational exposure
    MEDIUM = "MEDIUM"      # Moderate evidence requiring planned intervention or standard reorder
    LOW = "LOW"            # Minor drift or routine optimization opportunity (e.g. peak energy shifting)
    MONITOR = "MONITOR"    # Evidence insufficient for physical intervention; continue tracking


class ActionUrgency(str, Enum):
    """
    Operational execution timeline separated from priority.
    """
    IMMEDIATE = "IMMEDIATE"            # Intervene within current shift / immediate machine halt
    SAME_DAY = "SAME_DAY"              # Intervene within current production day
    NEXT_SHIFT = "NEXT_SHIFT"          # Handoff to upcoming shift maintenance crew
    SCHEDULED_MAINT = "SCHEDULED_MAINT"# Align with next scheduled routine maintenance window
    ROUTINE = "ROUTINE"                # Standard operational cadence


class EvidenceStrength(str, Enum):
    """
    Categorical evidence strength grounded in cross-domain corroboration across 5 physical domains.
    Financial exposure is impact context and NOT a corroborating physical evidence domain.
    """
    STRONG = "STRONG"              # Corroborated across >= 3 distinct physical/operational domains
    MODERATE = "MODERATE"          # Corroborated across 2 distinct physical/operational domains
    WEAK = "WEAK"                  # Present in 1 isolated operational domain
    INSUFFICIENT = "INSUFFICIENT"  # Sub-threshold or contradictory evidence


class EvidenceDomain(str, Enum):
    """
    The 5 genuine physical and operational evidence domains.
    Finance is strictly excluded from physical corroboration.
    """
    TELEMETRY_ANOMALY = "TELEMETRY_ANOMALY"    # Phase 7 PCA anomaly & raw sensor telemetry
    PREDICTIVE_FAILURE = "PREDICTIVE_FAILURE"  # Phase 6 XGBoost failure prob & C-MAPSS RUL cycles
    PRODUCTION_FLOW = "PRODUCTION_FLOW"        # Phase 8 Bottleneck event target, cycle ratio & delays
    DIAGNOSTIC_RCA = "DIAGNOSTIC_RCA"          # Phase 12 RCA candidate causes & temporal precedence
    INVENTORY_SPARE = "INVENTORY_SPARE"        # Phase 10 Stock levels & replenishment constraints


class EvidenceItem(BaseModel):
    """
    Atomic, auditable evidence item preserving its individual epistemic provenance.
    """
    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(description="Deterministic evidence identifier, e.g. EVID_P06_FAIL_M2")
    source_phase: str = Field(description="Upstream phase identifier, e.g. 'Phase 6'")
    source_module: str = Field(description="Generating component or model, e.g. 'XGBoostFailureClassifier'")
    domain: EvidenceDomain = Field(description="One of the 5 genuine physical/operational domains")
    metric: str = Field(description="Specific metric name, e.g. 'failure_probability', 'reconstruction_error'")
    value: Union[float, int, str, bool] = Field(description="Observed or derived metric value")
    unit: Optional[str] = Field(None, description="Physical or analytical unit, e.g. 'mms', 'cycles', 'min'")
    threshold_applied: Optional[Union[float, str]] = Field(None, description="Locked upstream threshold applied")
    timestamp: datetime = Field(description="UTC timestamp of the observation or evaluation")
    machine_id: str = Field(description="Target machine asset identifier (e.g. M1 to M5)")
    interpretation: str = Field(description="Domain-grounded interpretation of this evidence")
    epistemic_classification: EpistemicClassification = Field(description="Atomic epistemic provenance")


class InventoryEvidenceContext(BaseModel):
    """
    Explicitly distinguishes directly observed on-hand stock from projected post-action stock.
    Never reports a projected post-action stockout as a current stockout.
    """
    model_config = ConfigDict(frozen=True)

    sku_id: str = Field(description="Part or component SKU identifier")
    observed_current_stock: float = Field(description="Directly observed on-hand stock (e.g. 2.0)")
    safety_stock: float = Field(description="Configured safety stock threshold (e.g. 1.134)")
    reorder_point: float = Field(description="Configured reorder point (e.g. 1.367)")
    supplier_lead_time_days: float = Field(description="Supplier replenishment lead time (e.g. 7.0 days)")
    is_current_stock_below_safety: bool = Field(False, description="Must be False when current stock >= safety stock")
    hypothetical_consumption_units: float = Field(0.0, description="Units consumed if maintenance executed (e.g. 1.0)")
    projected_post_action_stock: float = Field(description="Projected on-hand stock after action (e.g. 1.0)")
    is_projected_stock_below_safety: bool = Field(False, description="True if projected stock < safety stock")
    epistemic_classification: EpistemicClassification = Field(
        default=EpistemicClassification.CONFIGURED_ASSUMPTION,
        description="Provenance of the inventory policy parameters"
    )


class FinancialEvidenceContext(BaseModel):
    """
    Contextual economic figures from Phase 14.
    Used strictly as decision support context, NEVER as an independent physical evidence domain.
    """
    model_config = ConfigDict(frozen=True)

    realized_loss_inr: float = Field(description="Traceable realized operational loss from Phase 14")
    gross_exposure_inr: float = Field(description="Gross financial exposure (realized + opportunity cost)")
    projected_opportunity_cost_inr: float = Field(0.0, description="Projected bottleneck opportunity cost")
    is_material_exposure: bool = Field(False, description="True if gross exposure exceeds Phase 15 threshold")
    materiality_threshold_inr: float = Field(25000.0, description="Configured Phase 15 decision-support threshold")
    epistemic_classification: EpistemicClassification = Field(
        default=EpistemicClassification.DERIVED_FROM_OBSERVED,
        description="Phase 14 financial provenance"
    )


class OperationalRecommendation(BaseModel):
    """
    Complete, auditable decision-support recommendation object.
    """
    model_config = ConfigDict(frozen=True)

    recommendation_id: str = Field(description="Deterministic recommendation ID, e.g. REC_M2_MAINT_001")
    timestamp: datetime = Field(description="UTC timestamp of recommendation generation")
    machine_id: str = Field(description="Target asset identifier (M1-M5 or FACTORY)")
    category: RecommendationCategory = Field(description="Operational category")
    action: RecommendationAction = Field(description="Closed taxonomy action")
    priority: RecommendationPriority = Field(description="Grounded priority level")
    urgency: ActionUrgency = Field(description="Action timeline")
    evidence_strength: EvidenceStrength = Field(description="Categorical strength across 5 physical domains")
    reason: str = Field(description="Diagnostic justification citing explicit evidence")
    evidence: List[EvidenceItem] = Field(description="Atomic supporting evidence items with provenance")
    source_phases: List[str] = Field(description="Distinct upstream phase identifiers, e.g. ['Phase 6', 'Phase 7']")
    operational_impact: str = Field(description="Operational consequence if unaddressed")
    financial_context: Optional[FinancialEvidenceContext] = Field(None, description="Phase 14 financial context")
    inventory_context: Optional[InventoryEvidenceContext] = Field(None, description="Phase 10 inventory state & projection")
    expected_benefit: str = Field(description="Qualitative expected benefit (no guaranteed savings claims)")
    requires_operator_verification: bool = Field(True, description="Strict human-in-the-loop decision-support governance")
    rule_id: Optional[str] = Field(None, description="Triggering rule identifier(s), e.g. 'R-M01'")
    epistemic_classification: EpistemicClassification = Field(description="Overall recommendation provenance classification")
