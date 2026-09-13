import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def cmapss_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "cmapss"


def test_cmapss_artifacts_exist(cmapss_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (cmapss_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_cmapss_metadata_integrity(cmapss_benchmark_dir):
    with open(cmapss_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "cmapss"
    assert meta["task"] == "remaining_useful_life_regression"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "XGBoost_Regressor"
    assert meta["features_count"] == 95


def test_cmapss_test_metrics(cmapss_benchmark_dir):
    with open(cmapss_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["rmse"] < 18.0
    assert metrics["mae"] < 15.0
    assert metrics["r2"] > 0.80
    assert metrics["wape"] < 0.20


def test_cmapss_model_inference(cmapss_benchmark_dir):
    model_path = cmapss_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 95))
    preds = model.predict(dummy_input)
    assert len(preds) == 2

