import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def defects_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "manufacturing_defects"


def test_defects_artifacts_exist(defects_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (defects_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_defects_metadata_integrity(defects_benchmark_dir):
    with open(defects_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "manufacturing_defects"
    assert meta["task"] == "manufacturing_defects_classification"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "Random_Forest_Natural"
    assert meta["features_count"] == 23


def test_defects_test_metrics(defects_benchmark_dir):
    with open(defects_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["roc_auc"] > 0.80
    assert metrics["f1"] > 0.90
    assert metrics["accuracy"] > 0.90


def test_defects_model_inference(defects_benchmark_dir):
    model_path = defects_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 23))
    preds = model.predict(dummy_input)
    assert len(preds) == 2
