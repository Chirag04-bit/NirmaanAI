"""
NirmaanAI Failure Classification Submodule
Implements baseline-first binary failure classification for shop-floor predictive maintenance.
Compares Dummy, Logistic Regression, Random Forest, and XGBoost models under severe class imbalance.
"""

from dataclasses import asdict, dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.utils.logger import logger


@dataclass
class ClassificationMetrics:
    model_name: str
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    macro_f1: float
    roc_auc: float
    pr_auc: float
    confusion_matrix: List[List[int]]
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int
    total_samples: int
    failure_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_classifier_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    model_name: str,
    threshold: float = 0.50
) -> ClassificationMetrics:
    """Computes full suite of classification metrics accounting for extreme class imbalance."""
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob)
    y_pred = (y_prob >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    # ROC-AUC and PR-AUC require probabilities
    try:
        roc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc = 0.50

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.0

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    return ClassificationMetrics(
        model_name=model_name,
        threshold=round(float(threshold), 3),
        accuracy=round(acc, 4),
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1_score=round(f1, 4),
        macro_f1=round(macro_f1, 4),
        roc_auc=round(roc, 4),
        pr_auc=round(pr_auc, 4),
        confusion_matrix=cm.tolist(),
        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
        true_positives=int(tp),
        total_samples=len(y_true),
        failure_count=int(y_true.sum())
    )


def find_optimal_f1_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    step: float = 0.02
) -> Tuple[float, float]:
    """Sweeps probability thresholds to find the threshold that maximizes F1 score on the validation set."""
    best_thresh = 0.50
    best_f1 = 0.0

    for thresh in np.arange(0.05, 0.95, step):
        preds = (y_prob >= thresh).astype(int)
        score = f1_score(y_true, preds, zero_division=0)
        if score > best_f1:
            best_f1 = score
            best_thresh = float(thresh)

    return round(best_thresh, 3), round(best_f1, 4)


class FailureClassifierBenchmark:
    """
    Orchestrates baseline-first training, threshold tuning, and model selection.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models: Dict[str, Any] = {}
        self.val_metrics: Dict[str, ClassificationMetrics] = {}
        self.test_metrics: Dict[str, ClassificationMetrics] = {}
        self.optimal_thresholds: Dict[str, float] = {}
        self.best_model_name: Optional[str] = None
        self.best_pipeline: Optional[Any] = None
        self.feature_names: List[str] = []

    def build_candidate_models(self, scale_pos_weight: float = 28.5) -> Dict[str, Any]:
        """Instantiates baselines and candidate non-linear models."""
        return {
            # 1. Baseline 1: Majority Dummy Classifier
            "dummy_majority": DummyClassifier(strategy="most_frequent"),

            # 2. Baseline 2: Balanced Logistic Regression with Feature Scaling
            "logistic_regression": Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=self.random_state
                ))
            ]),

            # 3. Candidate 1: Random Forest Classifier with Balanced Subsample
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                class_weight="balanced",
                max_depth=12,
                min_samples_split=5,
                random_state=self.random_state,
                n_jobs=-1
            ),

            # 4. Candidate 2: XGBoost Classifier with scale_pos_weight
            "xgboost": XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.08,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=self.random_state,
                n_jobs=-1
            )
        }

    def train_and_evaluate_all(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, Any]:
        """
        Trains all candidate models on X_train.
        Tunes thresholds on X_val.
        Evaluates final generalization metrics on X_test.
        """
        self.feature_names = list(X_train.columns)
        n_pos = int(y_train.sum())
        n_neg = int(len(y_train) - n_pos)
        scale_pos_weight = float(n_neg / max(n_pos, 1))

        self.models = self.build_candidate_models(scale_pos_weight=scale_pos_weight)

        logger.info(
            f"Training Failure Classifiers on {len(X_train)} samples (pos={n_pos}, neg={n_neg}, ratio={scale_pos_weight:.1f})."
        )

        for name, model in self.models.items():
            # 1. Fit model
            model.fit(X_train, y_train)

            # 2. Predict probabilities on validation set
            if hasattr(model, "predict_proba"):
                val_probs = model.predict_proba(X_val)[:, 1]
            else:
                val_probs = model.predict(X_val).astype(float)

            # 3. Find optimal threshold on validation set (except dummy)
            if name != "dummy_majority":
                opt_thresh, opt_f1 = find_optimal_f1_threshold(y_val.values, val_probs)
            else:
                opt_thresh = 0.50

            self.optimal_thresholds[name] = opt_thresh

            # 4. Record validation metrics at optimal threshold
            v_metric = evaluate_classifier_predictions(
                y_true=y_val.values,
                y_prob=val_probs,
                model_name=name,
                threshold=opt_thresh
            )
            self.val_metrics[name] = v_metric

            # 5. Evaluate on hold-out Test Set
            if hasattr(model, "predict_proba"):
                test_probs = model.predict_proba(X_test)[:, 1]
            else:
                test_probs = model.predict(X_test).astype(float)

            t_metric = evaluate_classifier_predictions(
                y_true=y_test.values,
                y_prob=test_probs,
                model_name=name,
                threshold=opt_thresh
            )
            self.test_metrics[name] = t_metric

            logger.info(
                f"Model [{name}]: Val F1={v_metric.f1_score:.4f}, Val ROC-AUC={v_metric.roc_auc:.4f} | "
                f"Test F1={t_metric.f1_score:.4f}, Test Recall={t_metric.recall:.4f}, Test Prec={t_metric.precision:.4f} "
                f"(Threshold={opt_thresh})"
            )

        # Select best model based on validation F1 score
        sorted_candidates = sorted(
            [m for m in self.val_metrics.items() if m[0] != "dummy_majority"],
            key=lambda x: (x[1].f1_score, x[1].pr_auc),
            reverse=True
        )
        self.best_model_name = sorted_candidates[0][0]
        self.best_pipeline = self.models[self.best_model_name]

        logger.info(f"Selected Champion Model: '{self.best_model_name}' based on validation performance.")

        return {
            "best_model_name": self.best_model_name,
            "optimal_threshold": self.optimal_thresholds[self.best_model_name],
            "val_metrics": {k: v.to_dict() for k, v in self.val_metrics.items()},
            "test_metrics": {k: v.to_dict() for k, v in self.test_metrics.items()}
        }

    def save_champion(self, output_dir: Path) -> Dict[str, Any]:
        """Serializes champion model pipeline and metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        model_path = output_dir / "failure_classifier.joblib"

        champion_payload = {
            "model_name": self.best_model_name,
            "model": self.best_pipeline,
            "threshold": self.optimal_thresholds[self.best_model_name],
            "feature_names": self.feature_names,
            "test_metrics": self.test_metrics[self.best_model_name].to_dict()
        }

        joblib.dump(champion_payload, model_path)
        logger.info(f"Saved champion failure classifier to {model_path}")

        return champion_payload

    @classmethod
    def load_champion(cls, model_path: Path) -> Dict[str, Any]:
        """Deserializes trained champion model payload."""
        payload = joblib.load(model_path)
        return payload
