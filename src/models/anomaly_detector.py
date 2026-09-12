"""
NirmaanAI Multi-Sensor Anomaly Detection Model Implementations
Provides unified scikit-learn compatible anomaly detectors:
1. Robust Multivariate Z-Score (Statistical Baseline)
2. PCA Reconstruction Error (Covariance Subspace Baseline)
3. One-Class SVM (Non-linear Kernel Baseline)
4. Isolation Forest (Ensemble Tree Partitioning)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.svm import OneClassSVM

from src.utils.logger import logger


class BaseAnomalyDetector(ABC):
    """Abstract base class for all NirmaanAI anomaly detectors."""

    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False
        self.threshold: float = 0.5
        self.feature_names: List[str] = []

    @abstractmethod
    def fit(self, X: pd.DataFrame) -> "BaseAnomalyDetector":
        pass

    @abstractmethod
    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        """Returns continuous anomaly score in [0, 1] range (higher = more anomalous)."""
        pass

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Returns binary predictions: 1 for anomaly, 0 for normal."""
        scores = self.score_samples(X)
        return (scores >= self.threshold).astype(int)

    def calibrate_threshold(self, X_val: pd.DataFrame, target_quantile: float = 0.99) -> float:
        """
        Calibrates threshold using the empirical quantile of the nominal validation set.
        Default target_quantile=0.99 aims for ~1% nominal false positive rate on unpolluted validation data.
        """
        scores = self.score_samples(X_val)
        self.threshold = float(np.quantile(scores, target_quantile))
        logger.info(f"[{self.name}] Calibrated threshold at quantile {target_quantile:.3f}: {self.threshold:.5f}")
        return self.threshold


class RobustZScoreDetector(BaseAnomalyDetector):
    """
    Multivariate Statistical Baseline.
    Uses median and Interquartile Range (IQR) fit on reference nominal data.
    Anomaly score = normalized RMS of robust z-scores, min-max scaled into [0, 1].
    """

    def __init__(self):
        super().__init__(name="robust_zscore")
        self.medians: Optional[np.ndarray] = None
        self.iqrs: Optional[np.ndarray] = None
        self.max_ref_score: float = 1.0

    def fit(self, X: pd.DataFrame) -> "RobustZScoreDetector":
        self.feature_names = list(X.columns)
        X_mat = X.values.astype(float)
        self.medians = np.median(X_mat, axis=0)
        q75 = np.percentile(X_mat, 75, axis=0)
        q25 = np.percentile(X_mat, 25, axis=0)
        iqrs = q75 - q25
        # Avoid division by zero for constant/low-variance features
        self.iqrs = np.where(iqrs > 1e-6, iqrs, 1.0)

        # Reference RMS score distribution to establish normalization
        devs = np.abs(X_mat - self.medians) / self.iqrs
        rms = np.sqrt(np.mean(devs ** 2, axis=1))
        self.max_ref_score = float(np.percentile(rms, 99.9)) or 1.0
        self.is_fitted = True
        return self

    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Model must be fit before scoring.")
        X_mat = X[self.feature_names].values.astype(float)
        devs = np.abs(X_mat - self.medians) / self.iqrs
        rms = np.sqrt(np.mean(devs ** 2, axis=1))
        # Continuous bounded score in [0, 1]
        scores = np.clip(rms / (self.max_ref_score * 2.0), 0.0, 1.0)
        return scores

    def compute_feature_contributions(self, X: pd.DataFrame) -> pd.DataFrame:
        """Returns normalized individual z-scores per feature."""
        X_mat = X[self.feature_names].values.astype(float)
        devs = np.abs(X_mat - self.medians) / self.iqrs
        return pd.DataFrame(devs, columns=self.feature_names, index=X.index)


