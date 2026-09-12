"""
NirmaanAI Multi-Sensor Anomaly Detection Feature Engineering
Extracts causal temporal features, operating regime normalizations, and physical interaction terms.
Provides clean reference training, validation calibration, and controlled evaluation splits.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler

from src.utils.logger import logger

# Primary telemetry features recorded by factory digital twin and shop floor sensors
CORE_SENSOR_COLS = [
    "vibration_mms",
    "temperature_c",
    "rotational_speed_rpm",
    "torque_nm",
    "sound_db",
    "power_consumption_kw",
    "oil_level_pct",
    "coolant_level_pct"
]


def engineer_synthetic_anomaly_features(
    df: pd.DataFrame,
    rolling_window: int = 5
) -> pd.DataFrame:
    """
    Computes physically grounded multi-sensor features and causal rolling indicators.
    All rolling statistics use strictly backward-looking lagging windows grouped by machine_id.
    Zero future leakage: min_periods=1 and standard pandas rolling (which defaults to left-anchored historical window).
    """
    df_feat = df.copy()
    df_feat["timestamp"] = pd.to_datetime(df_feat["timestamp"])
    df_feat = df_feat.sort_values(by=["machine_id", "timestamp"]).reset_index(drop=True)

    # 1. Thermal differentials (delta T = process temp - ambient temp)
    if "ambient_temperature_c" in df_feat.columns:
        df_feat["temp_diff_c"] = df_feat["temperature_c"] - df_feat["ambient_temperature_c"]
    else:
        df_feat["temp_diff_c"] = 0.0

    # 2. Mechanical Power (kW) = (2 * pi * speed_rpm * torque_nm) / 60000
    df_feat["mechanical_power_kw"] = (
        2.0 * np.pi * df_feat["rotational_speed_rpm"] * df_feat["torque_nm"]
    ) / 60000.0

    # 3. Apparent Efficiency Ratio: mechanical output power / electrical input power
    # In normal operation, this ratio is steady; mechanical drag / bearing friction causes this ratio to shift
    df_feat["power_ratio"] = df_feat["mechanical_power_kw"] / np.maximum(df_feat["power_consumption_kw"], 0.1)

    # 4. Mechanical Load Stress: Torque / max(RPM, 1.0)
    df_feat["torque_speed_ratio"] = df_feat["torque_nm"] / np.maximum(df_feat["rotational_speed_rpm"], 1.0)

    # 5. Causal Rolling Statistics grouped by machine_id
    # Window of 5 intervals = 25 minutes of historical telemetry
    for col in ["vibration_mms", "temperature_c", "power_consumption_kw", "sound_db"]:
        grouped = df_feat.groupby("machine_id")[col]
        # Rolling mean (smoothed trajectory)
        df_feat[f"{col}_roll_mean_{rolling_window}"] = grouped.transform(
            lambda s: s.rolling(window=rolling_window, min_periods=1).mean()
        )
        # Rolling standard deviation (process volatility / chatter)
        df_feat[f"{col}_roll_std_{rolling_window}"] = grouped.transform(
            lambda s: s.rolling(window=rolling_window, min_periods=1).std().fillna(0.0)
        )
        # Causal first difference / rate of change: value(t) - value(t-1)
        df_feat[f"{col}_diff_1"] = grouped.transform(
            lambda s: s.diff(1).fillna(0.0)
        )

    return df_feat


def prepare_synthetic_anomaly_splits(
    df: pd.DataFrame,
    target_machine_id: str = "M2",
    rolling_window: int = 5
) -> Dict[str, Any]:
    """
    Partitions synthetic factory telemetry into:
    - Train (Reference Normal): Days 1 to 15 (nominal, stable baseline for target machine).
    - Validation (Tuning): Days 16 to 17 (nominal, unpolluted baseline for threshold calibration).
    - Test / Evaluation: Days 18 to 30 (contains active degradation episode on Days 18-21 and post-maint).
    
    Also generates configured synthetic ground truth anomaly labels:
    - y = 1 during the active degradation episode on target_machine_id (Days 18 06:00 to 22 05:55 UTC).
    - y = 0 during nominal operating windows.
    """
    df_feat = engineer_synthetic_anomaly_features(df, rolling_window=rolling_window)
    m_df = df_feat[df_feat["machine_id"] == target_machine_id].copy()

    # Time boundaries (UTC timestamps)
    t_train_end = pd.to_datetime("2026-01-16 06:00:00+00:00")
    t_val_end = pd.to_datetime("2026-01-18 06:00:00+00:00")
    t_degrad_start = pd.to_datetime("2026-01-18 06:00:00+00:00")
    t_degrad_end = pd.to_datetime("2026-01-22 06:00:00+00:00")

    train_mask = m_df["timestamp"] < t_train_end
    val_mask = (m_df["timestamp"] >= t_train_end) & (m_df["timestamp"] < t_val_end)
    test_mask = m_df["timestamp"] >= t_val_end

    train_df = m_df[train_mask].copy()
    val_df = m_df[val_mask].copy()
    test_df = m_df[test_mask].copy()

    # Define feature column list
    exclude_cols = ["reading_id", "machine_id", "timestamp", "tool_wear_min"]
    feature_cols = [c for c in m_df.columns if c not in exclude_cols]

    # Configured synthetic ground truth anomaly labels
    # y = 1 strictly during the generative bearing degradation episode (Days 18 to 21 inclusive)
    y_train = np.zeros(len(train_df), dtype=int)
    y_val = np.zeros(len(val_df), dtype=int)
    y_test = (
        (test_df["timestamp"] >= t_degrad_start) & (test_df["timestamp"] < t_degrad_end)
    ).astype(int).values

    logger.info(
        f"Synthetic Anomaly Splits for {target_machine_id}: "
        f"Train (Days 1-15)={len(train_df)} rows, "
        f"Val (Days 16-17)={len(val_df)} rows, "
        f"Test (Days 18-30)={len(test_df)} rows (Anomalies={y_test.sum()})"
    )

    return {
        "feature_cols": feature_cols,
        "train_df": train_df,
        "val_df": val_df,
        "test_df": test_df,
        "X_train": train_df[feature_cols].copy(),
        "X_val": val_df[feature_cols].copy(),
        "X_test": test_df[feature_cols].copy(),
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test
    }


def prepare_ai4i_anomaly_splits(
    df: pd.DataFrame,
    test_size: float = 0.30,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Prepares AI4I 2020 for semi-supervised anomaly detection benchmarking.
    CRITICAL RESEARCH INTEGRITY:
    - Failure instances are completely excluded from X_train.
    - X_train consists strictly of normal non-failure instances (Machine failure == 0).
    - Failure labels are used ONLY for post-hoc unsupervised evaluation.
    """
    df_clean = df.copy()
    rename_dict = {
        "Air temperature [K]": "air_temperature_k",
        "Process temperature [K]": "process_temperature_k",
        "Rotational speed [rpm]": "rotational_speed_rpm",
        "Torque [Nm]": "torque_nm",
        "Tool wear [min]": "tool_wear_min"
    }
    df_clean = df_clean.rename(columns={k: v for k, v in rename_dict.items() if k in df_clean.columns})

    # Physical interaction features
    df_clean["temp_diff_k"] = df_clean["process_temperature_k"] - df_clean["air_temperature_k"]
    df_clean["mechanical_power_kw"] = (
        2.0 * np.pi * df_clean["rotational_speed_rpm"] * df_clean["torque_nm"]
    ) / 60000.0
    df_clean["torque_speed_ratio"] = df_clean["torque_nm"] / np.maximum(df_clean["rotational_speed_rpm"], 1.0)

    feature_cols = [
        "air_temperature_k",
        "process_temperature_k",
        "rotational_speed_rpm",
        "torque_nm",
        "tool_wear_min",
        "temp_diff_k",
        "mechanical_power_kw",
        "torque_speed_ratio"
    ]

    # Semi-supervised split: Train exclusively on normal instances (y == 0)
    normal_df = df_clean[df_clean["Machine failure"] == 0].copy()
    failure_df = df_clean[df_clean["Machine failure"] == 1].copy()

    # Split normal instances into train and test
    from sklearn.model_selection import train_test_split
    normal_train, normal_test = train_test_split(
        normal_df, test_size=test_size, random_state=random_state
    )

    # Test set combines holdout normal instances and ALL failure instances
    test_combined = pd.concat([normal_test, failure_df]).sample(frac=1.0, random_state=random_state)

    X_train = normal_train[feature_cols].copy()
    X_test = test_combined[feature_cols].copy()
    y_test = test_combined["Machine failure"].values

    return {
        "feature_cols": feature_cols,
        "X_train": X_train,
        "X_test": X_test,
        "y_test": y_test
    }
