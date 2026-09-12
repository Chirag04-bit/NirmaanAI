"""
NirmaanAI Bottleneck & Flow Intelligence Service
Exposes operational inference APIs for real-time production flow congestion assessment,
bottleneck risk forecasting, and active constraint machine identification.
Consumes Phase 4 unified schemas (ProductionJob, Machine, SensorReading).
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
import pandas as pd

from src.data.schema import JobStatus, Machine, ProductionJob, SensorReading
from src.models.bottleneck_predictor import BaseBottleneckClassifier, HeuristicBottleneckClassifier
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


@dataclass
class FlowAssessmentResult:
    timestamp: str
    flow_status: str  # "NOMINAL_FLOW", "MODERATE_CONGESTION", "CRITICAL_BOTTLENECK"
    active_constraint_machine: Optional[str]
    bottleneck_risk_score: float  # [0.0, 1.0]
    is_bottleneck_predicted: bool
    confidence: float
    affected_machines: List[str]
    contributing_flow_indicators: Dict[str, Any]
    operational_interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BottleneckService:
    """
    Unified real-time service for line flow congestion intelligence and bottleneck forecasting.
    Monitors sequential coupled production stages and predicts upcoming bottlenecks
    based on machine health telemetry and queue dynamics.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        machines: Optional[List[Machine]] = None
    ):
        root = get_project_root()
        if model_path is None:
            model_path = root / "models" / "bottleneck_prediction" / "bottleneck_predictor.joblib"

        self.model_path = model_path
        self.payload: Optional[Dict[str, Any]] = None
        self.model: Optional[BaseBottleneckClassifier] = None
        self.threshold: float = 0.40
        self.feature_names: List[str] = []

        # Nominal machine design parameters
        self.machines = machines or []
        self.machine_map = {m.machine_id: m for m in self.machines}

        # Causal in-memory rolling tracking per machine
        # Tracks recent completed cycle ratios and dispatch delays
        self._machine_cycle_history: Dict[str, List[float]] = {m: [] for m in ["M1", "M2", "M3", "M4", "M5"]}
        self._machine_delay_history: Dict[str, List[float]] = {m: [] for m in ["M1", "M2", "M3", "M4", "M5"]}

        if self.model_path.exists():
            self.payload = joblib.load(self.model_path)
            self.model = self.payload["model"]
            self.threshold = float(self.payload["threshold"])
            self.feature_names = self.payload["feature_names"]
            logger.info(
                f"Loaded champion bottleneck model: '{self.payload['model_name']}' "
                f"with threshold={self.threshold:.2f} ({len(self.feature_names)} features)"
            )
        else:
            # Fallback to initialized heuristic baseline
            self.model = HeuristicBottleneckClassifier(vib_dev_threshold=0.30, cycle_ratio_threshold=1.10)
            self.threshold = 0.40
            logger.warning(f"Bottleneck model not found at {self.model_path}; using fallback heuristic.")

    def record_job_completion(
        self,
        machine_id: str,
        actual_cycle_sec: float,
        start_delay_min: float,
        nominal_cycle_sec: float = 45.0
    ) -> None:
        """Updates machine flow history upon batch completion."""
        ratio = actual_cycle_sec / max(nominal_cycle_sec, 1.0)
        if machine_id not in self._machine_cycle_history:
            self._machine_cycle_history[machine_id] = []
            self._machine_delay_history[machine_id] = []

        self._machine_cycle_history[machine_id].append(ratio)
        self._machine_delay_history[machine_id].append(start_delay_min)

        # Retain last 5 jobs
        if len(self._machine_cycle_history[machine_id]) > 5:
            self._machine_cycle_history[machine_id].pop(0)
            self._machine_delay_history[machine_id].pop(0)

    def assess_upcoming_job(
        self,
        job: ProductionJob,
        pre_job_vibration_mms: Optional[float] = None,
        pre_job_temperature_c: Optional[float] = None,
        baseline_vibration_mms: float = 1.40
    ) -> FlowAssessmentResult:
        """
        Evaluates risk of upcoming scheduled batch becoming a bottleneck at dispatch time.
        Information available: scheduled start, batch size, prior machine history, pre-job sensor state.
        """
        m_id = job.machine_id
        t_now = job.scheduled_start.isoformat()

        # Compute prior lagging indicators
        prior_cycles = self._machine_cycle_history.get(m_id, [])
        prior_cycle_mean = float(np.mean(prior_cycles)) if len(prior_cycles) > 0 else 1.0

        prior_delays = self._machine_delay_history.get(m_id, [])
        prior_delay_mean = float(np.mean(prior_delays)) if len(prior_delays) > 0 else 0.0

        # Pre-job sensor indicators
        current_vib = pre_job_vibration_mms if pre_job_vibration_mms is not None else baseline_vibration_mms
        vib_dev = max(0.0, current_vib - baseline_vibration_mms)
        current_temp = pre_job_temperature_c if pre_job_temperature_c is not None else 38.0

        # Feature vector construction matching training pipeline
        feature_dict = {
            "batch_quantity": float(job.batch_quantity),
            "planned_duration_min": float(job.batch_quantity * 45.0 / 60.0),
            "batch_load_ratio": float(job.batch_quantity / 70.0),
            "hour_of_day": float(job.scheduled_start.hour),
            "is_afternoon_shift": 1.0 if job.scheduled_start.hour >= 14 else 0.0,
            "prior_cycle_ratio_mean": prior_cycle_mean,
            "prior_start_delay_mean": prior_delay_mean,
            "pre_job_vibration_1h": current_vib,
            "pre_job_temperature_1h": current_temp,
            "pre_job_vibration_dev_1h": vib_dev,
            "is_machine_M1": 1.0 if m_id == "M1" else 0.0,
            "is_machine_M2": 1.0 if m_id == "M2" else 0.0,
            "is_machine_M3": 1.0 if m_id == "M3" else 0.0,
            "is_machine_M4": 1.0 if m_id == "M4" else 0.0,
            "is_machine_M5": 1.0 if m_id == "M5" else 0.0
        }

        row_df = pd.DataFrame([feature_dict])

        # Model risk scoring
        if self.model is not None and hasattr(self.model, "predict_proba"):
            risk_score = float(self.model.predict_proba(row_df)[0, 1])
        else:
            # Fallback heuristic calculation
            vib_r = min(1.0, vib_dev / 0.50)
            cyc_r = min(1.0, max(0.0, (prior_cycle_mean - 1.0) / 0.25))
            risk_score = 0.50 * vib_r + 0.50 * cyc_r

        is_bottleneck = bool(risk_score >= self.threshold)

        # Categorize flow state
        if risk_score < 0.25:
            flow_status = "NOMINAL_FLOW"
            interpretation = "Production operating smoothly within design cycle time tolerances."
            constraint_machine = None
            affected = []
        elif risk_score < 0.60:
            flow_status = "MODERATE_CONGESTION"
            interpretation = f"Moderate flow lag detected on {m_id}. Buffer queues may accumulate."
            constraint_machine = m_id
            affected = [m_id]
        else:
            flow_status = "CRITICAL_BOTTLENECK"
            interpretation = (
                f"Critical bottleneck warning on {m_id}: pre-dispatch telemetry and cycle lag indicate "
                f"severe throughput loss (+25% cycle time) that will propagate downstream."
            )
            constraint_machine = m_id
            # Next in line sequentially: M1 -> M2 -> M3 -> M4 -> M5
            next_map = {"M1": "M2", "M2": "M3", "M3": "M4", "M4": "M5", "M5": None}
            affected = [m_id]
            if next_map.get(m_id):
                affected.append(next_map[m_id])

        confidence = round(float(abs(risk_score - 0.5) * 2.0), 4)

        return FlowAssessmentResult(
            timestamp=t_now,
            flow_status=flow_status,
            active_constraint_machine=constraint_machine,
            bottleneck_risk_score=round(risk_score, 4),
            is_bottleneck_predicted=is_bottleneck,
            confidence=confidence,
            affected_machines=affected,
            contributing_flow_indicators={
                "prior_cycle_ratio_mean": round(prior_cycle_mean, 3),
                "prior_start_delay_mean": round(prior_delay_mean, 2),
                "pre_job_vibration_dev": round(vib_dev, 3),
                "pre_job_temperature_c": round(current_temp, 1),
                "batch_quantity": job.batch_quantity
            },
            operational_interpretation=interpretation
        )
