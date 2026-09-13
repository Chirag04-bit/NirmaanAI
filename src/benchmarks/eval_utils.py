"""
NirmaanAI Benchmark Evaluation Utilities
Standardized, reproducible metric calculations for classification and regression baselines.
"""

from typing import Any, Dict
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


def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, Any]:
    """Computes standard classification metrics without threshold optimization."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    if y_prob is not None:
        try:
            # If 2D probability matrix, take positive class column
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


def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Computes standard regression metrics (MAE, RMSE, R2, WAPE, sMAPE)."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(root_mean_squared_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))

    # WAPE = sum(|y - y_hat|) / sum(|y|)
    denom_wape = float(np.sum(np.abs(y_true)))
    wape = float(np.sum(np.abs(y_true - y_pred)) / denom_wape) if denom_wape > 0 else 0.0

    # sMAPE = (200 / n) * sum(|y - y_hat| / (|y| + |y_hat|))
    denom_smape = np.abs(y_true) + np.abs(y_pred)
    # Avoid zero division
    valid_mask = denom_smape > 1e-8
    if np.any(valid_mask):
        smape = float(np.mean(2.0 * np.abs(y_true[valid_mask] - y_pred[valid_mask]) / denom_smape[valid_mask]))
    else:
        smape = 0.0

    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "wape": wape,
        "smape": smape,
    }
