import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
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
def root():
    return get_project_root()


def test_random_seed_reproducibility(root):
    for task in EXPECTED_TASKS:
        with open(root / "models" / "tuned" / task / "tuning_config.json") as f:
            cfg = json.load(f)
        assert cfg["random_seed"] == 42
        assert cfg["tuning_performed"] is True


def test_model_loading_and_inference(root):
    for task in EXPECTED_TASKS:
        t_path = root / "models" / "tuned" / task
        with open(t_path / "tuning_metadata.json") as f:
            meta = json.load(f)

        model_path = t_path / "locked_tuned_model.joblib"
        assert model_path.exists()
        model = joblib.load(model_path)

        dummy_input = np.zeros((2, meta["features_count"]))
        if hasattr(model, "predict"):
            preds = model.predict(dummy_input)
            assert len(preds) == 2
        elif hasattr(model, "score_samples"):
            scores = model.score_samples(dummy_input)
            assert len(scores) == 2


def test_canonical_checksum_immutable(root):
    csv_path = root / "data" / "synthetic" / "auto_components" / "operational_losses.csv"
    assert csv_path.exists()
    hasher = hashlib.md5()
    with open(csv_path, "rb") as f:
        hasher.update(f.read())
    digest = hasher.hexdigest().upper()
    assert digest == "34B12582B32D81E3121429C55EBF74E8"
