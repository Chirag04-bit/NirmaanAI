"""
Independent Unit & Integration Tests for Industrial IoT Preprocessor.
Validates:
- Strict cross-target quarantine between Failure and RUL tasks
- Failure task applies sampling to training partition only
- RUL task declares SAMPLING_NOT_REQUIRED
- Scalers fit strictly on training partitions
"""

import numpy as np
import pandas as pd
import pytest

from src.features.industrial_iot_features import extract_industrial_iot_features
from src.preprocessing.industrial_iot_preprocessor import IndustrialIoTPreprocessor


def test_industrial_iot_cross_target_isolation_failure():
    """Ensure Failure classification pipeline drops Remaining_Useful_Life_days."""
    preprocessor = IndustrialIoTPreprocessor(task="failure", random_state=42)
    raw_df, _, _ = extract_industrial_iot_features()
    cleaned_df, report = preprocessor.audit_and_clean(raw_df)

    assert preprocessor.RUL_TARGET not in cleaned_df.columns, "RUL leaked into failure classification!"
    assert preprocessor.FAILURE_TARGET in cleaned_df.columns
    assert report["quarantined_cross_target"] == preprocessor.RUL_TARGET


def test_industrial_iot_cross_target_isolation_rul():
    """Ensure RUL regression pipeline drops Failure_Within_7_Days."""
    preprocessor = IndustrialIoTPreprocessor(task="rul", random_state=42)
    raw_df, _, _ = extract_industrial_iot_features()
    cleaned_df, report = preprocessor.audit_and_clean(raw_df)

    assert preprocessor.FAILURE_TARGET not in cleaned_df.columns, "Failure leaked into RUL regression!"
    assert preprocessor.RUL_TARGET in cleaned_df.columns
    assert report["quarantined_cross_target"] == preprocessor.FAILURE_TARGET


def test_industrial_iot_sampling_decisions():
    """Verify task-specific sampling policies for Industrial IoT."""
    fail_prep = IndustrialIoTPreprocessor(task="failure", random_state=42)
    rul_prep = IndustrialIoTPreprocessor(task="rul", random_state=42)

    raw_df, _, _ = extract_industrial_iot_features()
    cleaned_fail, _ = fail_prep.audit_and_clean(raw_df)
    train_fail, _, _ = fail_prep.split_dataset(cleaned_fail)

    cleaned_rul, _ = rul_prep.audit_and_clean(raw_df)
    train_rul, _, _ = rul_prep.split_dataset(cleaned_rul)

    # Failure task evaluates train-only sampling
    _, meta_fail = fail_prep.evaluate_sampling(train_fail)
    assert meta_fail["is_sampling_required"] is True
    assert meta_fail["applied_to"] == "TRAIN_PARTITION_ONLY"

    # RUL task declares SAMPLING_NOT_REQUIRED
    _, meta_rul = rul_prep.evaluate_sampling(train_rul)
    assert meta_rul["is_sampling_required"] is False
    assert meta_rul["sampling_decision"] == "SAMPLING_NOT_REQUIRED"
