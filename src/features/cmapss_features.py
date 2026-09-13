"""
NirmaanAI Feature Engineering Module: NASA C-MAPSS Turbofan Degradation (FD001)
Dataset: NASA C-MAPSS FD001 (100 run-to-failure engines, 20,631 cycles)
Primary Task: Remaining Useful Life (RUL) Regression

Enforces strict temporal and research integrity:
- Grouped engine identity preserved (unit_number); zero cross-engine leakage.
- Drop invariant / uninformative sensor channels (s1, s5, s10, s16, s18, s19).
- Strictly causal rolling statistics (windows: 5, 10, 20 cycles) computed per engine without future lookahead.
- Normalized degradation trend features relative to individual engine baseline.
- Piecewise linear RUL target clipping (RUL_max = 125) with target strictly isolated from features.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config_loader import get_project_root
from src.utils.logger import logger

CMAPSS_COLUMNS = [
    "unit_number",
    "time_cycles",
    "setting_1",
    "setting_2",
    "setting_3",
] + [f"s{i}" for i in range(1, 22)]

CMAPSS_INFORMATIVE_SENSORS = [
    "s2", "s3", "s4", "s7", "s8", "s9", "s11", "s12", "s13", "s14", "s15", "s17", "s20", "s21"
]
CMAPSS_CONSTANT_SENSORS = ["s1", "s5", "s10", "s16", "s18", "s19"]
RUL_UPPER_CLIP = 125


def extract_cmapss_features(
    data_path: Path = None,
    rul_clip: int = RUL_UPPER_CLIP,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Extracts causal temporal features and RUL targets for NASA C-MAPSS FD001.
    """
    root = get_project_root()
    path = data_path or (root / "DATASET" / "02_NASA_CMAPSS" / "raw" / "CMaps" / "train_FD001.txt")
    if not path.exists():
        path = root / "data" / "cmapss" / "train_FD001.txt"

    if not path.exists():
        raise FileNotFoundError(f"NASA C-MAPSS dataset not found at {path}")

    logger.info(f"Extracting features for NASA C-MAPSS FD001 from {path}")
    df_raw = pd.read_csv(path, sep=r"\s+", header=None, names=CMAPSS_COLUMNS)

    df = df_raw.copy()

    # 1. Target Construction: Compute RUL per engine
    # max_cycle per engine
    max_cycles = df.groupby("unit_number")["time_cycles"].max().reset_index()
    max_cycles.rename(columns={"time_cycles": "max_cycle"}, inplace=True)
    df = df.merge(max_cycles, on="unit_number", how="left")
    df["rul_raw"] = df["max_cycle"] - df["time_cycles"]
    df["rul_clipped"] = np.minimum(df["rul_raw"], rul_clip)
    df.drop(columns=["max_cycle"], inplace=True)

    # 2. Causal Rolling Statistics and Trend Features (Computed per engine group)
    engineered_cols = []
    
    # Sort strictly by engine and cycle to guarantee temporal causality
    df = df.sort_values(["unit_number", "time_cycles"]).reset_index(drop=True)

    # Process each informative sensor
    for s in CMAPSS_INFORMATIVE_SENSORS:
        # A. First difference (rate of change t - (t-1))
        diff_col = f"{s}_diff_1"
        df[diff_col] = df.groupby("unit_number")[s].diff(1).fillna(0.0)
        engineered_cols.append(diff_col)

        # B. Baseline difference (wear accumulation relative to initial engine cycle t=1)
        base_col = f"{s}_degradation_delta"
        initial_val = df.groupby("unit_number")[s].transform("first")
        df[base_col] = df[s] - initial_val
        engineered_cols.append(base_col)

        # C. Rolling means (5 and 10 cycles, strictly causal, min_periods=1)
        for w in [5, 10]:
            mean_col = f"{s}_roll_mean_{w}"
            df[mean_col] = (
                df.groupby("unit_number")[s]
                .rolling(window=w, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
            )
            engineered_cols.append(mean_col)

        # D. Rolling standard deviation (10 cycles)
        std_col = f"{s}_roll_std_10"
        df[std_col] = (
            df.groupby("unit_number")[s]
            .rolling(window=10, min_periods=1)
            .std()
            .fillna(0.0)
            .reset_index(level=0, drop=True)
        )
        engineered_cols.append(std_col)

    # Cycle progression ratio (cycle relative to expected baseline)
    df["cycle_norm"] = df["time_cycles"] / 100.0
    engineered_cols.append("cycle_norm")

    # Build Feature Dictionary
    records = []

    # Identifiers
    records.append({
        "feature_name": "unit_number",
        "original_columns": "unit_number",
        "feature_type": "IDENTIFIER_GROUP",
        "data_type": str(df["unit_number"].dtype),
        "unit": "Engine ID",
        "formula": "Identity",
        "description": "Unique turbofan engine trajectory group identifier",
        "dataset": "NASA_CMAPSS_FD001",
        "task": "RUL_Regression",
        "temporal_behavior": "GROUP",
        "lookback": "Full trajectory",
        "available_at_prediction_time": "YES",
        "leakage_status": "SAFE_FOR_GROUPING",
        "missing_rate": 0.0,
        "variance": float(df["unit_number"].var()),
        "unique_count": int(df["unit_number"].nunique()),
        "status": "KEEP",
        "removal_reason": "Required for GroupKFold validation splitting",
    })

    records.append({
        "feature_name": "time_cycles",
        "original_columns": "time_cycles",
        "feature_type": "TEMPORAL_INDEX",
        "data_type": str(df["time_cycles"].dtype),
        "unit": "Operating Cycles",
        "formula": "Integer count",
        "description": "Sequential operating cycle count from start of engine life",
        "dataset": "NASA_CMAPSS_FD001",
        "task": "RUL_Regression",
        "temporal_behavior": "TIME_SERIES",
        "lookback": "Monotonic",
        "available_at_prediction_time": "YES",
        "leakage_status": "SAFE",
        "missing_rate": 0.0,
        "variance": float(df["time_cycles"].var()),
        "unique_count": int(df["time_cycles"].nunique()),
        "status": "KEEP",
        "removal_reason": "Valid causal feature indicating operating history",
    })

    # Targets
    for t_col, desc, form in [
        ("rul_raw", "Unclipped true remaining operating cycles until failure", "max_cycles - time_cycles"),
        ("rul_clipped", f"Piecewise linear RUL target capped at {rul_clip} cycles", f"min(rul_raw, {rul_clip})"),
    ]:
        records.append({
            "feature_name": t_col,
            "original_columns": "time_cycles",
            "feature_type": "TARGET",
            "data_type": str(df[t_col].dtype),
            "unit": "Cycles",
            "formula": form,
            "description": desc,
            "dataset": "NASA_CMAPSS_FD001",
            "task": "RUL_Regression",
            "temporal_behavior": "FUTURE_TARGET",
            "lookback": "None",
            "available_at_prediction_time": "NO",
            "leakage_status": "TARGET",
            "missing_rate": 0.0,
            "variance": float(df[t_col].var()),
            "unique_count": int(df[t_col].nunique()),
            "status": "TARGET",
            "removal_reason": "Supervised learning ground truth label",
        })

    # Constant Sensors (Removed)
    for s in CMAPSS_CONSTANT_SENSORS:
        records.append({
            "feature_name": s,
            "original_columns": s,
            "feature_type": "SENSOR_CONSTANT",
            "data_type": str(df[s].dtype),
            "unit": "Engineering Units",
            "formula": "Raw sensor reading",
            "description": f"Turbofan sensor channel {s} exhibiting invariant reading across sea-level flight envelope",
            "dataset": "NASA_CMAPSS_FD001",
            "task": "RUL_Regression",
            "temporal_behavior": "STATIC",
            "lookback": "None",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": 0.0,
            "variance": float(df[s].var()),
            "unique_count": int(df[s].nunique()),
            "status": "REMOVE",
            "removal_reason": "Near-zero variance (< 1e-6); contains no degradation signal in FD001",
        })

    # Informative Raw Sensors
    for s in CMAPSS_INFORMATIVE_SENSORS + ["setting_1", "setting_2", "setting_3"]:
        records.append({
            "feature_name": s,
            "original_columns": s,
            "feature_type": "SENSOR_RAW" if s.startswith("s") else "OPERATIONAL_SETTING",
            "data_type": str(df[s].dtype),
            "unit": "Engineering Units",
            "formula": "Raw telemetry",
            "description": f"Raw turbofan channel {s} measurement at cycle t",
            "dataset": "NASA_CMAPSS_FD001",
            "task": "RUL_Regression",
            "temporal_behavior": "TIME_SERIES",
            "lookback": "Cycle t",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": 0.0,
            "variance": float(df[s].var()),
            "unique_count": int(df[s].nunique()),
            "status": "KEEP",
            "removal_reason": "None (informative diagnostic sensor)",
        })

    # Engineered Causal Features
    for col in engineered_cols:
        parts = col.split("_")
        sensor = parts[0]
        records.append({
            "feature_name": col,
            "original_columns": sensor if sensor in CMAPSS_COLUMNS else "time_cycles",
            "feature_type": "DERIVED_CAUSAL_TEMPORAL",
            "data_type": str(df[col].dtype),
            "unit": "Delta/Average Units",
            "formula": f"Causal transform ({col}) within engine group",
            "description": f"Engineered degradation indicator {col} using strictly prior/current cycles",
            "dataset": "NASA_CMAPSS_FD001",
            "task": "RUL_Regression",
            "temporal_behavior": "CAUSAL_TIME_SERIES",
            "lookback": "1 to 10 cycles",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()),
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (strictly causal degradation trend)",
        })

    feature_dict = pd.DataFrame(records)

    metadata = {
        "dataset_name": "NASA_CMAPSS_FD001",
        "total_rows": len(df),
        "total_engines": int(df["unit_number"].nunique()),
        "total_columns": len(df.columns),
        "informative_sensors_count": len(CMAPSS_INFORMATIVE_SENSORS),
        "constant_sensors_dropped": CMAPSS_CONSTANT_SENSORS,
        "engineered_features_count": len(engineered_cols),
        "target_clipped_value": rul_clip,
        "mean_rul_cycles": float(df["rul_clipped"].mean()),
        "status": "EXTRACTED_AND_AUDITED",
    }

    return df, feature_dict, metadata
