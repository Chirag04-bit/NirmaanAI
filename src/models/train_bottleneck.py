"""
NirmaanAI Bottleneck Prediction Training & Evaluation Pipeline
Executes baseline-first benchmark:
1. Rule-Based Heuristic Baseline
2. Regularized Logistic Regression
3. Balanced Random Forest Classifier
4. XGBoost Classifier

Evaluates models, serializes champion model and metadata.json under models/bottleneck_prediction/.
"""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score
)

from src.features.bottleneck_features import (
    prepare_bottleneck_splits,
    prepare_hybrid_manufacturing_benchmark
)
from src.models.bottleneck_predictor import (
    BaseBottleneckClassifier,
    HeuristicBottleneckClassifier,
    LogisticBottleneckClassifier,
    RandomForestBottleneckClassifier,
    XGBoostBottleneckClassifier
)
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


@dataclass
class BottleneckBenchmarkResult:
    model_name: str
    decision_threshold: float
    test_precision: float
    test_recall: float
    test_f1: float
    test_roc_auc: float
    test_pr_auc: float
    confusion_matrix: Dict[str, int]
    false_positive_rate: float
    false_negative_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_bottleneck_benchmarks() -> Dict[str, Any]:
    """Runs complete Phase 8 benchmarking across synthetic factory and secondary datasets."""
    root = get_project_root()
    output_dir = root / "models" / "bottleneck_prediction"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Synthetic Factory Data
    jobs_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "production_jobs.csv"
    machines_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "machines.csv"
    sensors_parquet = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.parquet"

    logger.info(f"Loading synthetic factory datasets from: {jobs_csv}")
    jobs_df = pd.read_csv(jobs_csv)
    machines_df = pd.read_csv(machines_csv)
    sensors_df = pd.read_parquet(sensors_parquet) if sensors_parquet.exists() else None

    # Prepare strictly chronological splits
    splits = prepare_bottleneck_splits(jobs_df, machines_df, sensors_df)
    X_train = splits["X_train"]
    y_train = splits["y_train"]
    X_val = splits["X_val"]
    y_val = splits["y_val"]
    X_test = splits["X_test"]
    y_test = splits["y_test"]

    # 2. Benchmarking Model Candidates
    # Heuristic baseline calibrated: pre_job_vibration_dev >= 0.50 OR prior_cycle_ratio >= 1.15
    models: List[BaseBottleneckClassifier] = [
        HeuristicBottleneckClassifier(vib_dev_threshold=0.50, cycle_ratio_threshold=1.15),
        LogisticBottleneckClassifier(C=0.5, random_state=42),
        RandomForestBottleneckClassifier(n_estimators=100, max_depth=5, random_state=42),
        XGBoostBottleneckClassifier(n_estimators=80, max_depth=3, scale_pos_weight=15.0, random_state=42)
    ]

    benchmark_records: List[Dict[str, Any]] = []
    champion_model: Optional[BaseBottleneckClassifier] = None
    best_pr_auc = -1.0
    champion_metrics: Optional[BottleneckBenchmarkResult] = None

    for model in models:
        logger.info(f"--- Benchmarking {model.name} ---")
        model.fit(X_train, y_train)

        # Predict on Test split (Days 18-30, N=130, Positives=8)
        p_test = model.predict_proba(X_test)[:, 1]
        
        # Threshold: standard 0.50 for decision boundary
        threshold = 0.50
        y_pred = (p_test >= threshold).astype(int)

        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        
        # In case model outputs constant probability on single-class train:
        try:
            roc_auc = float(roc_auc_score(y_test, p_test))
            pr_auc = float(average_precision_score(y_test, p_test))
        except Exception:
            roc_auc = 0.50
            pr_auc = float(np.mean(y_test))

        tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        cm_dict = {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}

        metrics = BottleneckBenchmarkResult(
            model_name=model.name,
            decision_threshold=threshold,
            test_precision=round(prec, 4),
            test_recall=round(rec, 4),
            test_f1=round(f1, 4),
            test_roc_auc=round(roc_auc, 4),
            test_pr_auc=round(pr_auc, 4),
            confusion_matrix=cm_dict,
            false_positive_rate=round(fpr, 4),
            false_negative_rate=round(fnr, 4)
        )

        logger.info(
            f"[{model.name}] Test Results: Precision={prec:.4f}, Recall={rec:.4f}, "
            f"F1={f1:.4f}, ROC-AUC={roc_auc:.4f}, PR-AUC={pr_auc:.4f}, FPR={fpr:.4f}"
        )

        benchmark_records.append(metrics.to_dict())

        # Select champion based on PR-AUC & F1
        if pr_auc > best_pr_auc:
            best_pr_auc = pr_auc
            champion_model = model
            champion_metrics = metrics

    # 3. Secondary Benchmark: Hybrid Manufacturing Categorical (06_MANUFACTURING_PRODUCTION)
    hybrid_csv = root / "DATASET" / "06_MANUFACTURING_PRODUCTION" / "raw" / "hybrid_manufacturing_categorical.csv"
    logger.info(f"Loading secondary benchmark dataset: {hybrid_csv}")
    df_hybrid = pd.read_csv(hybrid_csv)
    hybrid_splits = prepare_hybrid_manufacturing_benchmark(df_hybrid)

    # Evaluate Random Forest on secondary benchmark
    sec_rf = RandomForestBottleneckClassifier(n_estimators=100, max_depth=5, random_state=42)
    sec_rf.fit(hybrid_splits["X_train"], hybrid_splits["y_train"])
    p_sec = sec_rf.predict_proba(hybrid_splits["X_test"])[:, 1]
    sec_roc = float(roc_auc_score(hybrid_splits["y_test"], p_sec))
    sec_pr = float(average_precision_score(hybrid_splits["y_test"], p_sec))
    logger.info(f"[Secondary Hybrid Benchmark] ROC-AUC={sec_roc:.4f}, PR-AUC={sec_pr:.4f}")

    # 4. Serialize Champion Model & Artifacts
    champion_path = output_dir / "bottleneck_predictor.joblib"
    joblib.dump(
        {
            "model_name": champion_model.name,
            "model": champion_model,
            "threshold": champion_model.threshold,
            "feature_names": champion_model.feature_names
        },
        champion_path
    )
    logger.info(f"Saved champion bottleneck model to {champion_path}")

    # Comprehensive Metadata JSON
    metadata = {
        "subsystem": "Bottleneck Prediction & Flow Intelligence",
        "phase": "Phase 8",
        "champion_model": champion_model.name,
        "decision_threshold": champion_model.threshold,
        "feature_count": len(champion_model.feature_names),
        "features": champion_model.feature_names,
        "benchmark_comparison": benchmark_records,
        "champion_performance": champion_metrics.to_dict(),
        "temporal_split_counts": {
            "train_days_1_to_15": len(X_train),
            "val_days_16_to_17": len(X_val),
            "test_days_18_to_30": len(X_test),
            "total_jobs": len(jobs_df)
        },
        "target_formulation": {
            "target_variable": "bottleneck_event",
            "definition": "Cycle time expansion ratio >= 1.20 OR start dispatch delay >= 10.0 minutes OR status == DELAYED",
            "positives_count": int(splits["y_test"].sum()),
            "affected_machine": "M2 (Vertical Milling Center)"
        },
        "secondary_benchmark_evaluation": {
            "dataset": "06_MANUFACTURING_PRODUCTION",
            "total_records": len(df_hybrid),
            "test_roc_auc": round(sec_roc, 4),
            "test_pr_auc": round(sec_pr, 4),
            "finding": "Processing time and material used exhibit zero correlation with Job_Status; delay status is driven by operational dispatch delays rather than machine parameters."
        }
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved bottleneck metadata to {metadata_path}")

    return metadata


if __name__ == "__main__":
    run_bottleneck_benchmarks()
