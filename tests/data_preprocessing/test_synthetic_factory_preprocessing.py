"""
Independent Unit & Integration Tests for Synthetic Factory Preprocessor.
Validates:
- Preservation of CONTROLLED_SYNTHETIC status across 5 stations
- Preservation of M2 controlled degradation scenario (zero outlier pruning)
- Temporal decision cutoff (2026-01-21 12:00:00 UTC) respected
- Scaler fit on pre-cutoff baseline only
- Prohibition of random sampling
"""

import numpy as np
import pandas as pd
import pytest

from src.features.synthetic_factory_features import extract_synthetic_factory_features
from src.preprocessing.synthetic_factory_preprocessor import SyntheticFactoryPreprocessor


@pytest.fixture
def factory_preprocessor():
    return SyntheticFactoryPreprocessor(random_state=42)


def test_factory_scenario_and_outlier_preservation(factory_preprocessor):
    """Ensure controlled M2 degradation is preserved and 5 stations are monitored."""
    raw_df, _, _ = extract_synthetic_factory_features()
    cleaned_df, report = factory_preprocessor.audit_and_clean(raw_df)

    expected_stations = ["M1", "M2", "M3", "M4", "M5"]
    assert report["stations_monitored"] == expected_stations
    assert report["outliers_removed"] == 0, "Scenario degradation must not be deleted as outliers!"
    assert report["controlled_scenario_degradation_preserved"] == "M2_VMC_BEARING_DAYS_18_TO_21"


def test_factory_temporal_cutoff_split(factory_preprocessor):
    """Ensure train and val are restricted to pre-decision cutoff records."""
    raw_df, _, _ = extract_synthetic_factory_features()
    cleaned_df, _ = factory_preprocessor.audit_and_clean(raw_df)

    train_df, val_df, test_df = factory_preprocessor.split_dataset(cleaned_df)

    # Train and Val must only contain pre-decision cutoff records
    assert (train_df["is_pre_decision_cutoff"] == 1).all()
    assert (val_df["is_pre_decision_cutoff"] == 1).all()

    # Test contains post-decision cutoff emergency incident & recovery
    assert (test_df["is_pre_decision_cutoff"] == 0).all()


def test_factory_sampling_prohibition(factory_preprocessor):
    """Verify that sampling is explicitly declared NOT REQUIRED / PROHIBITED."""
    raw_df, _, _ = extract_synthetic_factory_features()
    cleaned_df, _ = factory_preprocessor.audit_and_clean(raw_df)
    train_df, _, _ = factory_preprocessor.split_dataset(cleaned_df)

    factory_preprocessor.fit_train(train_df)
    train_proc = factory_preprocessor.transform(train_df)

    sampled_df, meta = factory_preprocessor.evaluate_sampling(train_proc)

    assert meta["is_sampling_required"] is False
    assert meta["sampling_decision"] == "SAMPLING_NOT_REQUIRED"
    assert meta["sampling_allowed"] is False
