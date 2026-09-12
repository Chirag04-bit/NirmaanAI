"""
Phase 1 Foundation Test Suite
Validates workspace structure, configuration parsing, logging, and reproducibility defaults.
"""

import os
from pathlib import Path
import pytest
from src.utils.config_loader import get_base_config, get_factory_defaults, get_project_root
from src.utils.logger import logger

def test_project_root_exists():
    root = get_project_root()
    assert root.exists(), f"Project root {root} must exist."

def test_directory_scaffolding_exists():
    root = get_project_root()
    expected_dirs = [
        "DATASET",
        "data/raw",
        "data/processed",
        "data/synthetic",
        "data/external",
        "notebooks",
        "src/data",
        "src/features",
        "src/models",
        "src/explainability",
        "src/decision",
        "src/utils",
        "models",
        "backend",
        "frontend",
        "rag/documents",
        "rag/embeddings",
        "rag/vector_db",
        "tests",
        "docs",
        "configs",
        "experiments",
        "logs"
    ]
    for rel_dir in expected_dirs:
        dir_path = root / rel_dir
        assert dir_path.is_dir(), f"Expected directory {rel_dir} does not exist at {dir_path}"

def test_base_config_loading():
    config = get_base_config()
    assert config is not None
    assert config["project"]["name"] == "NirmaanAI"
    assert config["project"]["group"] == 59
    assert config["project"]["guide"] == "PROF. KUNTAL MONDAL"
    assert config["system"]["random_seed"] == 42
    assert "paths" in config
    assert "modules" in config

def test_factory_defaults_loading():
    factory_defaults = get_factory_defaults()
    assert factory_defaults is not None
    assert "financial_assumptions" in factory_defaults
    assert "machine_baseline_parameters" in factory_defaults
    assert factory_defaults["financial_assumptions"]["downtime_hourly_cost_inr"] > 0
    assert "machine_2" in factory_defaults["machine_baseline_parameters"]

def test_logger_functionality(caplog):
    logger.info("Foundation test log message.")
    # Verify no unhandled exception occurred
    assert True

def test_documentation_files_exist():
    root = get_project_root()
    expected_docs = [
        ".gitignore",
        "README.md",
        "requirements.txt",
        "docs/datasets.md",
        "docs/architecture.md",
        "configs/base_config.yaml",
        "configs/factory_defaults.yaml"
    ]
    for rel_file in expected_docs:
        file_path = root / rel_file
        assert file_path.is_file(), f"Expected file {rel_file} does not exist."
