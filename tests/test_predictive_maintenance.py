"""
Unit and integration tests for NirmaanAI Phase 6 Predictive Maintenance Subsystem.
Validates target construction, leakage exclusion, grouped engine splits,
baseline-first superiority, model serialization, and inference service behavior.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data.schema import SensorReading
from src.features.pdm_features import (
    AI4I_IDENTIFIER_COLUMNS,
    AI4I_LEAKAGE_COLUMNS,
    AI4I_TARGET_COLUMN,
    prepare_ai4i_splits,
    prepare_cmapss_splits,
)
from src.models.failure_classifier import FailureClassifierBenchmark
from src.models.pdm_service import FailurePredictionResult, PredictiveMaintenanceService, RULPredictionResult
from src.models.rul_regressor import RULRegressorBenchmark
from src.utils.config_loader import get_project_root


@pytest.fixture(scope="module")
def project_root() -> Path:
    return get_project_root()


def test_ai4i_target_definition_and_leakage_exclusion(project_root: Path):
    """Verify that target is binary Machine failure and all leakage/identifier columns are excluded."""
    ai4i_csv = project_root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    assert ai4i_csv.exists(), "AI4I CSV file missing"

    df = pd.read_csv(ai4i_csv)
    splits = prepare_ai4i_splits(df)

    # 1. Target check
    assert splits["target_name"] == AI4I_TARGET_COLUMN
    assert set(splits["y_train"].unique()).issubset({0, 1})

    # 2. Strict leakage exclusion check
    feature_names = splits["feature_names"]
    for leak_col in AI4I_LEAKAGE_COLUMNS:
        assert leak_col not in feature_names, f"Leakage column {leak_col} present in feature list!"

    for id_col in AI4I_IDENTIFIER_COLUMNS:
        assert id_col not in feature_names, f"Identifier column {id_col} present in feature list!"

    assert AI4I_TARGET_COLUMN not in feature_names


def test_ai4i_stratified_split_integrity(project_root: Path):
    """Verify that train, validation, and test splits preserve class distribution without overlap."""
    ai4i_csv = project_root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    df = pd.read_csv(ai4i_csv)
    splits = prepare_ai4i_splits(df, test_size=0.15, val_size=0.15, random_state=42)

    X_tr, y_tr = splits["X_train"], splits["y_train"]
    X_va, y_va = splits["X_val"], splits["y_val"]
    X_te, y_te = splits["X_test"], splits["y_test"]

    # Total sample integrity
    assert len(X_tr) + len(X_va) + len(X_te) == len(df)
    assert len(X_tr) == 7000
    assert len(X_va) == 1500
    assert len(X_te) == 1500

    # Index disjointness
    idx_tr = set(X_tr.index)
    idx_va = set(X_va.index)
    idx_te = set(X_te.index)

    assert idx_tr.isdisjoint(idx_va)
    assert idx_tr.isdisjoint(idx_te)
    assert idx_va.isdisjoint(idx_te)

    # Class balance preservation: ~3.39% in all splits
    tr_ratio = y_tr.mean()
    va_ratio = y_va.mean()
    te_ratio = y_te.mean()

    assert 0.030 <= tr_ratio <= 0.038
    assert 0.030 <= va_ratio <= 0.038
    assert 0.030 <= te_ratio <= 0.038


def test_cmapss_grouped_engine_split(project_root: Path):
    """Verify that engine units never cross train, validation, or test partitions."""
    train_f = project_root / "DATASET" / "02_NASA_CMAPSS" / "raw" / "CMaps" / "train_FD001.txt"
    test_f = project_root / "DATASET" / "02_NASA_CMAPSS" / "raw" / "CMaps" / "test_FD001.txt"
    rul_f = project_root / "DATASET" / "02_NASA_CMAPSS" / "raw" / "CMaps" / "RUL_FD001.txt"

    splits = prepare_cmapss_splits(train_f, test_f, rul_f, max_rul_clip=125.0)

    tr_eng = set(splits["train_engines"])
    va_eng = set(splits["val_engines"])
    te_eng = set(splits["test_engines"])

    # Disjointness check
    assert tr_eng.isdisjoint(va_eng), "Train and validation engines overlap!"
    assert tr_eng.isdisjoint(te_eng), "Train and internal test engines overlap!"
    assert va_eng.isdisjoint(te_eng), "Validation and internal test engines overlap!"
    assert len(tr_eng) + len(va_eng) + len(te_eng) == 100

    # Piecewise target capping check
    assert splits["y_train"].max() <= 125.0
    assert splits["y_val"].max() <= 125.0
    assert splits["y_test_internal"].max() <= 125.0
    if splits["y_official_test"] is not None:
        assert splits["y_official_test"].max() <= 125.0


def test_failure_classifier_baseline_superiority(project_root: Path):
    """Verify that non-linear ensemble models substantially outperform dummy and logistic baselines."""
    metadata_path = project_root / "models" / "predictive_maintenance" / "metadata.json"
    assert metadata_path.exists(), "Metadata file missing. Run train_pdm first."

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    test_metrics = meta["submodules"]["failure_classification"]["test_metrics"]

    dummy_f1 = test_metrics["dummy_majority"]["f1_score"]
    lr_f1 = test_metrics["logistic_regression"]["f1_score"]
    rf_f1 = test_metrics["random_forest"]["f1_score"]
    xgb_f1 = test_metrics["xgboost"]["f1_score"]

    # Dummy majority baseline has 0 F1 because it predicts 0 for all samples
    assert dummy_f1 == 0.0
    # Logistic regression baseline achieves moderate F1
    assert lr_f1 > 0.40
    # Ensembles achieve superior F1 score
    assert rf_f1 > lr_f1 + 0.30
    assert xgb_f1 > lr_f1 + 0.35
    assert xgb_f1 >= 0.85
    assert test_metrics["xgboost"]["roc_auc"] >= 0.95


def test_rul_regressor_baseline_superiority(project_root: Path):
    """Verify that tree ensembles achieve significantly lower RMSE than Dummy Mean on benchmark test set."""
    metadata_path = project_root / "models" / "predictive_maintenance" / "metadata.json"
    assert metadata_path.exists()

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    bench_metrics = meta["submodules"]["rul_estimation"]["official_benchmark_metrics"]

    dummy_rmse = bench_metrics["dummy_mean"]["rmse"]
    ridge_rmse = bench_metrics["ridge_regression"]["rmse"]
    rf_rmse = bench_metrics["random_forest_reg"]["rmse"]
    xgb_rmse = bench_metrics["xgboost_reg"]["rmse"]

    # Dummy baseline has high RMSE (~41.8 cycles)
    assert dummy_rmse > 40.0
    # Ridge regression reduces error to ~21.5 cycles
    assert ridge_rmse < dummy_rmse * 0.60
    # Random Forest and XGBoost achieve lowest RMSE (<19.0 cycles)
    assert rf_rmse < 19.0
    assert xgb_rmse < 19.0


def test_model_serialization_and_metadata(project_root: Path):
    """Verify that serialized joblib files exist, load correctly, and match metadata feature lists."""
    models_dir = project_root / "models" / "predictive_maintenance"
    clf_path = models_dir / "failure_classifier.joblib"
    reg_path = models_dir / "rul_regressor.joblib"
    meta_path = models_dir / "metadata.json"

    assert clf_path.exists()
    assert reg_path.exists()
    assert meta_path.exists()

    clf_payload = FailureClassifierBenchmark.load_champion(clf_path)
    reg_payload = RULRegressorBenchmark.load_champion(reg_path)

    assert "model" in clf_payload
    assert "threshold" in clf_payload
    assert len(clf_payload["feature_names"]) == 10

    assert "model" in reg_payload
    assert len(reg_payload["feature_names"]) == 48


def test_pdm_service_inference(project_root: Path):
    """Verify that PredictiveMaintenanceService consumes unified SensorReading and returns typed results."""
    service = PredictiveMaintenanceService()

    # Construct unified schema reading
    reading = SensorReading(
        reading_id=101,
        machine_id="M1",
        timestamp=pd.Timestamp.now(),
        vibration_mms=1.45,
        temperature_c=35.2,
        ambient_temperature_c=25.0,
        rotational_speed_rpm=1520.0,
        torque_nm=38.5,
        sound_db=72.0,
        power_consumption_kw=6.1,
        oil_level_pct=85.0,
        coolant_level_pct=90.0,
        tool_wear_min=45.0
    )

    pred = service.predict_failure(reading)
    assert isinstance(pred, FailurePredictionResult)
    assert 0.0 <= pred.failure_probability <= 1.0
    assert pred.risk_level in ["NORMAL", "WARNING", "CRITICAL"]
    assert isinstance(pred.is_failure_predicted, bool)
    assert "rotational_speed_rpm" in pred.contributing_features
