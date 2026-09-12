"""
NirmaanAI Bottleneck Prediction Feature Engineering & Dataset Preparation
Implements strictly causal zero-lookahead production flow features, machine capacity stress,
and multi-sensor health coupling available AT OR PRIOR to scheduled job dispatch.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.utils.logger import logger


def engineer_bottleneck_features(
    jobs_df: pd.DataFrame,
    machines_df: pd.DataFrame,
    sensor_df: Optional[pd.DataFrame] = None,
    lookback_jobs: int = 3
) -> pd.DataFrame:
    """
    Computes zero-lookahead predictive features for upcoming production jobs.
    CRITICAL RESEARCH INTEGRITY & ZERO LOOKAHEAD:
    - Target: bottleneck_event (1 if job experiences cycle expansion >= 1.20 or dispatch delay >= 10 min; 0 otherwise).
    - Features represent state of the factory and machine PRIOR to job execution.
    - Excludes Actual_End, future duration, future scrap, or post-completion outcomes.
    - For each job scheduled at t_sch, rolling machine history uses only strictly completed prior jobs.
    """
    df = jobs_df.copy()
    m_info = machines_df.copy()

    # Merge design parameters
    if "design_cycle_time_sec" not in df.columns:
        df = df.merge(m_info[["machine_id", "design_cycle_time_sec", "rated_capacity_units_per_hour", "baseline_vibration_mms"]], on="machine_id", how="left")

    df["scheduled_start_dt"] = pd.to_datetime(df["scheduled_start"], utc=True)
    df["scheduled_end_dt"] = pd.to_datetime(df["scheduled_end"], utc=True)
    df["actual_start_dt"] = pd.to_datetime(df["actual_start"], utc=True)
    df["actual_end_dt"] = pd.to_datetime(df["actual_end"], utc=True)

    # Target calculation (for training / evaluation ground truth)
    df["start_delay_min"] = (df["actual_start_dt"] - df["scheduled_start_dt"]).dt.total_seconds() / 60.0
    df["cycle_ratio"] = df["actual_cycle_time_sec"] / df["design_cycle_time_sec"]
    df["bottleneck_event"] = (
        (df["cycle_ratio"] >= 1.20) | (df["start_delay_min"] >= 10.0) | (df["status"] == "DELAYED")
    ).astype(int)

    # Sort strictly chronologically by scheduled start
    df = df.sort_values(by=["scheduled_start_dt", "machine_id"]).reset_index(drop=True)

    # 1. Scheduled Workload & Capacity Features (known at scheduling time)
    # Nominal planned job duration in minutes
    df["planned_duration_min"] = (df["batch_quantity"] * df["design_cycle_time_sec"]) / 60.0
    # Capacity utilization ratio: batch size relative to rated hourly capacity
    df["batch_load_ratio"] = df["batch_quantity"] / np.maximum(df["rated_capacity_units_per_hour"], 1.0)
    # Shift identification (Shift 1 = morning 06:00, Shift 2 = afternoon 14:00)
    df["hour_of_day"] = df["scheduled_start_dt"].dt.hour
    df["is_afternoon_shift"] = (df["hour_of_day"] >= 14).astype(int)

    # 2. Machine Historical Flow Dynamics (Causal lagging indicators)
    # Track historical cycle ratio and start delays of prior completed jobs on the same machine
    lag_cycle_means = []
    lag_delay_means = []

    for i in range(len(df)):
        cur_row = df.iloc[i]
        m_id = cur_row["machine_id"]
        t_sch = cur_row["scheduled_start_dt"]

        # Find prior jobs on same machine that finished before t_sch
        prior_jobs = df.iloc[:i]
        prior_m = prior_jobs[
            (prior_jobs["machine_id"] == m_id) & 
            (prior_jobs["actual_end_dt"] < t_sch)
        ]

        if len(prior_m) > 0:
            recent = prior_m.tail(lookback_jobs)
            lag_cycle_means.append(float(recent["cycle_ratio"].mean()))
            lag_delay_means.append(float(recent["start_delay_min"].mean()))
        else:
            lag_cycle_means.append(1.0)  # Nominal default
            lag_delay_means.append(0.0)

    df["prior_cycle_ratio_mean"] = lag_cycle_means
    df["prior_start_delay_mean"] = lag_delay_means

    # 3. Telemetry Physical Coupling (1-Hour Pre-Job Sensor Telemetry)
    # If sensor telemetry is provided, calculate pre-dispatch 1-hour sensor baseline
    if sensor_df is not None and len(sensor_df) > 0:
        s_df = sensor_df.copy()
        s_df["timestamp_dt"] = pd.to_datetime(s_df["timestamp"], utc=True)
        s_df = s_df.sort_values(by="timestamp_dt").reset_index(drop=True)

        pre_vib_list = []
        pre_temp_list = []
        pre_vib_dev_list = []

        for i in range(len(df)):
            cur_row = df.iloc[i]
            m_id = cur_row["machine_id"]
            t_sch = cur_row["scheduled_start_dt"]

            # Causal 1-hour window prior to scheduled dispatch: (t_sch - 1h, t_sch]
            w = s_df[
                (s_df["machine_id"] == m_id) & 
                (s_df["timestamp_dt"] <= t_sch) & 
                (s_df["timestamp_dt"] > t_sch - pd.Timedelta(hours=1))
            ]

            if len(w) > 0:
                mean_vib = float(w["vibration_mms"].mean())
                mean_temp = float(w["temperature_c"].mean())
            else:
                mean_vib = float(cur_row["baseline_vibration_mms"])
                mean_temp = 38.0

            vib_dev = mean_vib - float(cur_row["baseline_vibration_mms"])
            pre_vib_list.append(mean_vib)
            pre_temp_list.append(mean_temp)
            pre_vib_dev_list.append(vib_dev)

        df["pre_job_vibration_1h"] = pre_vib_list
        df["pre_job_temperature_1h"] = pre_temp_list
        df["pre_job_vibration_dev_1h"] = pre_vib_dev_list
    else:
        # Fallback if raw sensor dataframe is not joined
        df["pre_job_vibration_1h"] = df["baseline_vibration_mms"]
        df["pre_job_temperature_1h"] = 38.0
        df["pre_job_vibration_dev_1h"] = 0.0

    # 4. Machine Identity One-Hot Encoding
    for m in ["M1", "M2", "M3", "M4", "M5"]:
        df[f"is_machine_{m}"] = (df["machine_id"] == m).astype(int)

    return df


def prepare_bottleneck_splits(
    jobs_df: pd.DataFrame,
    machines_df: pd.DataFrame,
    sensor_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Chronological splitting strictly preserving factory temporal order:
    - Train (Days 1 to 15): Jobs 1 to 150 (Nominal baseline, 0 bottlenecks).
    - Validation (Days 16 to 17): Jobs 151 to 170 (Nominal baseline tuning, 0 bottlenecks).
    - Test (Days 18 to 30): Jobs 171 to 300 (Contains 8 M2 bottleneck episodes and post-maint recovery).
    """
    df_feat = engineer_bottleneck_features(jobs_df, machines_df, sensor_df)

    t_train_end = pd.to_datetime("2026-01-16 00:00:00+00:00")
    t_val_end = pd.to_datetime("2026-01-18 00:00:00+00:00")

    train_mask = df_feat["scheduled_start_dt"] < t_train_end
    val_mask = (df_feat["scheduled_start_dt"] >= t_train_end) & (df_feat["scheduled_start_dt"] < t_val_end)
    test_mask = df_feat["scheduled_start_dt"] >= t_val_end

    train_df = df_feat[train_mask].copy()
    val_df = df_feat[val_mask].copy()
    test_df = df_feat[test_mask].copy()

    feature_cols = [
        "batch_quantity",
        "planned_duration_min",
        "batch_load_ratio",
        "hour_of_day",
        "is_afternoon_shift",
        "prior_cycle_ratio_mean",
        "prior_start_delay_mean",
        "pre_job_vibration_1h",
        "pre_job_temperature_1h",
        "pre_job_vibration_dev_1h",
        "is_machine_M1",
        "is_machine_M2",
        "is_machine_M3",
        "is_machine_M4",
        "is_machine_M5"
    ]

    target_col = "bottleneck_event"

    logger.info(
        f"Bottleneck Splits: Train={len(train_df)} (Positives={train_df[target_col].sum()}), "
        f"Val={len(val_df)} (Positives={val_df[target_col].sum()}), "
        f"Test={len(test_df)} (Positives={test_df[target_col].sum()})"
    )

    return {
        "feature_cols": feature_cols,
        "target_col": target_col,
        "train_df": train_df,
        "val_df": val_df,
        "test_df": test_df,
        "X_train": train_df[feature_cols].copy(),
        "y_train": train_df[target_col].values,
        "X_val": val_df[feature_cols].copy(),
        "y_val": val_df[target_col].values,
        "X_test": test_df[feature_cols].copy(),
        "y_test": test_df[target_col].values
    }


def prepare_hybrid_manufacturing_benchmark(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Prepares secondary benchmark dataset 06_MANUFACTURING_PRODUCTION.
    Target: Job_Status != 'Completed' (Delayed or Failed).
    Predictive features: Processing_Time, Material_Used, Energy_Consumption, Machine_Availability, Machine_ID.
    """
    df_clean = df.copy()
    df_clean["is_bottleneck_or_fail"] = (df_clean["Job_Status"] != "Completed").astype(int)

    # Machine one-hot
    m_dummies = pd.get_dummies(df_clean["Machine_ID"], prefix="m", drop_first=True, dtype=int)
    feature_df = pd.concat([
        df_clean[["Processing_Time", "Material_Used", "Energy_Consumption", "Machine_Availability"]],
        m_dummies
    ], axis=1)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        feature_df, df_clean["is_bottleneck_or_fail"].values,
        test_size=test_size, random_state=random_state,
        stratify=df_clean["is_bottleneck_or_fail"].values
    )

    return {
        "feature_cols": list(feature_df.columns),
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }
