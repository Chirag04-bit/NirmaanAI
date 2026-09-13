import json
from pathlib import Path
import pytest

from src.utils.config_loader import get_project_root


EXPECTED_TASKS = [
    "manufacturing_production",
    "secom",
    "industrial_iot_failure",
    "ai4i",
    "cmapss",
    "electricity",
    "industrial_iot_rul",
    "manufacturing_defects",
    "textile",
    "synthetic_factory",
]


@pytest.fixture
def tuned_dir():
    root = get_project_root()
    return root / "models" / "tuned"


@pytest.fixture
def benchmarks_dir():
    root = get_project_root()
    return root / "models" / "benchmarks"


def test_all_10_tuned_directories_exist(tuned_dir):
    for task in EXPECTED_TASKS:
        t_path = tuned_dir / task
        assert t_path.exists(), f"Tuned task directory missing: {task}"
        assert (t_path / "model_comparison.csv").exists()
        assert (t_path / "validation_metrics.json").exists()
        assert (t_path / "final_test_metrics.json").exists()
        assert (t_path / "tuning_config.json").exists()
        assert (t_path / "tuning_metadata.json").exists()
        assert (t_path / "locked_tuned_model.joblib").exists()
        assert (t_path / "improvement_summary.json").exists()


def test_baseline_artifacts_unmodified(benchmarks_dir):
    for task in EXPECTED_TASKS:
        b_path = benchmarks_dir / task
        assert b_path.exists()
        assert (b_path / "locked_baseline_model.joblib").exists()
        assert (b_path / "final_test_metrics.json").exists()
        assert (b_path / "training_config.json").exists()


def test_global_tuning_summary(tuned_dir):
    summary_path = tuned_dir / "global_tuning_summary.json"
    assert summary_path.exists()
    with open(summary_path) as f:
        summary = json.load(f)

    assert summary["total_tasks"] == 10
    assert summary["tasks_accepted"] == 5
    assert summary["tasks_retained"] == 5
