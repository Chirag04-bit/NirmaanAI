import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def iiot_failure_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "industrial_iot_failure"


@pytest.fixture
def iiot_rul_dir():
    root = get_project_root()
    return root / "models" / "benchmarks" / "industrial_iot_rul"


def test_industrial_iot_failure_artifacts_exist(iiot_failure_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (iiot_failure_dir / fname).exists(), f"Missing artifact: {fname}"


def test_industrial_iot_failure_target_quarantine(iiot_failure_dir):
    with open(iiot_failure_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert "Remaining_Useful_Life_days" in meta["quarantined_columns"]
    assert "Machine_ID" in meta["quarantined_columns"]
    assert meta["tuning_status"] == "NOT_STARTED"


def test_industrial_iot_failure_metrics(iiot_failure_dir):
    with open(iiot_failure_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["pr_auc"] > 0.65
    assert metrics["roc_auc"] > 0.90
    assert metrics["recall"] > 0.80


def test_industrial_iot_rul_artifacts_exist(iiot_rul_dir):
    expected_files = [
        "model_comparison.csv",
        "validation_metrics.json",
        "final_test_metrics.json",
        "training_config.json",
        "benchmark_metadata.json",
        "locked_baseline_model.joblib",
    ]
    for fname in expected_files:
        assert (iiot_rul_dir / fname).exists(), f"Missing artifact: {fname}"


def test_industrial_iot_rul_target_quarantine(iiot_rul_dir):
    with open(iiot_rul_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)

    assert "Failure_Within_7_Days" in meta["quarantined_columns"]
    assert "Machine_ID" in meta["quarantined_columns"]
    assert meta["tuning_status"] == "NOT_STARTED"


def test_industrial_iot_rul_metrics(iiot_rul_dir):
    with open(iiot_rul_dir / "final_test_metrics.json") as f:
        metrics = json.load(f)

    assert metrics["rmse"] < 60.0
    assert metrics["mae"] < 45.0
    assert metrics["r2"] > 0.90
    assert metrics["wape"] < 0.15
