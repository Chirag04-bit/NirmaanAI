"""
NirmaanAI Root Cause Analysis (RCA) — Data Models & Schemas
Phase 12: Root Cause Analysis

Strictly typed, validated Pydantic v2 schemas for Root Cause Analysis:
- Ingestion contexts (predictions, anomaly scores, telemetry, flow, maintenance, spares)
- Multi-source signal evidence representations
- Temporal sequence steps
- Candidate cause evaluation and ranking
- Human-interpretable RCA reports with mandatory scientific disclaimers.

RESEARCH INTEGRITY:
- Strict prohibition of causal probability claims (e.g. no "87% probability of causation").
- Confidence categories represent evidence strength, not probability of physical causation.
- Clear separation between controlled synthetic demonstrations and empirical model evaluations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class RCAConfidenceLevel(str, Enum):
    """Categorical evidence confidence levels (not physical probabilities)."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EvidenceSourceType(str, Enum):
    """Source domain of individual evidence signals."""
    SHAP_MODEL_ATTRIBUTION = "SHAP_MODEL_ATTRIBUTION"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    MACHINE_TELEMETRY = "MACHINE_TELEMETRY"
    OPERATIONAL_FLOW = "OPERATIONAL_FLOW"
    MAINTENANCE_LOG = "MAINTENANCE_LOG"
    INVENTORY_SPARE = "INVENTORY_SPARE"
    ENERGY_LOAD = "ENERGY_LOAD"


class SignalEvidenceItem(BaseModel):
    """Individual normalized evidence signal supporting or penalizing a candidate cause."""
    signal_name: str = Field(..., description="Canonical signal identifier")
    source: EvidenceSourceType = Field(..., description="Originating domain source")
    observed_value: float = Field(..., description="Observed numerical value")
    baseline_value: Optional[float] = Field(default=None, description="Nominal machine baseline reference")
    normalized_evidence: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized evidence magnitude in [0.0, 1.0]"
    )
    direction: str = Field(default="ELEVATED", description="Deviation direction (ELEVATED, DEPRESSED, NOMINAL)")
    is_corroborating: bool = Field(default=True, description="True if signal supports the hypothesis")
    is_contradictory: bool = Field(default=False, description="True if signal contradicts the hypothesis")
    description: str = Field(..., description="Human-readable domain interpretation of signal")


class TemporalStage(str, Enum):
    """Standard temporal progression stages without lookahead leakage."""
    T0_PRECURSOR = "t0_precursor"
    T1_ESCALATION = "t1_escalation"
    T2_CONSEQUENCE = "t2_consequence"
    T3_EVENT = "t3_event"


class TemporalStep(BaseModel):
    """A chronologically verified observation step in the event progression."""
    stage: TemporalStage
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    signal_name: str
    observed_value: float
    description: str


class CandidateCauseScore(BaseModel):
    """Evaluated candidate cause with composite evidence score and contributing signals."""
    cause_category: str = Field(..., description="Controlled taxonomy category")
    display_name: str = Field(..., description="Human-readable category title")
    rank: int = Field(..., ge=1, description="Ranking ordinal (1 = primary candidate)")
    composite_score: float = Field(
        ..., ge=0.0, le=1.0, description="Configured analytical evidence score in [0.0, 1.0]"
    )
    supporting_signals: List[SignalEvidenceItem] = Field(default_factory=list)
    contradictory_signals: List[SignalEvidenceItem] = Field(default_factory=list)
    investigation_suggestion: str = Field(..., description="Recommended diagnostic next step")
    summary: str = Field(..., description="Evidence-grounded rationale for this candidate")


