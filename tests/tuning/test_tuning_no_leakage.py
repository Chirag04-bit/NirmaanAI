import json
from pathlib import Path
import pandas as pd
import pytest

from src.utils.config_loader import get_project_root


@pytest.fixture
def root():
    return get_project_root()


def test_industrial_iot_quarantine_integrity(root):
    # Failure predictors must not contain RUL or Machine_ID
    with open(root / "models" / "tuned" / "industrial_iot_failure" / "tuning_metadata.json") as f:
        fail_meta = json.load(f)
    assert "Remaining_Useful_Life_days" in fail_meta["quarantined_columns"]
    assert "Machine_ID" in fail_meta["quarantined_columns"]

    # RUL predictors must not contain Failure or Machine_ID
    with open(root / "models" / "tuned" / "industrial_iot_rul" / "tuning_metadata.json") as f:
        rul_meta = json.load(f)
    assert "Failure_Within_7_Days" in rul_meta["quarantined_columns"]
    assert "Machine_ID" in rul_meta["quarantined_columns"]


def test_cmapss_engine_isolation(root):
    train_df = pd.read_parquet(root / "models" / "processed" / "cmapss" / "train.parquet")
    val_df = pd.read_parquet(root / "models" / "processed" / "cmapss" / "val.parquet")
    test_df = pd.read_parquet(root / "models" / "processed" / "cmapss" / "test.parquet")

    train_engines = set(train_df["unit_number"].unique())
    val_engines = set(val_df["unit_number"].unique())
    test_engines = set(test_df["unit_number"].unique())

    assert len(train_engines.intersection(val_engines)) == 0
    assert len(train_engines.intersection(test_engines)) == 0
    assert len(val_engines.intersection(test_engines)) == 0


def test_electricity_chronological_ordering(root):
    train_df = pd.read_parquet(root / "models" / "processed" / "electricity" / "train.parquet")
    val_df = pd.read_parquet(root / "models" / "processed" / "electricity" / "val.parquet")
    test_df = pd.read_parquet(root / "models" / "processed" / "electricity" / "test.parquet")

    max_train_ts = train_df["timestamp"].max()
    min_val_ts = val_df["timestamp"].min()
    max_val_ts = val_df["timestamp"].max()
    min_test_ts = test_df["timestamp"].min()

    assert max_train_ts < min_val_ts
    assert max_val_ts < min_test_ts
