"""
Phase 2 Dataset Verification Test Suite
Validates dataset directory organization, working file integrity, metadata manifests, and source safety.
"""

import json
import os
from pathlib import Path
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

def test_manifests_exist_and_valid():
    for ds_name in EXPECTED_DATASETS:
        manifest_path = DATASET_ROOT / ds_name / "metadata" / "dataset_manifest.json"
        assert manifest_path.is_file(), f"Manifest missing for {ds_name}"
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["dataset_id"] == ds_name
            assert "source_archive" in data
            assert "license" in data

def test_raw_data_files_exist_and_non_empty():
    raw_files_check = {
        "01_AI4I_2020": ["raw/ai4i2020.csv"],
        "02_NASA_CMAPSS": [
            "raw/CMaps/train_FD001.txt",
            "raw/CMaps/test_FD001.txt",
            "raw/CMaps/RUL_FD001.txt"
        ],
        "03_UCI_SECOM": [
            "raw/uci-secom.csv",
            "raw/secom.data",
            "raw/secom_labels.data"
        ],
        "04_ENERGY": ["raw/LD2011_2014.txt"],
        "05_INDUSTRIAL_IOT": ["raw/factory_sensor_simulator_2040.csv"],
        "06_MANUFACTURING_PRODUCTION": ["raw/hybrid_manufacturing_categorical.csv"],
        "08_MANUFACTURING_DEFECTS": ["raw/manufacturing_defect_dataset.csv"]
    }
    for ds_name, files in raw_files_check.items():
        for rel_file in files:
            file_path = DATASET_ROOT / ds_name / rel_file
            assert file_path.is_file(), f"Expected data file {rel_file} missing in {ds_name}"
            assert file_path.stat().st_size > 0, f"Data file {rel_file} is empty"

def test_source_dataset_folder_untouched():
    assert SOURCE_ROOT.is_dir(), "Source dataset directory must exist"
    source_files = [f for f in os.listdir(SOURCE_ROOT) if f.endswith(".zip")]
    assert len(source_files) == 10, f"Source folder should contain exactly 10 archives, found {len(source_files)}"
