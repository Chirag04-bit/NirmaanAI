"""
Phase 2 Dataset Verification Test Suite
Validates directory organization, lightweight schema/shape checks,
manifest completeness, representation notes, and source safety.
"""

import json
import os
from pathlib import Path
import pandas as pd
import pytest
from src.utils.config_loader import get_project_root

DATASET_ROOT = get_project_root() / "DATASET"
SOURCE_ROOT = Path(r"C:\Users\user\OneDrive\Desktop\NIRMAAN\DATASET")

EXPECTED_DATASETS = [
    "01_AI4I_2020",
    "02_NASA_CMAPSS",
    "03_UCI_SECOM",
    "04_ENERGY",
    "05_INDUSTRIAL_IOT",
    "06_MANUFACTURING_PRODUCTION",
    "07_FACTORY_OEE_DOWNTIME",
    "08_MANUFACTURING_DEFECTS"
]

def test_dataset_directories_exist():
    for ds_name in EXPECTED_DATASETS:
        ds_path = DATASET_ROOT / ds_name
        assert ds_path.is_dir(), f"Dataset directory {ds_name} missing at {ds_path}"

def test_manifest_metadata_completeness():
    """Verify that every dataset manifest contains non-empty provenance, license, target, and guardrail."""
    for ds_name in EXPECTED_DATASETS:
        manifest_path = DATASET_ROOT / ds_name / "metadata" / "dataset_manifest.json"
        assert manifest_path.is_file(), f"Manifest missing for {ds_name}"
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["dataset_id"] == ds_name
            assert data.get("dataset_name"), f"Missing dataset_name in {ds_name}"
            assert data.get("source_archive"), f"Missing source_archive in {ds_name}"
            assert data.get("license"), f"Missing license in {ds_name}"
            assert data.get("primary_target"), f"Missing primary_target in {ds_name}"
            if ds_name != "07_FACTORY_OEE_DOWNTIME":
                assert data.get("leakage_guardrail"), f"Missing leakage_guardrail in {ds_name}"

def test_ai4i_schema_and_shape():
    """Lightweight shape and column verification for AI4I 2020."""
    csv_path = DATASET_ROOT / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    assert csv_path.is_file()
    df = pd.read_csv(csv_path)
    assert df.shape == (10000, 14), f"Unexpected shape for AI4I: {df.shape}"
    expected_cols = [
        "UDI", "Product ID", "Type", "Air temperature [K]", "Process temperature [K]",
        "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]", "Machine failure",
        "TWF", "HDF", "PWF", "OSF", "RNF"
    ]
    assert list(df.columns) == expected_cols
    assert set(df["Machine failure"].unique()).issubset({0, 1})

def test_cmapss_schema_and_shape():
    """Lightweight shape and line count verification for NASA C-MAPSS."""
    cmaps_dir = DATASET_ROOT / "02_NASA_CMAPSS" / "raw" / "CMaps"
    assert (cmaps_dir / "Damage Propagation Modeling.pdf").is_file()
    
    # Check train_FD001
    with open(cmaps_dir / "train_FD001.txt", "r") as f:
        first_line = f.readline().strip().split()
        assert len(first_line) == 26, f"Expected 26 columns in CMaps, got {len(first_line)}"
        total_train_1 = 1 + sum(1 for _ in f)
        assert total_train_1 == 20631, f"Expected 20,631 rows in train_FD001, got {total_train_1}"

    # Check test_FD001
    with open(cmaps_dir / "test_FD001.txt", "r") as f:
        total_test_1 = sum(1 for _ in f)
        assert total_test_1 == 13096, f"Expected 13,096 rows in test_FD001, got {total_test_1}"

    # Check RUL_FD001
    with open(cmaps_dir / "RUL_FD001.txt", "r") as f:
        total_rul_1 = sum(1 for _ in f)
        assert total_rul_1 == 100, f"Expected 100 RUL values in RUL_FD001, got {total_rul_1}"

