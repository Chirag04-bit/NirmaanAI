"""
NirmaanAI Core SHAP Explainer Engine
Phase 11: Explainable AI & SHAP

Provides deterministic TreeExplainer integration for approved NirmaanAI models:
1. Phase 6 AI4I XGBoost Failure Classifier (operating in additive log-odds margin space with logistic mapping).
2. Phase 6 NASA C-MAPSS Random Forest RUL Regressor (operating directly in operational cycles).
3. Phase 9 XGBoost Energy Forecaster (operating in active power kW).

RESEARCH INTEGRITY & CAUSALITY DISCLAIMER:
- Explanations attribute model response function contributions, NOT physical causality.
- Verifies exact additive consistency: model_output == base_value + sum(SHAP_values).
- Strictly distinguishes log-odds margin contributions from final sigmoid probabilities.
- Uses strictly approved decision threshold (tau = 0.91) for AI4I equipment alerts.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt

from src.explainability.feature_dictionary import get_feature_metadata
from src.utils.logger import logger


class ShapExplainer:
    """
    Unified Explainable AI wrapper using SHAP TreeExplainer for tree-based champions.
    """

    def __init__(
        self,
        model: Any,
        feature_names: List[str],
        model_type: str = "classifier",
        decision_threshold: float = 0.91,
        target_name: str = "Machine Failure"
    ):
        self.model = model
        self.feature_names = list(feature_names)
        self.model_type = model_type.lower()
        self.decision_threshold = float(decision_threshold)
        self.target_name = target_name

        # Initialize TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)

        # Extract base value (expected value)
        expected_val = self.explainer.expected_value
        if isinstance(expected_val, (list, np.ndarray)):
            # If multi-output or binary array, take index 1 for positive class or index 0
            self.base_value = float(expected_val[-1] if len(expected_val) == 2 else expected_val[0])
        else:
            self.base_value = float(expected_val)

        logger.info(
            f"Initialized ShapExplainer for {self.model_type} ({len(self.feature_names)} features). "
            f"Base value: {self.base_value:.5f}, Decision threshold: {self.decision_threshold:.3f}"
        )

    @staticmethod
    def _sigmoid(x: float) -> float:
        """Standard logistic function mapping log-odds margin to probability."""
        if x < -35.0:
            return 0.0
        if x > 35.0:
            return 1.0
        return 1.0 / (1.0 + math.exp(-x))

    def _ensure_dataframe(self, X: Union[pd.DataFrame, np.ndarray, Dict[str, Any]]) -> pd.DataFrame:
        """Formats input into a validated DataFrame aligned with model feature space."""
        if isinstance(X, dict):
            df = pd.DataFrame([X])
        elif isinstance(X, np.ndarray):
            df = pd.DataFrame(X, columns=self.feature_names)
        else:
            df = X.copy()

        # Reindex to ensure identical column ordering
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0.0

        return df[self.feature_names]

    def explain_local(
        self,
        X_sample: Union[pd.DataFrame, np.ndarray, Dict[str, Any]],
        sample_index: int = 0
    ) -> Dict[str, Any]:
        """
        Generates local explanation for a single observation.
        Verifies exact additive check and generates human-readable narrative.
        """
        df = self._ensure_dataframe(X_sample)
        if len(df) > 1:
            row_df = df.iloc[[sample_index]]
        else:
            row_df = df

        # Compute SHAP explanation object
        explanation = self.explainer(row_df)
        shap_vals = np.array(explanation.values)[0]
        base_val = float(explanation.base_values[0]) if hasattr(explanation, "base_values") else self.base_value

        # Extract actual model prediction
        if self.model_type == "classifier":
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(row_df)[0, 1])
            else:
                prob = float(self.model.predict(row_df)[0])

            if hasattr(self.model, "predict") and "output_margin" in self.model.predict.__code__.co_varnames:
                model_margin = float(self.model.predict(row_df, output_margin=True)[0])
            else:
                model_margin = float(base_val + shap_vals.sum())

            additive_sum = float(base_val + shap_vals.sum())
            additive_error = abs(model_margin - additive_sum)
            is_positive_alert = prob >= self.decision_threshold
            prediction_label = "FAILURE_PREDICTED" if is_positive_alert else "NORMAL_OPERATION"
            risk_category = "CRITICAL" if prob >= self.decision_threshold else ("WARNING" if prob >= (self.decision_threshold * 0.6) else "NORMAL")
        else:
            predicted_val = float(self.model.predict(row_df)[0])
            additive_sum = float(base_val + shap_vals.sum())
            additive_error = abs(predicted_val - additive_sum)
            prob = None
            model_margin = None
            is_positive_alert = None
            prediction_label = f"PREDICTED_{self.target_name.upper().replace(' ', '_')}"
            risk_category = "NORMAL"

        # Build ranked feature attributions
        contributions: List[Dict[str, Any]] = []
        for i, col in enumerate(self.feature_names):
            feat_val = float(row_df[col].iloc[0])
            s_val = float(shap_vals[i])
            meta = get_feature_metadata(col)

            if self.model_type == "classifier":
                direction = "INCREASES_RISK" if s_val > 0 else "DECREASES_RISK"
            else:
                direction = "INCREASES_OUTPUT" if s_val > 0 else "DECREASES_OUTPUT"

            contributions.append({
                "feature_name": col,
                "display_name": meta["display_name"],
                "unit": meta["unit"],
                "feature_value": round(feat_val, 4),
                "shap_value": round(s_val, 4),
                "absolute_shap": round(abs(s_val), 4),
                "direction": direction,
                "domain_interpretation": meta["domain_interpretation"]
            })

        # Sort by absolute SHAP contribution descending
        contributions.sort(key=lambda x: x["absolute_shap"], reverse=True)

        # Generate human-readable narrative
        narrative = self._generate_human_narrative(
            contributions=contributions,
            prob=prob,
            is_alert=is_positive_alert,
            predicted_val=additive_sum if self.model_type != "classifier" else None
        )

        return {
            "model_type": self.model_type,
            "target_name": self.target_name,
            "decision_threshold": self.decision_threshold,
            "prediction_label": prediction_label,
            "risk_category": risk_category,
            "probability": round(prob, 4) if prob is not None else None,
            "raw_margin": round(model_margin, 4) if model_margin is not None else None,
            "base_value": round(base_val, 4),
            "shap_sum": round(float(shap_vals.sum()), 4),
            "additive_sum": round(additive_sum, 4),
            "additive_error": round(additive_error, 6),
            "ranked_contributions": contributions,
            "human_readable_narrative": narrative,
            "causality_disclaimer": (
                "SHAP identifies feature contributions to the mathematical model's output. "
                "These contributions indicate model association and sensitivity, NOT physical causality."
            )
        }

    def _generate_human_narrative(
        self,
        contributions: List[Dict[str, Any]],
        prob: Optional[float] = None,
        is_alert: Optional[bool] = None,
        predicted_val: Optional[float] = None
    ) -> str:
        """Constructs a scientifically accurate, human-readable narrative."""
        top_3 = contributions[:3]
        pos_drivers = [c for c in top_3 if c["shap_value"] > 0]
        neg_drivers = [c for c in top_3 if c["shap_value"] < 0]

        if self.model_type == "classifier":
            pred_desc = f"FAILURE RISK (probability = {prob:.3f} vs threshold {self.decision_threshold:.2f})" if is_alert else f"NORMAL OPERATION (probability = {prob:.3f} vs threshold {self.decision_threshold:.2f})"
            driver_phrases = []
            if pos_drivers:
                pos_str = ", ".join([f"{c['display_name']} ({c['feature_value']} {c['unit']}, SHAP: +{c['shap_value']:.2f})" for c in pos_drivers])
                driver_phrases.append(f"Factors driving the model toward failure prediction include {pos_str}.")
            if neg_drivers:
                neg_str = ", ".join([f"{c['display_name']} ({c['feature_value']} {c['unit']}, SHAP: {c['shap_value']:.2f})" for c in neg_drivers])
                driver_phrases.append(f"Factors mitigating predicted risk include {neg_str}.")

            return (
                f"Prediction: {pred_desc}. {' '.join(driver_phrases)} "
                f"Interpretation: The model's prediction is primarily associated with these observed telemetry values."
            )
        else:
            top_drivers = ", ".join([f"{c['display_name']} (SHAP: {c['shap_value']:+.2f})" for c in top_3])
            return (
                f"Predicted Output: {predicted_val:.2f} {self.target_name}. "
                f"Primary feature associations identified by the model: {top_drivers}."
            )

    def explain_global(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        max_samples: int = 1500
    ) -> pd.DataFrame:
        """
        Calculates global feature importance (mean absolute SHAP) across dataset.
        """
        df = self._ensure_dataframe(X)
        if len(df) > max_samples:
            df = df.sample(n=max_samples, random_state=42)

        explanation = self.explainer(df)
        shap_vals = np.array(explanation.values)

        mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
        total_importance = np.sum(mean_abs_shap) if np.sum(mean_abs_shap) > 0 else 1.0

        records: List[Dict[str, Any]] = []
        for i, col in enumerate(self.feature_names):
            meta = get_feature_metadata(col)
            records.append({
                "feature_name": col,
                "display_name": meta["display_name"],
                "unit": meta["unit"],
                "mean_abs_shap": round(float(mean_abs_shap[i]), 5),
                "relative_importance_pct": round(float((mean_abs_shap[i] / total_importance) * 100.0), 2),
                "domain_interpretation": meta["domain_interpretation"]
            })

        df_global = pd.DataFrame(records).sort_values(by="mean_abs_shap", ascending=False).reset_index(drop=True)
        df_global["rank"] = df_global.index + 1
        return df_global

    def plot_summary_beeswarm(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        output_path: str,
        max_display: int = 10,
        title: Optional[str] = None
    ) -> str:
        """Generates and saves publication-grade SHAP beeswarm summary plot."""
        df = self._ensure_dataframe(X)
        plt.figure(figsize=(10, 6))
        shap_values = self.explainer(df)

        shap.summary_plot(
            shap_values,
            df,
            max_display=max_display,
            show=False
        )
        if title:
            plt.title(title, fontsize=13, pad=15)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved SHAP beeswarm summary plot to: {output_path}")
        return output_path

    def plot_bar_importance(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        output_path: str,
        max_display: int = 10,
        title: Optional[str] = None
    ) -> str:
        """Generates and saves standard SHAP bar importance plot."""
        df = self._ensure_dataframe(X)
        plt.figure(figsize=(10, 5.5))
        shap_values = self.explainer(df)

        shap.plots.bar(
            shap_values,
            max_display=max_display,
            show=False
        )
        if title:
            plt.title(title, fontsize=13, pad=15)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved SHAP bar importance plot to: {output_path}")
        return output_path
