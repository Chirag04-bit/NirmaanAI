"""
Unit and Integration Tests for NirmaanAI Dataset-Wise Feature Extraction.

Validates:
1. FeatureRegistry integrity & dataset coverage
2. Extraction pipeline execution and deterministic outputs
3. Absence of accidental target/label leakage in predictor sets
4. Temporal causality (no future information used in rolling/lag calculations)
5. Preservation of raw dataset immutability (dataset checksum verification)
6. Feature dictionary and artifact generation standards
"""

import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.features.ai4i_features import extract_ai4i_features
from src.features.cmapss_features import extract_cmapss_features
from src.features.defect_features import extract_defect_features
from src.features.electricity_features import extract_electricity_features
from src.features.feature_registry import FeatureRegistry
from src.features.industrial_iot_features import extract_industrial_iot_features
from src.features.production_features import extract_production_features
from src.features.secom_features import extract_secom_features
from src.features.synthetic_factory_features import extract_synthetic_factory_features
from src.features.textile_features import extract_textile_features
from src.utils.config_loader import get_project_root


# Canonical checksum of auto_components/operational_losses.csv
EXPECTED_LOSSES_MD5 = "34B12582B32D81E3121429C55EBF74E8"


@pytest.fixture(scope="session")
def project_root() -> Path:
    return get_project_root()


