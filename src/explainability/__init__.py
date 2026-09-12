"""
NirmaanAI Explainability Subsystem
Phase 11: Explainable AI & SHAP
"""

from src.explainability.feature_dictionary import (
    AI4I_FEATURE_DICTIONARY,
    CMAPSS_FEATURE_DICTIONARY,
    EXCLUDED_LEAKAGE_DICTIONARY,
    FORECASTING_FEATURE_DICTIONARY,
    get_feature_metadata,
)
from src.explainability.shap_explainer import ShapExplainer
from src.explainability.explanation_service import ExplanationService

__all__ = [
    "AI4I_FEATURE_DICTIONARY",
    "CMAPSS_FEATURE_DICTIONARY",
    "EXCLUDED_LEAKAGE_DICTIONARY",
    "FORECASTING_FEATURE_DICTIONARY",
    "get_feature_metadata",
    "ShapExplainer",
    "ExplanationService",
]
