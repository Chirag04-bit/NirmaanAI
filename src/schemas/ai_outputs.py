"""
NirmaanAI Subsystem AI Output Schemas (Pydantic v2)
Covers Phase 6, 7, 8, 9, 11, 12, 13 subsystems.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictiveMaintenanceResponse(BaseModel):
    """Phase 6 Predictive Maintenance failure prediction."""
    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    machine_id: str
    prediction_timestamp: datetime
    failure_probability: float = Field(description="Model failure probability [0-1].")
    prediction_class: int = Field(description="Binary alert classification (0 or 1).")
    threshold: float = Field(default=0.91, description="Operational decision threshold (0.91).")
    predicted_failure_mode: Optional[str] = None
    rul_cycles_estimate: Optional[float] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None


class AnomalyDetectionResponse(BaseModel):
    """Phase 7 Multi-Sensor PCA Anomaly Detection result."""
    model_config = ConfigDict(from_attributes=True)

    result_id: int
    machine_id: str
    timestamp: datetime
    anomaly_score: float = Field(description="Normalized PCA reconstruction error.")
    threshold: float = Field(default=0.24050, description="Calibrated PCA threshold.")
    anomaly_status: str = Field(description="NORMAL or ANOMALOUS.")
    detector_name: Optional[str] = None
    top_contributing_features: Optional[str] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None


class BottleneckResponse(BaseModel):
    """
    Phase 8 Production Bottleneck & Flow prediction.
    Preserves authoritative target: 1 iff (cycle_ratio >= 1.20 OR start_delay >= 10 OR status == DELAYED).
    """
    model_config = ConfigDict(from_attributes=True)

    result_id: int
    machine_id: str
    job_id: Optional[str] = None
    timestamp: datetime
    bottleneck_status: str = Field(description="NOMINAL_FLOW, MODERATE_CONGESTION, or BOTTLENECK.")
    bottleneck_probability: float
    target_metric: Optional[str] = None
    cycle_time_ratio: Optional[float] = None
    dispatch_delay_minutes: Optional[float] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None


class ForecastingResponse(BaseModel):
    """Phase 9 Production and Grid Energy forecasting result."""
    model_config = ConfigDict(from_attributes=True)

    forecast_id: int
    target_series: str = Field(description="production_volume, power_consumption_kw, electricity_cost_inr.")
    forecast_timestamp: datetime
    horizon_hours: int
    predicted_value: float
    actual_value: Optional[float] = None
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    model_name: Optional[str] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None


class ShapExplanationResponse(BaseModel):
    """Phase 11 Explainable AI TreeExplainer feature attribution."""
    model_config = ConfigDict(from_attributes=True)

    explanation_id: int
    prediction_ref_id: Optional[str] = None
    machine_id: str
    feature_name: str
    feature_value: float
    shap_value: float
    ranking: int
    context_type: Optional[str] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None


class RcaResultResponse(BaseModel):
    """Phase 12 Root Cause Analysis diagnostic finding."""
    model_config = ConfigDict(from_attributes=True)

    rca_id: str
    machine_id: str
    event_timestamp: datetime
    primary_cause: str
    cause_score: float
    secondary_cause: Optional[str] = None
    severity: str
    evidence_strength: str
    evidence_details: Optional[str] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None


class FactoryHealthScoreResponse(BaseModel):
    """
    Phase 13 Composite Machine/Factory Health Index.
    Preserves authoritative bands:
    EXCELLENT (90-100), HEALTHY (75-89), WATCH (60-74), DEGRADED (40-59), CRITICAL (0-39).
    """
    model_config = ConfigDict(from_attributes=True)

    health_id: int
    machine_id: Optional[str] = None
    factory_id: Optional[str] = None
    timestamp: datetime
    health_score: float = Field(description="Composite health score [0-100].")
    health_state: str = Field(description="EXCELLENT, HEALTHY, WATCH, DEGRADED, CRITICAL.")
    coverage_pct: float
    vibration_health: Optional[float] = None
    temperature_health: Optional[float] = None
    cycle_efficiency_health: Optional[float] = None
    maintenance_health: Optional[float] = None
    diagnostic_modifier: Optional[float] = None
    source: Optional[str] = None
    as_of_timestamp: Optional[datetime] = None
    provenance: Optional[str] = None
    epistemic_status: Optional[str] = None
