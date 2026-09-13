import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def textile_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "textile"


def test_textile_artifacts_exist(textile_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (textile_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_textile_metadata_integrity(textile_benchmark_dir):
    with open(textile_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "textile"
    assert meta["task"] == "loom_telemetry_anomaly_tracking"
    assert meta["epistemic_status"] == "CONTROLLED_SYNTHETIC"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "Isolation_Forest_Detector"
    assert meta["features_count"] == 16


def test_textile_test_metrics(textile_benchmark_dir):
    with open(textile_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert "mean_anomaly_score" in metrics
    assert metrics["mean_anomaly_score"] < 0  # Standard sklearn score_samples format
    assert metrics["std_anomaly_score"] > 0


def test_textile_model_inference(textile_benchmark_dir):
    model_path = textile_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 16))
    scores = model.score_samples(dummy_input)
    assert len(scores) == 2