class PCAReconstructionDetector(BaseAnomalyDetector):
    """
    Subspace Reconstruction Error Baseline.
    Fits PCA on nominal features. Reconstruction error = ||x - x_reconstructed||^2.
    """

    def __init__(self, variance_retained: float = 0.90):
        super().__init__(name="pca_reconstruction")
        self.variance_retained = variance_retained
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=variance_retained, svd_solver="full")
        self.max_ref_error: float = 1.0

    def fit(self, X: pd.DataFrame) -> "PCAReconstructionDetector":
        self.feature_names = list(X.columns)
        X_scaled = self.scaler.fit_transform(X.values)
        self.pca.fit(X_scaled)
        reconstructed = self.pca.inverse_transform(self.pca.transform(X_scaled))
        errors = np.mean((X_scaled - reconstructed) ** 2, axis=1)
        self.max_ref_error = float(np.percentile(errors, 99.9)) or 1.0
        self.is_fitted = True
        logger.info(
            f"[{self.name}] Retained {self.pca.n_components_} components "
            f"explaining {np.sum(self.pca.explained_variance_ratio_):.2%} of variance."
        )
        return self

    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Model must be fit before scoring.")
        X_mat = X[self.feature_names].values
        X_scaled = self.scaler.transform(X_mat)
        reconstructed = self.pca.inverse_transform(self.pca.transform(X_scaled))
        errors = np.mean((X_scaled - reconstructed) ** 2, axis=1)
        scores = np.clip(errors / (self.max_ref_error * 3.0), 0.0, 1.0)
        return scores

    def compute_feature_contributions(self, X: pd.DataFrame) -> pd.DataFrame:
        """Returns squared reconstruction error per individual feature."""
        X_mat = X[self.feature_names].values
        X_scaled = self.scaler.transform(X_mat)
        reconstructed = self.pca.inverse_transform(self.pca.transform(X_scaled))
        feature_errors = (X_scaled - reconstructed) ** 2
        return pd.DataFrame(feature_errors, columns=self.feature_names, index=X.index)


class OneClassSVMDetector(BaseAnomalyDetector):
    """
    Non-linear Support Vector Machine Baseline.
    RBF kernel estimates support of nominal training distribution.
    Anomaly score = sigmoid normalized negative decision function.
    """

    def __init__(self, nu: float = 0.05, gamma: str = "scale"):
        super().__init__(name="one_class_svm")
        self.nu = nu
        self.gamma = gamma
        self.scaler = RobustScaler()
        self.svm = OneClassSVM(nu=nu, gamma=gamma, kernel="rbf")

    def fit(self, X: pd.DataFrame) -> "OneClassSVMDetector":
        self.feature_names = list(X.columns)
        X_scaled = self.scaler.fit_transform(X.values)
        self.svm.fit(X_scaled)
        self.is_fitted = True
        return self

    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Model must be fit before scoring.")
        X_scaled = self.scaler.transform(X[self.feature_names].values)
        # Decision function: positive for inliers, negative for outliers
        dec = self.svm.decision_function(X_scaled)
        # Sigmoidal mapping so that large negative distance -> 1.0 anomaly score
        scores = 1.0 / (1.0 + np.exp(dec))
        return scores


class IsolationForestDetector(BaseAnomalyDetector):
    """
    Tree-based Ensemble Isolation Detector (Candidate Champion).
    Standardized score: s(x, n) in [0, 1].
    """

    def __init__(
        self,
        n_estimators: int = 150,
        contamination: Union[str, float] = 0.02,
        random_state: int = 42
    ):
        super().__init__(name="isolation_forest")
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.iforest = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: pd.DataFrame) -> "IsolationForestDetector":
        self.feature_names = list(X.columns)
        X_scaled = self.scaler.fit_transform(X.values)
        self.iforest.fit(X_scaled)
        self.is_fitted = True
        return self

    def score_samples(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"[{self.name}] Model must be fit before scoring.")
        X_scaled = self.scaler.transform(X[self.feature_names].values)
        # score_samples returns opposite of anomaly score (lower is more anomalous)
        raw_scores = self.iforest.score_samples(X_scaled)
        # Standardized conversion: map raw scores (~ [-0.8, -0.2]) to [0, 1] where 1 is highest anomaly
        # In sklearn, raw_score = -0.5 is the offset boundary
        scores = np.clip(0.5 - raw_scores, 0.0, 1.0)
        return scores
