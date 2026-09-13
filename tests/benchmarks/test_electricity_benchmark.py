import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def electricity_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "electricity"


def test_electricity_artifacts_exist(electricity_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (electricity_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_electricity_metadata_integrity(electricity_benchmark_dir):
    with open(electricity_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "electricity"
    assert meta["task"] == "electricity_consumption_forecasting"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "XGBoost_Regressor"
    assert meta["features_count"] == 19


def test_electricity_test_metrics(electricity_benchmark_dir):
    with open(electricity_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["wape"] < 0.10
    assert metrics["r2"] > 0.90
    assert metrics["mae"] < 30.0


def test_electricity_model_inference(electricity_benchmark_dir):
    model_path = electricity_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 19))
    preds = model.predict(dummy_input)
    assert len(preds) == 2
