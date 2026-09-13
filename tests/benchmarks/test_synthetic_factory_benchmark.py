import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def synthetic_factory_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "synthetic_factory"


def test_synthetic_factory_artifacts_exist(synthetic_factory_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (synthetic_factory_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_synthetic_factory_metadata_integrity(synthetic_factory_benchmark_dir):
    with open(synthetic_factory_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "synthetic_factory"
    assert meta["task"] == "factory_telemetry_anomaly_tracking"
    assert meta["epistemic_status"] == "CONTROLLED_SYNTHETIC"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "Isolation_Forest_Detector"
    assert meta["features_count"] == 20


def test_synthetic_factory_test_metrics(synthetic_factory_benchmark_dir):
    with open(synthetic_factory_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert "mean_anomaly_score" in metrics
    assert metrics["mean_anomaly_score"] < 0
    assert metrics["std_anomaly_score"] > 0


def test_synthetic_factory_model_inference(synthetic_factory_benchmark_dir):
    model_path = synthetic_factory_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 20))
    scores = model.score_samples(dummy_input)
    assert len(scores) == 2
