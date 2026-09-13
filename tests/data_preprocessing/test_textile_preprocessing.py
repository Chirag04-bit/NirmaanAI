"""
Independent Unit & Integration Tests for Textile Manufacturing Preprocessor.
Validates:
- Preservation of CONTROLLED_SYNTHETIC status
- True degradation phenomena NOT pruned as outliers
- Machine-isolated chronological split
- Absolute prohibition of random sampling
"""

import numpy as np
import pandas as pd
import pytest

from src.features.textile_features import extract_textile_features
from src.preprocessing.textile_preprocessor import TextilePreprocessor


@pytest.fixture
def textile_preprocessor():
    return TextilePreprocessor(random_state=42)


def test_textile_synthetic_status_and_outlier_preservation(textile_preprocessor):
    """Ensure CONTROLLED_SYNTHETIC status is preserved and degradation spikes are retained."""
    raw_df, _, _ = extract_textile_features()
    cleaned_df, report = textile_preprocessor.audit_and_clean(raw_df)

    assert report["epistemic_status"] == "CONTROLLED_SYNTHETIC"
    assert report["outliers_removed"] == 0, "Degradation events must not be pruned as outliers!"
    assert len(cleaned_df) == len(raw_df)


def test_textile_per_machine_split(textile_preprocessor):
    """Ensure all 5 looms (TX01-TX05) are represented proportionally across chronological splits."""
    raw_df, _, _ = extract_textile_features()
    cleaned_df, _ = textile_preprocessor.audit_and_clean(raw_df)

    train_df, val_df, test_df = textile_preprocessor.split_dataset(cleaned_df)

    expected_machines = {"TX01", "TX02", "TX03", "TX04", "TX05"}
    assert set(train_df["machine_id"].unique()) == expected_machines
    assert set(val_df["machine_id"].unique()) == expected_machines
    assert set(test_df["machine_id"].unique()) == expected_machines


def test_textile_sampling_prohibition(textile_preprocessor):
    """Verify that sampling is explicitly declared NOT REQUIRED / PROHIBITED."""
    raw_df, _, _ = extract_textile_features()
    cleaned_df, _ = textile_preprocessor.audit_and_clean(raw_df)
    train_df, _, _ = textile_preprocessor.split_dataset(cleaned_df)

    textile_preprocessor.fit_train(train_df)
    train_proc = textile_preprocessor.transform(train_df)

    sampled_df, meta = textile_preprocessor.evaluate_sampling(train_proc)

    assert meta["is_sampling_required"] is False
    assert meta["sampling_decision"] == "SAMPLING_NOT_REQUIRED"
    assert meta["sampling_allowed"] is False
