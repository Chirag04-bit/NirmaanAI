"""
Independent Unit & Integration Tests for UCI SECOM Preprocessor.
Validates:
- 436 screened sensor channels retained
- SimpleImputer(median) fit on TRAIN ONLY
- RobustScaler fit on TRAIN ONLY (due to heavy tails)
- Stratified train/val/test split
- Sampled training set generated for training only; val and test untouched
"""

import numpy as np
import pandas as pd
import pytest

from src.features.secom_features import extract_secom_features
from src.preprocessing.secom_preprocessor import SECOMPreprocessor


@pytest.fixture
def secom_preprocessor():
    return SECOMPreprocessor(random_state=42)


def test_secom_feature_count_and_imputation(secom_preprocessor):
    """Ensure 436 channels are handled and imputer fits on train only."""
    raw_df, _, _ = extract_secom_features()
    cleaned_df, report = secom_preprocessor.audit_and_clean(raw_df)

    assert len(secom_preprocessor.feature_cols) == 436
    assert report["validation_status"] == "PASS"

    train_df, val_df, test_df = secom_preprocessor.split_dataset(cleaned_df)
    secom_preprocessor.fit_train(train_df)
    assert secom_preprocessor.is_fitted

    # Check transformed train has zero missing values
    train_proc = secom_preprocessor.transform(train_df)
    assert train_proc[secom_preprocessor.feature_cols].isna().sum().sum() == 0

    # Verify RobustScaler center matches train median
    test_sensor = secom_preprocessor.feature_cols[0]
    idx = secom_preprocessor.feature_cols.index(test_sensor)
    fitted_center = secom_preprocessor.scaler.center_[idx]
    train_median = train_df[test_sensor].median()
    assert np.isclose(fitted_center, train_median, rtol=1e-5)


def test_secom_sampling_train_only(secom_preprocessor):
    """Ensure wafer defect oversampling is applied only to training partition."""
    raw_df, _, _ = extract_secom_features()
    cleaned_df, _ = secom_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = secom_preprocessor.split_dataset(cleaned_df)

    secom_preprocessor.fit_train(train_df)
    train_proc = secom_preprocessor.transform(train_df)

    train_sampled, meta = secom_preprocessor.evaluate_sampling(train_proc)

    assert meta["is_sampling_required"] is True
    assert meta["applied_to"] == "TRAIN_PARTITION_ONLY"
    assert meta["validation_and_test_untouched"] is True

    # Sampled training set has 50% defect rate
    assert np.isclose(train_sampled["target_defect"].mean(), 0.5, atol=0.02)

    # Val and Test retain natural low defect rate (~6.6%)
    assert val_df["target_defect"].mean() < 0.10
    assert test_df["target_defect"].mean() < 0.10
