"""
Independent Unit & Integration Tests for UCI Electricity MT_124 Preprocessor.
Validates:
- Chronological split (t_train < t_val < t_test)
- Scaler fit on training timeline only
- Absolute prohibition of random row shuffling and synthetic timestamp creation
"""

import numpy as np
import pandas as pd
import pytest

from src.features.electricity_features import extract_electricity_features
from src.preprocessing.electricity_preprocessor import ElectricityPreprocessor


@pytest.fixture
def electricity_preprocessor():
    return ElectricityPreprocessor(random_state=42)


def test_electricity_chronological_split(electricity_preprocessor):
    """Ensure strict chronological partition: train < val < test with zero time inversion."""
    raw_df, _, _ = extract_electricity_features()
    cleaned_df, report = electricity_preprocessor.audit_and_clean(raw_df)

    train_df, val_df, test_df = electricity_preprocessor.split_dataset(cleaned_df)

    # Max train timestamp must be strictly before min val timestamp
    train_max_t = pd.to_datetime(train_df["timestamp"]).max()
    val_min_t = pd.to_datetime(val_df["timestamp"]).min()
    val_max_t = pd.to_datetime(val_df["timestamp"]).max()
    test_min_t = pd.to_datetime(test_df["timestamp"]).min()

    assert train_max_t < val_min_t, "Train timeline leaks into validation!"
    assert val_max_t < test_min_t, "Validation timeline leaks into test!"

    assert report["validation_status"] == "PASS"
    assert report["negative_load_records"] == 0


def test_electricity_scaler_fit_on_train_only(electricity_preprocessor):
    """Ensure StandardScaler uses only train timeline statistics."""
    raw_df, _, _ = extract_electricity_features()
    cleaned_df, _ = electricity_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = electricity_preprocessor.split_dataset(cleaned_df)

    electricity_preprocessor.fit_train(train_df)
    assert electricity_preprocessor.is_fitted

    feat = "hour"
    feat_idx = electricity_preprocessor.feature_cols.index(feat)
    fitted_mean = electricity_preprocessor.scaler.mean_[feat_idx]
    train_mean = train_df[feat].mean()

    assert np.isclose(fitted_mean, train_mean, rtol=1e-5)


def test_electricity_prohibition_of_sampling(electricity_preprocessor):
    """Verify that sampling is explicitly declared NOT REQUIRED / PROHIBITED."""
    raw_df, _, _ = extract_electricity_features()
    cleaned_df, _ = electricity_preprocessor.audit_and_clean(raw_df)
    train_df, _, _ = electricity_preprocessor.split_dataset(cleaned_df)

    electricity_preprocessor.fit_train(train_df)
    train_proc = electricity_preprocessor.transform(train_df)

    sampled_df, meta = electricity_preprocessor.evaluate_sampling(train_proc)

    assert meta["is_sampling_required"] is False
    assert meta["sampling_decision"] == "SAMPLING_NOT_REQUIRED"
    assert meta["sampling_allowed"] is False
    assert len(sampled_df) == len(train_proc)
