"""
NirmaanAI Data Profiling & Statistical Diagnostics Engine
Provides reusable, reproducible exploratory analysis utilities for tabular and time-series factory data.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from src.utils.logger import logger

def profile_dataframe(df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes comprehensive summary statistics, missingness rates, and target balance.
    
    Args:
        df: Input pandas DataFrame.
        target_col: Optional target variable name.
        
    Returns:
        Structured dictionary containing statistical diagnostics.
    """
    n_rows, n_cols = df.shape
    memory_usage_mb = float(df.memory_usage(deep=True).sum() / (1024 * 1024))
    
    # Missingness analysis
    null_counts = df.isnull().sum()
    null_pct = (null_counts / n_rows) * 100.0
    missing_summary = {
        col: {
            "null_count": int(null_counts[col]),
            "null_pct": round(float(null_pct[col]), 4)
        }
        for col in df.columns if null_counts[col] > 0
    }
    
    # Numeric feature statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_summary = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 0:
            numeric_summary[col] = {
                "mean": round(float(series.mean()), 4),
                "std": round(float(series.std()), 4),
                "min": round(float(series.min()), 4),
                "p25": round(float(series.quantile(0.25)), 4),
                "median": round(float(series.median()), 4),
                "p75": round(float(series.quantile(0.75)), 4),
                "max": round(float(series.max()), 4),
                "skewness": round(float(series.skew()), 4) if len(series) > 2 else 0.0
            }

    # Categorical feature summary
    categorical_cols = df.select_dtypes(include=["object", "category", "bool", "string", "str"]).columns.tolist()
    categorical_summary = {}
    for col in categorical_cols:
        series = df[col].dropna()
        val_counts = series.value_counts().head(10).to_dict()
        categorical_summary[col] = {
            "num_unique": int(series.nunique()),
            "top_categories": {str(k): int(v) for k, v in val_counts.items()}
        }

    # Target distribution
    target_summary = {}
    if target_col and target_col in df.columns:
        counts = df[target_col].value_counts(dropna=False).to_dict()
        total_valid = df[target_col].count()
        dist = {str(k): int(v) for k, v in counts.items()}
        
        # Calculate imbalance ratio if binary/categorical
        imbalance_ratio = None
        if len(counts) > 1 and total_valid > 0:
            values = sorted(counts.values(), reverse=True)
            imbalance_ratio = round(float(values[0] / values[-1]), 2)

        target_summary = {
            "target_column": target_col,
            "distribution": dist,
            "imbalance_ratio": imbalance_ratio
        }

    return {
        "rows": n_rows,
        "cols": n_cols,
        "memory_mb": round(memory_usage_mb, 2),
        "total_missing_cells": int(null_counts.sum()),
        "columns_with_missing": len(missing_summary),
        "missing_summary": missing_summary,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "target_summary": target_summary
    }

def compute_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Computes correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    return numeric_df.corr(method=method)

def detect_potential_leakage(
    df: pd.DataFrame,
    target_col: str,
    correlation_threshold: float = 0.95
) -> List[Dict[str, Any]]:
    """
    Flags features that exhibit suspiciously high linear or rank correlation with the target.
    """
    if target_col not in df.columns:
        return []
    
    flagged = []
    numeric_df = df.select_dtypes(include=[np.number])
    if target_col in numeric_df.columns:
        corr_series = numeric_df.corr()[target_col].abs()
        for col, corr in corr_series.items():
            if col != target_col and corr >= correlation_threshold:
                flagged.append({
                    "column": col,
                    "correlation": round(float(corr), 4),
                    "reason": f"High absolute correlation ({corr:.2f}) with target."
                })

    return flagged
