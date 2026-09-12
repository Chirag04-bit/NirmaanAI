"""
NirmaanAI Forecasting Feature Engineering & Temporal Splitting Module
Phase 9: Production & Energy Forecasting

Strict research-integrity rules enforced:
1. Strict chronological train / validation / test partitioning (no random shuffle or lookahead).
2. Explicit target definitions and temporal resolution documentation.
3. Causal zero-lookahead lag features and rolling statistics.
4. Scale-independent metrics (WAPE, sMAPE) alongside MAE, RMSE, and R2.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from src.utils.logger import logger


def calculate_forecasting_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes regression performance metrics for time-series forecasting.
    Includes MAE, RMSE, R2, and scale-independent metrics WAPE and sMAPE.
    Avoids numerical instability when actual values approach zero.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = float(np.mean(np.abs(y_true - y_pred)))
    mse = float(np.mean((y_true - y_pred) ** 2))
    rmse = float(np.sqrt(mse))

    # R-squared
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-9 else 0.0

    # WAPE (Weighted Absolute Percentage Error) = sum(|y - y_hat|) / sum(y)
    sum_true = float(np.sum(np.abs(y_true)))
    wape = float(np.sum(np.abs(y_true - y_pred)) / sum_true) if sum_true > 1e-9 else 0.0

    # sMAPE (Symmetric Mean Absolute Percentage Error) = (100% / N) * sum(2 * |y - y_hat| / (|y| + |y_hat|))
    denominator = np.abs(y_true) + np.abs(y_pred)
    # Mask where both are zero
    valid_mask = denominator > 1e-9
    if np.sum(valid_mask) > 0:
        smape = float(np.mean(200.0 * np.abs(y_true[valid_mask] - y_pred[valid_mask]) / denominator[valid_mask]))
    else:
        smape = 0.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
        "wape": round(wape, 4),
        "smape": round(smape, 4)
    }


def prepare_uci_electricity_data(
    file_path: Union[str, Path],
    client_id: str = "MT_124",
    resample_freq: str = "1h",
    start_date: Optional[str] = "2012-01-01",
    end_date: Optional[str] = "2014-12-31"
) -> pd.DataFrame:
    """
    Loads and resamples the UCI Electricity Load Diagrams (LD2011_2014.txt).
    NATIVE FREQUENCY: 15-minute intervals.
    TARGET RESOLUTION: 1-hour average active power draw (kW) or native 15-minute.
    DEMARCATION: This is an empirical grid electricity benchmark. It is NEVER represented
    as factory equipment.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"UCI Electricity dataset not found at: {path}")

    logger.info(f"Loading UCI Electricity dataset for client {client_id} from {path}")
    # Read only timestamp and target client column for memory and speed efficiency
    df = pd.read_csv(
        path,
        sep=";",
        usecols=["Unnamed: 0", client_id],
        decimal=","
    )
    df.rename(columns={"Unnamed: 0": "timestamp", client_id: "power_kw"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Filter date range if specified (e.g. 2012-2014 where MT_124 is fully active)
    if start_date:
        df = df[df["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["timestamp"] <= pd.to_datetime(end_date)]

    # Resample if requested
    if resample_freq != "15min":
        df = df.set_index("timestamp").resample(resample_freq).mean().reset_index()

    # Drop any trailing NaNs from resampling
    df = df.dropna().reset_index(drop=True)
    logger.info(f"UCI Electricity ({client_id}) prepared: {len(df)} records at {resample_freq} resolution")
    return df


def build_energy_features(
    df: pd.DataFrame,
    target_col: str = "power_kw",
    freq: str = "1h"
) -> pd.DataFrame:
    """
    Constructs strictly causal time-series features for energy demand forecasting.
    
    TEMPORAL FREQUENCY MAPPING:
    For 1-hour resolution (freq='1h'):
    - lag_1h: 1 hour prior (t-1)
    - lag_2h: 2 hours prior (t-2)
    - lag_3h: 3 hours prior (t-3)
    - lag_24h: 24 hours prior (t-24, same hour yesterday)
    - lag_168h: 168 hours prior (t-168, same hour last week)
    - rolling_mean_24h: rolling 24-hour mean strictly excluding current timestamp (shift(1))
    - rolling_std_24h: rolling 24-hour standard deviation strictly excluding current timestamp
    - cyclical features: sin_hour, cos_hour (24h period), sin_dow, cos_dow (7d period)
    """
    data = df.copy().sort_values("timestamp").reset_index(drop=True)

    # 1. Calendar & Cyclical Encodings
    hour = data["timestamp"].dt.hour
    dow = data["timestamp"].dt.dayofweek
    month = data["timestamp"].dt.month

    data["hour"] = hour
    data["day_of_week"] = dow
    data["is_weekend"] = (dow >= 5).astype(int)

    # Cyclical sin/cos
    data["sin_hour"] = np.sin(2.0 * np.pi * hour / 24.0)
    data["cos_hour"] = np.cos(2.0 * np.pi * hour / 24.0)
    data["sin_dow"] = np.sin(2.0 * np.pi * dow / 7.0)
    data["cos_dow"] = np.cos(2.0 * np.pi * dow / 7.0)

    # 2. Autoregressive Lags (Strictly Causal: shift >= 1)
    # Lags mapped to semantic hours:
    data["lag_1h"] = data[target_col].shift(1)
    data["lag_2h"] = data[target_col].shift(2)
    data["lag_3h"] = data[target_col].shift(3)
    data["lag_24h"] = data[target_col].shift(24)
    data["lag_168h"] = data[target_col].shift(168)

    # 3. Rolling Causal Statistics (shift(1) ensures current row is excluded)
    data["rolling_mean_6h"] = data[target_col].shift(1).rolling(window=6, min_periods=1).mean()
    data["rolling_mean_24h"] = data[target_col].shift(1).rolling(window=24, min_periods=1).mean()
    data["rolling_std_24h"] = data[target_col].shift(1).rolling(window=24, min_periods=1).std().fillna(0.0)

    # 4. Target variable
    target_vals = data[target_col].values
    data = data.drop(columns=[target_col])
    data["target"] = target_vals

    # Drop warm-up rows containing NaNs from long lags (168h = 7 days)
    data = data.dropna().reset_index(drop=True)
    return data


def prepare_synthetic_factory_energy_data(
    sensor_parquet_path: Union[str, Path],
    resample_freq: str = "1h"
) -> pd.DataFrame:
    """
    Loads synthetic factory sensor readings (5-minute telemetry) and aggregates
    total active plant power (sum of power_consumption_kw across M1 to M5).
    DEMARCATION: This is a controlled manufacturing simulation environment.
    """
    path = Path(sensor_parquet_path)
    if not path.exists():
        raise FileNotFoundError(f"Synthetic sensor parquet not found at: {path}")

    logger.info(f"Loading synthetic sensor telemetry from {path}")
    df = pd.read_parquet(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Pivot machine power: sum across all machines at each 5-min timestamp
    plant_power = df.groupby("timestamp")["power_consumption_kw"].sum().reset_index()
    plant_power.rename(columns={"power_consumption_kw": "plant_power_kw"}, inplace=True)

    # Resample to hourly resolution (mean active kW over the hour)
    hourly_df = plant_power.set_index("timestamp").resample(resample_freq).mean().reset_index()
    hourly_df = hourly_df.dropna().reset_index(drop=True)

    logger.info(f"Synthetic plant power aggregated: {len(hourly_df)} records at {resample_freq} resolution")
    return hourly_df


def prepare_synthetic_production_throughput_data(
    jobs_csv_path: Union[str, Path]
) -> pd.DataFrame:
    """
    Prepares daily/shift production throughput dataset from production_jobs.csv.
    STRICT CAUSALITY GUARDRAIL:
    - Target: completed_units on target day (sum of completed_quantity).
    - Causal predictors: planned_units (sum of scheduled batch_quantity), scheduled job count,
      and strictly lagged prior completion ratios from historical days.
    - Future scrap, future actual end, and future downtime CANNOT leak into predictors.
    """
    path = Path(jobs_csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Production jobs CSV not found at: {path}")

    logger.info(f"Loading production jobs from {path}")
    df = pd.read_csv(path)
    df["scheduled_start_dt"] = pd.to_datetime(df["scheduled_start"], utc=True)
    df["date"] = df["scheduled_start_dt"].dt.date

    # Daily aggregation
    daily = df.groupby("date").agg(
        total_planned_jobs=("job_id", "count"),
        total_planned_units=("batch_quantity", "sum"),
        total_completed_units=("completed_quantity", "sum")
    ).reset_index()

    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    # Causal lagging indicators
    daily["lag_completed_1d"] = daily["total_completed_units"].shift(1)
    daily["lag_completed_7d"] = daily["total_completed_units"].shift(7)
    daily["prior_completion_rate_3d"] = (
        (daily["total_completed_units"].shift(1) / daily["total_planned_units"].shift(1))
        .rolling(window=3, min_periods=1)
        .mean()
    )

    # Calendar features
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)

    # Target: drop total_completed_units from feature frame to prevent contemporaneous target leakage
    target_completed = daily["total_completed_units"].values
    daily = daily.drop(columns=["total_completed_units"])
    daily["target_completed_units"] = target_completed

    # Drop NaNs from 7-day lag
    daily = daily.dropna().reset_index(drop=True)
    logger.info(f"Synthetic production throughput prepared: {len(daily)} daily records")
    return daily


def split_chronologically(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    feature_cols: Optional[List[str]] = None,
    target_col: str = "target"
) -> Dict[str, Any]:
    """
    Splits time-series data chronologically into Train, Validation, and Test sets.
    STRICT RESEARCH INTEGRITY:
    - Preserves temporal order (Train < Validation < Test).
    - No random shuffling.
    - Test split is reserved strictly for untouched final evaluation.
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    if feature_cols is None:
        exclude = [
            "timestamp", "date", "target", target_col,
            "power_kw", "plant_power_kw", "total_completed_units", "target_completed_units"
        ]
        feature_cols = [c for c in df.columns if c not in exclude]

    X_train = train_df[feature_cols].values
    y_train = train_df[target_col].values

    X_val = val_df[feature_cols].values
    y_val = val_df[target_col].values

    X_test = test_df[feature_cols].values
    y_test = test_df[target_col].values

    logger.info(
        f"Chronological Split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}"
    )

    return {
        "train_df": train_df,
        "val_df": val_df,
        "test_df": test_df,
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
        "feature_names": feature_cols
    }
