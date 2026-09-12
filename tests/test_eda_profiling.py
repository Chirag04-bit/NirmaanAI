"""
Phase 3 EDA and Data Profiling Test Suite
Validates statistical profiling functions, leakage detection, and notebook structure integrity.
"""

import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.data.profiling import (
    compute_correlation_matrix,
    detect_potential_leakage,
    profile_dataframe,
)
from src.utils.config_loader import get_project_root

PROJECT_ROOT = get_project_root()
DATASET_ROOT = PROJECT_ROOT / "DATASET"
NOTEBOOKS_ROOT = PROJECT_ROOT / "notebooks"

def test_profile_dataframe_synthetic():
    """Verify profile_dataframe handles mixed types, missing values, and targets."""
    df = pd.DataFrame({
        "num1": [1.0, 2.0, np.nan, 4.0, 5.0],
        "cat1": ["A", "B", "A", "B", "C"],
        "target": [0, 0, 0, 1, 1]
    })
    profile = profile_dataframe(df, target_col="target")
    assert profile["rows"] == 5
    assert profile["cols"] == 3
    assert profile["total_missing_cells"] == 1
    assert "num1" in profile["missing_summary"]
    assert profile["missing_summary"]["num1"]["null_count"] == 1
    assert "num1" in profile["numeric_summary"]
    assert "cat1" in profile["categorical_summary"]
    assert profile["target_summary"]["target_column"] == "target"
    assert profile["target_summary"]["distribution"] == {"0": 3, "1": 2}

def test_compute_correlation_matrix():
    """Verify correlation matrix calculation on numeric data."""
    df = pd.DataFrame({
        "a": [1.0, 2.0, 3.0, 4.0],
        "b": [2.0, 4.0, 6.0, 8.0],
        "c": [4.0, 3.0, 2.0, 1.0]
    })
    corr = compute_correlation_matrix(df)
    assert corr.shape == (3, 3)
    assert np.isclose(corr.loc["a", "b"], 1.0)
    assert np.isclose(corr.loc["a", "c"], -1.0)

def test_detect_potential_leakage():
    """Verify detection of target-leaking features."""
    df = pd.DataFrame({
        "feature_ok": [1.0, 5.0, 2.0, 8.0, 3.0],
        "feature_leaking": [0.0, 0.0, 0.0, 1.0, 1.0],
        "target": [0, 0, 0, 1, 1]
    })
    leaks = detect_potential_leakage(df, target_col="target", correlation_threshold=0.99)
    assert len(leaks) == 1
    assert leaks[0]["column"] == "feature_leaking"

def test_eda_notebooks_exist_and_valid():
    """Verify that all 7 EDA notebooks exist and parse cleanly as valid nbformat 4 JSON."""
    expected_notebooks = [
        "01_eda_ai4i_maintenance.ipynb",
        "02_eda_nasa_cmapss_degradation.ipynb",
        "03_eda_uci_secom_process.ipynb",
        "04_eda_energy_consumption.ipynb",
        "05_eda_industrial_iot_sensors.ipynb",
        "06_eda_production_scheduling.ipynb",
        "07_eda_manufacturing_defects.ipynb"
    ]
    for nb_name in expected_notebooks:
        nb_path = NOTEBOOKS_ROOT / nb_name
        assert nb_path.is_file(), f"Notebook {nb_name} missing at {nb_path}"
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
            assert nb.get("nbformat") == 4
            assert "cells" in nb
            assert len(nb["cells"]) >= 3

def test_ai4i_profiling_execution():
    """Verify profiling on real working copy of AI4I dataset."""
    ai4i_path = DATASET_ROOT / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    assert ai4i_path.is_file()
    df = pd.read_csv(ai4i_path)
    profile = profile_dataframe(df, target_col="Machine failure")
    assert profile["rows"] == 10000
    assert profile["cols"] == 14
    assert profile["total_missing_cells"] == 0
    assert profile["target_summary"]["distribution"]["1"] == 339
    assert profile["target_summary"]["distribution"]["0"] == 9661
