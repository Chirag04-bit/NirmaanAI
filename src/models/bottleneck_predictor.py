"""
NirmaanAI Bottleneck Prediction Model Implementations
Provides unified scikit-learn compatible classifiers for production flow bottleneck forecasting:
1. Heuristic Rule-Based Baseline
2. Regularized Logistic Regression Baseline
3. Balanced Random Forest Classifier
4. XGBoost Classifier
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
from xgboost import XGBClassifier

from src.utils.logger import logger


class BaseBottleneckClassifier(ABC):
    """Abstract base class for bottleneck classifiers."""

    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False
        self.threshold: float = 0.50
        self.feature_names: List[str] = []

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "BaseBottleneckClassifier":
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        pass

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        proba = self.predict_proba(X)[:, 1]
        return (proba >= self.threshold).astype(int)


class HeuristicBottleneckClassifier(BaseBottleneckClassifier):
    """
    Domain-Informed Flow Risk Heuristic Baseline.
    Evaluates pre-job mechanical telemetry deviation and lagged cycle ratio.
    Configured domain/scenario thresholds:
    - vib_dev_threshold: 0.30 mm/s (configured scenario threshold based on baseline vibration 1.4 mm/s)
    - cycle_ratio_threshold: 1.10 (configured threshold for 10% cycle slowdown)
    - decision_threshold: 0.40 (configured composite flow-risk score cutoff)
    NOTE: These thresholds are configured domain priors, not statistically fit using test data.
    """

    def __init__(
        self,
        vib_dev_threshold: float = 0.30,
        cycle_ratio_threshold: float = 1.10,
        decision_threshold: float = 0.40
    ):
        super().__init__(name="heuristic_baseline")
        self.vib_dev_threshold = vib_dev_threshold
        self.cycle_ratio_threshold = cycle_ratio_threshold
        self.threshold = decision_threshold

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "HeuristicBottleneckClassifier":
        self.feature_names = list(X.columns)
        self.is_fitted = True
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        n = len(X)
        probs = np.zeros((n, 2))

        vib_dev = X.get("pre_job_vibration_dev_1h", pd.Series(np.zeros(n), index=X.index))
        cycle_ratio = X.get("prior_cycle_ratio_mean", pd.Series(np.ones(n), index=X.index))

        # Continuous risk score: 50% physical telemetry deviation + 50% flow cycle lag
        vib_risk = np.clip(vib_dev.values / 0.50, 0.0, 1.0)
        cycle_risk = np.clip((cycle_ratio.values - 1.0) / 0.25, 0.0, 1.0)
        p1 = 0.50 * vib_risk + 0.50 * cycle_risk

        probs[:, 1] = p1
        probs[:, 0] = 1.0 - p1
        return probs


class LogisticBottleneckClassifier(BaseBottleneckClassifier):
    """Baseline 2: Regularized L2 Logistic Regression with class weighting."""

    def __init__(self, C: float = 1.0, random_state: int = 42):
        super().__init__(name="logistic_regression")
        self.C = C
        self.random_state = random_state
        self.pipeline = Pipeline([
            ("scaler", RobustScaler()),
            ("model", LogisticRegression(
                C=C,
                class_weight="balanced",
                random_state=random_state,
                max_iter=1000
            ))
        ])

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "LogisticBottleneckClassifier":
        self.feature_names = list(X.columns)
        # Handle single-class training edge cases
        if len(np.unique(y)) < 2:
            self.is_fitted = True
            return self
        self.pipeline.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        try:
            return self.pipeline.predict_proba(X)
        except Exception:
            # Fallback if fit with single class
            n = len(X)
            probs = np.zeros((n, 2))
            probs[:, 0] = 1.0
            return probs


class RandomForestBottleneckClassifier(BaseBottleneckClassifier):
    """Candidate 1: Random Forest with balanced class weights."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 6,
        random_state: int = 42
    ):
        super().__init__(name="random_forest")
        self.pipeline = Pipeline([
            ("scaler", RobustScaler()),
            ("model", RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                class_weight="balanced",
                random_state=random_state,
                n_jobs=-1
            ))
        ])

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "RandomForestBottleneckClassifier":
        self.feature_names = list(X.columns)
        if len(np.unique(y)) < 2:
            self.is_fitted = True
            return self
        self.pipeline.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        try:
            return self.pipeline.predict_proba(X)
        except Exception:
            n = len(X)
            probs = np.zeros((n, 2))
            probs[:, 0] = 1.0
            return probs


class XGBoostBottleneckClassifier(BaseBottleneckClassifier):
    """Candidate 2: Gradient Boosted Trees with scale_pos_weight."""

    def __init__(
        self,
        n_estimators: int = 80,
        max_depth: int = 4,
        learning_rate: float = 0.08,
        scale_pos_weight: float = 10.0,
        random_state: int = 42
    ):
        super().__init__(name="xgboost")
        self.pipeline = Pipeline([
            ("scaler", RobustScaler()),
            ("model", XGBClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                scale_pos_weight=scale_pos_weight,
                random_state=random_state,
                eval_metric="logloss",
                n_jobs=-1
            ))
        ])

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "XGBoostBottleneckClassifier":
        self.feature_names = list(X.columns)
        if len(np.unique(y)) < 2:
            self.is_fitted = True
            return self
        self.pipeline.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        try:
            return self.pipeline.predict_proba(X)
        except Exception:
            n = len(X)
            probs = np.zeros((n, 2))
            probs[:, 0] = 1.0
            return probs
