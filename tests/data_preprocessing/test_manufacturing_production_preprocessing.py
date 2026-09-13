"""
Independent Unit & Integration Tests for Manufacturing Production Preprocessor.
Validates:
- Strict quarantine of post-event diagnostic delay metrics
- Preservation of prospective dispatch features
- Job-sequence split
- Scaler fit strictly on training jobs
"""

import numpy as np
import pandas as pd
import pytest

from src.features.production_features import extract_production_features
from src.preprocessing.production_preprocessor import ProductionPreprocessor


@pytest.fixture
def production_preprocessor():
    return ProductionPreprocessor(random_state=42)


def test_production_post_event_quarantine(production_preprocessor):
    """Ensure realized delays, actual completion times, and final status are quarantined from prospective data."""
    raw_df, _, _ = extract_production_features()
    cleaned_df, report = production_preprocessor.audit_and_clean(raw_df)

    for col in production_preprocessor.POST_EVENT_QUARANTINED:
        assert col not in cleaned_df.columns, f"Post-event feature {col} leaked into prospective data!"

    # Prospective predictors must be retained
    assert "planned_duration_min" in cleaned_df.columns
    assert "planned_energy_rate" in cleaned_df.columns
    assert production_preprocessor.TARGET_COL in cleaned_df.columns


def test_production_split_and_scaler(production_preprocessor):
    """Verify 70/15/15 split and train-only scaler fitting."""
    raw_df, _, _ = extract_production_features()
    cleaned_df, _ = production_preprocessor.audit_and_clean(raw_df)
    train_df, val_df, test_df = production_preprocessor.split_dataset(cleaned_df)

    assert len(train_df) == 700
    assert len(val_df) == 150
    assert len(test_df) == 150

    production_preprocessor.fit_train(train_df)
    assert production_preprocessor.is_fitted

    feat = "planned_duration_min"
    feat_idx = production_preprocessor.feature_cols.index(feat)
    fitted_mean = production_preprocessor.scaler.mean_[feat_idx]
    train_mean = train_df[feat].mean()

    assert np.isclose(fitted_mean, train_mean, rtol=1e-5)
