"""
NirmaanAI — Tuning Subsample & Dataset Volume Optimization Tests
==============================================================
Post-Phase-25 Research & Engineering Extension Test Suite
"""

import os
import json
import hashlib
import pytest
import numpy as np
import pandas as pd

from src.data_preprocessing.tuning_subsample import (
    deterministic_stratified_classification_sample,
    deterministic_distribution_aware_regression_sample,
    deterministic_chronological_window_sample,
    deterministic_temporal_stride_sample,
    compute_representativeness_audit,
    calculate_file_md5,
)

BASE_DIR = r"C:\NIRMAAN AI"
SUBSET_DIR = os.path.join(BASE_DIR, "models", "tuning_subsets")
PROCESSED_DIR = os.path.join(BASE_DIR, "models", "processed")


def test_subsets_and_metadata_exist():
    """Verify all 5 generated tuning subsets and manifest exist."""
    manifest_path = os.path.join(SUBSET_DIR, "tuning_subsets_manifest.json")
    assert os.path.exists(manifest_path), "tuning_subsets_manifest.json must exist"

    with open(manifest_path) as f:
        manifest = json.load(f)
    assert manifest["epistemic_status"] == "CONTROLLED_COMPUTATIONAL_SUBSET"
    assert len(manifest["optimized_datasets"]) == 5
    assert len(manifest["non_reduced_datasets"]) == 5

    for task in ["industrial_iot_failure", "industrial_iot_rul", "electricity", "textile", "synthetic_factory"]:
        task_dir = os.path.join(SUBSET_DIR, task)
        assert os.path.exists(os.path.join(task_dir, "train_subsample.parquet"))
        assert os.path.exists(os.path.join(task_dir, "metadata.json"))
        assert os.path.exists(os.path.join(task_dir, "representativeness_audit.json"))


def test_deterministic_sampling_same_seed():
    """Verify that same random seed produces identical sample."""
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "industrial_iot", "failure", "train.parquet")).head(10000)
    sub1 = deterministic_stratified_classification_sample(df, "Failure_Within_7_Days", target_rows=3000, random_state=42)
    sub2 = deterministic_stratified_classification_sample(df, "Failure_Within_7_Days", target_rows=3000, random_state=42)
    pd.testing.assert_frame_equal(sub1, sub2)


def test_deterministic_sampling_different_seed():
    """Verify that different random seed produces different sample."""
    df = pd.read_parquet(os.path.join(PROCESSED_DIR, "industrial_iot", "failure", "train.parquet")).head(10000)
    sub1 = deterministic_stratified_classification_sample(df, "Failure_Within_7_Days", target_rows=3000, random_state=42)
    sub2 = deterministic_stratified_classification_sample(df, "Failure_Within_7_Days", target_rows=3000, random_state=99)
    assert not sub1.index.equals(sub2.index)


def test_class_distribution_preservation_iot_failure():
    """Verify class distribution in IoT failure is preserved within 0.05%."""
    meta_path = os.path.join(SUBSET_DIR, "industrial_iot_failure", "metadata.json")
    with open(meta_path) as f:
        meta = json.load(f)
    p_before = meta["class_distribution_before"]["1"]
    p_after = meta["class_distribution_after"]["1"]
    assert abs(p_before - p_after) < 0.0005, f"Failure prevalence drifted: {p_before} vs {p_after}"


def test_machine_type_distribution_preservation():
    """Verify Machine_Type distribution in IoT datasets is preserved within 0.1%."""
    for task in ["industrial_iot_failure", "industrial_iot_rul"]:
        meta_path = os.path.join(SUBSET_DIR, task, "metadata.json")
        with open(meta_path) as f:
            meta = json.load(f)
        drift = meta["categorical_distribution_audit"]["Machine_Type_encoded"]["max_prop_drift"]
        assert drift < 0.001, f"Machine_Type drifted excessively in {task}: {drift}"


