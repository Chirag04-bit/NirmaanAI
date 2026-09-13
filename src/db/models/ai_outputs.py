"""
NirmaanAI AI & Decision Persistence Models
Defines PostgreSQL tables for AI outputs from Phases 6 to 16:
- Predictive Maintenance (Phase 6)
- Anomaly Detection (Phase 7)
- Bottleneck Prediction (Phase 8)
- Time-Series Forecasting (Phase 9)
- Model Explainability & SHAP (Phase 11)
- Root Cause Analysis (Phase 12)
- Factory Health Score (Phase 13)
- Financial Loss Accounting (Phase 14)
- Operational Recommendations (Phase 15)
- Digital Twin Simulation Scenarios (Phase 16)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, ProvenanceMixin, TimestampMixin, utcnow


class PredictiveMaintenancePrediction(Base, ProvenanceMixin, TimestampMixin):
    """Phase 6 Predictive Maintenance failure predictions with locked 0.91 threshold."""
    __tablename__ = "ai_pdm_predictions"

    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    prediction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    failure_probability: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_class: Mapped[int] = mapped_column(Integer, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.91)

    __table_args__ = (
        CheckConstraint("failure_probability >= 0.0 AND failure_probability <= 1.0", name="chk_pdm_prob_range"),
        CheckConstraint("prediction_class IN (0, 1)", name="chk_pdm_class_binary"),
        Index("idx_pdm_machine_time", "machine_id", "prediction_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<PdMPrediction {self.machine_id}: p={self.failure_probability:.4f} class={self.prediction_class}>"


class AnomalyDetectionResult(Base, ProvenanceMixin, TimestampMixin):
    """Phase 7 Anomaly detection results with locked PCA threshold 0.24050."""
    __tablename__ = "ai_anomaly_results"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.24050)
    detector_name: Mapped[str] = mapped_column(String(100), nullable=False, default="pca_detector")
    anomaly_status: Mapped[str] = mapped_column(String(30), nullable=False, default="NORMAL")

    __table_args__ = (
        Index("idx_anomaly_machine_time", "machine_id", "timestamp"),
        Index("idx_anomaly_status", "anomaly_status"),
    )

    def __repr__(self) -> str:
        return f"<AnomalyResult {self.machine_id}: score={self.anomaly_score:.4f} ({self.anomaly_status})>"


class BottleneckPredictionResult(Base, ProvenanceMixin, TimestampMixin):
    """Phase 8 Bottleneck prediction results."""
    __tablename__ = "ai_bottleneck_results"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    bottleneck_status: Mapped[str] = mapped_column(String(30), nullable=False, default="NORMAL")
    bottleneck_probability: Mapped[float] = mapped_column(Float, nullable=False)
    target_metric: Mapped[str] = mapped_column(String(100), nullable=False, default="cycle_time_deviation")

    __table_args__ = (
        Index("idx_bottleneck_machine_time", "machine_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<BottleneckResult {self.machine_id}: prob={self.bottleneck_probability:.4f} status={self.bottleneck_status}>"


class ForecastingResult(Base, ProvenanceMixin, TimestampMixin):
    """Phase 9 Multi-horizon production and energy forecasts."""
    __tablename__ = "ai_forecasting_results"

    forecast_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_series: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    forecast_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    horizon_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("idx_forecast_series_time", "target_series", "forecast_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Forecast {self.target_series} @ {self.forecast_timestamp}: pred={self.predicted_value:.2f}>"


class ShapExplanation(Base, TimestampMixin):
    """Phase 11 Normalized SHAP local and global feature attribution explanations."""
    __tablename__ = "ai_shap_explanations"

    explanation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prediction_ref_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    shap_value: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    context_type: Mapped[str] = mapped_column(String(20), nullable=False, default="LOCAL")
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, default="xgboost")
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="champion_v1")
    as_of_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_shap_machine_rank", "machine_id", "ranking"),
        Index("idx_shap_ref", "prediction_ref_id"),
    )

    def __repr__(self) -> str:
        return f"<ShapExplanation {self.machine_id} rank={self.ranking}: {self.feature_name}={self.shap_value:+.4f}>"


class RcaResult(Base, ProvenanceMixin, TimestampMixin):
    """Phase 12 Structured Root Cause Analysis findings."""
    __tablename__ = "ai_rca_results"

    rca_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    primary_cause: Mapped[str] = mapped_column(String(150), nullable=False)
    cause_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    evidence_strength: Mapped[str] = mapped_column(String(30), nullable=False)
    evidence_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_rca_machine_time", "machine_id", "event_timestamp"),
    )

    def __repr__(self) -> str:
        return f"<RcaResult {self.rca_id}: {self.machine_id} -> {self.primary_cause}>"


class FactoryHealthScore(Base, ProvenanceMixin, TimestampMixin):
    """
    Phase 13 Factory and Machine Health scores.
    Locked Bands:
    90-100: EXCELLENT
    75-89: HEALTHY
    60-74: WATCH
    40-59: DEGRADED
    0-39: CRITICAL
    """
    __tablename__ = "ai_factory_health_scores"

    health_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=True, index=True
    )
    factory_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("factories.factory_id", ondelete="CASCADE"), nullable=True, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    health_state: Mapped[str] = mapped_column(String(30), nullable=False)
    coverage_pct: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    vibration_health: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    temperature_health: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    cycle_efficiency_health: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    maintenance_health: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    diagnostic_modifier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    __table_args__ = (
        CheckConstraint("health_score >= 0.0 AND health_score <= 100.0", name="chk_health_score_range"),
        Index("idx_health_machine_time", "machine_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<HealthScore {self.machine_id}: {self.health_score:.2f} ({self.health_state})>"


class FinancialLossRecord(Base, ProvenanceMixin, TimestampMixin):
    """
    Phase 14 Financial Loss Records.
    Maintains strict separation between:
    - REALIZED_LOSS (actual cost incurred)
    - PROJECTED_OPPORTUNITY_COST (unrealized theoretical capacity ceiling)
    - PROJECTED_BENEFIT (counterfactual service savings)
    - GROSS_EXPOSURE (combined reference scope)
    """
    __tablename__ = "finance_loss_records"

    loss_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    loss_type: Mapped[str] = mapped_column(String(50), nullable=False)
    downtime_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    downtime_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    scrap_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rework_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    emergency_labor_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    energy_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    opportunity_cost_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_loss_inr: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("idx_loss_machine_type", "machine_id", "loss_type"),
        Index("idx_loss_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<FinancialLossRecord {self.machine_id} {self.loss_type}: ₹{self.total_loss_inr:,.2f}>"


class OperationalRecommendation(Base, TimestampMixin):
    """
    Phase 15 Evidence-grounded operational recommendations.
    Strictly preserves the closed 26-action taxonomy.
    """
    __tablename__ = "ai_recommendations"

    recommendation_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence_strength: Mapped[str] = mapped_column(String(20), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_references: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    as_of_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[str] = mapped_column(String(60), nullable=False, default="RULE_DERIVED")

    __table_args__ = (
        Index("idx_rec_machine_priority", "machine_id", "priority"),
        Index("idx_rec_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Recommendation {self.recommendation_id}: {self.action} on {self.machine_id} ({self.priority})>"


class SimulationScenario(Base, TimestampMixin):
    """
    Phase 16 Digital-Twin-Inspired What-If Simulation Scenarios.
    Enforces strict temporal counterfactual semantics:
    - decision_cutoff is fixed at 2026-01-21T12:00:00Z.
    - Day-22 MAINT_0003 is evaluated retrospectively as RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.
    - Unsupported causal intervention KPIs remain NOT_PROJECTABLE.
    - Fully normalized queryable columns for baseline, intervention, and financial outcomes.
    """
    __tablename__ = "simulation_scenarios"

    scenario_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_name: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_cutoff: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # 1. Baseline State at Decision Cutoff (<= 2026-01-21T12:00:00Z)
    baseline_downtime_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    baseline_failure_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.9959)
    baseline_anomaly_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.35)
    baseline_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=26.88)
    baseline_realized_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=73062.28)
    baseline_gross_exposure_inr: Mapped[float] = mapped_column(Float, nullable=False, default=97382.28)

    # 2. Operational Scenario Execution
    planned_service_downtime_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_avoided_downtime_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # 3. Normalized Financial Projections
    avoided_downtime_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avoided_emergency_labor_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    projected_avoided_breakdown_loss_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    planned_service_cost_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_counterfactual_benefit_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    remaining_gross_exposure_inr: Mapped[float] = mapped_column(Float, nullable=False, default=97382.28)

    # 4. Diagnostic KPI Governance (NOT_PROJECTABLE under Intervention)
    projected_failure_probability: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_PROJECTABLE")
    projected_anomaly_score: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_PROJECTABLE")
    projected_health_score: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_PROJECTABLE")
    projected_health_state: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_PROJECTABLE")

    # 5. Metadata, Provenance, & Full Serialized Payloads
    temporal_semantics: Mapped[str] = mapped_column(
        String(60), nullable=False, default="COUNTERFACTUAL_EVALUATION"
    )
    epistemic_status: Mapped[str] = mapped_column(
        String(60), nullable=False, default="HYPOTHETICAL_COUNTERFACTUAL"
    )
    diagnostic_kpi_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="NOT_PROJECTABLE"
    )
    provenance: Mapped[str] = mapped_column(
        String(60), nullable=False, default="COUNTERFACTUAL_PROJECTION"
    )
    intervention_list: Mapped[str] = mapped_column(Text, nullable=False)
    projected_metrics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    financial_projection: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    configured_assumptions: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("idx_sim_machine_cutoff", "machine_id", "decision_cutoff"),
        Index("idx_sim_net_benefit", "net_counterfactual_benefit_inr"),
    )

    def __repr__(self) -> str:
        return f"<SimulationScenario {self.scenario_id}: {self.scenario_name} on {self.machine_id} (Benefit: ₹{self.net_counterfactual_benefit_inr:,.2f})>"
