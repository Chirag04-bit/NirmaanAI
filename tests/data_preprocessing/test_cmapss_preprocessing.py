"""
Independent Unit & Integration Tests for NASA C-MAPSS FD001 Preprocessor.
Validates:
- Engine-grouped split (zero engine overlap across train/val/test)
- Monotonic cycle continuity per engine
- RUL cap = 125 preserved
- Scaler fit strictly on training engines (1..70)
- Absolute prohibition of random row shuffling and SMOTE
"""

import numpy as np
import pandas as pd
import pytest

from src.features.cmapss_features import extract_cmapss_features
from src.preprocessing.cmapss_preprocessor import CMAPSSPreprocessor


@pytest.fixture
def cmapss_preprocessor():
    return CMAPSSPreprocessor(random_state=42)


def test_cmapss_engine_grouped_split(cmapss_preprocessor):
    """Verify that engines 1-70 are in train, 71-85 in val, and 86-100 in test with zero overlap."""
    raw_df, _, _ = extract_cmapss_features()
    cleaned_df, report = cmapss_preprocessor.audit_and_clean(raw_df)

    train_df, val_df, test_df = cmapss_preprocessor.split_dataset(cleaned_df)

    train_engines = set(train_df["unit_number"].unique())
    val_engines = set(val_df["unit_number"].unique())
    test_engines = set(test_df["unit_number"].unique())

    assert len(train_engines) == 70
    assert len(val_engines) == 15
    assert len(test_engines) == 15

    # Zero overlap
    assert train_engines.isdisjoint(val_engines)
    assert train_engines.isdisjoint(test_engines)
    assert val_engines.isdisjoint(test_engines)

    assert report["total_engines"] == 100
    assert report["trajectory_continuity_breaks"] == 0


def test_cmapss_rul_clipping_cap(cmapss_preprocessor):
    """Verify that the target RUL is strictly capped at 125 cycles."""
    raw_df, _, _ = extract_cmapss_features()
    cleaned_df, _ = cmapss_preprocessor.audit_and_clean(raw_df)

    assert cleaned_df["rul_clipped"].max() <= 125.0
    assert (cleaned_df["rul_clipped"] >= 0).all()


def test_cmapss_scaler_fit_on_train_engines_only(cmapss_preprocessor):
    """Verify StandardScaler parameters are computed strictly from training engines (1-70)."""
    raw_df, _, _ = extract_cmapss_features()
    cleaned_df, _ = cmapss_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = cmapss_preprocessor.split_dataset(cleaned_df)

    cmapss_preprocessor.fit_train(train_df)
    assert cmapss_preprocessor.is_fitted

    feat = "s2"
    feat_idx = cmapss_preprocessor.feature_cols.index(feat)
    fitted_mean = cmapss_preprocessor.scaler.mean_[feat_idx]
    actual_train_mean = train_df[feat].mean()
    full_mean = cleaned_df[feat].mean()

    assert np.isclose(fitted_mean, actual_train_mean, rtol=1e-5)
    assert not np.isclose(fitted_mean, full_mean, rtol=1e-8)


def test_cmapss_prohibition_of_sampling(cmapss_preprocessor):
    """Verify that sampling is explicitly declared NOT REQUIRED / PROHIBITED."""
    raw_df, _, _ = extract_cmapss_features()
    cleaned_df, _ = cmapss_preprocessor.audit_and_clean(raw_df)
    train_df, _, _ = cmapss_preprocessor.split_dataset(cleaned_df)

    cmapss_preprocessor.fit_train(train_df)
    train_proc = cmapss_preprocessor.transform(train_df)

    sampled_df, meta = cmapss_preprocessor.evaluate_sampling(train_proc)

    assert meta["is_sampling_required"] is False
    assert meta["sampling_decision"] == "SAMPLING_NOT_REQUIRED"
    assert meta["sampling_allowed"] is False
    assert len(sampled_df) == len(train_proc)
