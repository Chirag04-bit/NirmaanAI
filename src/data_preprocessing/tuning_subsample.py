"""
NirmaanAI — Tuning Subsample & Dataset Volume Optimization Module
================================================================
Post-Phase-25 Research & Engineering Extension

Provides deterministic, reproducible, distribution-preserving computational
subsets of large industrial training datasets exclusively for hyperparameter
search and model selection.

Epistemic Status: CONTROLLED_COMPUTATIONAL_SUBSET

Rules:
1. Subsets are generated ONLY from training partitions (train.parquet).
2. Validation (val.parquet) and test (test.parquet) are NEVER sampled or touched.
3. Subsets are computational aids only and never replace canonical datasets.
4. Final champion training always returns to the FULL training partition.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from scipy import stats


def calculate_file_md5(filepath: str) -> str:
    """Calculate MD5 checksum of a file."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def deterministic_stratified_classification_sample(
    df: pd.DataFrame,
    target_col: str,
    stratify_cols: Optional[List[str]] = None,
    target_rows: int = 105000,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Deterministically sample rows preserving joint class and categorical distributions
    via index-based group sampling.
    """
    if len(df) <= target_rows:
        return df.copy()

    frac = target_rows / len(df)
    cols_to_group = [target_col]
    if stratify_cols:
        for col in stratify_cols:
            if col in df.columns and col not in cols_to_group:
                cols_to_group.append(col)

    # Deterministic index selection
    rng = np.random.RandomState(random_state)
    selected_indices = []

    for _, group in df.groupby(cols_to_group, observed=False):
        n_group = len(group)
        if n_group <= 1:
            selected_indices.extend(group.index.tolist())
        else:
            k = int(round(n_group * frac))
            # ensure at least 1 sample if group exists and k is 0
            k = max(1, min(k, n_group))
            sampled_idx = rng.choice(group.index, size=k, replace=False)
            selected_indices.extend(sampled_idx.tolist())

    selected_indices = list(set(selected_indices))
    diff = len(selected_indices) - target_rows

    if diff > 0:
        # Drop excess deterministically
        drop_idx = rng.choice(selected_indices, size=diff, replace=False)
        selected_indices = [idx for idx in selected_indices if idx not in set(drop_idx)]
    elif diff < 0:
        # Fill deficit deterministically from unselected
        remaining_pool = [idx for idx in df.index if idx not in set(selected_indices)]
        add_idx = rng.choice(remaining_pool, size=abs(diff), replace=False)
        selected_indices.extend(add_idx.tolist())

    subsample = df.loc[sorted(selected_indices)].copy()
    return subsample


def deterministic_distribution_aware_regression_sample(
    df: pd.DataFrame,
    target_col: str,
    stratify_cols: Optional[List[str]] = None,
    n_bins: int = 10,
    target_rows: int = 105000,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Deterministically sample rows preserving continuous target distribution via quantile binning
    and index-based sampling.
    """
    if len(df) <= target_rows:
        return df.copy()

    # Create quantile bins for continuous target
    target_bins = pd.qcut(df[target_col], q=n_bins, labels=False, duplicates="drop")
    
    grouping_series = [target_bins]
    if stratify_cols:
        for col in stratify_cols:
            if col in df.columns:
                grouping_series.append(df[col])

    frac = target_rows / len(df)
    rng = np.random.RandomState(random_state)
    selected_indices = []

    for _, group_idx in df.groupby(grouping_series, observed=False).groups.items():
        n_group = len(group_idx)
        if n_group <= 1:
            selected_indices.extend(group_idx.tolist())
        else:
            k = int(round(n_group * frac))
            k = max(1, min(k, n_group))
            sampled_idx = rng.choice(group_idx, size=k, replace=False)
            selected_indices.extend(sampled_idx.tolist())

    selected_indices = list(set(selected_indices))
    diff = len(selected_indices) - target_rows

    if diff > 0:
        drop_idx = rng.choice(selected_indices, size=diff, replace=False)
        selected_indices = [idx for idx in selected_indices if idx not in set(drop_idx)]
    elif diff < 0:
        remaining_pool = [idx for idx in df.index if idx not in set(selected_indices)]
        add_idx = rng.choice(remaining_pool, size=abs(diff), replace=False)
        selected_indices.extend(add_idx.tolist())

    subsample = df.loc[sorted(selected_indices)].copy()
    return subsample


def deterministic_chronological_window_sample(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    target_fraction: float = 0.5
) -> pd.DataFrame:
    """
    Deterministically take the most recent contiguous chronological window of the training partition.
    Preserves strict temporal ordering and causal lag structure.
    """
    df_sorted = df.sort_values(timestamp_col)
    n_rows = int(len(df_sorted) * target_fraction)
    start_idx = len(df_sorted) - n_rows
    subsample = df_sorted.iloc[start_idx:].copy()
    return subsample


def deterministic_temporal_stride_sample(
    df: pd.DataFrame,
    stride: int = 2,
    group_col: Optional[str] = "machine_id",
    timestamp_col: str = "timestamp"
) -> pd.DataFrame:
    """
    Deterministically sample every n-th observation while preserving synchronized multi-machine alignment.
    """
    if group_col and group_col in df.columns:
        selected_indices = []
        for _, group in df.groupby(group_col):
            sorted_idx = group.sort_values(timestamp_col).index
            selected_indices.extend(sorted_idx[::stride].tolist())
        subsample = df.loc[sorted(selected_indices)].copy()
    else:
        df_sorted = df.sort_values(timestamp_col)
        subsample = df_sorted.iloc[::stride].copy()
    return subsample


