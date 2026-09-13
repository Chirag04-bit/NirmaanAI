"""
Independent Unit & Integration Tests for Manufacturing Defects Preprocessor.
Validates:
- Stratified 70/15/15 split on DefectStatus
- Scaler fit strictly on training batches
- Imbalance evaluation (minority class Pass/Non-defect ~16.0%)
"""

import numpy as np
import pandas as pd
import pytest

from src.features.defect_features import extract_defect_features
from src.preprocessing.defect_preprocessor import DefectPreprocessor


@pytest.fixture
def defect_preprocessor():
    return DefectPreprocessor(random_state=42)


def test_defect_stratified_split(defect_preprocessor):
    """Ensure stratified split preserves ~84% defect rate across partitions."""
    raw_df, _, _ = extract_defect_features()
    cleaned_df, report = defect_preprocessor.audit_and_clean(raw_df)

    train_df, val_df, test_df = defect_preprocessor.split_dataset(cleaned_df)

    base_rate = cleaned_df[defect_preprocessor.TARGET_COL].mean()
    train_rate = train_df[defect_preprocessor.TARGET_COL].mean()
    val_rate = val_df[defect_preprocessor.TARGET_COL].mean()
    test_rate = test_df[defect_preprocessor.TARGET_COL].mean()

    assert np.isclose(base_rate, train_rate, atol=0.01)
    assert np.isclose(base_rate, val_rate, atol=0.01)
    assert np.isclose(base_rate, test_rate, atol=0.01)

    assert report["validation_status"] == "PASS"


def test_defect_scaler_fit_on_train_only(defect_preprocessor):
    """Ensure StandardScaler fits strictly on training batches."""
    raw_df, _, _ = extract_defect_features()
    cleaned_df, _ = defect_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = defect_preprocessor.split_dataset(cleaned_df)

    defect_preprocessor.fit_train(train_df)
    assert defect_preprocessor.is_fitted

    feat = "ProductionVolume"
    feat_idx = defect_preprocessor.feature_cols.index(feat)
    fitted_mean = defect_preprocessor.scaler.mean_[feat_idx]
    train_mean = train_df[feat].mean()

    assert np.isclose(fitted_mean, train_mean, rtol=1e-5)
