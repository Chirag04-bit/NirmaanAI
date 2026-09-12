"""
NirmaanAI Explanation Service Layer
Phase 11: Explainable AI & SHAP

Exposes real-time API services for:
1. Local SHAP explanations for equipment failure predictions.
2. Human-readable feature attributions and risk directionality.
3. Machine 2 synthetic scenario explanation with explicit causality and distribution-shift disclaimers.
4. Global model feature importance rankings.

RESEARCH INTEGRITY:
- Preserves Phase 6 AI4I decision threshold (tau = 0.91).
- Strictly distinguishes model attribution from physical causality.
- Operates on frozen model checkpoints without retraining or altering predictions.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import pandas as pd
from pydantic import BaseModel, Field

from src.data.schema import SensorReading
from src.explainability.feature_dictionary import get_feature_metadata
from src.explainability.shap_explainer import ShapExplainer
from src.features.pdm_features import engineer_ai4i_features
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class FeatureContribution(BaseModel):
    feature_name: str
    display_name: str
    unit: str
    feature_value: float
    shap_value: float
    absolute_shap: float
    direction: str
    domain_interpretation: str


class LocalExplanationRequest(BaseModel):
    machine_id: str = Field(default="M2", description="Target machine identifier")
    air_temperature_k: float = Field(default=300.0, description="Ambient air temperature in Kelvin")
    process_temperature_k: float = Field(default=310.0, description="Process temperature in Kelvin")
    rotational_speed_rpm: float = Field(default=1500.0, description="Spindle rotational speed in RPM")
    torque_nm: float = Field(default=40.0, description="Spindle torque in Nm")
    tool_wear_min: float = Field(default=100.0, description="Accumulated tool cutting time in minutes")
    product_type: str = Field(default="M", description="Workpiece material quality grade (L, M, H)")


class LocalExplanationResponse(BaseModel):
    machine_id: str
    prediction_label: str
    risk_category: str
    probability: float
    raw_margin: float
    decision_threshold: float
    base_value: float
    additive_error: float
    ranked_contributions: List[FeatureContribution]
    human_readable_narrative: str
    causality_disclaimer: str


class GlobalFeatureImportanceItem(BaseModel):
    rank: int
    feature_name: str
    display_name: str
    unit: str
    mean_abs_shap: float
    relative_importance_pct: float
    domain_interpretation: str


class GlobalExplanationResponse(BaseModel):
    model_name: str
    target_name: str
    decision_threshold: float
    features_count: int
    ranked_features: List[GlobalFeatureImportanceItem]


class Machine2ExplanationRequest(BaseModel):
    machine_id: str = Field(default="M2", description="Machine identifier")
    vibration_mms: float = Field(ge=0.0, description="Current spindle vibration in mm/s")
    temperature_c: float = Field(description="Internal process temperature in Celsius")
    ambient_temperature_c: float = Field(default=25.0, description="Ambient room temperature in Celsius")
    rotational_speed_rpm: float = Field(ge=0.0, description="Spindle RPM")
    torque_nm: float = Field(ge=0.0, description="Spindle torque in Nm")
    tool_wear_min: float = Field(ge=0.0, description="Tool wear minutes")


class Machine2ExplanationResponse(BaseModel):
    machine_id: str
    synthetic_vibration_mms: float
    synthetic_vibration_trigger: float
    is_synthetic_vibration_alert: bool
    ai4i_model_probability: float
    empirical_decision_threshold: float
    is_empirical_failure_predicted: bool
    top_contributing_features: List[FeatureContribution]
    human_readable_narrative: str
    distribution_shift_warning: str
    causality_disclaimer: str


class ExplanationService:
    """Service facade providing real-time Explainable AI attributions."""

    def __init__(
        self,
        classifier_path: Optional[Path] = None,
        cmapss_regressor_path: Optional[Path] = None
    ):
        root = get_project_root()
        pdm_dir = root / "models" / "predictive_maintenance"

        clf_path = classifier_path or (pdm_dir / "failure_classifier.joblib")
        reg_path = cmapss_regressor_path or (pdm_dir / "rul_regressor.joblib")

        self.ai4i_explainer: Optional[ShapExplainer] = None
        self.cmapss_explainer: Optional[ShapExplainer] = None

        # Load AI4I Classifier
        if clf_path.exists():
            b = joblib.load(clf_path)
            self.ai4i_model = b["model"]
            self.ai4i_features = b["feature_names"]
            self.ai4i_threshold = 0.91  # Strictly approved Phase 6 threshold
            self.ai4i_explainer = ShapExplainer(
                model=self.ai4i_model,
                feature_names=self.ai4i_features,
                model_type="classifier",
                decision_threshold=self.ai4i_threshold,
                target_name="Machine Failure"
            )
        else:
            logger.warning(f"AI4I classifier artifact not found at {clf_path}")

        # Load NASA C-MAPSS Regressor
        if reg_path.exists():
            b_reg = joblib.load(reg_path)
            self.cmapss_model = b_reg["model"]
            self.cmapss_features = b_reg["feature_names"]
            self.cmapss_explainer = ShapExplainer(
                model=self.cmapss_model,
                feature_names=self.cmapss_features,
                model_type="regressor",
                decision_threshold=0.0,
                target_name="Remaining Useful Life (Cycles)"
            )
        else:
            logger.warning(f"C-MAPSS regressor artifact not found at {reg_path}")

    def explain_ai4i_reading(
        self,
        reading: Union[SensorReading, Dict[str, Any], LocalExplanationRequest]
    ) -> LocalExplanationResponse:
        """Generates local SHAP explanation for an AI4I observation."""
        if self.ai4i_explainer is None:
            raise RuntimeError("AI4I Explainer is not initialized.")

        # Convert to dictionary
        if isinstance(reading, LocalExplanationRequest):
            raw_dict = {
                "Air temperature [K]": reading.air_temperature_k,
                "Process temperature [K]": reading.process_temperature_k,
                "Rotational speed [rpm]": reading.rotational_speed_rpm,
                "Torque [Nm]": reading.torque_nm,
                "Tool wear [min]": reading.tool_wear_min,
                "Type": reading.product_type
            }
            m_id = reading.machine_id
        elif isinstance(reading, SensorReading):
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
            input_dict = dict(reading)
            m_id = input_dict.get("machine_id", "M2")
            # Map snake_case inputs to raw column names if present
            raw_dict = {}
            alias_map = {
                "air_temperature_k": "Air temperature [K]",
                "process_temperature_k": "Process temperature [K]",
                "rotational_speed_rpm": "Rotational speed [rpm]",
                "torque_nm": "Torque [Nm]",
                "tool_wear_min": "Tool wear [min]",
                "product_type": "Type"
            }
            for k, v in input_dict.items():
                if k in alias_map:
                    raw_dict[alias_map[k]] = v
                else:
                    raw_dict[k] = v

        # Ensure standard baseline keys exist in raw_dict for feature engineering
        default_raw = {
            "Air temperature [K]": 300.0,
            "Process temperature [K]": 310.0,
            "Rotational speed [rpm]": 1500.0,
            "Torque [Nm]": 40.0,
            "Tool wear [min]": 0.0,
            "Type": "M"
        }
        for k, v in default_raw.items():
            if k not in raw_dict:
                raw_dict[k] = v

        # Feature engineering pipeline
        df_raw = pd.DataFrame([raw_dict])
        df_eng = engineer_ai4i_features(df_raw)

        # Explain via ShapExplainer
        res = self.ai4i_explainer.explain_local(df_eng)

        return LocalExplanationResponse(
            machine_id=m_id,
            prediction_label=res["prediction_label"],
            risk_category=res["risk_category"],
            probability=res["probability"],
            raw_margin=res["raw_margin"],
            decision_threshold=res["decision_threshold"],
            base_value=res["base_value"],
            additive_error=res["additive_error"],
            ranked_contributions=[FeatureContribution(**c) for c in res["ranked_contributions"]],
            human_readable_narrative=res["human_readable_narrative"],
            causality_disclaimer=res["causality_disclaimer"]
        )

    def explain_machine2_scenario(
        self,
        req: Machine2ExplanationRequest
    ) -> Machine2ExplanationResponse:
        """
        Investigates the AI4I model's explanation on synthetic Machine 2 telemetry.
        RESEARCH INTEGRITY:
        - Labels vibration trigger (3.80 mm/s) as CONFIGURED SYNTHETIC SCENARIO TRIGGER.
        - Discloses distribution shift between AI4I empirical dataset and synthetic factory simulator.
        - Disclaims physical causality.
        """
        if self.ai4i_explainer is None:
            raise RuntimeError("AI4I Explainer is not initialized.")

        # Map Machine 2 inputs to AI4I domain features
        raw_dict = {
            "Air temperature [K]": req.ambient_temperature_c + 273.15,
            "Process temperature [K]": req.temperature_c + 273.15,
            "Rotational speed [rpm]": req.rotational_speed_rpm,
            "Torque [Nm]": req.torque_nm,
            "Tool wear [min]": req.tool_wear_min,
            "Type": "M"
        }

        df_raw = pd.DataFrame([raw_dict])
        df_eng = engineer_ai4i_features(df_raw)

        res = self.ai4i_explainer.explain_local(df_eng)

        # Evaluate scenario triggers
        is_vib_alert = req.vibration_mms >= 3.80
        is_ai4i_alert = res["probability"] >= self.ai4i_threshold

        narrative = (
            f"Machine 2 Telemetry Explanation: Model predicted failure probability of {res['probability']:.3f} "
            f"(threshold {self.ai4i_threshold:.2f}). "
            f"The model's output is primarily associated with: {res['ranked_contributions'][0]['display_name']} "
            f"(SHAP: {res['ranked_contributions'][0]['shap_value']:+.2f}) and {res['ranked_contributions'][1]['display_name']} "
            f"(SHAP: {res['ranked_contributions'][1]['shap_value']:+.2f}). "
            f"Synthetic vibration trigger (>= 3.80 mm/s) status: {'TRIGGERED' if is_vib_alert else 'NORMAL'} ({req.vibration_mms:.2f} mm/s)."
        )

        dist_warning = (
            "DISTRIBUTION SHIFT NOTICE: Machine 2 telemetry originates from the synthetic factory digital twin, "
            "whereas the XGBoost classifier was trained on the empirical AI4I 2020 dataset. "
            "Differences in sensor noise, cooling dynamics, and machine scale must be accounted for."
        )

        causality_disclaimer = (
            "RESEARCH INTEGRITY WARNING: SHAP identifies which features the mathematical model weighted "
            "most heavily for this observation. It does NOT prove that vibration or temperature physically caused "
            "the failure state. Physical root cause analysis requires domain engineering investigation."
        )

        return Machine2ExplanationResponse(
            machine_id=req.machine_id,
            synthetic_vibration_mms=req.vibration_mms,
            synthetic_vibration_trigger=3.80,
            is_synthetic_vibration_alert=is_vib_alert,
            ai4i_model_probability=res["probability"],
            empirical_decision_threshold=self.ai4i_threshold,
            is_empirical_failure_predicted=is_ai4i_alert,
            top_contributing_features=[FeatureContribution(**c) for c in res["ranked_contributions"][:5]],
            human_readable_narrative=narrative,
            distribution_shift_warning=dist_warning,
            causality_disclaimer=causality_disclaimer
        )
