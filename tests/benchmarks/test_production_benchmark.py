import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def production_benchmark_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "manufacturing_production"


def test_production_artifacts_exist(production_benchmark_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (production_benchmark_dir / fname).exists(), f"Missing artifact: {fname}"


def test_production_metadata_integrity(production_benchmark_dir):
    with open(production_benchmark_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "manufacturing_production"
    assert meta["task"] == "bottleneck_dispatch_classification"
    assert meta["tuning_status"] == "NOT_STARTED"
    assert meta["champion_model"] == "Random_Forest_Weighted"
    assert meta["features_count"] == 12


def test_production_test_metrics(production_benchmark_dir):
    with open(production_benchmark_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["pr_auc"] > 0.25
    assert metrics["accuracy"] > 0.50
    assert metrics["roc_auc"] > 0.50


def test_production_model_inference(production_benchmark_dir):
    model_path = production_benchmark_dir / "locked_baseline_model.joblib"
    model = joblib.load(model_path)
    dummy_input = np.zeros((2, 12))
    preds = model.predict(dummy_input)
    assert len(preds) == 2