class RCAEventContext(BaseModel):
    """Input context representing an event subjected to Root Cause Analysis."""
    event_id: str = Field(..., description="Unique event identifier, e.g., EVT_2026_M2_001")
    timestamp: str = Field(..., description="Event timestamp in ISO 8601 format")
    machine_id: str = Field(..., description="Machine identifier, e.g., M2, MC_001")
    event_type: str = Field(
        default="PREDICTED_DEGRADATION",
        description="Event category: PREDICTED_DEGRADATION, ANOMALY_ALERT, BOTTLENECK_ESCALATION, UNPLANNED_STOP"
    )
    severity: str = Field(default="CRITICAL", description="Severity level: WARNING, CRITICAL, EMERGENCY")
    observed_outcome: str = Field(
        default="Telemetry excursion with elevated failure risk",
        description="Observable real-world manifestation"
    )
    
    # Model & Detector signals
    prediction_probability: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Phase 6 failure classifier probability"
    )
    prediction_threshold: float = Field(default=0.91, description="Approved decision threshold tau")
    anomaly_score: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Phase 7 multi-sensor anomaly score"
    )
    anomaly_threshold: float = Field(default=0.2405, description="Phase 7 calibrated anomaly threshold")
    
    # Bottleneck & Operational flow context
    bottleneck_state: Optional[str] = Field(
        default=None, description="Phase 8 bottleneck state: NOMINAL, MODERATE, CRITICAL"
    )
    cycle_time_sec: Optional[float] = Field(default=None, ge=0.0, description="Measured unit cycle time")
    cycle_ratio: Optional[float] = Field(default=None, ge=0.0, description="Measured cycle time / design cycle time")
    dispatch_delay_min: Optional[float] = Field(default=None, ge=0.0, description="Queue / dispatch delay")
    
    # Telemetry snapshot at event point
    telemetry: Dict[str, float] = Field(
        default_factory=dict, description="Current sensor readings dictionary"
    )
    
    # Local SHAP feature contributions (from Phase 11)
    shap_contributions: Dict[str, float] = Field(
        default_factory=dict, description="Feature -> SHAP attribution in margin space"
    )
    
    # Historical telemetry sequence prior to event (for temporal precedence evaluation)
    historical_telemetry: List[Dict[str, Any]] = Field(
        default_factory=list, description="Chronological sensor readings before event timestamp"
    )
    
    # Maintenance and spare inventory context
    maintenance_state: Optional[Dict[str, Any]] = Field(
        default=None, description="Recent maintenance records and elapsed hours"
    )
    spare_state: Optional[Dict[str, Any]] = Field(
        default=None, description="Coupled critical spare stock, lead time, and shortage risk"
    )
    
    # Scenario metadata
    is_synthetic_scenario: bool = Field(
        default=False, description="True if originating from synthetic factory digital twin"
    )


class RCAReportResponse(BaseModel):
    """Comprehensive, deterministic Root Cause Analysis report."""
    event_id: str
    timestamp: str
    machine_id: str
    event_type: str
    severity: str
    observed_outcome: str
    scenario_type: str = Field(
        default="EMPIRICAL MODEL ATTRIBUTION",
        description="Explicit label: 'CONTROLLED SYNTHETIC SCENARIO' vs 'EMPIRICAL BENCHMARK'"
    )
    
    # Model attribution & detection summary
    prediction_probability: Optional[float]
    anomaly_score: Optional[float]
    bottleneck_state: Optional[str]
    
    # Core RCA findings
    primary_candidate: CandidateCauseScore
    secondary_candidates: List[CandidateCauseScore] = Field(default_factory=list)
    confidence: RCAConfidenceLevel
    confidence_rationale: str
    
    # Supporting evidence breakdown
    top_contributors: List[SignalEvidenceItem] = Field(default_factory=list)
    contradictory_evidence: List[SignalEvidenceItem] = Field(default_factory=list)
    
    # Temporal precedence reconstruction
    temporal_chain: List[TemporalStep] = Field(default_factory=list)
    temporal_precedence_verified: bool = Field(default=False)
    
    # Next investigation (operational diagnostics, NOT automated procurement/scheduling)
    recommended_next_investigation: List[str] = Field(default_factory=list)
    
    # Scientific integrity disclosures
    interpretation: str
    limitations: List[str] = Field(default_factory=list)
    causality_disclaimer: str = Field(
        default=(
            "SCIENTIFIC CAUSALITY NOTICE: This Root Cause Analysis establishes operational "
            "and temporal consistency among available signals. It does NOT prove physical causality. "
            "Calculated evidence scores represent configured analytical weights, not probabilities "
            "of physical causation."
        )
    )
