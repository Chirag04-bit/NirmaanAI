"""
NirmaanAI Explainable AI (SHAP) Unit & Integration Tests
Phase 11: Explainable AI & SHAP

Comprehensive test suite verifying:
- Model and explainer loading for AI4I classifier and C-MAPSS regressor.
- Feature count and feature space exactness.
- Exact additive SHAP consistency in log-odds space (classifier) and cycle space (regressor).
- Strict exclusion of leakage columns (UDI, Product ID, TWF, HDF, PWF, OSF, RNF).
- Preservation of approved decision threshold (tau = 0.91).
- Invariance of model predictions before vs after SHAP explanation.
- Systematic coverage of representative TP, TN, FP, and FN test observations.
- Machine 2 synthetic scenario explanation and causality disclaimers.
- Completeness of feature dictionary semantics.
- Deterministic reproducibility and safety under invalid inputs.
"""

import json
import math
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest

from src.explainability.feature_dictionary import (
    AI4I_FEATURE_DICTIONARY,
    CMAPSS_FEATURE_DICTIONARY,
    EXCLUDED_LEAKAGE_DICTIONARY,
    get_feature_metadata,
)
from src.explainability.shap_explainer import ShapExplainer
from src.explainability.explanation_service import (
    ExplanationService,
    LocalExplanationRequest,
    Machine2ExplanationRequest,
)
from src.features.pdm_features import (
    AI4I_LEAKAGE_COLUMNS,
    AI4I_IDENTIFIER_COLUMNS,
    prepare_ai4i_splits,
)
from src.utils.config_loader import get_project_root


class TestExplainerInitialization:
    """Verifies explainer loading, model invariance, and feature space alignment."""

    def test_ai4i_explainer_loading(self):
        """AI4I XGBoost explainer loads with 10 features, threshold 0.91, and valid base value."""
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "failure_classifier.joblib"
        b = joblib.load(model_path)

        explainer = ShapExplainer(
            model=b["model"],
            feature_names=b["feature_names"],
            model_type="classifier",
            decision_threshold=0.91
        )

        assert explainer.model_type == "classifier"
        assert len(explainer.feature_names) == 10
        assert explainer.decision_threshold == 0.91
        assert isinstance(explainer.base_value, float)

    def test_cmapss_explainer_loading(self):
        """NASA C-MAPSS Random Forest explainer loads with 48 features and valid base cycles."""
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "rul_regressor.joblib"
        b = joblib.load(model_path)

        explainer = ShapExplainer(
            model=b["model"],
            feature_names=b["feature_names"],
            model_type="regressor",
            decision_threshold=0.0
        )

        assert explainer.model_type == "regressor"
        assert len(explainer.feature_names) == 48
        assert 50.0 < explainer.base_value < 125.0  # Training mean RUL ~86.5 cycles


class TestLeakageAndFeatureIntegrity:
    """Guarantees strict leakage exclusions and zero contamination."""

    def test_excluded_features_never_in_explainer(self):
        """Barred leakage columns must NEVER appear in explainer feature space."""
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "failure_classifier.joblib"
        b = joblib.load(model_path)
        feature_names = set(b["feature_names"])

        for col in AI4I_LEAKAGE_COLUMNS + AI4I_IDENTIFIER_COLUMNS:
            assert col not in feature_names, f"Leakage column '{col}' leaked into feature names!"
            assert col in EXCLUDED_LEAKAGE_DICTIONARY

    def test_feature_dictionary_covers_all_model_features(self):
        """All 10 AI4I model features must have documented human-readable semantics."""
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "failure_classifier.joblib"
        b = joblib.load(model_path)

        for feat in b["feature_names"]:
            meta = get_feature_metadata(feat)
            assert "display_name" in meta
            assert "unit" in meta
            assert "domain_interpretation" in meta
            assert len(meta["domain_interpretation"]) > 10