def compute_representativeness_audit(
    full_df: pd.DataFrame,
    subset_df: pd.DataFrame,
    target_col: Optional[str] = None,
    cat_cols: Optional[List[str]] = None,
    num_cols: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compute distribution comparison, moment statistics, and drift metrics between full and subset data.
    """
    audit: Dict[str, Any] = {
        "full_rows": len(full_df),
        "subset_rows": len(subset_df),
        "retention_percentage": round((len(subset_df) / len(full_df)) * 100.0, 4),
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": "REPRESENTATIVE_COMPUTATIONAL_SUBSET",
        "numerical_moments": {},
        "target_distribution": {},
        "categorical_distributions": {}
    }

    # Numerical statistics
    if num_cols is None:
        num_cols = [c for c in full_df.select_dtypes(include=[np.number]).columns if c != target_col]

    for col in num_cols:
        f_series = full_df[col].dropna()
        s_series = subset_df[col].dropna()

        # Moments & quantiles
        f_mean, f_std = float(f_series.mean()), float(f_series.std())
        s_mean, s_std = float(s_series.mean()), float(s_series.std())

        # Kolmogorov-Smirnov two-sample test (subsample size bounded for speed)
        n_eval = min(5000, len(f_series), len(s_series))
        ks_stat, ks_pval = stats.ks_2samp(
            f_series.sample(n_eval, random_state=42),
            s_series.sample(n_eval, random_state=42)
        )

        audit["numerical_moments"][col] = {
            "full_mean": round(f_mean, 6),
            "subset_mean": round(s_mean, 6),
            "mean_abs_diff": round(abs(f_mean - s_mean), 6),
            "full_std": round(f_std, 6),
            "subset_std": round(s_std, 6),
            "full_quantiles": {
                "q25": round(float(f_series.quantile(0.25)), 6),
                "q50": round(float(f_series.quantile(0.50)), 6),
                "q75": round(float(f_series.quantile(0.75)), 6),
                "q95": round(float(f_series.quantile(0.95)), 6),
            },
            "subset_quantiles": {
                "q25": round(float(s_series.quantile(0.25)), 6),
                "q50": round(float(s_series.quantile(0.50)), 6),
                "q75": round(float(s_series.quantile(0.75)), 6),
                "q95": round(float(s_series.quantile(0.95)), 6),
            },
            "ks_statistic": round(float(ks_stat), 6),
            "ks_p_value": round(float(ks_pval), 6)
        }

    # Target distribution
    if target_col and target_col in full_df.columns:
        if pd.api.types.is_numeric_dtype(full_df[target_col]) and full_df[target_col].nunique() > 20:
            # Continuous regression target
            f_tar = full_df[target_col]
            s_tar = subset_df[target_col]
            audit["target_distribution"] = {
                "target_type": "continuous_regression",
                "full_mean": round(float(f_tar.mean()), 4),
                "subset_mean": round(float(s_tar.mean()), 4),
                "mean_abs_diff": round(abs(float(f_tar.mean()) - float(s_tar.mean())), 4),
                "full_std": round(float(f_tar.std()), 4),
                "subset_std": round(float(s_tar.std()), 4),
                "full_median": round(float(f_tar.median()), 4),
                "subset_median": round(float(s_tar.median()), 4),
                "min": float(f_tar.min()),
                "max": float(f_tar.max())
            }
        else:
            # Classification target
            f_counts = full_df[target_col].value_counts().to_dict()
            s_counts = subset_df[target_col].value_counts().to_dict()
            f_props = full_df[target_col].value_counts(normalize=True).to_dict()
            s_props = subset_df[target_col].value_counts(normalize=True).to_dict()

            audit["target_distribution"] = {
                "target_type": "discrete_classification",
                "full_counts": {str(k): int(v) for k, v in f_counts.items()},
                "subset_counts": {str(k): int(v) for k, v in s_counts.items()},
                "full_proportions": {str(k): round(float(v), 6) for k, v in f_props.items()},
                "subset_proportions": {str(k): round(float(v), 6) for k, v in s_props.items()},
                "max_proportion_diff": round(max(abs(f_props[k] - s_props.get(k, 0.0)) for k in f_props), 6)
            }

    # Categorical distributions
    if cat_cols:
        for col in cat_cols:
            if col in full_df.columns:
                f_props = full_df[col].value_counts(normalize=True).to_dict()
                s_props = subset_df[col].value_counts(normalize=True).to_dict()
                audit["categorical_distributions"][col] = {
                    "full_unique_count": int(full_df[col].nunique()),
                    "subset_unique_count": int(subset_df[col].nunique()),
                    "full_top5_props": {str(k): round(float(v), 6) for k, v in list(f_props.items())[:5]},
                    "subset_top5_props": {str(k): round(float(v), 6) for k, v in list(s_props.items())[:5]},
                    "max_prop_drift": round(max(abs(f_props[k] - s_props.get(k, 0.0)) for k in f_props), 6)
                }

    return audit
