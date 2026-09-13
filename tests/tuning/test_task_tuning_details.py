import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def tuned_dir():
    root = get_project_root()
    return root / "models" / "tuned"


def test_production_tuning_details(tuned_dir):
    p_dir = tuned_dir / "manufacturing_production"
    with open(p_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "BASELINE_RETAINED"
    assert imp["baseline_val"] > 0.40


def test_secom_tuning_details(tuned_dir):
    s_dir = tuned_dir / "secom"
    with open(s_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "TUNED_MODEL_ACCEPTED"
    assert imp["val_abs_improvement"] > 0.15
    assert imp["val_rel_improvement_pct"] > 50.0


def test_industrial_iot_failure_tuning_details(tuned_dir):
    f_dir = tuned_dir / "industrial_iot_failure"
    with open(f_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "BASELINE_RETAINED"
    assert imp["baseline_val"] > 0.70


def test_ai4i_tuning_details(tuned_dir):
    a_dir = tuned_dir / "ai4i"
    with open(a_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "BASELINE_RETAINED"
    assert imp["baseline_val"] > 0.90


def test_cmapss_tuning_details(tuned_dir):
    c_dir = tuned_dir / "cmapss"
    with open(c_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "TUNED_MODEL_ACCEPTED"
    assert imp["val_abs_improvement"] > 1.0  # Reduction in RMSE cycles


def test_electricity_tuning_details(tuned_dir):
    e_dir = tuned_dir / "electricity"
    with open(e_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "TUNED_MODEL_ACCEPTED"
    assert imp["val_abs_improvement"] > 0.002  # Reduction in WAPE


def test_industrial_iot_rul_tuning_details(tuned_dir):
    r_dir = tuned_dir / "industrial_iot_rul"
    with open(r_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "BASELINE_RETAINED"


def test_defects_tuning_details(tuned_dir):
    d_dir = tuned_dir / "manufacturing_defects"
    with open(d_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "TUNED_MODEL_ACCEPTED"
    assert imp["val_abs_improvement"] >= 0.005


def test_textile_tuning_details(tuned_dir):
    t_dir = tuned_dir / "textile"
    with open(t_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "TUNED_MODEL_ACCEPTED"
    assert imp["val_abs_improvement"] > 0.5


def test_synthetic_factory_tuning_details(tuned_dir):
    sf_dir = tuned_dir / "synthetic_factory"
    with open(sf_dir / "improvement_summary.json") as f:
        imp = json.load(f)
    assert imp["decision_status"] == "BASELINE_RETAINED"
