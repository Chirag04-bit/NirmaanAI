"""
NirmaanAI Tuning Utilities
Standardized evaluation, bounded search utilities, threshold policies, and comparative improvement calculators.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
    auc,
)

from src.utils.config_loader import get_project_root
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class PCAReconstructionModel:
    def __init__(self, n_components: int = 5, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components, random_state=random_state)

    def fit(self, X: np.ndarray, y=None):
        X_scaled = self.scaler.fit_transform(X)
        self.pca.fit(X_scaled)
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        X_scaled = self.scaler.transform(X)
        X_reconstructed = self.pca.inverse_transform(self.pca.transform(X_scaled))
        mse = np.mean(np.square(X_scaled - X_reconstructed), axis=1)
        return -mse

    def get_params(self, deep: bool = True):
        return {"n_components": self.n_components, "random_state": self.random_state}


class RobustZScoreModel:
    def __init__(self):
        self.median_ = None
        self.iqr_ = None

    def fit(self, X: np.ndarray, y=None):
        self.median_ = np.median(X, axis=0)
        q75, q25 = np.percentile(X, [75, 25], axis=0)
        self.iqr_ = q75 - q25
        self.iqr_[self.iqr_ == 0] = 1.0
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        z_scores = np.abs(X - self.median_) / (self.iqr_ / 1.349)
        max_z = np.max(z_scores, axis=1)
        return -max_z

    def get_params(self, deep: bool = True):
        return {}


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """Computes standardized classification metrics."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "operating_threshold": float(threshold),
    }

    if y_prob is not None:
        try:
            if len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
                prob_pos = y_prob[:, 1]
            else:
                prob_pos = y_prob
            metrics["roc_auc"] = float(roc_auc_score(y_true, prob_pos))
            precision_pts, recall_pts, _ = precision_recall_curve(y_true, prob_pos)
            metrics["pr_auc"] = float(auc(recall_pts, precision_pts))
        except Exception:
            metrics["roc_auc"] = None
            metrics["pr_auc"] = None
    else:
        metrics["roc_auc"] = None
        metrics["pr_auc"] = None

    cm = confusion_matrix(y_true, y_pred).tolist()
    metrics["confusion_matrix"] = cm
    return metrics


def find_optimal_validation_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    metric_target: str = "f1",
) -> Tuple[float, float]:
    """
    Finds the optimal decision threshold on validation data ONLY.
    Never uses test data.
    """
    if len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
        prob_pos = y_prob[:, 1]
    else:
        prob_pos = y_prob

    best_thresh = 0.5
    best_score = -1.0

    thresholds = np.linspace(0.05, 0.95, 19)
    for t in thresholds:
        preds = (prob_pos >= t).astype(int)
        if metric_target == "f1":
            score = float(f1_score(y_true, preds, zero_division=0))
        elif metric_target == "recall":
            score = float(recall_score(y_true, preds, zero_division=0))
        elif metric_target == "precision":
            score = float(precision_score(y_true, preds, zero_division=0))
        else:
            score = float(f1_score(y_true, preds, zero_division=0))

        if score > best_score:
            best_score = score
            best_thresh = float(t)

    return best_thresh, best_score


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Computes standardized regression metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(root_mean_squared_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))

    denom_wape = float(np.sum(np.abs(y_true)))
    wape = float(np.sum(np.abs(y_true - y_pred)) / denom_wape) if denom_wape > 0 else 0.0

    denom_smape = np.abs(y_true) + np.abs(y_pred)
    valid_mask = denom_smape > 1e-8
    smape = float(np.mean(2.0 * np.abs(y_true[valid_mask] - y_pred[valid_mask]) / denom_smape[valid_mask])) if np.any(valid_mask) else 0.0

    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "wape": wape,
        "smape": smape,
    }


def compute_improvement(
    baseline_val: float,
    tuned_val: float,
    baseline_test: float,
    tuned_test: float,
    higher_is_better: bool = True,
) -> Dict[str, Any]:
    """Computes absolute and relative improvement metrics."""
    if higher_is_better:
        val_abs = tuned_val - baseline_val
        test_abs = tuned_test - baseline_test
        val_rel = (val_abs / abs(baseline_val) * 100.0) if baseline_val != 0 else 0.0
        test_rel = (test_abs / abs(baseline_test) * 100.0) if baseline_test != 0 else 0.0
    else:
        # For error metrics like RMSE, MAE, WAPE (lower is better)
        val_abs = baseline_val - tuned_val  # Positive means error reduced
        test_abs = baseline_test - tuned_test
        val_rel = (val_abs / abs(baseline_val) * 100.0) if baseline_val != 0 else 0.0
        test_rel = (test_abs / abs(baseline_test) * 100.0) if baseline_test != 0 else 0.0

    return {
        "baseline_val": baseline_val,
        "tuned_val": tuned_val,
        "val_abs_improvement": val_abs,
        "val_rel_improvement_pct": val_rel,
        "baseline_test": baseline_test,
        "tuned_test": tuned_test,
        "test_abs_delta": test_abs,
        "test_rel_delta_pct": test_rel,
        "higher_is_better": higher_is_better,
    }


def load_baseline_benchmark(dataset_id: str) -> Dict[str, Any]:
    """Loads the locked frozen baseline benchmark for comparative auditing."""
    root = get_project_root()
    b_dir = root / "models" / "benchmarks" / dataset_id
    with open(b_dir / "benchmark_metadata.json") as f:
        meta = json.load(f)
    with open(b_dir / "final_test_metrics.json") as f:
        test_m = json.load(f)
    with open(b_dir / "validation_metrics.json") as f:
        val_m = json.load(f)

    # Extract primary validation score
    val_score = meta.get("validation_score")
    if val_score is None:
        for k in ["validation_score_pr_auc", "validation_score_rmse", "validation_score_wape", "validation_score_mean"]:
            if k in meta:
                val_score = meta[k]
                break

    # Extract primary test score
    test_score = meta.get("test_score")
    if test_score is None:
        for k in ["test_score_pr_auc", "test_score_rmse", "test_score_wape", "test_score_mean"]:
            if k in meta:
                test_score = meta[k]
                break

    return {
        "metadata": meta,
        "test_metrics": test_m,
        "validation_metrics": val_m,
        "val_score": float(val_score) if val_score is not None else None,
        "test_score": float(test_score) if test_score is not None else None,
    }

