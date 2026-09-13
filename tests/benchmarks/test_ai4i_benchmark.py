import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def ai4i_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "ai4i"


def test_ai4i_artifacts_exist(ai4i_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (ai4i_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_ai4i_metadata_integrity(ai4i_benchmark_dir):
    with open(ai4i_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "ai4i"
    assert meta["task"] == "machine_failure_classification"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "Random_Forest_Natural"
    assert meta["features_count"] == 13


def test_ai4i_test_metrics(ai4i_benchmark_dir):
    with open(ai4i_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["pr_auc"] >= 0.85
    assert metrics["roc_auc"] >= 0.90
    assert metrics["accuracy"] >= 0.95
    assert metrics["f1"] >= 0.80


def test_ai4i_model_inference(ai4i_benchmark_dir):
    model_path = ai4i_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 13))
    preds = model.predict(dummy_input)
    assert len(preds) == 2
