"""
NirmaanAI Feature Engineering Module: Industrial IoT Sensor Simulator (2040)
Dataset: Industrial IoT Simulator (500,000 multi-sensor factory records)
Tasks: Binary Failure Prediction (Failure_Within_7_Days) & RUL Estimation (Remaining_Useful_Life_days)

Enforces strict research integrity:
- Explicit separation between failure target (Failure_Within_7_Days) and RUL target (Remaining_Useful_Life_days) to prevent cross-target leakage.
- Machine identifier (Machine_ID) isolated as categorical identifier.
- Domain physics-derived features: thermal deviation, ISO 10816 vibration severity ratio, fluid depletion index, mechanical stress interaction.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config_loader import get_project_root
from src.utils.logger import logger

IIOT_TARGET_FAILURE = "Failure_Within_7_Days"
IIOT_TARGET_RUL = "Remaining_Useful_Life_days"
IIOT_IDENTIFIER = "Machine_ID"


def extract_industrial_iot_features(
    data_path: Path = None,
    sample_limit: int = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Extracts sensor and operational features for the Industrial IoT simulator dataset.
    """
    root = get_project_root()
    path = data_path or (root / "DATASET" / "05_INDUSTRIAL_IOT" / "raw" / "factory_sensor_simulator_2040.csv")
    if not path.exists():
        path = root / "data" / "industrial_iot" / "factory_sensor_simulator_2040.csv"

    if not path.exists():
        raise FileNotFoundError(f"Industrial IoT dataset not found at {path}")

    logger.info(f"Extracting features for Industrial IoT from {path}")
    if sample_limit:
        df_raw = pd.read_csv(path, nrows=sample_limit)
    else:
        df_raw = pd.read_csv(path)

    df = df_raw.copy()

    # 1. Thermal stress: Temperature deviation from nominal operating midpoint (~55 C)
    df["thermal_deviation_c"] = df["Temperature_C"] - 55.0

    # 2. Vibration Severity Ratio according to ISO 10816-3 (2.8 mm/s alert boundary)
    df["vibration_severity_ratio"] = df["Vibration_mms"] / 2.80

    # 3. Combined Fluid Depletion Index (sum of oil and coolant deficiencies)
    df["fluid_depletion_index"] = (100.0 - df["Oil_Level_pct"]) + (100.0 - df["Coolant_Level_pct"])

    # 4. Mechanical Thermo-Vibration Stress Product
    df["thermo_vibration_stress"] = df["Temperature_C"] * df["Vibration_mms"]

    # 5. Hydraulic Pressure Deviation from nominal 120 bar
    df["hydraulic_pressure_deviation"] = (df["Hydraulic_Pressure_bar"] - 120.0).abs()

    # 6. Error Frequency Rate (Errors per operational hour proxy)
    df["error_rate_per_1k_hours"] = df["Error_Codes_Last_30_Days"] / np.maximum(df["Operational_Hours"] / 1000.0, 0.1)

    # 7. Coolant Flow to Temperature Ratio (heat removal capacity)
    df["coolant_thermal_efficiency"] = df["Coolant_Flow_L_min"] / np.maximum(df["Temperature_C"], 1.0)

    # Build Feature Dictionary
    records = []

    # Identifiers
    records.append({
        "feature_name": "Machine_ID",
        "original_columns": "Machine_ID",
        "feature_type": "IDENTIFIER",
        "data_type": str(df["Machine_ID"].dtype),
        "unit": "ID String",
        "formula": "Identity",
        "description": "Unique factory machine entity identifier",
        "dataset": "Industrial_IoT_2040",
        "task": "Failure_and_RUL_Prediction",
        "temporal_behavior": "STATIC",
        "lookback": "None",
        "available_at_prediction_time": "YES",
        "leakage_status": "SAFE_FOR_GROUPING",
        "missing_rate": float(df["Machine_ID"].isna().mean()),
        "variance": 0.0,
        "unique_count": int(df["Machine_ID"].nunique()),
        "status": "KEEP_METADATA",
        "removal_reason": "Required for entity-level cross-validation",
    })

    # Targets & Cross-Target Leakage
    records.append({
        "feature_name": IIOT_TARGET_FAILURE,
        "original_columns": IIOT_TARGET_FAILURE,
        "feature_type": "TARGET",
        "data_type": str(df[IIOT_TARGET_FAILURE].dtype),
        "unit": "Binary (0/1)",
        "formula": "Binary label",
        "description": "Machine breakdown occurring within 7 days",
        "dataset": "Industrial_IoT_2040",
        "task": "Failure_Classification",
        "temporal_behavior": "FUTURE_WINDOW",
        "lookback": "Next 7 days",
        "available_at_prediction_time": "NO",
        "leakage_status": "TARGET",
        "missing_rate": float(df[IIOT_TARGET_FAILURE].isna().mean()),
        "variance": float(df[IIOT_TARGET_FAILURE].var()),
        "unique_count": 2,
        "status": "TARGET",
        "removal_reason": "Supervised binary classification target",
    })

    records.append({
        "feature_name": IIOT_TARGET_RUL,
        "original_columns": IIOT_TARGET_RUL,
        "feature_type": "TARGET_OR_LEAKAGE",
        "data_type": str(df[IIOT_TARGET_RUL].dtype),
        "unit": "Days",
        "formula": "Remaining life in days",
        "description": "Remaining useful operating life in days until failure",
        "dataset": "Industrial_IoT_2040",
        "task": "RUL_Regression",
        "temporal_behavior": "FUTURE_TARGET",
        "lookback": "Future",
        "available_at_prediction_time": "NO",
        "leakage_status": "LEAKAGE_IF_CLASSIFYING_FAILURE",
        "missing_rate": float(df[IIOT_TARGET_RUL].isna().mean()),
        "variance": float(df[IIOT_TARGET_RUL].var()),
        "unique_count": int(df[IIOT_TARGET_RUL].nunique()),
        "status": "CONDITIONAL",
        "removal_reason": "Target for RUL regression; strict leakage if evaluating binary failure",
    })

    # Raw Operational & Sensor Channels
    raw_channels = [
        ("Machine_Type", "CATEGORICAL", "Category", "Machine physical classification (CNC, Robot, etc.)"),
        ("Installation_Year", "TEMPORAL", "Year", "Machine equipment commissioning year"),
        ("Operational_Hours", "OPERATIONAL", "Hours", "Total cumulative active runtime hours"),
        ("Temperature_C", "SENSOR", "Degrees Celsius", "Spindle/core internal operating temperature"),
        ("Vibration_mms", "SENSOR", "mm/s", "RMS vibration velocity"),
        ("Sound_dB", "SENSOR", "dB", "Acoustic operational noise emission"),
        ("Oil_Level_pct", "SENSOR", "Percentage (0-100)", "Lubrication fluid reservoir level"),
        ("Coolant_Level_pct", "SENSOR", "Percentage (0-100)", "Coolant fluid reservoir level"),
        ("Power_Consumption_kW", "SENSOR", "kW", "Active power drawn by the equipment"),
        ("Last_Maintenance_Days_Ago", "MAINTENANCE", "Days", "Days elapsed since previous maintenance intervention"),
        ("Maintenance_History_Count", "MAINTENANCE", "Count", "Total historical scheduled maintenance count"),
        ("Failure_History_Count", "MAINTENANCE", "Count", "Total historical breakdown events recorded"),
        ("AI_Supervision", "CATEGORICAL", "Category", "Supervisory AI monitoring tier"),
        ("Error_Codes_Last_30_Days", "OPERATIONAL", "Count", "Diagnostic error codes logged in preceding 30 days"),
        ("Laser_Intensity", "SENSOR", "Index", "Laser tooling power / sensor intensity"),
        ("Hydraulic_Pressure_bar", "SENSOR", "bar", "Active hydraulic manifold pressure"),
        ("Coolant_Flow_L_min", "SENSOR", "L/min", "Coolant circulation volumetric flow rate"),
        ("Heat_Index", "SENSOR", "Index", "Composite thermal index"),
        ("AI_Override_Events", "OPERATIONAL", "Count", "Number of safety override interventions"),
    ]
    for col, ftype, unit, desc in raw_channels:
        records.append({
            "feature_name": col,
            "original_columns": col,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": "Raw feature",
            "description": desc,
            "dataset": "Industrial_IoT_2040",
            "task": "Failure_and_RUL_Prediction",
            "temporal_behavior": "INSTANTANEOUS",
            "lookback": "Current snapshot",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()) if pd.api.types.is_numeric_dtype(df[col]) else 0.0,
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (informative diagnostic telemetry)",
        })

    # Engineered Features
    eng_channels = [
        ("thermal_deviation_c", "Temperature_C", "DERIVED_THERMAL", "Delta Celsius", "Temperature deviation from nominal operating midpoint (~55 C)", "Temperature_C - 55.0"),
        ("vibration_severity_ratio", "Vibration_mms", "DERIVED_MECHANICAL", "Ratio", "Vibration severity relative to ISO 10816 2.8 mm/s alert boundary", "Vibration_mms / 2.80"),
        ("fluid_depletion_index", "Oil_Level_pct, Coolant_Level_pct", "DERIVED_MAINTENANCE", "Index (0-200)", "Total fluid deficiency score", "(100 - Oil) + (100 - Coolant)"),
        ("thermo_vibration_stress", "Temperature_C, Vibration_mms", "DERIVED_STRESS", "C * mm/s", "Composite thermal-mechanical stress product", "Temperature_C * Vibration_mms"),
        ("hydraulic_pressure_deviation", "Hydraulic_Pressure_bar", "DERIVED_MECHANICAL", "bar", "Absolute deviation from nominal 120 bar pressure", "abs(Hydraulic_Pressure_bar - 120.0)"),
        ("error_rate_per_1k_hours", "Error_Codes, Operational_Hours", "DERIVED_RELIABILITY", "Errors/k-hr", "Error frequency normalized by machine age", "Error_Codes / (Hours / 1000)"),
        ("coolant_thermal_efficiency", "Coolant_Flow, Temperature_C", "DERIVED_THERMAL", "L/min/C", "Cooling flow capacity per degree temperature", "Coolant_Flow / Temperature_C"),
    ]
    for col, orig, ftype, unit, desc, formula in eng_channels:
        records.append({
            "feature_name": col,
            "original_columns": orig,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": formula,
            "description": desc,
            "dataset": "Industrial_IoT_2040",
            "task": "Failure_and_RUL_Prediction",
            "temporal_behavior": "INSTANTANEOUS",
            "lookback": "Current snapshot",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()),
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (domain physics derived feature)",
        })

    feature_dict = pd.DataFrame(records)

    metadata = {
        "dataset_name": "Industrial_IoT_2040",
        "total_records": len(df),
        "total_columns": len(df.columns),
        "engineered_features_count": len(eng_channels),
        "failure_target_col": IIOT_TARGET_FAILURE,
        "rul_target_col": IIOT_TARGET_RUL,
        "failure_rate": float(df[IIOT_TARGET_FAILURE].mean()),
        "mean_rul_days": float(df[IIOT_TARGET_RUL].mean()),
        "status": "EXTRACTED_AND_AUDITED",
    }

    return df, feature_dict, metadata
