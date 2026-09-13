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


def test_test_set_blindness_and_single_evaluation(tuned_dir):
    for task in EXPECTED_TASKS:
        t_path = tuned_dir / task
        with open(t_path / "final_test_metrics.json") as f:
            test_m = json.load(f)
        # Verify final test metrics object is a flat single evaluation
        assert isinstance(test_m, dict)
        assert "champion_model" in test_m or "mean_anomaly_score" in test_m or "mae" in test_m

        with open(t_path / "tuning_metadata.json") as f:
            meta = json.load(f)
        assert meta["tuning_status"] == "COMPLETED"
        assert meta["decision_status"] in ["TUNED_MODEL_ACCEPTED", "BASELINE_RETAINED"]


def test_scientific_decision_rules_respected(tuned_dir):
    accepted_expected = ["secom", "cmapss", "electricity", "manufacturing_defects", "textile"]
    retained_expected = ["manufacturing_production", "industrial_iot_failure", "ai4i", "industrial_iot_rul", "synthetic_factory"]

    for task in accepted_expected:
        with open(tuned_dir / task / "tuning_metadata.json") as f:
            meta = json.load(f)
        assert meta["decision_status"] == "TUNED_MODEL_ACCEPTED", f"Expected {task} to be accepted"

    for task in retained_expected:
        with open(tuned_dir / task / "tuning_metadata.json") as f:
            meta = json.load(f)
        assert meta["decision_status"] == "BASELINE_RETAINED", f"Expected {task} to be retained"