def test_uci_secom_schema_and_representation_note():
    """Verify SECOM schema and explicit representation note."""
    secom_dir = DATASET_ROOT / "03_UCI_SECOM"
    csv_path = secom_dir / "raw" / "uci-secom.csv"
    assert csv_path.is_file()
    
    # Verify shape
    df_head = pd.read_csv(csv_path, nrows=5)
    assert len(df_head.columns) == 592
    assert df_head.columns[0] == "Time"
    assert df_head.columns[-1] == "Pass/Fail"
    
    # Verify raw files line count
    with open(secom_dir / "raw" / "secom.data", "r") as f:
        assert sum(1 for _ in f) == 1567
    with open(secom_dir / "raw" / "secom_labels.data", "r") as f:
        assert sum(1 for _ in f) == 1567

    # Verify representation distinction in manifest
    manifest_path = secom_dir / "metadata" / "dataset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "representation_note" in data
        assert "SAME single SECOM dataset" in data["representation_note"]

def test_energy_schema_and_shape():
    """Lightweight delimiter and client header check for Electricity Load Diagrams."""
    energy_file = DATASET_ROOT / "04_ENERGY" / "raw" / "LD2011_2014.txt"
    assert energy_file.is_file()
    with open(energy_file, "r", encoding="utf-8") as f:
        header = f.readline().strip().split(";")
        assert len(header) == 371, f"Expected 371 columns in Electricity dataset, got {len(header)}"
        assert header[1] == '"MT_001"'
        assert header[-1] == '"MT_370"'
        line2 = f.readline().strip().split(";")
        assert line2[0] == '"2011-01-01 00:15:00"'

def test_industrial_iot_schema_and_shape():
    """Lightweight column and line count verification for Factory Sensor Simulator 2040."""
    iot_file = DATASET_ROOT / "05_INDUSTRIAL_IOT" / "raw" / "factory_sensor_simulator_2040.csv"
    assert iot_file.is_file()
    df_head = pd.read_csv(iot_file, nrows=5)
    assert len(df_head.columns) == 22
    assert "Machine_ID" in df_head.columns
    assert "Vibration_mms" in df_head.columns
    assert "Temperature_C" in df_head.columns
    assert "Failure_Within_7_Days" in df_head.columns
    assert "Remaining_Useful_Life_days" in df_head.columns

def test_hybrid_manufacturing_schema_and_shape():
    """Lightweight shape and column check for Hybrid Manufacturing Categorical."""
    hybrid_file = DATASET_ROOT / "06_MANUFACTURING_PRODUCTION" / "raw" / "hybrid_manufacturing_categorical.csv"
    assert hybrid_file.is_file()
    df = pd.read_csv(hybrid_file)
    assert df.shape == (1000, 13)
    assert "Job_ID" in df.columns
    assert "Machine_ID" in df.columns
    assert "Job_Status" in df.columns

def test_manufacturing_defects_schema_and_shape():
    """Lightweight shape and target check for Manufacturing Defect Dataset."""
    defect_file = DATASET_ROOT / "08_MANUFACTURING_DEFECTS" / "raw" / "manufacturing_defect_dataset.csv"
    assert defect_file.is_file()
    df = pd.read_csv(defect_file)
    assert df.shape == (3240, 17)
    assert "DefectStatus" in df.columns
    assert set(df["DefectStatus"].unique()).issubset({0, 1})

def test_oee_schema_specification_present():
    """Verify OEE schema specification assets exist."""
    oee_doc_dir = DATASET_ROOT / "07_FACTORY_OEE_DOWNTIME" / "documentation"
    assert (oee_doc_dir / "dataset-metadata.json").is_file()
    assert (oee_doc_dir / "LICENSE").is_file()
    assert (oee_doc_dir / "NIRMAAN_OEE_SPEC.md").is_file()

def test_source_dataset_folder_untouched():
    """Verify that source archives in original desktop directory remain strictly untouched."""
    assert SOURCE_ROOT.is_dir(), "Source dataset directory must exist"
    source_files = [f for f in os.listdir(SOURCE_ROOT) if f.endswith(".zip")]
    assert len(source_files) == 10, f"Source folder should contain exactly 10 archives, found {len(source_files)}"
