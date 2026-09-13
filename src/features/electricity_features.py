"""
NirmaanAI Feature Engineering Module: UCI Electricity Load Diagrams (2011–2014)
Dataset: UCI Electricity Load Diagrams (Client MT_124, 1-hour resampled series)
Primary Task: Industrial Plant Grid Electricity Demand Forecasting (kW)

Enforces strict research integrity:
- Strictly causal zero-lookahead lag structure (all lags t-1, t-2, t-24, t-168 relative to forecast origin).
- Causal rolling statistics (24-hour moving window) evaluated strictly on historical observations.
- Calendar and diurnal cyclical features (hour, day of week, weekend, evening peak indicator).
- Explicit target demarcation: power_kw at time t is the regression target.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config_loader import get_project_root
from src.utils.logger import logger

ELECTRICITY_CLIENT_TARGET = "MT_124"
ELECTRICITY_TARGET_COL = "power_kw"


def extract_electricity_features(
    data_path: Path = None,
    client_id: str = ELECTRICITY_CLIENT_TARGET,
    resample_freq: str = "1h",
    start_date: str = "2012-01-01",
    end_date: str = "2014-12-31",
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Extracts time-series lag, calendar, and volatility features for electricity forecasting.
    """
    root = get_project_root()
    path = data_path or (root / "DATASET" / "04_ENERGY" / "raw" / "LD2011_2014.txt")
    if not path.exists():
        path = root / "data" / "uci_electricity" / "LD2011_2014.txt"

    if not path.exists():
        raise FileNotFoundError(f"UCI Electricity dataset not found at {path}")

    logger.info(f"Extracting features for UCI Electricity ({client_id}) from {path}")

    # Read only timestamp and target client column for memory efficiency
    df_raw = pd.read_csv(
        path,
        sep=";",
        usecols=["Unnamed: 0", client_id],
        decimal=",",
    )
    df_raw.rename(columns={"Unnamed: 0": "timestamp", client_id: ELECTRICITY_TARGET_COL}, inplace=True)
    df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])
    df_raw = df_raw.sort_values("timestamp").reset_index(drop=True)

    # Filter date range
    if start_date:
        df_raw = df_raw[df_raw["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        df_raw = df_raw[df_raw["timestamp"] <= pd.to_datetime(end_date)]

    # Resample to 1-hour frequency
    if resample_freq != "15min":
        df = df_raw.set_index("timestamp").resample(resample_freq).mean().reset_index()
    else:
        df = df_raw.copy()

    df = df.dropna().reset_index(drop=True)

    # 1. Calendar & Diurnal Features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["month"] = df["timestamp"].dt.month
    df["is_peak_hours"] = df["hour"].isin([18, 19, 20, 21, 22]).astype(int)

    # Cyclical hour encoding
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)

    # 2. Strictly Causal Lag Features (relative to target time t)
    # At prediction time for hour t, the most recent available reading is t-1
    df["lag_1h"] = df[ELECTRICITY_TARGET_COL].shift(1)
    df["lag_2h"] = df[ELECTRICITY_TARGET_COL].shift(2)
    df["lag_3h"] = df[ELECTRICITY_TARGET_COL].shift(3)
    df["lag_4h"] = df[ELECTRICITY_TARGET_COL].shift(4)
    df["lag_24h"] = df[ELECTRICITY_TARGET_COL].shift(24)
    df["lag_168h"] = df[ELECTRICITY_TARGET_COL].shift(168)

    # 3. Causal Rolling Window Statistics (computed strictly on lag_1h to prevent lookahead)
    lag1_series = df["lag_1h"]
    df["rolling_mean_24h"] = lag1_series.rolling(window=24, min_periods=1).mean()
    df["rolling_std_24h"] = lag1_series.rolling(window=24, min_periods=1).std().fillna(0.0)
    df["rolling_min_24h"] = lag1_series.rolling(window=24, min_periods=1).min()
    df["rolling_max_24h"] = lag1_series.rolling(window=24, min_periods=1).max()

    # 4. Causal Differences & Momentum
    df["load_diff_1h"] = df["lag_1h"] - df["lag_2h"]
    df["load_diff_24h"] = df["lag_1h"] - df["lag_24h"]

    # Drop warm-up NaN rows caused by 168-hour (1 week) lookback
    df_clean = df.dropna().reset_index(drop=True)

    # Build Feature Dictionary
    records = []

    # Timestamp
    records.append({
        "feature_name": "timestamp",
        "original_columns": "Unnamed: 0",
        "feature_type": "TIMESTAMP",
        "data_type": "datetime64[ns]",
        "unit": "ISO-8601 Datetime",
        "formula": "Original timestamp resampled to 1h",
        "description": "Chronological hourly timestamp of electrical metering",
        "dataset": "UCI_Electricity_Load",
        "task": "Energy_Demand_Forecasting",
        "temporal_behavior": "CHRONOLOGICAL_INDEX",
        "lookback": "None",
        "available_at_prediction_time": "YES",
        "leakage_status": "SAFE",
        "missing_rate": 0.0,
        "variance": 0.0,
        "unique_count": int(df_clean["timestamp"].nunique()),
        "status": "KEEP_METADATA",
        "removal_reason": "Time-series index",
    })

    # Target
    records.append({
        "feature_name": ELECTRICITY_TARGET_COL,
        "original_columns": client_id,
        "feature_type": "TARGET",
        "data_type": "float64",
        "unit": "kW",
        "formula": "Hourly average power consumption",
        "description": f"Active electrical power draw for client {client_id} at hour t",
        "dataset": "UCI_Electricity_Load",
        "task": "Energy_Demand_Forecasting",
        "temporal_behavior": "FUTURE_TARGET",
        "lookback": "Hour t",
        "available_at_prediction_time": "NO",
        "leakage_status": "TARGET",
        "missing_rate": 0.0,
        "variance": float(df_clean[ELECTRICITY_TARGET_COL].var()),
        "unique_count": int(df_clean[ELECTRICITY_TARGET_COL].nunique()),
        "status": "TARGET",
        "removal_reason": "Forecasting target variable",
    })

    # Engineered Features Info
    eng_metadata = [
        ("hour", "timestamp", "CALENDAR", "Integer (0-23)", "Hour of the day", "timestamp.dt.hour"),
        ("day_of_week", "timestamp", "CALENDAR", "Integer (0-6)", "Day of the week (0=Mon, 6=Sun)", "timestamp.dt.dayofweek"),
        ("is_weekend", "timestamp", "CALENDAR", "Binary (0/1)", "Weekend indicator flag", "day_of_week in [5, 6]"),
        ("month", "timestamp", "CALENDAR", "Integer (1-12)", "Calendar month", "timestamp.dt.month"),
        ("is_peak_hours", "timestamp", "CALENDAR", "Binary (0/1)", "Industrial evening peak tariff period (18:00-22:00)", "hour in [18, 19, 20, 21, 22]"),
        ("hour_sin", "timestamp", "CYCLICAL", "Sine value", "Sine transform of 24h diurnal cycle", "sin(2*pi*hour/24)"),
        ("hour_cos", "timestamp", "CYCLICAL", "Cosine value", "Cosine transform of 24h diurnal cycle", "cos(2*pi*hour/24)"),
        ("lag_1h", client_id, "CAUSAL_LAG", "kW", "Electricity demand 1 hour prior (t-1)", "power_kw(t-1)"),
        ("lag_2h", client_id, "CAUSAL_LAG", "kW", "Electricity demand 2 hours prior (t-2)", "power_kw(t-2)"),
        ("lag_3h", client_id, "CAUSAL_LAG", "kW", "Electricity demand 3 hours prior (t-3)", "power_kw(t-3)"),
        ("lag_4h", client_id, "CAUSAL_LAG", "kW", "Electricity demand 4 hours prior (t-4)", "power_kw(t-4)"),
        ("lag_24h", client_id, "CAUSAL_LAG", "kW", "Electricity demand 24 hours prior (same hour yesterday)", "power_kw(t-24)"),
        ("lag_168h", client_id, "CAUSAL_LAG", "kW", "Electricity demand 168 hours prior (same hour last week)", "power_kw(t-168)"),
        ("rolling_mean_24h", client_id, "CAUSAL_ROLLING", "kW", "24-hour historical rolling mean demand", "rolling_mean(lag_1h, window=24)"),
        ("rolling_std_24h", client_id, "CAUSAL_ROLLING", "kW", "24-hour historical demand standard deviation", "rolling_std(lag_1h, window=24)"),
        ("rolling_min_24h", client_id, "CAUSAL_ROLLING", "kW", "24-hour historical minimum demand", "rolling_min(lag_1h, window=24)"),
        ("rolling_max_24h", client_id, "CAUSAL_ROLLING", "kW", "24-hour historical maximum demand", "rolling_max(lag_1h, window=24)"),
        ("load_diff_1h", client_id, "CAUSAL_MOMENTUM", "kW", "Load change over previous hour (lag_1h - lag_2h)", "lag_1h - lag_2h"),
        ("load_diff_24h", client_id, "CAUSAL_MOMENTUM", "kW", "Load change relative to 24 hours prior (lag_1h - lag_24h)", "lag_1h - lag_24h"),
    ]

    for col, orig, ftype, unit, desc, formula in eng_metadata:
        records.append({
            "feature_name": col,
            "original_columns": orig,
            "feature_type": ftype,
            "data_type": str(df_clean[col].dtype),
            "unit": unit,
            "formula": formula,
            "description": desc,
            "dataset": "UCI_Electricity_Load",
            "task": "Energy_Demand_Forecasting",
            "temporal_behavior": "CAUSAL_TIME_SERIES",
            "lookback": "1h to 168h strictly past",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df_clean[col].isna().mean()),
            "variance": float(df_clean[col].var()),
            "unique_count": int(df_clean[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (strictly causal time-series feature)",
        })

    feature_dict = pd.DataFrame(records)

    metadata = {
        "dataset_name": "UCI_Electricity_Load",
        "client_id": client_id,
        "resample_frequency": resample_freq,
        "total_hourly_records": len(df_clean),
        "total_columns": len(df_clean.columns),
        "max_lag_lookback_hours": 168,
        "mean_power_kw": float(df_clean[ELECTRICITY_TARGET_COL].mean()),
        "std_power_kw": float(df_clean[ELECTRICITY_TARGET_COL].std()),
        "status": "EXTRACTED_AND_AUDITED",
    }

    return df_clean, feature_dict, metadata
