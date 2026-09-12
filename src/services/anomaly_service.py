"""
NirmaanAI Anomaly Detection Service
Exposes inference APIs for real-time multi-sensor anomaly detection, scoring, and diagnostics.
Consumes Phase 4 unified schemas (SensorReading, Machine) and provides operating-regime awareness.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
import pandas as pd

from src.data.schema import AlertSeverity, HealthState, SensorReading
from src.features.anomaly_features import engineer_synthetic_anomaly_features
from src.models.anomaly_detector import BaseAnomalyDetector
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


@dataclass
class AnomalyDetectionResult:
    machine_id: str
    timestamp: str
    anomaly_score: float  # Bounded continuous score in [0, 1]
    is_anomaly: bool
    severity: str  # "NORMAL", "WARNING", "CRITICAL"
    decision_threshold: float
    top_contributing_sensors: Dict[str, float]
    operating_regime_status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AnomalyDetectionService:
    """
    Unified real-time inference service for multi-sensor equipment anomaly detection.
    Maintains a rolling causal buffer of recent sensor readings per machine to compute
    dynamic features without future leakage.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        buffer_size: int = 10
    ):
        root = get_project_root()
        if model_path is None:
            model_path = root / "models" / "anomaly_detection" / "anomaly_detector.joblib"

        self.model_path = model_path
        self.buffer_size = buffer_size
        self.payload: Optional[Dict[str, Any]] = None
        self.model: Optional[BaseAnomalyDetector] = None
        self.threshold: float = 0.2405
        self.feature_names: List[str] = []

        # Causal rolling buffer of recent readings per machine
        self._reading_buffer: Dict[str, List[Dict[str, Any]]] = {}

        if self.model_path.exists():
            self.payload = joblib.load(self.model_path)
            self.model = self.payload["model"]
            self.threshold = float(self.payload["threshold"])
            self.feature_names = self.payload["feature_names"]
            logger.info(
                f"Loaded champion anomaly detector: '{self.payload['model_name']}' "
                f"with threshold={self.threshold:.5f} ({len(self.feature_names)} features)"
            )
        else:
            logger.warning(f"Anomaly detector artifact not found at: {self.model_path}")

    def update_buffer(self, reading: SensorReading) -> None:
        """Appends reading to machine's causal buffer, maintaining max size."""
        m_id = reading.machine_id
        if m_id not in self._reading_buffer:
            self._reading_buffer[m_id] = []

        data = {
            "reading_id": reading.reading_id or 0,
            "machine_id": reading.machine_id,
            "timestamp": reading.timestamp,
            "vibration_mms": reading.vibration_mms,
            "temperature_c": reading.temperature_c,
            "ambient_temperature_c": reading.ambient_temperature_c if reading.ambient_temperature_c is not None else 25.0,
            "rotational_speed_rpm": reading.rotational_speed_rpm if reading.rotational_speed_rpm is not None else 1500.0,
            "torque_nm": reading.torque_nm if reading.torque_nm is not None else 140.0,
            "sound_db": reading.sound_db if reading.sound_db is not None else 74.0,
            "power_consumption_kw": reading.power_consumption_kw if reading.power_consumption_kw is not None else 22.0,
            "oil_level_pct": reading.oil_level_pct if reading.oil_level_pct is not None else 85.0,
            "coolant_level_pct": reading.coolant_level_pct if reading.coolant_level_pct is not None else 90.0,
            "tool_wear_min": reading.tool_wear_min if reading.tool_wear_min is not None else 10.0
        }
        self._reading_buffer[m_id].append(data)
        if len(self._reading_buffer[m_id]) > self.buffer_size:
            self._reading_buffer[m_id].pop(0)

    def detect(self, reading: SensorReading) -> AnomalyDetectionResult:
        """
        Executes real-time anomaly inference for an incoming SensorReading.
        Computes causal rolling features across the internal historical buffer.
        """
        if self.model is None:
            raise RuntimeError("Anomaly detector model is not initialized or trained.")

        self.update_buffer(reading)
        m_id = reading.machine_id
        buffer_df = pd.DataFrame(self._reading_buffer[m_id])

        # Engineer features using causal backward-looking rolling statistics
        feat_df = engineer_synthetic_anomaly_features(buffer_df, rolling_window=5)
        latest_row = feat_df.iloc[[-1]][self.feature_names]

        # Compute continuous anomaly score in [0, 1]
        score = float(self.model.score_samples(latest_row)[0])
        is_anomaly = bool(score >= self.threshold)

        # Categorize severity
        # Normal: score < threshold
        # Warning: threshold <= score < threshold * 2.0
        # Critical: score >= threshold * 2.0 or score >= 0.70
        if not is_anomaly:
            severity = "NORMAL"
        elif score < min(0.70, self.threshold * 2.5):
            severity = "WARNING"
        else:
            severity = "CRITICAL"

        # Diagnose top contributing sensors using reconstruction error or feature deviation
        top_contributions: Dict[str, float] = {}
        if hasattr(self.model, "compute_feature_contributions"):
            contrib_df = self.model.compute_feature_contributions(latest_row)
            row_contrib = contrib_df.iloc[0].sort_values(ascending=False).head(4)
            top_contributions = {k: round(float(v), 4) for k, v in row_contrib.items()}
        else:
            # Fallback simple deviation ranking
            top_contributions = {"vibration_mms": round(float(reading.vibration_mms), 2)}

        # Operating regime verification
        regime_status = "NOMINAL_REGIME"
        if m_id != "M2":
            regime_status = f"CROSS_MACHINE_{m_id}_NEEDS_VERTICAL_CALIBRATION"

        return AnomalyDetectionResult(
            machine_id=m_id,
            timestamp=str(reading.timestamp),
            anomaly_score=round(score, 5),
            is_anomaly=is_anomaly,
            severity=severity,
            decision_threshold=round(self.threshold, 5),
            top_contributing_sensors=top_contributions,
            operating_regime_status=regime_status
        )
