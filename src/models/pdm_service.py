"""
NirmaanAI Predictive Maintenance Service
Exposes inference APIs for real-time sensor failure risk scoring and RUL estimation.
Consumes Phase 4 unified schemas (SensorReading, Machine) and provides controlled synthetic validation.
"""

from dataclasses import asdict, dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from src.data.schema import AlertSeverity, HealthState, SensorReading
from src.features.pdm_features import engineer_ai4i_features
from src.models.failure_classifier import FailureClassifierBenchmark
from src.models.rul_regressor import RULRegressorBenchmark
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


@dataclass
class FailurePredictionResult:
    machine_id: str
    failure_probability: float
    is_failure_predicted: bool
    risk_level: str  # "NORMAL", "WARNING", "CRITICAL"
    confidence: float
    decision_threshold: float
    contributing_features: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RULPredictionResult:
    machine_id: str
    predicted_rul_cycles: float
    risk_category: str  # "SAFE", "WARNING", "CRITICAL"
    estimated_remaining_days: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PredictiveMaintenanceService:
    """
    Unified inference service orchestrating Failure Classification and RUL Estimation models.
    """

    def __init__(
        self,
        classifier_path: Optional[Path] = None,
        regressor_path: Optional[Path] = None
    ):
        root = get_project_root()
        models_dir = root / "models" / "predictive_maintenance"

        if classifier_path is None:
            classifier_path = models_dir / "failure_classifier.joblib"
        if regressor_path is None:
            regressor_path = models_dir / "rul_regressor.joblib"

        self.classifier_path = classifier_path
        self.regressor_path = regressor_path

        self.classifier_payload: Optional[Dict[str, Any]] = None
        self.regressor_payload: Optional[Dict[str, Any]] = None

        if classifier_path.exists():
            self.classifier_payload = FailureClassifierBenchmark.load_champion(classifier_path)
            logger.info(f"Loaded champion failure classifier: '{self.classifier_payload['model_name']}'")

        if regressor_path.exists():
            self.regressor_payload = RULRegressorBenchmark.load_champion(regressor_path)
            logger.info(f"Loaded champion RUL regressor: '{self.regressor_payload['model_name']}'")

    def predict_failure(
        self,
        reading: Union[SensorReading, Dict[str, Any]],
        machine_id: str = "UNKNOWN"
    ) -> FailurePredictionResult:
        """
        Calculates failure probability for an incoming telemetry reading.
        Applies calibrated decision threshold and risk categorizations.
        """
        if self.classifier_payload is None:
            raise RuntimeError("Failure classifier model is not loaded. Train models first via train_pdm.")

        # Extract data from SensorReading or dict
        if isinstance(reading, SensorReading):
            raw_dict = {
                "Air temperature [K]": reading.ambient_temperature_c + 273.15,
                "Process temperature [K]": reading.temperature_c + 273.15,
                "Rotational speed [rpm]": reading.rotational_speed_rpm,
                "Torque [Nm]": reading.torque_nm,
                "Tool wear [min]": reading.tool_wear_min,
                "Type": "M"
            }
            m_id = reading.machine_id
        else:
            raw_dict = reading.copy()
            m_id = raw_dict.get("machine_id", machine_id)

        df_in = pd.DataFrame([raw_dict])
        df_eng = engineer_ai4i_features(df_in)

        feature_cols = self.classifier_payload["feature_names"]
        # Ensure all expected feature columns exist
        for col in feature_cols:
            if col not in df_eng.columns:
                df_eng[col] = 0.0

        X_eval = df_eng[feature_cols]

        model = self.classifier_payload["model"]
        threshold = float(self.classifier_payload.get("threshold", 0.50))

        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(X_eval)[0, 1])
        else:
            prob = float(model.predict(X_eval)[0])

        is_fail = bool(prob >= threshold)

        if prob >= threshold:
            risk = "CRITICAL"
        elif prob >= (threshold * 0.60):
            risk = "WARNING"
        else:
            risk = "NORMAL"

        confidence = round(float(abs(prob - threshold) / max(threshold, 1.0 - threshold)), 4)
        confidence = min(1.0, max(0.0, confidence))

        # Top contributing raw features (normalized deviation from typical means)
        feature_vals = {
            "rotational_speed_rpm": float(df_eng.get("rotational_speed_rpm", [0])[0]),
            "torque_nm": float(df_eng.get("torque_nm", [0])[0]),
            "tool_wear_min": float(df_eng.get("tool_wear_min", [0])[0]),
            "temp_diff_k": float(df_eng.get("temp_diff_k", [0])[0]),
            "mechanical_power_kw": float(df_eng.get("mechanical_power_kw", [0])[0])
        }

        return FailurePredictionResult(
            machine_id=m_id,
            failure_probability=round(prob, 4),
            is_failure_predicted=is_fail,
            risk_level=risk,
            confidence=confidence,
            decision_threshold=threshold,
            contributing_features=feature_vals
        )

    def predict_rul(
        self,
        features: Union[pd.DataFrame, Dict[str, Any]],
        machine_id: str = "UNKNOWN"
    ) -> RULPredictionResult:
        """
        Estimates Remaining Useful Life in operating cycles.
        """
        if self.regressor_payload is None:
            raise RuntimeError("RUL regressor model is not loaded. Train models first via train_pdm.")

        if isinstance(features, dict):
            df_in = pd.DataFrame([features])
        else:
            df_in = features.copy()

        feature_cols = self.regressor_payload["feature_names"]
        for col in feature_cols:
            if col not in df_in.columns:
                df_in[col] = 0.0

        X_eval = df_in[feature_cols]
        model = self.regressor_payload["model"]

        predicted_rul = float(model.predict(X_eval)[0])
        predicted_rul = max(0.0, round(predicted_rul, 1))

        if predicted_rul <= 25.0:
            risk = "CRITICAL"
        elif predicted_rul <= 50.0:
            risk = "WARNING"
        else:
            risk = "SAFE"

        return RULPredictionResult(
            machine_id=machine_id,
            predicted_rul_cycles=predicted_rul,
            risk_category=risk,
            estimated_remaining_days=round(predicted_rul * 1.0, 1)  # 1 cycle ~ 1 shift/day equivalent
        )

    def run_controlled_synthetic_validation(
        self,
        synthetic_csv_path: Path,
        target_machine_id: str = "M2"
    ) -> Dict[str, Any]:
        """
        Controlled Synthetic Validation:
        Tests whether the predictive maintenance pipeline detects the configured degradation
        episode on Machine 2 (Days 18-21) vs normal baseline operations (Days 1-10).
        Results are strictly labeled as controlled synthetic validation and not physical causality.
        """
        logger.info(f"Running controlled synthetic validation on {synthetic_csv_path} for machine {target_machine_id}...")
        df = pd.read_csv(synthetic_csv_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        start = df["timestamp"].min()
        df["day"] = (df["timestamp"] - start).dt.total_seconds() / (24 * 3600) + 1.0

        df_m2 = df[df["machine_id"] == target_machine_id].copy()

        # Score all readings through FailurePredictor
        predictions = []
        for _, row in df_m2.iterrows():
            reading = SensorReading(
                reading_id=int(row["reading_id"]),
                machine_id=str(row["machine_id"]),
                timestamp=row["timestamp"],
                vibration_mms=float(row["vibration_mms"]),
                temperature_c=float(row["temperature_c"]),
                ambient_temperature_c=float(row["ambient_temperature_c"]),
                rotational_speed_rpm=float(row["rotational_speed_rpm"]),
                torque_nm=float(row["torque_nm"]),
                sound_db=float(row["sound_db"]),
                power_consumption_kw=float(row["power_consumption_kw"]),
                oil_level_pct=float(row["oil_level_pct"]),
                coolant_level_pct=float(row["coolant_level_pct"]),
                tool_wear_min=float(row["tool_wear_min"])
            )
            pred = self.predict_failure(reading)
            predictions.append({
                "day": row["day"],
                "prob": pred.failure_probability,
                "is_fail": pred.is_failure_predicted,
                "risk": pred.risk_level
            })

        df_results = pd.DataFrame(predictions)

        # Compare normal baseline (Days 1-10) vs Degradation window (Days 18-21)
        baseline_mask = (df_results["day"] >= 1.0) & (df_results["day"] <= 10.0)
        degraded_mask = (df_results["day"] >= 18.0) & (df_results["day"] <= 21.0)

        mean_baseline_prob = float(df_results.loc[baseline_mask, "prob"].mean())
        mean_degraded_prob = float(df_results.loc[degraded_mask, "prob"].mean())
        max_degraded_prob = float(df_results.loc[degraded_mask, "prob"].max())
        degraded_alarms = int(df_results.loc[degraded_mask, "is_fail"].sum())

        logger.info(
            f"Controlled synthetic validation results: Baseline mean prob={mean_baseline_prob:.4f}, "
            f"Degraded mean prob={mean_degraded_prob:.4f}, Max prob={max_degraded_prob:.4f}, Alarms={degraded_alarms}."
        )

        return {
            "validation_type": "Controlled synthetic validation",
            "target_machine": target_machine_id,
            "mean_baseline_probability": round(mean_baseline_prob, 4),
            "mean_degraded_probability": round(mean_degraded_prob, 4),
            "max_degraded_probability": round(max_degraded_prob, 4),
            "degraded_window_alarms": degraded_alarms,
            "detected_configured_degradation": bool(mean_degraded_prob > mean_baseline_prob * 1.5)
        }
