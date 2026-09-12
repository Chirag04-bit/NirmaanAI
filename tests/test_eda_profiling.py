"""
Phase 3 EDA and Data Profiling Test Suite
Validates statistical profiling functions, leakage detection, exact audited metrics,
and verified execution of all 7 exploratory analysis notebooks.
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

def test_ai4i_audited_statistics():
    """Verify exact audited thresholds for Tool Wear and HDF Temperature Difference in AI4I."""
    ai4i_path = DATASET_ROOT / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    assert ai4i_path.is_file()
    df = pd.read_csv(ai4i_path)
    
    # 1. Tool wear in TWF
    twf_wear = df[df["TWF"] == 1]["Tool wear [min]"]
    assert len(twf_wear) == 46
    assert twf_wear.min() == 198.0
    assert twf_wear.max() == 253.0
    assert (twf_wear >= 200).sum() == 45  # Exactly 45 of 46 (97.8%)
    
    # 2. HDF Temperature difference
    df["Temp_Diff"] = df["Process temperature [K]"] - df["Air temperature [K]"]
    hdf_diff = df[df["HDF"] == 1]["Temp_Diff"]
    assert len(hdf_diff) == 115
    assert np.isclose(hdf_diff.max(), 8.60)  # Exactly 100% of HDF have Temp_Diff <= 8.6 K
    assert np.isclose(hdf_diff.mean(), 8.2278, atol=0.01)

def test_industrial_iot_audited_statistics():
    """Verify exact audited vibration shift and deterministic RUL leakage in Industrial IoT."""
    iot_path = DATASET_ROOT / "05_INDUSTRIAL_IOT" / "raw" / "factory_sensor_simulator_2040.csv"
    assert iot_path.is_file()
    df = pd.read_csv(iot_path)
    
    # Class vibration means
    vib_healthy = df[df["Failure_Within_7_Days"] == False]["Vibration_mms"].mean()
    vib_failed = df[df["Failure_Within_7_Days"] == True]["Vibration_mms"].mean()
    assert np.isclose(vib_healthy, 9.94, atol=0.05)
    assert np.isclose(vib_failed, 10.73, atol=0.05)
    assert vib_failed > vib_healthy
    
    # Deterministic leakage check
    max_rul_when_fail = df[df["Failure_Within_7_Days"] == True]["Remaining_Useful_Life_days"].max()
    assert max_rul_when_fail <= 7.0  # Confirmed: RUL <= 7 perfectly predicts failure

def test_cmapss_lifespan_statistics():
    """Verify exact lifespan statistics for NASA C-MAPSS FD001."""
    train_path = DATASET_ROOT / "02_NASA_CMAPSS" / "raw" / "CMaps" / "train_FD001.txt"
    cols = ["unit", "cycle"] + [f"col_{i}" for i in range(24)]
    df = pd.read_csv(train_path, sep=r"\s+", names=cols)
    max_cycles = df.groupby("unit")["cycle"].max()
    assert len(max_cycles) == 100
    assert max_cycles.min() == 128
    assert max_cycles.max() == 362
    assert np.isclose(max_cycles.mean(), 206.3, atol=0.1)

def test_hybrid_manufacturing_delay_statistics():
    """Verify exact dispatch delay bounds in Hybrid Manufacturing."""
    hyb_path = DATASET_ROOT / "06_MANUFACTURING_PRODUCTION" / "raw" / "hybrid_manufacturing_categorical.csv"
    df = pd.read_csv(hyb_path)
    df["Scheduled_Start"] = pd.to_datetime(df["Scheduled_Start"])
    df["Actual_Start"] = pd.to_datetime(df["Actual_Start"])
    df["Start_Delay_min"] = (df["Actual_Start"] - df["Scheduled_Start"]).dt.total_seconds() / 60.0
    
    # Completed jobs delay range
    comp_delays = df[df["Job_Status"] == "Completed"]["Start_Delay_min"]
    assert comp_delays.min() >= -5.0
    assert comp_delays.max() <= 5.0
    
    # Delayed jobs delay range
    del_delays = df[df["Job_Status"] == "Delayed"]["Start_Delay_min"]
    assert del_delays.min() >= 10.0
    assert del_delays.max() <= 30.0
    assert (df["Start_Delay_min"] >= 10.0).sum() == len(del_delays)

def test_all_eda_notebooks_executable():
    """Verify that all 7 EDA notebooks execute their code cells end-to-end without unhandled errors."""
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
        
        # Execute each code cell in an isolated environment
        env = {}
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                code = "".join(cell["source"])
                try:
                    exec(code, env)
                except Exception as e:
                    pytest.fail(f"Execution failed in {nb_name}: {e}")