class TestAdditiveShapConsistency:
    """Verifies mathematical additive check: model_output == base_value + sum(SHAP)."""

    def test_ai4i_log_odds_additive_identity(self):
        """
        In log-odds (margin) space:
        raw_margin == base_value + sum(SHAP) within 1e-4 tolerance.
        """
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "failure_classifier.joblib"
        b = joblib.load(model_path)

        df_raw = pd.read_csv(root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv")
        splits = prepare_ai4i_splits(df_raw, random_state=42)
        X_test = splits["X_test"][b["feature_names"]]

        explainer = ShapExplainer(
            model=b["model"],
            feature_names=b["feature_names"],
            model_type="classifier",
            decision_threshold=0.91
        )

        # Test on 5 random observations
        sample_batch = X_test.iloc[:5]
        for idx in range(len(sample_batch)):
            res = explainer.explain_local(sample_batch, sample_index=idx)
            assert res["additive_error"] < 1e-4, f"Additive check failed for sample {idx}: {res['additive_error']}"
            # Verify probability mapping: prob == sigmoid(raw_margin)
            expected_prob = 1.0 / (1.0 + math.exp(-res["raw_margin"]))
            assert pytest.approx(res["probability"], abs=1e-3) == expected_prob

    def test_cmapss_cycles_additive_identity(self):
        """
        In cycles space:
        predicted_rul == base_value + sum(SHAP) within 1e-4 tolerance.
        """
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "rul_regressor.joblib"
        b = joblib.load(model_path)

        explainer = ShapExplainer(
            model=b["model"],
            feature_names=b["feature_names"],
            model_type="regressor",
            decision_threshold=0.0
        )

        dummy_sample = np.ones((1, 48)) * 0.5
        res = explainer.explain_local(dummy_sample)
        assert res["additive_error"] < 1e-4


class TestPredictionInvariance:
    """Verifies that running SHAP explanations NEVER modifies model predictions."""

    def test_predictions_unchanged_before_and_after_shap(self):
        """Model predict_proba output before SHAP must match output after SHAP."""
        root = get_project_root()
        model_path = root / "models" / "predictive_maintenance" / "failure_classifier.joblib"
        b = joblib.load(model_path)
        model = b["model"]

        df_raw = pd.read_csv(root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv")
        splits = prepare_ai4i_splits(df_raw, random_state=42)
        X_sample = splits["X_test"][b["feature_names"]].iloc[:10]

        # Prior predictions
        probs_before = model.predict_proba(X_sample)[:, 1]

        # Initialize explainer & explain
        explainer = ShapExplainer(model=model, feature_names=b["feature_names"], decision_threshold=0.91)
        _ = explainer.explain_global(X_sample)
        for i in range(len(X_sample)):
            _ = explainer.explain_local(X_sample, sample_index=i)

        # Posterior predictions
        probs_after = model.predict_proba(X_sample)[:, 1]

        np.testing.assert_array_almost_equal(probs_before, probs_after, decimal=8)


class TestRepresentativeLocalCases:
    """Verifies coverage of actual TP, TN, FP, FN test observations."""

    def test_local_cases_artifact_exists_and_valid(self):
        """Verifies models/explainability/ai4i_local_cases.json contains all 4 quadrants."""
        root = get_project_root()
        cases_file = root / "models" / "explainability" / "ai4i_local_cases.json"
        assert cases_file.exists(), f"Local cases JSON missing at: {cases_file}"

        with open(cases_file, "r", encoding="utf-8") as f:
            cases = json.load(f)

        for q in ["true_positive", "true_negative", "false_positive", "false_negative"]:
            assert q in cases, f"Quadrant {q} missing from local cases!"
            c = cases[q]
            assert "predicted_probability" in c
            assert "raw_margin" in c
            assert "base_value" in c
            assert "top_positive_contributors" in c
            assert "top_negative_contributors" in c
            assert "human_readable_narrative" in c
            assert c["decision_threshold"] == 0.91
            assert c["additive_error"] < 1e-4

        # Specific quadrant sanity
        assert cases["true_positive"]["actual_label"] == 1
        assert cases["true_positive"]["predicted_probability"] >= 0.91

        assert cases["true_negative"]["actual_label"] == 0
        assert cases["true_negative"]["predicted_probability"] < 0.91

        assert cases["false_positive"]["actual_label"] == 0
        assert cases["false_positive"]["predicted_probability"] >= 0.91

        assert cases["false_negative"]["actual_label"] == 1
        assert cases["false_negative"]["predicted_probability"] < 0.91


class TestServiceLayerAndMachine2:
    """Tests ExplanationService facade, Pydantic schemas, and Machine 2 disclaimers."""

    def test_service_single_reading_explanation(self):
        """Verifies ExplanationService.explain_ai4i_reading with Pydantic request."""
        service = ExplanationService()
        req = LocalExplanationRequest(
            machine_id="M2",
            air_temperature_k=298.0,
            process_temperature_k=308.0,
            rotational_speed_rpm=1500.0,
            torque_nm=40.0,
            tool_wear_min=50.0,
            product_type="M"
        )
        res = service.explain_ai4i_reading(req)

        assert res.machine_id == "M2"
        assert res.decision_threshold == 0.91
        assert 0.0 <= res.probability <= 1.0
        assert len(res.ranked_contributions) == 10
        assert "SHAP identifies feature contributions" in res.causality_disclaimer

    def test_machine2_synthetic_explanation_and_disclaimers(self):
        """Verifies Machine 2 scenario explanation with explicit causality and shift notices."""
        service = ExplanationService()
        req = Machine2ExplanationRequest(
            machine_id="M2",
            vibration_mms=4.15,
            temperature_c=52.0,
            ambient_temperature_c=25.0,
            rotational_speed_rpm=1420.0,
            torque_nm=58.0,
            tool_wear_min=190.0
        )
        res = service.explain_machine2_scenario(req)

        assert res.machine_id == "M2"
        assert res.is_synthetic_vibration_alert is True
        assert res.synthetic_vibration_trigger == 3.80
        assert res.empirical_decision_threshold == 0.91
        assert len(res.top_contributing_features) <= 5

        # Strict wording checks
        assert "DISTRIBUTION SHIFT NOTICE" in res.distribution_shift_warning
        assert "does NOT prove that vibration or temperature physically caused" in res.causality_disclaimer
        assert "contributes" in res.human_readable_narrative or "associated" in res.human_readable_narrative
        assert "causes failure" not in res.human_readable_narrative.lower()

    def test_deterministic_local_explanation(self):
        """Two identical explanation requests must yield identical SHAP values and narrative."""
        service = ExplanationService()
        req = LocalExplanationRequest(machine_id="M1", rotational_speed_rpm=1400.0, torque_nm=55.0)
        res1 = service.explain_ai4i_reading(req)
        res2 = service.explain_ai4i_reading(req)

        assert res1.probability == res2.probability
        assert res1.raw_margin == res2.raw_margin
        assert res1.human_readable_narrative == res2.human_readable_narrative
        assert len(res1.ranked_contributions) == len(res2.ranked_contributions)
        for i in range(len(res1.ranked_contributions)):
            assert res1.ranked_contributions[i].shap_value == res2.ranked_contributions[i].shap_value

    def test_safe_handling_of_missing_or_partial_features(self):
        """Missing feature columns are imputed with 0.0 without throwing errors."""
        service = ExplanationService()
        partial_dict = {"rotational_speed_rpm": 1600.0, "torque_nm": 30.0}
        res = service.explain_ai4i_reading(partial_dict)

        assert res.machine_id == "M2"
        assert res.probability >= 0.0
        assert len(res.ranked_contributions) == 10

    def test_global_importance_csv_matches_model_features(self):
        """ai4i_global_importance.csv has exactly 10 rows and non-negative mean_abs_shap."""
        root = get_project_root()
        csv_path = root / "models" / "explainability" / "ai4i_global_importance.csv"
        assert csv_path.exists()

        df_global = pd.read_csv(csv_path)
        assert len(df_global) == 10
        assert "mean_abs_shap" in df_global.columns
        assert (df_global["mean_abs_shap"] >= 0).all()
        assert df_global["mean_abs_shap"].iloc[0] > df_global["mean_abs_shap"].iloc[-1]
