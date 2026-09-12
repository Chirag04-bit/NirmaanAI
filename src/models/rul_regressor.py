"""
NirmaanAI Remaining Useful Life (RUL) Regression Submodule
Implements baseline-first RUL regression for turbofan engine degradation on NASA C-MAPSS.
Evaluates Dummy Mean, Ridge/Linear, Random Forest, and XGBoost models.
"""

from dataclasses import asdict, dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from src.utils.logger import logger


@dataclass
class RegressionMetrics:
    model_name: str
    mae: float
    rmse: float
    r2: float
    nasa_score: float
    sample_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_nasa_scoring_function(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes NASA C-MAPSS asymmetric scoring function:
    Penalizes late predictions (optimistic, d >= 0) more severely than early predictions (pessimistic, d < 0).
    d_i = y_pred_i - y_true_i
    S = sum(exp(-d_i / 13) - 1 for d_i < 0) + sum(exp(d_i / 10) - 1 for d_i >= 0)
    """
    d = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)
    # Clip large positive errors to avoid floating point overflow in exp(d/10)
    d_clipped = np.clip(d, -100.0, 100.0)

    score = 0.0
    for diff in d_clipped:
        if diff < 0:
            score += np.exp(-diff / 13.0) - 1.0
        else:
            score += np.exp(diff / 10.0) - 1.0

    return float(score)


def evaluate_regression_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str
) -> RegressionMetrics:
    """Computes MAE, RMSE, R^2, and NASA asymmetric score."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    nasa_score = compute_nasa_scoring_function(y_true, y_pred)

    return RegressionMetrics(
        model_name=model_name,
        mae=round(mae, 3),
        rmse=round(rmse, 3),
        r2=round(r2, 4),
        nasa_score=round(nasa_score, 2),
        sample_count=len(y_true)
    )


class RULRegressorBenchmark:
    """
    Orchestrates baseline-first training and evaluation for RUL estimation.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models: Dict[str, Any] = {}
        self.val_metrics: Dict[str, RegressionMetrics] = {}
        self.internal_test_metrics: Dict[str, RegressionMetrics] = {}
        self.official_test_metrics: Dict[str, RegressionMetrics] = {}
        self.best_model_name: Optional[str] = None
        self.best_pipeline: Optional[Any] = None
        self.feature_names: List[str] = []

    def build_candidate_models(self) -> Dict[str, Any]:
        """Instantiates baselines and candidate non-linear regression models."""
        return {
            # 1. Baseline 1: Dummy Mean Predictor
            "dummy_mean": DummyRegressor(strategy="mean"),

            # 2. Baseline 2: Ridge Regression with Feature Scaling
            "ridge_regression": Pipeline([
                ("scaler", StandardScaler()),
                ("reg", Ridge(alpha=100.0, random_state=self.random_state))
            ]),

            # 3. Candidate 1: Random Forest Regressor
            "random_forest_reg": RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=6,
                random_state=self.random_state,
                n_jobs=-1
            ),

            # 4. Candidate 2: XGBoost Regressor
            "xgboost_reg": XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.06,
                subsample=0.85,
                colsample_bytree=0.85,
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
        X_test_internal: pd.DataFrame,
        y_test_internal: pd.Series,
        X_official_test: Optional[pd.DataFrame] = None,
        y_official_test: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Trains candidate models on grouped training engines.
        Validates on grouped validation engines.
        Evaluates on internal test engines and official benchmark test set.
        """
        self.feature_names = list(X_train.columns)
        self.models = self.build_candidate_models()

        logger.info(f"Training RUL Regressors on {len(X_train)} samples across engine trajectories...")

        for name, model in self.models.items():
            model.fit(X_train, y_train)

            # 1. Validation evaluation
            val_preds = model.predict(X_val)
            v_metric = evaluate_regression_predictions(y_val.values, val_preds, name)
            self.val_metrics[name] = v_metric

            # 2. Internal test evaluation
            int_test_preds = model.predict(X_test_internal)
            it_metric = evaluate_regression_predictions(y_test_internal.values, int_test_preds, name)
            self.internal_test_metrics[name] = it_metric

            # 3. Official benchmark test evaluation
            if X_official_test is not None and y_official_test is not None:
                off_test_preds = model.predict(X_official_test)
                ot_metric = evaluate_regression_predictions(y_official_test, off_test_preds, name)
                self.official_test_metrics[name] = ot_metric

            logger.info(
                f"RUL Model [{name}]: Val RMSE={v_metric.rmse:.2f}, Val MAE={v_metric.mae:.2f} | "
                f"Internal Test RMSE={it_metric.rmse:.2f}, Official Benchmark RMSE={self.official_test_metrics.get(name, it_metric).rmse:.2f}"
            )

        # Select best model based on validation RMSE
        sorted_candidates = sorted(
            [m for m in self.val_metrics.items() if m[0] != "dummy_mean"],
            key=lambda x: x[1].rmse
        )
        self.best_model_name = sorted_candidates[0][0]
        self.best_pipeline = self.models[self.best_model_name]

        logger.info(f"Selected Champion RUL Model: '{self.best_model_name}' (Validation RMSE={self.val_metrics[self.best_model_name].rmse:.2f}).")

        return {
            "best_model_name": self.best_model_name,
            "val_metrics": {k: v.to_dict() for k, v in self.val_metrics.items()},
            "internal_test_metrics": {k: v.to_dict() for k, v in self.internal_test_metrics.items()},
            "official_test_metrics": {k: v.to_dict() for k, v in self.official_test_metrics.items()}
        }

    def save_champion(self, output_dir: Path) -> Dict[str, Any]:
        """Serializes champion RUL regressor pipeline and metadata."""
        output_dir.mkdir(parents=True, exist_ok=True)
        model_path = output_dir / "rul_regressor.joblib"

        champion_payload = {
            "model_name": self.best_model_name,
            "model": self.best_pipeline,
            "feature_names": self.feature_names,
            "val_metrics": self.val_metrics[self.best_model_name].to_dict(),
            "internal_test_metrics": self.internal_test_metrics[self.best_model_name].to_dict(),
            "official_test_metrics": self.official_test_metrics.get(self.best_model_name, {}).to_dict()
            if self.best_model_name in self.official_test_metrics else {}
        }

        joblib.dump(champion_payload, model_path)
        logger.info(f"Saved champion RUL regressor to {model_path}")

        return champion_payload

    @classmethod
    def load_champion(cls, model_path: Path) -> Dict[str, Any]:
        """Deserializes trained champion RUL regressor payload."""
        payload = joblib.load(model_path)
        return payload
