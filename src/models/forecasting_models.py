"""
NirmaanAI Time-Series Forecasting Model Implementations
Phase 9: Production & Energy Forecasting

Models implemented following baseline-first hierarchy:
1. Persistence / Naive Baseline (lag-24h / lag-1h)
2. Seasonal Diurnal Profile Baseline (hour-of-day x day-of-week historical mean)
3. Regularized L2 Linear Regression (Ridge)
4. Random Forest Regressor
5. XGBoost Regressor (Candidate Champion)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from src.features.forecasting_features import calculate_forecasting_metrics
from src.utils.logger import logger


class BaseForecaster(ABC):
    """Abstract base class for all NirmaanAI forecasting models."""

    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False
        self.feature_names: List[str] = []

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "BaseForecaster":
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluates predictions using MAE, RMSE, R2, WAPE, and sMAPE."""
        preds = self.predict(X)
        return calculate_forecasting_metrics(y, preds)


class PersistenceForecaster(BaseForecaster):
    """
    Baseline 1: Persistence / Naive Baseline.
    Predicts using semantic lag column: lag_24h (same hour yesterday) if present,
    otherwise falls back to lag_1h.
    """

    def __init__(self, lag_col_preference: str = "lag_24h"):
        super().__init__(name="persistence_baseline")
        self.lag_col_preference = lag_col_preference
        self.lag_index: int = 0
        self.default_fallback: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "PersistenceForecaster":
        self.is_fitted = True
        self.default_fallback = float(np.mean(y))
        if feature_names:
            self.feature_names = feature_names
            if self.lag_col_preference in feature_names:
                self.lag_index = feature_names.index(self.lag_col_preference)
            elif "lag_1h" in feature_names:
                self.lag_index = feature_names.index("lag_1h")
            elif "lag_completed_1d" in feature_names:
                self.lag_index = feature_names.index("lag_completed_1d")
            else:
                self.lag_index = 0
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if X.shape[1] > self.lag_index:
            preds = X[:, self.lag_index].copy()
            # Replace any NaNs with fallback
            nan_mask = np.isnan(preds)
            preds[nan_mask] = self.default_fallback
            return np.maximum(0.0, preds)
        return np.full(len(X), self.default_fallback)


class SeasonalDiurnalForecaster(BaseForecaster):
    """
    Baseline 2: Seasonal Diurnal Profile Baseline.
    Fits historical conditional mean by (hour_of_day, is_weekend).
    Captures standard diurnal cycle without parameterized machine learning.
    """

    def __init__(self):
        super().__init__(name="seasonal_diurnal_baseline")
        self.diurnal_profile: Dict[Tuple[int, int], float] = {}
        self.overall_mean: float = 0.0
        self.hour_idx: int = -1
        self.weekend_idx: int = -1

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "SeasonalDiurnalForecaster":
        self.is_fitted = True
        self.overall_mean = float(np.mean(y))
        if feature_names:
            self.feature_names = feature_names
            if "hour" in feature_names:
                self.hour_idx = feature_names.index("hour")
            if "is_weekend" in feature_names:
                self.weekend_idx = feature_names.index("is_weekend")

        if self.hour_idx != -1:
            hours = X[:, self.hour_idx].astype(int)
            weekends = X[:, self.weekend_idx].astype(int) if self.weekend_idx != -1 else np.zeros(len(X), dtype=int)
            
            df_temp = pd.DataFrame({"hour": hours, "weekend": weekends, "y": y})
            grouped = df_temp.groupby(["hour", "weekend"])["y"].mean().to_dict()
            self.diurnal_profile = grouped
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        if self.hour_idx == -1:
            return np.full(len(X), self.overall_mean)

        hours = X[:, self.hour_idx].astype(int)
        weekends = X[:, self.weekend_idx].astype(int) if self.weekend_idx != -1 else np.zeros(len(X), dtype=int)
        
        preds = np.zeros(len(X))
        for i in range(len(X)):
            key = (int(hours[i]), int(weekends[i]))
            preds[i] = self.diurnal_profile.get(key, self.overall_mean)
        return np.maximum(0.0, preds)


class RidgeForecaster(BaseForecaster):
    """
    Candidate 1: Regularized L2 Linear Regression (Ridge).
    Applies StandardScaler pipeline for stable coefficient estimation.
    """

    def __init__(self, alpha: float = 1.0, random_state: int = 42):
        super().__init__(name="ridge_regression")
        self.alpha = alpha
        self.random_state = random_state
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=alpha, random_state=random_state))
        ])

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "RidgeForecaster":
        self.feature_names = feature_names or []
        self.pipeline.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        preds = self.pipeline.predict(X)
        return np.maximum(0.0, preds)


class RandomForestForecaster(BaseForecaster):
    """
    Candidate 2: Non-linear Random Forest Regressor.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        random_state: int = 42
    ):
        super().__init__(name="random_forest")
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "RandomForestForecaster":
        self.feature_names = feature_names or []
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        preds = self.model.predict(X)
        return np.maximum(0.0, preds)


class XGBoostForecaster(BaseForecaster):
    """
    Candidate 3: Gradient Boosted Trees (XGBoost Regressor).
    Candidate champion for capturing non-linear diurnal cycles and autoregressive lag dynamics.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.05,
        max_depth: int = 5,
        subsample: float = 0.85,
        random_state: int = 42
    ):
        super().__init__(name="xgboost")
        self.model = XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            subsample=subsample,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "XGBoostForecaster":
        self.feature_names = feature_names or []
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Must be fit before predicting.")
        preds = self.model.predict(X)
        return np.maximum(0.0, preds)
