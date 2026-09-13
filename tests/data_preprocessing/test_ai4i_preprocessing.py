"""
Independent Unit & Integration Tests for AI4I 2020 Preprocessor.
Validates:
- No leakage of failure modes (TWF, HDF, PWF, OSF, RNF) or IDs (UDI, Product ID)
- Stratified train/val/test split
- Scaler fit strictly on training numericals only
- Validation and test sets retain natural distribution and are NOT sampled
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.preprocessing.ai4i_preprocessor import AI4IPreprocessor
from src.utils.config_loader import get_project_root


@pytest.fixture
def ai4i_preprocessor():
    return AI4IPreprocessor(random_state=42)


def test_ai4i_leakage_exclusion(ai4i_preprocessor):
    """Ensure quarantined failure modes and IDs are completely excluded from predictor set."""
    from src.features.ai4i_features import extract_ai4i_features
    raw_df, _, _ = extract_ai4i_features()

    cleaned_df, report = ai4i_preprocessor.audit_and_clean(raw_df)

    for leaked in ai4i_preprocessor.QUARANTINED_COLS:
        assert leaked not in cleaned_df.columns, f"Leaked column {leaked} found in cleaned AI4I data!"

    assert report["validation_status"] == "PASS"
    assert report["duplicates_removed"] == 0


def test_ai4i_stratified_split_proportions(ai4i_preprocessor):
    """Ensure 70/15/15 stratified split preserves target positive rate across splits."""
    from src.features.ai4i_features import extract_ai4i_features
    raw_df, _, _ = extract_ai4i_features()
    cleaned_df, _ = ai4i_preprocessor.audit_and_clean(raw_df)

    train_df, val_df, test_df = ai4i_preprocessor.split_dataset(cleaned_df)

    # 10,000 total rows -> 7,000 train, 1,500 val, 1,500 test
    assert len(train_df) == 7000
    assert len(val_df) == 1500
    assert len(test_df) == 1500

    base_rate = cleaned_df["machine_failure"].mean()
    train_rate = train_df["machine_failure"].mean()
    val_rate = val_df["machine_failure"].mean()
    test_rate = test_df["machine_failure"].mean()

    # Stratified balance check
    assert np.isclose(base_rate, train_rate, atol=0.005)
    assert np.isclose(base_rate, val_rate, atol=0.005)
    assert np.isclose(base_rate, test_rate, atol=0.005)


def test_ai4i_scaler_fit_on_train_only(ai4i_preprocessor):
    """Verify that StandardScaler parameters are derived strictly from training data."""
    from src.features.ai4i_features import extract_ai4i_features
    raw_df, _, _ = extract_ai4i_features()
    cleaned_df, _ = ai4i_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = ai4i_preprocessor.split_dataset(cleaned_df)

    ai4i_preprocessor.fit_train(train_df)
    assert ai4i_preprocessor.is_fitted

    # Verify fitted mean matches training partition mean, NOT full cleaned_df mean
    feat = "air_temperature_k"
    feat_idx = ai4i_preprocessor.NUMERICAL_FEATURES.index(feat)
    fitted_mean = ai4i_preprocessor.scaler.mean_[feat_idx]
    actual_train_mean = train_df[feat].mean()
    full_mean = cleaned_df[feat].mean()

    assert np.isclose(fitted_mean, actual_train_mean, rtol=1e-5)
    # The training mean and full mean are slightly different due to split
    assert not np.isclose(fitted_mean, full_mean, rtol=1e-8)


def test_ai4i_sampling_train_only(ai4i_preprocessor):
    """Verify that sampling is applied only to training data; val/test remain pristine."""
    from src.features.ai4i_features import extract_ai4i_features
    raw_df, _, _ = extract_ai4i_features()
    cleaned_df, _ = ai4i_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = ai4i_preprocessor.split_dataset(cleaned_df)

    ai4i_preprocessor.fit_train(train_df)
    train_proc = ai4i_preprocessor.transform(train_df)

    sampled_train, meta = ai4i_preprocessor.evaluate_sampling(train_proc)

    assert meta["is_sampling_required"] is True
    assert meta["applied_to"] == "TRAIN_PARTITION_ONLY"
    assert meta["validation_and_test_untouched"] is True

    # Sampled training set is balanced (50% positive)
    assert np.isclose(sampled_train["machine_failure"].mean(), 0.5, atol=0.01)

    # Validation and test still have natural ~3.39% distribution
    assert val_df["machine_failure"].mean() < 0.05
    assert test_df["machine_failure"].mean() < 0.05
