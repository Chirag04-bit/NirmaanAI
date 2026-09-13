import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def secom_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "secom"


def test_secom_artifacts_exist(secom_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (secom_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_secom_metadata_integrity(secom_benchmark_dir):
    with open(secom_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "secom"
    assert meta["task"] == "wafer_defect_classification"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "XGBoost_Weighted"


def test_secom_test_metrics(secom_benchmark_dir):
    with open(secom_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["roc_auc"] > 0.60
    assert metrics["pr_auc"] > 0.10
    assert metrics["accuracy"] > 0.90


def test_secom_model_inference(secom_benchmark_dir):
    model_path = secom_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    with open(secom_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)
    dummy_input = np.zeros((2, meta["features_count"]))
    preds = model.predict(dummy_input)
    assert len(preds) == 2
