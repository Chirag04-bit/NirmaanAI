"""
NirmaanAI Feature Engineering Module: AI4I 2020 Predictive Maintenance
Dataset: UCI AI4I 2020 Predictive Maintenance (10,000 records)
Target: Machine failure (binary)

Enforces strict research integrity:
- Strict exclusion of component failure breakdown flags (TWF, HDF, PWF, OSF, RNF) to prevent target leakage.
- Strict exclusion of arbitrary row identifiers (UDI, Product ID).
- Domain physics-derived features: thermal difference, mechanical power, torque-speed stress, tool wear acceleration.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config_loader import get_project_root
from src.utils.logger import logger

AI4I_IDENTIFIER_COLUMNS = ["UDI", "Product ID"]
AI4I_LEAKAGE_COLUMNS = ["TWF", "HDF", "PWF", "OSF", "RNF"]
AI4I_TARGET_COLUMN = "Machine failure"
AI4I_RAW_OPERATIONAL_COLUMNS = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Type",
]


def extract_ai4i_features(
    data_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Extracts raw and engineered features for AI4I 2020 dataset.
    Returns:
        df_features: DataFrame containing raw, derived, and target columns.
        feature_dict: DataFrame documenting all features and leakage statuses.
        metadata: Summary metadata dictionary.
    """
    root = get_project_root()
    path = data_path or (root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv")
    if not path.exists():
        path = root / "data" / "ai4i2020" / "ai4i2020.csv"

    if not path.exists():
        raise FileNotFoundError(f"AI4I 2020 dataset not found at {path}")

    logger.info(f"Extracting features for AI4I 2020 from {path}")
    df_raw = pd.read_csv(path)

    # Standardize column naming for compatibility
    df = df_raw.copy()
    rename_map = {
        "Air temperature [K]": "air_temperature_k",
        "Process temperature [K]": "process_temperature_k",
        "Rotational speed [rpm]": "rotational_speed_rpm",
        "Torque [Nm]": "torque_nm",
        "Tool wear [min]": "tool_wear_min",
        "Machine failure": "machine_failure",
        "Type": "product_type",
    }
    df = df.rename(columns=rename_map)

    # Engineered Features (Physically Grounded)
    # 1. Thermal difference: Delta T = Process Temp - Air Temp (K)
    df["temp_diff_k"] = df["process_temperature_k"] - df["air_temperature_k"]

    # 2. Temperature ratio: Process Temp / Air Temp
    df["temp_ratio"] = df["process_temperature_k"] / np.maximum(df["air_temperature_k"], 1.0)

    # 3. Mechanical power: P = (2 * pi * N * tau) / 60000 (kW)
    # N in rpm, tau in Nm
    df["mechanical_power_kw"] = (
        2.0 * np.pi * df["rotational_speed_rpm"] * df["torque_nm"]
    ) / 60000.0

    # 4. Torque to Speed Ratio (load stress indicator)
    df["torque_speed_ratio"] = df["torque_nm"] / np.maximum(df["rotational_speed_rpm"], 1.0)

    # 5. Torque-Speed Interaction (raw product: torque * rpm)
    df["torque_speed_product"] = df["torque_nm"] * df["rotational_speed_rpm"]

    # 6. Tool Wear Risk Index: non-linear quadratic wear rate past 200 min
    df["tool_wear_risk_index"] = (df["tool_wear_min"] / 200.0) ** 2

    # 7. Power to Temperature Ratio (dissipation efficiency)
    df["power_temp_ratio"] = df["mechanical_power_kw"] / np.maximum(df["temp_diff_k"], 0.1)

    # 8. Encoded product type: L=0, M=1, H=2
    type_map = {"L": 0, "M": 1, "H": 2}
    df["product_type_encoded"] = df["product_type"].map(type_map).fillna(0).astype(int)

    # Build Feature Dictionary
    records = []

    # Raw Identifiers
    for col in AI4I_IDENTIFIER_COLUMNS:
        records.append({
            "feature_name": col,
            "original_columns": col,
            "feature_type": "IDENTIFIER",
            "data_type": str(df_raw[col].dtype),
            "unit": "None",
            "formula": "Identity",
            "description": "Unique record or product serial identifier",
            "dataset": "AI4I_2020",
            "task": "Predictive_Maintenance_Classification",
            "temporal_behavior": "STATIC",
            "lookback": "None",
            "available_at_prediction_time": "YES",
            "leakage_status": "LEAKAGE",
            "missing_rate": float(df_raw[col].isna().mean()),
            "variance": 0.0,
            "unique_count": int(df_raw[col].nunique()),
            "status": "REMOVE",
            "removal_reason": "High-cardinality arbitrary identifier causing spurious correlation",
        })

    # Target
    records.append({
        "feature_name": "machine_failure",
        "original_columns": "Machine failure",
        "feature_type": "TARGET",
        "data_type": str(df["machine_failure"].dtype),
        "unit": "Binary (0/1)",
        "formula": "Ground truth label",
        "description": "Binary machine component breakdown indicator",
        "dataset": "AI4I_2020",
        "task": "Predictive_Maintenance_Classification",
        "temporal_behavior": "INSTANTANEOUS",
        "lookback": "None",
        "available_at_prediction_time": "NO",
        "leakage_status": "TARGET",
        "missing_rate": float(df["machine_failure"].isna().mean()),
        "variance": float(df["machine_failure"].var()),
        "unique_count": int(df["machine_failure"].nunique()),
        "status": "TARGET",
        "removal_reason": "Target variable (supervised learning label)",
    })

    # Failure Mode Leakage Columns
    for col in AI4I_LEAKAGE_COLUMNS:
        records.append({
            "feature_name": col,
            "original_columns": col,
            "feature_type": "POST_EVENT_DIAGNOSTIC",
            "data_type": str(df_raw[col].dtype),
            "unit": "Binary (0/1)",
            "formula": "Sub-failure mode diagnostic label",
            "description": f"Specific component failure mode ({col}) determined post-breakdown",
            "dataset": "AI4I_2020",
            "task": "Predictive_Maintenance_Classification",
            "temporal_behavior": "POST_EVENT",
            "lookback": "None",
            "available_at_prediction_time": "NO",
            "leakage_status": "LEAKAGE",
            "missing_rate": float(df_raw[col].isna().mean()),
            "variance": float(df_raw[col].var()),
            "unique_count": int(df_raw[col].nunique()),
            "status": "REMOVE",
            "removal_reason": "Direct post-event target leakage (deterministic sub-failure breakdown flags)",
        })

    # Raw Operational Sensors
    raw_info = [
        ("air_temperature_k", "Air temperature [K]", "SENSOR", "Kelvin (K)", "Ambient factory atmospheric temperature"),
        ("process_temperature_k", "Process temperature [K]", "SENSOR", "Kelvin (K)", "Machine tool process operating temperature"),
        ("rotational_speed_rpm", "Rotational speed [rpm]", "SENSOR", "RPM", "Spindle angular rotational speed"),
        ("torque_nm", "Torque [Nm]", "SENSOR", "Nm", "Applied spindle torque"),
        ("tool_wear_min", "Tool wear [min]", "OPERATIONAL", "Minutes", "Cumulative active cutting time of cutting insert"),
        ("product_type", "Type", "CATEGORICAL", "Category", "Product quality variant (Low, Medium, High)"),
    ]
    for col, orig, ftype, unit, desc in raw_info:
        records.append({
            "feature_name": col,
            "original_columns": orig,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": "Raw sensor reading",
            "description": desc,
            "dataset": "AI4I_2020",
            "task": "Predictive_Maintenance_Classification",
            "temporal_behavior": "INSTANTANEOUS",
            "lookback": "Current tick",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()) if pd.api.types.is_numeric_dtype(df[col]) else 0.0,
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (valid prospective operational input)",
        })

    # Engineered Features
    eng_info = [
        ("temp_diff_k", "Process temp - Air temp", "DERIVED_THERMAL", "Kelvin (K)", "Process temperature minus air temperature (heat accumulation)", "process_temperature_k - air_temperature_k"),
        ("temp_ratio", "Process temp / Air temp", "DERIVED_THERMAL", "Ratio", "Thermodynamic heat ratio indicator", "process_temperature_k / air_temperature_k"),
        ("mechanical_power_kw", "Torque, RPM", "DERIVED_MECHANICAL", "kW", "Active mechanical cutting power = 2*pi*RPM*Torque / 60000", "(2*pi*rotational_speed_rpm*torque_nm)/60000"),
        ("torque_speed_ratio", "Torque, RPM", "DERIVED_MECHANICAL", "Nm/RPM", "Mechanical load stress factor", "torque_nm / rotational_speed_rpm"),
        ("torque_speed_product", "Torque, RPM", "DERIVED_MECHANICAL", "Nm*RPM", "Direct torque-speed interaction term", "torque_nm * rotational_speed_rpm"),
        ("tool_wear_risk_index", "Tool wear [min]", "DERIVED_DEGRADATION", "Index", "Quadratic wear acceleration index = (wear / 200)^2", "(tool_wear_min / 200.0)^2"),
        ("power_temp_ratio", "Power, Temp Diff", "DERIVED_EFFICIENCY", "kW/K", "Thermal power dissipation ratio", "mechanical_power_kw / temp_diff_k"),
        ("product_type_encoded", "Type", "CATEGORICAL_ENCODED", "Ordinal (0,1,2)", "Ordinal encoding of variant: L=0, M=1, H=2", "map(L:0, M:1, H:2)"),
    ]
    for col, orig, ftype, unit, desc, formula in eng_info:
        records.append({
            "feature_name": col,
            "original_columns": orig,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": formula,
            "description": desc,
            "dataset": "AI4I_2020",
            "task": "Predictive_Maintenance_Classification",
            "temporal_behavior": "INSTANTANEOUS",
            "lookback": "Current tick",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()),
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (scientifically grounded derived feature)",
        })

    feature_dict = pd.DataFrame(records)

    metadata = {
        "dataset_name": "AI4I_2020",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "raw_columns_count": len(df_raw.columns),
        "engineered_features_count": len(eng_info),
        "target_column": "machine_failure",
        "leakage_features_excluded": AI4I_LEAKAGE_COLUMNS + AI4I_IDENTIFIER_COLUMNS,
        "positive_class_ratio": float(df["machine_failure"].mean()),
        "status": "EXTRACTED_AND_AUDITED",
    }

    return df, feature_dict, metadata
