"""
Focused Invariant Tests for Industrial IoT 2040 RUL Split-Leakage Audit.
Verifies:
- Machine_ID uniquely identifies exactly one row in the source dataset (0 repeated machine snapshots).
- Entity overlap across train, validation, and test partitions is strictly zero.
- Confirms the random 70/15/15 row split is naturally isomorphic to an entity-grouped split.
"""

from pathlib import Path
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.utils.config_loader import get_project_root


@pytest.fixture(scope="session")
def industrial_iot_raw_entities():
    root = get_project_root()
    csv_path = root / "DATASET" / "05_INDUSTRIAL_IOT" / "raw" / "factory_sensor_simulator_2040.csv"
    assert csv_path.exists(), f"Source dataset missing: {csv_path}"
    # Read only Machine_ID column
    return pd.read_csv(csv_path, usecols=["Machine_ID"])["Machine_ID"]


def test_source_dataset_machine_uniqueness(industrial_iot_raw_entities):
    """Verify that every row in the source Industrial IoT dataset has a unique Machine_ID."""
    total_rows = len(industrial_iot_raw_entities)
    unique_entities = industrial_iot_raw_entities.nunique()

    assert total_rows == 500000, f"Expected 500,000 rows, got {total_rows}"
    assert unique_entities == 500000, f"Expected 500,000 unique machines, got {unique_entities}"
    assert not industrial_iot_raw_entities.duplicated().any(), "Repeated machine snapshots detected in raw dataset!"


def test_zero_entity_leakage_across_partitions(industrial_iot_raw_entities):
    """
    Verify that applying the exact 70/15/15 split produces zero entity overlap across train, val, and test:
    train intersect val == 0
    train intersect test == 0
    val intersect test == 0
    """
    X = industrial_iot_raw_entities
    y = pd.Series(range(len(X)))  # Dummy target for split preservation

    X_train, X_temp, _, y_temp = train_test_split(X, y, test_size=0.30, random_state=42)
    X_val, X_test, _, _ = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42)

    set_train = set(X_train)
    set_val = set(X_val)
    set_test = set(X_test)

    assert len(set_train) == 350000
    assert len(set_val) == 75000
    assert len(set_test) == 75000

    # Invariant: Zero overlap between any pair of partitions
    assert len(set_train.intersection(set_val)) == 0, "Leakage detected: Machines overlap between Train and Val!"
    assert len(set_train.intersection(set_test)) == 0, "Leakage detected: Machines overlap between Train and Test!"
    assert len(set_val.intersection(set_test)) == 0, "Leakage detected: Machines overlap between Val and Test!"
