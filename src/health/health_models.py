"""
NirmaanAI Factory Health Score — Data Models & Schemas
Phase 13: Factory Health Score

Strictly typed, validated Pydantic v2 models representing machine-level and
plant-level analytical health scores, evidence coverage, dimension breakdowns,
and human-interpretable diagnostic narratives.

SCIENTIFIC INTEGRITY:
- Health scores are bounded analytical indicators in [0, 100], NOT probabilities.
- Confidence is separated from health status.
- Prevents double counting of SHAP (already represented in Failure Risk) and RCA
  (treated as a diagnostic severity modifier, not duplicate telemetry).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class HealthState(str, Enum):
    """Configured operational health bands."""
    EXCELLENT = "EXCELLENT"        # 90.0 - 100.0
    HEALTHY = "HEALTHY"            # 75.0 - 89.9
    WATCH = "WATCH"                # 60.0 - 74.9
    DEGRADED = "DEGRADED"          # 40.0 - 59.9
    CRITICAL = "CRITICAL"          # 0.0 - 39.9
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"  # Coverage < 40% override


class HealthAssessmentConfidence(str, Enum):
    """Evidence completeness & consistency confidence level."""
    HIGH = "HIGH"                  # Coverage >= 80% with signal agreement
    MEDIUM = "MEDIUM"              # Coverage 50% - 79%
    LOW = "LOW"                    # Coverage < 50% or conflicting signals


class EvidenceCoverageStatus(str, Enum):
    """Categorical evidence coverage state."""
    FULL_EVIDENCE = "FULL_EVIDENCE"          # Coverage == 100%
    PARTIAL_EVIDENCE = "PARTIAL_EVIDENCE"    # 40% <= Coverage < 100%
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"  # Coverage < 40%


class HealthDimensionType(str, Enum):
    """Six core operational health dimensions."""
    FAILURE_RISK = "FAILURE_RISK"
    ANOMALY_HEALTH = "ANOMALY_HEALTH"
    FLOW_HEALTH = "FLOW_HEALTH"
    ENERGY_HEALTH = "ENERGY_HEALTH"
    MAINTENANCE_CONTEXT = "MAINTENANCE_CONTEXT"
    DIAGNOSTIC_CONSISTENCY = "DIAGNOSTIC_CONSISTENCY"


class DimensionScoreBreakdown(BaseModel):
    """Detailed score breakdown for an individual health dimension."""
    dimension: HealthDimensionType
    display_name: str
    raw_value: Optional[float] = None
    normalized_score: float = Field(
        ..., ge=0.0, le=100.0, description="Bounded dimension health score in [0.0, 100.0]"
    )
    configured_weight: float = Field(..., ge=0.0, le=1.0)
    effective_weight: float = Field(..., ge=0.0, le=1.0)
    weighted_contribution: float = Field(..., ge=0.0, le=100.0)
    penalty_points: float = Field(default=0.0, ge=0.0, description="Deduction from 100 (100 - score)")
    is_available: bool = Field(default=True)
    description: str = Field(..., description="Human-readable engineering rationale")

    @property
    def raw_score(self) -> float:
        return self.normalized_score

    @property
    def dimension_name(self) -> str:
        return self.dimension.value


class HealthEvidenceContext(BaseModel):
    """Input evidence bundle for a machine at a specific point in time."""
    machine_id: str
    timestamp: str = Field(..., description="ISO 8601 evaluation timestamp")
    
    # Phase 6 Predictive Maintenance
    prediction_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    prediction_threshold: float = Field(default=0.910)
    
    # Phase 7 Anomaly Detection
    anomaly_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    anomaly_threshold: float = Field(default=0.2405)
    
    # Phase 8 Flow Intelligence
    cycle_time_sec: Optional[float] = Field(default=None, ge=0.0)
    design_cycle_time_sec: Optional[float] = Field(default=None, gt=0.0)
    cycle_ratio: Optional[float] = Field(default=None, ge=0.0)
    bottleneck_state: Optional[str] = Field(default=None)  # NOMINAL, MODERATE, CRITICAL
    dispatch_delay_min: Optional[float] = Field(default=None, ge=0.0)
    
    # Phase 9 Energy Forecasting
    power_consumption_kw: Optional[float] = Field(default=None, ge=0.0)
    baseline_power_kw: Optional[float] = Field(default=None, ge=0.0)
    forecast_residual_kw: Optional[float] = Field(default=None)
    
    # Phase 10 Maintenance & Spare Inventory
    spare_stock_level: Optional[int] = Field(default=None, ge=0)
    spare_safety_stock: Optional[int] = Field(default=None, ge=0)
    days_of_supply: Optional[float] = Field(default=None, ge=0.0)
    is_maintenance_overdue: Optional[bool] = Field(default=None)
    hours_since_last_maintenance: Optional[float] = Field(default=None, ge=0.0)
    
    # Phase 12 Root Cause Analysis Context (Diagnostic Severity Modifier)
    active_rca_severity: Optional[str] = Field(default=None)  # WARNING, CRITICAL, EMERGENCY
    active_rca_confidence: Optional[str] = Field(default=None)  # HIGH, MEDIUM, LOW, INSUFFICIENT_EVIDENCE
    has_active_unresolved_rca: bool = Field(default=False)
    
    # Optional SHAP contributions (AUDIT ONLY: strictly excluded from score calculation to avoid double counting)
    shap_contributions: Optional[Dict[str, float]] = Field(default_factory=dict)
    
    # Scenario flag
    is_synthetic_scenario: bool = Field(default=False)


class MachineHealthScore(BaseModel):
    """Complete machine-level health assessment."""
    machine_id: str
    timestamp: str
    health_score: float = Field(..., ge=0.0, le=100.0)
    state: HealthState
    confidence: HealthAssessmentConfidence
    evidence_coverage_pct: float = Field(..., ge=0.0, le=100.0)
    coverage_status: EvidenceCoverageStatus
    dimension_breakdowns: List[DimensionScoreBreakdown]
    top_degraders: List[str] = Field(default_factory=list)
    explanation_narrative: str
    limitations: List[str] = Field(default_factory=list)
    causality_disclaimer: str = Field(
        default=(
            "SCIENTIFIC HEALTH DISCLAIMER: The Factory Health Score is an analytical decision-support "
            "indicator reflecting empirical cross-signal alignment. It is NOT a probability of failure, "
            "a clinical diagnosis, or proof of physical machine causality."
        )
    )


class FactoryHealthScore(BaseModel):
    """Aggregated plant-level health assessment across all active machines."""
    timestamp: str
    factory_health_score: float = Field(..., ge=0.0, le=100.0)
    state: HealthState
    confidence: HealthAssessmentConfidence
    evidence_coverage_pct: float = Field(..., ge=0.0, le=100.0)
    coverage_status: EvidenceCoverageStatus
    machine_scores: Dict[str, MachineHealthScore]
    critical_machine_id: str
    critical_machine_score: float = Field(..., ge=0.0, le=100.0)
    critical_machine_alert: bool = Field(default=False)
    critical_alert_message: Optional[str] = None
    machine_weights: Dict[str, float] = Field(default_factory=dict)
    aggregation_method: str = Field(
        default="Equal Baseline Weighting (0.20 per machine) with Critical-Machine Constraint Alert"
    )
    limitations: List[str] = Field(default_factory=list)
    causality_disclaimer: str = Field(
        default=(
            "SCIENTIFIC HEALTH DISCLAIMER: The Factory Health Score is an analytical decision-support "
            "indicator reflecting empirical cross-signal alignment. It is NOT a probability of failure, "
            "a clinical diagnosis, or proof of physical machine causality."
        )
    )


class HealthTrendPoint(BaseModel):
    """Historical time-series point for health trend analysis."""
    timestamp: str
    machine_id: str
    health_score: float = Field(..., ge=0.0, le=100.0)
    state: HealthState
    is_post_maintenance_recovery: bool = Field(default=False)

    @property
    def score(self) -> float:
        return self.health_score

