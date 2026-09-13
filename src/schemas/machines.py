"""
NirmaanAI Machine Schemas (Pydantic v2)
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import ResponseMetadata


class MachineResponse(BaseModel):
    """Core machine representation with physical baselines."""
    model_config = ConfigDict(from_attributes=True)

    machine_id: str
    factory_id: str
    machine_code: str
    machine_name: str
    machine_type: str
    station: Optional[str] = None
    line_number: Optional[int] = None
    status: str
    design_cycle_time_sec: Optional[float] = None
    baseline_power_kw: Optional[float] = None
    baseline_vibration_mms: Optional[float] = None
    alert_vibration_mms: Optional[float] = None
    critical_vibration_mms: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MachineOverviewResponse(BaseModel):
    """
    Synthesized machine state explicitly separating:
    - OBSERVED (physical telemetry baselines, maintenance history)
    - MODEL_INFERENCE (PdM probability, anomaly score, bottleneck state)
    - COMPOSITE_INDEX (Health score, health band)
    - COUNTERFACTUAL (What-If simulated intervention status)
    """
    model_config = ConfigDict(from_attributes=True)

    machine_id: str
    machine_name: str
    machine_type: str
    status: str

    # 1. Observed State
    station: Optional[str] = None
    design_cycle_time_sec: Optional[float] = None
    baseline_vibration_mms: Optional[float] = None
    alert_vibration_mms: Optional[float] = None
    critical_vibration_mms: Optional[float] = None

    # 2. Model Inference State
    failure_probability: Optional[float] = Field(default=None, description="Phase 6 failure probability [0-1].")
    pdm_threshold: float = Field(default=0.91, description="Operational decision threshold.")
    pdm_alert: bool = Field(default=False, description="True if failure_probability >= pdm_threshold.")
    anomaly_score: Optional[float] = Field(default=None, description="Phase 7 PCA anomaly reconstruction error.")
    anomaly_threshold: float = Field(default=0.24050, description="PCA anomaly threshold.")
    anomaly_status: Optional[str] = Field(default=None, description="NORMAL or ANOMALOUS.")
    bottleneck_status: Optional[str] = Field(default=None, description="NOMINAL_FLOW or BOTTLENECK.")

    # 3. Composite Health State
    health_score: Optional[float] = Field(default=None, description="Phase 13 composite health index [0-100].")
    health_state: Optional[str] = Field(default=None, description="EXCELLENT, HEALTHY, WATCH, DEGRADED, CRITICAL.")

    # 4. Inventory & Spares Context
    spare_sku: Optional[str] = Field(default=None, description="Coupled critical spare SKU.")
    current_stock: Optional[float] = Field(default=None, description="Current stock level.")
    safety_stock: Optional[float] = Field(default=None, description="Safety stock threshold.")
    reorder_point: Optional[float] = Field(default=None, description="Reorder point threshold.")
    inventory_status: Optional[str] = Field(default=None, description="Shortage status.")

    # 5. Financial Exposure & Recommendations
    realized_historical_loss_inr: float = Field(default=0.0, description="Observed downtime/scrap loss (INR).")
    gross_financial_exposure_inr: float = Field(default=0.0, description="Realized loss + Opportunity cost (INR).")
    active_recommendations_count: int = Field(default=0, description="Total active recommendations.")
    top_recommendation_action: Optional[str] = Field(default=None, description="Highest priority pending recommendation.")

    metadata: Optional[ResponseMetadata] = None