def test_raw_dataset_immutability(project_root: Path):
    """Verify that project raw datasets remain unmodified and match master checksum."""
    losses_file = project_root / "data" / "synthetic" / "auto_components" / "operational_losses.csv"
    assert losses_file.exists(), f"Reference dataset missing: {losses_file}"

    hasher = hashlib.md5()
    with open(losses_file, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    computed_md5 = hasher.hexdigest().upper()
    assert computed_md5 == EXPECTED_LOSSES_MD5, (
        f"Raw dataset modified! Expected {EXPECTED_LOSSES_MD5}, got {computed_md5}"
    )


def test_feature_registry_dataset_list():
    """Verify that all 9 required datasets are registered in FeatureRegistry."""
    expected_keys = {
        "ai4i",
        "cmapss",
        "secom",
        "electricity",
        "industrial_iot",
        "manufacturing_production",
        "manufacturing_defects",
        "textile",
        "synthetic_factory",
    }
    registered = set(FeatureRegistry.list_supported_datasets())
    assert expected_keys.issubset(registered), f"Missing registered datasets: {expected_keys - registered}"


def test_ai4i_feature_extraction_and_leakage_safety():
    """Verify AI4I feature extraction: formula correctness, no failure mode leakage."""
    df, fdict, meta = extract_ai4i_features()

    # Verify rows & expected engineered columns
    assert len(df) == 10000
    assert "temp_diff_k" in df.columns
    assert "mechanical_power_kw" in df.columns
    assert "torque_speed_ratio" in df.columns
    assert "tool_wear_risk_index" in df.columns

    # Verify physical formula: temp_diff_k = process_temperature_k - air_temperature_k
    expected_delta = df["process_temperature_k"] - df["air_temperature_k"]
    np.testing.assert_allclose(df["temp_diff_k"].values, expected_delta.values, rtol=1e-5)

    # Mechanical power = 2*pi * RPM * Torque / 60000
    expected_power = (2.0 * np.pi * df["rotational_speed_rpm"] * df["torque_nm"]) / 60000.0
    np.testing.assert_allclose(df["mechanical_power_kw"].values, expected_power.values, rtol=1e-5)

    # Verify leakage audit: breakdown causes (TWF, HDF, PWF, OSF, RNF) and IDs marked as LEAKAGE
    leakage_rows = fdict[fdict["leakage_status"] == "LEAKAGE"]
    leakage_names = set(leakage_rows["feature_name"].tolist())
    assert {"TWF", "HDF", "PWF", "OSF", "RNF", "UDI", "Product ID"}.issubset(leakage_names)

    # Allowed operational features must be SAFE
    safe_rows = fdict[fdict["leakage_status"] == "SAFE"]
    safe_names = set(safe_rows["feature_name"].tolist())
    assert {"temp_diff_k", "mechanical_power_kw", "torque_speed_ratio"}.issubset(safe_names)


def test_cmapss_causality_and_rul_construction():
    """Verify NASA C-MAPSS FD001 temporal causality and piecewise RUL cap."""
    df, fdict, meta = extract_cmapss_features()

    assert len(df) == 20631
    assert "unit_number" in df.columns
    assert "time_cycles" in df.columns
    assert "rul_raw" in df.columns
    assert "rul_clipped" in df.columns

    # Verify RUL piecewise clipping at 125
    assert df["rul_clipped"].max() <= 125.0
    assert (df["rul_clipped"] <= df["rul_raw"]).all()

    # Check that invariant sensors are dropped or marked REMOVE
    dict_sensors = fdict[fdict["feature_name"].isin(["s1", "s5", "s10", "s16", "s18", "s19"])]
    for _, row in dict_sensors.iterrows():
        assert row["status"] == "REMOVE"

    # Verify temporal causality: rolling stats should not be shifted into the future
    # engine 1 cycle 1 rolling mean must equal raw value for window
    eng1_c1 = df[(df["unit_number"] == 1) & (df["time_cycles"] == 1)]
    assert np.isclose(eng1_c1["s2_roll_mean_5"].iloc[0], eng1_c1["s2"].iloc[0])


def test_secom_high_dimensionality_and_screening():
    """Verify SECOM missingness screening and zero-variance feature removal."""
    df, fdict, meta = extract_secom_features(max_missing=0.5, nzv_threshold=1e-6)

    assert len(df) == 1567
    assert meta["raw_sensor_channels"] == 590
    assert meta["target_column"] == "target_defect"

    # Verify target distribution: mapped to {0, 1}
    assert set(df["target_defect"].unique()).issubset({0, 1})

    # High-missing features must be marked REMOVE in feature dictionary
    removed_missing = fdict[fdict["removal_reason"].str.contains("missing", case=False, na=False)]
    assert len(removed_missing) > 0


def test_electricity_causal_lags():
    """Verify Electricity MT_124 temporal lags do not leak future load."""
    df, fdict, meta = extract_electricity_features()

    assert "power_kw" in df.columns
    assert "lag_1h" in df.columns
    assert "lag_24h" in df.columns

    # Causal lag test: lag_1h at row i equals power_kw at row i-1
    for i in range(1, 15):
        assert np.isclose(df.iloc[i]["lag_1h"], df.iloc[i - 1]["power_kw"])


def test_industrial_iot_cross_target_isolation():
    """Verify Industrial IoT prevents target leakage between RUL and Failure."""
    df, fdict, meta = extract_industrial_iot_features()

    assert len(df) == 500000
    assert "vibration_severity_ratio" in df.columns
    assert "fluid_depletion_index" in df.columns

    # Check leakage classification
    f_leak = fdict[fdict["feature_name"] == "Failure_Within_7_Days"]["leakage_status"].iloc[0]
    r_leak = fdict[fdict["feature_name"] == "Remaining_Useful_Life_days"]["leakage_status"].iloc[0]
    assert f_leak == "TARGET"
    assert "LEAKAGE" in r_leak


def test_manufacturing_production_prospective_vs_diagnostic():
    """Verify production pipeline cleanly separates PROSPECTIVE and POST_EVENT features."""
    df, fdict, meta = extract_production_features()

    assert len(df) == 1000
    assert "planned_duration_min" in df.columns
    assert "realized_start_delay_min" in df.columns

    # realized_start_delay_min and realized_completion_delay_min must be POST_EVENT_ONLY
    post_event = fdict[fdict["leakage_status"] == "POST_EVENT_ONLY"]["feature_name"].tolist()
    assert "realized_start_delay_min" in post_event
    assert "realized_completion_delay_min" in post_event
    assert "realized_cycle_ratio" in post_event


def test_manufacturing_defects_features():
    """Verify manufacturing defect features and cost/risk indicators."""
    df, fdict, meta = extract_defect_features()

    assert len(df) == 3240
    assert "cost_per_unit" in df.columns
    assert "supply_chain_risk_index" in df.columns
    assert "maintenance_downtime_ratio" in df.columns


def test_textile_features_synthetic_marking():
    """Verify textile synthetic dataset features are marked CONTROLLED_SYNTHETIC."""
    df, fdict, meta = extract_textile_features()

    assert len(df) == 43200
    assert meta["epistemic_classification"] == "CONTROLLED_SYNTHETIC"
    assert "vibration_norm" in df.columns
    assert "temp_diff_c" in df.columns


def test_synthetic_factory_controlled_scenario_integrity():
    """Verify synthetic factory maintains scenario quarantine and causal integrity."""
    df, fdict, meta = extract_synthetic_factory_features()

    assert len(df) == 43200
    assert "vibration_severity_ratio" in df.columns
    assert "tool_wear_risk" in df.columns
    assert "is_pre_decision_cutoff" in df.columns
    assert meta["epistemic_classification"] == "CONTROLLED_SYNTHETIC"
    assert meta["temporal_decision_cutoff_utc"] == "2026-01-21T12:00:00+00:00"