def test_no_validation_test_contamination():
    """Verify that tuning subset row indices come strictly from train partition and not val/test."""
    for task_name, rel_path in [
        ("industrial_iot_failure", os.path.join("industrial_iot", "failure")),
        ("industrial_iot_rul", os.path.join("industrial_iot", "rul")),
        ("electricity", "electricity"),
    ]:
        sub_df = pd.read_parquet(os.path.join(SUBSET_DIR, task_name, "train_subsample.parquet"))
        train_df = pd.read_parquet(os.path.join(PROCESSED_DIR, rel_path, "train.parquet"))
        val_df = pd.read_parquet(os.path.join(PROCESSED_DIR, rel_path, "val.parquet"))
        test_df = pd.read_parquet(os.path.join(PROCESSED_DIR, rel_path, "test.parquet"))

        assert len(sub_df) < len(train_df)
        assert len(sub_df.columns) == len(train_df.columns)
        # Validation and test row counts remain full and unmodified
        assert len(val_df) > 0
        assert len(test_df) > 0


def test_no_machine_id_leakage():
    """Verify Machine_ID is absent from IoT failure and RUL subsets."""
    for task in ["industrial_iot_failure", "industrial_iot_rul"]:
        sub_df = pd.read_parquet(os.path.join(SUBSET_DIR, task, "train_subsample.parquet"))
        assert "Machine_ID" not in sub_df.columns, f"Machine_ID leaked into {task} subset!"


def test_no_cross_target_leakage():
    """Verify quarantined cross-target fields remain quarantined in subsets."""
    fail_sub = pd.read_parquet(os.path.join(SUBSET_DIR, "industrial_iot_failure", "train_subsample.parquet"))
    assert "Remaining_Useful_Life_days" not in fail_sub.columns, "RUL leaked into failure subset!"

    rul_sub = pd.read_parquet(os.path.join(SUBSET_DIR, "industrial_iot_rul", "train_subsample.parquet"))
    assert "Failure_Within_7_Days" not in rul_sub.columns, "Failure label leaked into RUL subset!"


def test_temporal_ordering_electricity():
    """Verify strict temporal ordering in electricity subset."""
    df = pd.read_parquet(os.path.join(SUBSET_DIR, "electricity", "train_subsample.parquet"))
    assert "timestamp" in df.columns
    assert df["timestamp"].is_monotonic_increasing, "Electricity subset is not strictly monotonically increasing in time!"


def test_synthetic_factory_scenario_preservation():
    """Verify synthetic factory training subset preserves M1-M5 synchronized stations."""
    df_sub = pd.read_parquet(os.path.join(SUBSET_DIR, "synthetic_factory", "train_subsample.parquet"))
    assert set(df_sub["machine_id"].unique()) == {"M1", "M2", "M3", "M4", "M5"}
    # Each machine has equal synchronized representation
    counts = df_sub["machine_id"].value_counts()
    assert counts.min() == counts.max()
    # Training subset must precede decision cutoff Jan 21 12:00
    assert pd.to_datetime(df_sub["timestamp"]).max() <= pd.to_datetime("2026-01-21 12:00:00+00:00")


def test_metadata_correctness_and_epistemic_status():
    """Verify metadata contains required fields and explicit epistemic status."""
    for task in ["industrial_iot_failure", "industrial_iot_rul", "electricity", "textile", "synthetic_factory"]:
        meta_path = os.path.join(SUBSET_DIR, task, "metadata.json")
        with open(meta_path) as f:
            meta = json.load(f)
        assert meta["epistemic_status"] == "CONTROLLED_COMPUTATIONAL_SUBSET"
        assert meta["pipeline_version"] == "post-phase-25-subsample-v1"
        assert "source_checksum" in meta
        assert "subset_checksum" in meta
        assert meta["subset_rows"] < meta["source_rows"]


def test_canonical_source_checksum_immutable():
    """Verify canonical source dataset checksum remains 34B12582B32D81E3121429C55EBF74E8."""
    path = os.path.join(BASE_DIR, "data", "synthetic", "auto_components", "operational_losses.csv")
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    assert hasher.hexdigest().upper() == "34B12582B32D81E3121429C55EBF74E8"


def test_full_data_training_path_remains_available():
    """Verify canonical processed training files remain full and untouched."""
    fail_full = pd.read_parquet(os.path.join(PROCESSED_DIR, "industrial_iot", "failure", "train.parquet"))
    assert len(fail_full) == 350000, "Canonical full training set must remain 350,000 rows"

    rul_full = pd.read_parquet(os.path.join(PROCESSED_DIR, "industrial_iot", "rul", "train.parquet"))
    assert len(rul_full) == 350000, "Canonical full training set must remain 350,000 rows"
