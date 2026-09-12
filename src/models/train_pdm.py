"""
NirmaanAI Predictive Maintenance Training Pipeline
Executes end-to-end baseline-first training for Failure Classification (AI4I 2020)
and RUL Estimation (NASA C-MAPSS FD001). Saves champion models and detailed metadata.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict
import numpy as np
import pandas as pd

from src.features.pdm_features import prepare_ai4i_splits, prepare_cmapss_splits
from src.models.failure_classifier import FailureClassifierBenchmark
from src.models.pdm_service import PredictiveMaintenanceService
from src.models.rul_regressor import RULRegressorBenchmark
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


def run_pdm_training_pipeline() -> Dict[str, Any]:
    """Orchestrates end-to-end training and evaluation for Phase 6."""
    root = get_project_root()
    models_dir = root / "models" / "predictive_maintenance"
    models_dir.mkdir(parents=True, exist_ok=True)

    logger.info("==================================================")
    logger.info("STARTING PHASE 6 PREDICTIVE MAINTENANCE PIPELINE")
    logger.info("==================================================")

    timestamp_utc = datetime.now(timezone.utc).isoformat()

    # -------------------------------------------------------------
    # 1. AI4I 2020: Machine Failure Classification
    # -------------------------------------------------------------
    ai4i_path = root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    if not ai4i_path.exists():
        raise FileNotFoundError(f"AI4I dataset not found at {ai4i_path}")

    logger.info(f"Loading AI4I 2020 dataset from {ai4i_path}...")
    df_ai4i = pd.read_csv(ai4i_path)

    # Prepare features and stratified splits with leakage exclusions
    ai4i_splits = prepare_ai4i_splits(df_ai4i, test_size=0.15, val_size=0.15, random_state=42)

    classifier_benchmark = FailureClassifierBenchmark(random_state=42)
    classifier_results = classifier_benchmark.train_and_evaluate_all(
        X_train=ai4i_splits["X_train"],
        y_train=ai4i_splits["y_train"],
        X_val=ai4i_splits["X_val"],
        y_val=ai4i_splits["y_val"],
        X_test=ai4i_splits["X_test"],
        y_test=ai4i_splits["y_test"]
    )

    classifier_payload = classifier_benchmark.save_champion(models_dir)

    # -------------------------------------------------------------
    # 2. NASA C-MAPSS: Turbofan Engine RUL Regression
    # -------------------------------------------------------------
    cmapss_dir = root / "DATASET" / "02_NASA_CMAPSS" / "raw" / "CMaps"
    train_fd001 = cmapss_dir / "train_FD001.txt"
    test_fd001 = cmapss_dir / "test_FD001.txt"
    rul_fd001 = cmapss_dir / "RUL_FD001.txt"

    if not train_fd001.exists():
        raise FileNotFoundError(f"NASA C-MAPSS train file not found at {train_fd001}")

    logger.info(f"Loading NASA C-MAPSS FD001 dataset from {train_fd001}...")
    cmapss_splits = prepare_cmapss_splits(
        train_file=train_fd001,
        test_file=test_fd001,
        rul_file=rul_fd001,
        max_rul_clip=125.0,
        val_engine_ratio=0.15,
        test_engine_ratio=0.15,
        random_state=42
    )

    regressor_benchmark = RULRegressorBenchmark(random_state=42)
    regressor_results = regressor_benchmark.train_and_evaluate_all(
        X_train=cmapss_splits["X_train"],
        y_train=cmapss_splits["y_train"],
        X_val=cmapss_splits["X_val"],
        y_val=cmapss_splits["y_val"],
        X_test_internal=cmapss_splits["X_test_internal"],
        y_test_internal=cmapss_splits["y_test_internal"],
        X_official_test=cmapss_splits["X_official_test"],
        y_official_test=cmapss_splits["y_official_test"]
    )

    regressor_payload = regressor_benchmark.save_champion(models_dir)

    # -------------------------------------------------------------
    # 3. Controlled Synthetic Validation on Machine 2
    # -------------------------------------------------------------
    synthetic_telemetry = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.csv"
    pdm_service = PredictiveMaintenanceService(
        classifier_path=models_dir / "failure_classifier.joblib",
        regressor_path=models_dir / "rul_regressor.joblib"
    )
    synthetic_val_results = pdm_service.run_controlled_synthetic_validation(
        synthetic_csv_path=synthetic_telemetry,
        target_machine_id="M2"
    )

    # -------------------------------------------------------------
    # 4. Metadata Registry
    # -------------------------------------------------------------
    metadata = {
        "pipeline_name": "NirmaanAI Predictive Maintenance Subsystem",
        "training_timestamp_utc": timestamp_utc,
        "random_seed": 42,
        "submodules": {
            "failure_classification": {
                "dataset": "DATASET/01_AI4I_2020/raw/ai4i2020.csv",
                "target": "Machine failure (Binary 0/1)",
                "split_strategy": "Stratified train (70%) / val (15%) / test (15%)",
                "leakage_exclusions": [
                    "UDI (row index)",
                    "Product ID (identifier)",
                    "TWF (tool wear failure mode indicator)",
                    "HDF (heat dissipation failure mode indicator)",
                    "PWF (power failure mode indicator)",
                    "OSF (overstrain failure mode indicator)",
                    "RNF (random failure mode indicator)"
                ],
                "feature_names": classifier_payload["feature_names"],
                "champion_model": classifier_results["best_model_name"],
                "optimal_threshold": classifier_results["optimal_threshold"],
                "validation_metrics": classifier_results["val_metrics"],
                "test_metrics": classifier_results["test_metrics"]
            },
            "rul_estimation": {
                "dataset": "DATASET/02_NASA_CMAPSS/raw/CMaps/ (FD001)",
                "target": "Remaining Useful Life (RUL in cycles, capped at 125)",
                "split_strategy": "Grouped engine split (70 engines train / 15 val / 15 internal test)",
                "sensor_selection": "14 informative degradation sensors (s2, s3, s4, s7, s8, s9, s11, s12, s13, s14, s15, s17, s20, s21)",
                "feature_names": regressor_payload["feature_names"],
                "champion_model": regressor_results["best_model_name"],
                "validation_metrics": regressor_results["val_metrics"],
                "internal_test_metrics": regressor_results["internal_test_metrics"],
                "official_benchmark_metrics": regressor_results["official_test_metrics"]
            },
            "controlled_synthetic_validation": synthetic_val_results
        }
    }

    metadata_path = models_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Pipeline complete! Saved metadata registry to {metadata_path}")
    logger.info("==================================================")

    return metadata


if __name__ == "__main__":
    run_pdm_training_pipeline()
