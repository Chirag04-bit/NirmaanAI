"""
NirmaanAI Feature Engineering Module: Manufacturing Production Operations
Dataset: Hybrid Manufacturing Operations (1,000 discrete batch jobs)
Primary Task: Production Bottleneck Prediction & Flow Congestion Analysis

Enforces strict temporal and research integrity:
- Rigid separation between PROSPECTIVE FEATURES (available at job dispatch time t <= Scheduled_Start)
  and POST-EVENT DIAGNOSTIC FEATURES (Actual_Start, Actual_End, Job_Status, realized delays).
- Prohibits using post-completion cycle time or final completion delay for prospective bottleneck models.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config_loader import get_project_root
from src.utils.logger import logger


def extract_production_features(
    data_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Extracts prospective dispatch features and post-event diagnostic metrics.
    """
    root = get_project_root()
    path = data_path or (root / "DATASET" / "06_MANUFACTURING_PRODUCTION" / "raw" / "hybrid_manufacturing_categorical.csv")
    if not path.exists():
        path = root / "data" / "manufacturing_production" / "hybrid_manufacturing_categorical.csv"

    if not path.exists():
        raise FileNotFoundError(f"Manufacturing production dataset not found at {path}")

    logger.info(f"Extracting features for Manufacturing Production from {path}")
    df_raw = pd.read_csv(path)
    df = df_raw.copy()

    # Parse timestamps
    df["Scheduled_Start_dt"] = pd.to_datetime(df["Scheduled_Start"])
    df["Scheduled_End_dt"] = pd.to_datetime(df["Scheduled_End"])
    df["Actual_Start_dt"] = pd.to_datetime(df["Actual_Start"], errors="coerce")
    df["Actual_End_dt"] = pd.to_datetime(df["Actual_End"], errors="coerce")

    # A. PROSPECTIVE FEATURES (Available prior to job release)
    # 1. Planned scheduled duration in minutes
    df["planned_duration_min"] = (
        (df["Scheduled_End_dt"] - df["Scheduled_Start_dt"]).dt.total_seconds() / 60.0
    ).clip(lower=1.0)

    # 2. Scheduled timing indicators
    df["scheduled_hour"] = df["Scheduled_Start_dt"].dt.hour
    df["scheduled_day_of_week"] = df["Scheduled_Start_dt"].dt.dayofweek

    # 3. Planned energy intensity per minute of processing
    df["planned_energy_rate"] = df["Energy_Consumption"] / np.maximum(df["Processing_Time"], 1.0)

    # 4. Material to Processing Time Ratio
    df["material_intensity"] = df["Material_Used"] / np.maximum(df["Processing_Time"], 1.0)

    # 5. Machine availability stress factor (100 - Availability)
    df["machine_unavailability_pct"] = 100.0 - df["Machine_Availability"]

    # 6. One-hot / frequency encoding for Operation_Type
    op_map = {"Grinding": 0, "Lathe": 1, "Milling": 2, "Drilling": 3, "Additive": 4}
    df["operation_type_code"] = df["Operation_Type"].map(op_map).fillna(-1).astype(int)

    # B. POST-EVENT DIAGNOSTIC FEATURES (Strictly quarantined from prospective models)
    # 1. Start delay in minutes
    df["realized_start_delay_min"] = (
        (df["Actual_Start_dt"] - df["Scheduled_Start_dt"]).dt.total_seconds() / 60.0
    ).fillna(0.0)

    # 2. Realized actual duration in minutes
    df["realized_duration_min"] = (
        (df["Actual_End_dt"] - df["Actual_Start_dt"]).dt.total_seconds() / 60.0
    ).fillna(df["planned_duration_min"])

    # 3. Cycle ratio = Actual duration / Planned duration
    df["realized_cycle_ratio"] = df["realized_duration_min"] / df["planned_duration_min"]

    # 4. Total completion delay
    df["realized_completion_delay_min"] = (
        (df["Actual_End_dt"] - df["Scheduled_End_dt"]).dt.total_seconds() / 60.0
    ).fillna(0.0)

    # 5. Bottleneck Indicator (Ground Truth Target)
    # True if delayed start >= 10m OR cycle ratio >= 1.20 OR status is Delayed/Failed
    df["target_is_bottleneck"] = (
        (df["Job_Status"].isin(["Delayed", "Failed"]))
        | (df["realized_start_delay_min"] >= 10.0)
        | (df["realized_cycle_ratio"] >= 1.20)
    ).astype(int)

    # Build Feature Dictionary
    records = []

    # Identifiers
    for col in ["Job_ID", "Machine_ID"]:
        records.append({
            "feature_name": col,
            "original_columns": col,
            "feature_type": "IDENTIFIER",
            "data_type": str(df[col].dtype),
            "unit": "String ID",
            "formula": "Identity",
            "description": f"Unique identifier for {col}",
            "dataset": "Manufacturing_Production",
            "task": "Bottleneck_Flow_Prediction",
            "temporal_behavior": "STATIC",
            "lookback": "None",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE_FOR_GROUPING" if col == "Machine_ID" else "LEAKAGE_IDENTIFIER",
            "missing_rate": float(df[col].isna().mean()),
            "variance": 0.0,
            "unique_count": int(df[col].nunique()),
            "status": "KEEP_METADATA" if col == "Machine_ID" else "REMOVE",
            "removal_reason": "High-cardinality job identifier" if col == "Job_ID" else "Required for station grouping",
        })

    # Prospective Inputs
    prosp_features = [
        ("Operation_Type", "Operation_Type", "CATEGORICAL", "String", "Manufacturing station process type", "Raw"),
        ("operation_type_code", "Operation_Type", "CATEGORICAL_ENCODED", "Integer", "Ordinal code of operation type", "map(op_map)"),
        ("Material_Used", "Material_Used", "NUMERICAL_OPERATIONAL", "Units/kg", "Raw material quantity allocated for job", "Raw"),
        ("Processing_Time", "Processing_Time", "NUMERICAL_OPERATIONAL", "Minutes", "Nominal design processing time", "Raw"),
        ("Energy_Consumption", "Energy_Consumption", "NUMERICAL_ENERGY", "kWh", "Planned electrical energy allocation", "Raw"),
        ("Machine_Availability", "Machine_Availability", "OPERATIONAL", "Percentage (0-100)", "Reported machine availability at dispatch", "Raw"),
        ("planned_duration_min", "Scheduled_End - Scheduled_Start", "DERIVED_SCHEDULE", "Minutes", "Planned scheduled duration", "Scheduled_End - Scheduled_Start"),
        ("scheduled_hour", "Scheduled_Start", "CALENDAR", "Hour (0-23)", "Scheduled dispatch hour of day", "Scheduled_Start.dt.hour"),
        ("scheduled_day_of_week", "Scheduled_Start", "CALENDAR", "Day (0-6)", "Scheduled dispatch day of week", "Scheduled_Start.dt.dayofweek"),
        ("planned_energy_rate", "Energy, Processing_Time", "DERIVED_ENERGY", "kWh/min", "Planned energy consumption per minute", "Energy / Processing_Time"),
        ("material_intensity", "Material, Processing_Time", "DERIVED_OPERATIONAL", "Units/min", "Material consumption rate", "Material / Processing_Time"),
        ("machine_unavailability_pct", "Machine_Availability", "DERIVED_OPERATIONAL", "Percentage", "Machine unavailability risk factor", "100 - Machine_Availability"),
    ]
    for col, orig, ftype, unit, desc, formula in prosp_features:
        records.append({
            "feature_name": col,
            "original_columns": orig,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": formula,
            "description": desc,
            "dataset": "Manufacturing_Production",
            "task": "Bottleneck_Flow_Prediction",
            "temporal_behavior": "PROSPECTIVE_DISPATCH",
            "lookback": "t <= Scheduled_Start",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()) if pd.api.types.is_numeric_dtype(df[col]) else 0.0,
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (valid prospective operational predictor)",
        })

    # Post-Event Diagnostic Features (Quarantined)
    post_event_features = [
        ("Actual_Start", "Actual_Start", "TIMESTAMP", "Datetime", "Empirical job commencement timestamp", "Raw"),
        ("Actual_End", "Actual_End", "TIMESTAMP", "Datetime", "Empirical job completion timestamp", "Raw"),
        ("Job_Status", "Job_Status", "CATEGORICAL", "String", "Final completed execution status (Completed/Delayed/Failed)", "Raw"),
        ("Optimization_Category", "Optimization_Category", "CATEGORICAL", "String", "Post-hoc operational efficiency rating", "Raw"),
        ("realized_start_delay_min", "Actual_Start - Scheduled_Start", "POST_EVENT_DIAGNOSTIC", "Minutes", "Empirical dispatch latency", "Actual_Start - Scheduled_Start"),
        ("realized_duration_min", "Actual_End - Actual_Start", "POST_EVENT_DIAGNOSTIC", "Minutes", "Empirical run duration", "Actual_End - Actual_Start"),
        ("realized_cycle_ratio", "Duration / Planned", "POST_EVENT_DIAGNOSTIC", "Ratio", "Empirical cycle time expansion ratio", "realized_duration / planned_duration"),
        ("realized_completion_delay_min", "Actual_End - Scheduled_End", "POST_EVENT_DIAGNOSTIC", "Minutes", "Empirical completion delay", "Actual_End - Scheduled_End"),
    ]
    for col, orig, ftype, unit, desc, formula in post_event_features:
        records.append({
            "feature_name": col,
            "original_columns": orig,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": formula,
            "description": desc,
            "dataset": "Manufacturing_Production",
            "task": "Bottleneck_Flow_Prediction",
            "temporal_behavior": "POST_EVENT",
            "lookback": "t >= Actual_End",
            "available_at_prediction_time": "NO",
            "leakage_status": "POST_EVENT_ONLY",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()) if pd.api.types.is_numeric_dtype(df[col]) else 0.0,
            "unique_count": int(df[col].nunique()),
            "status": "REMOVE_FOR_PROSPECTIVE",
            "removal_reason": "Strict post-event feature; available only after job execution completes",
        })

    # Target
    records.append({
        "feature_name": "target_is_bottleneck",
        "original_columns": "Job_Status, Actual_Start, Actual_End",
        "feature_type": "TARGET",
        "data_type": "int64",
        "unit": "Binary (0/1)",
        "formula": "(Status in ['Delayed','Failed']) or (start_delay >= 10m) or (cycle_ratio >= 1.20)",
        "description": "Composite bottleneck flow restriction label",
        "dataset": "Manufacturing_Production",
        "task": "Bottleneck_Flow_Prediction",
        "temporal_behavior": "TARGET_OUTCOME",
        "lookback": "Post-event",
        "available_at_prediction_time": "NO",
        "leakage_status": "TARGET",
        "missing_rate": 0.0,
        "variance": float(df["target_is_bottleneck"].var()),
        "unique_count": 2,
        "status": "TARGET",
        "removal_reason": "Supervised classification target",
    })

    feature_dict = pd.DataFrame(records)

    metadata = {
        "dataset_name": "Manufacturing_Production",
        "total_jobs": len(df),
        "total_columns": len(df.columns),
        "prospective_features_count": len(prosp_features),
        "post_event_features_count": len(post_event_features),
        "bottleneck_count": int(df["target_is_bottleneck"].sum()),
        "bottleneck_rate": float(df["target_is_bottleneck"].mean()),
        "status": "EXTRACTED_AND_AUDITED",
    }

    return df, feature_dict, metadata
