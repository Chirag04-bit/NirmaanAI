"""
NirmaanAI Predictive Maintenance Feature Engineering & Dataset Preparation
Implements domain physics features, rolling temporal features, strict leakage guardrails,
and grouped/stratified dataset splitting for AI4I 2020 and NASA C-MAPSS.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.logger import logger

# AI4I Strict Exclusion List: These columns MUST NOT be used as inputs for binary failure classification
AI4I_LEAKAGE_COLUMNS = ["TWF", "HDF", "PWF", "OSF", "RNF"]
AI4I_IDENTIFIER_COLUMNS = ["UDI", "Product ID"]
AI4I_TARGET_COLUMN = "Machine failure"

# NASA C-MAPSS Sensor Selection: 14 informative degradation sensors (7 flat/constant sensors dropped)
CMAPSS_INFORMATIVE_SENSORS = [
    "s2", "s3", "s4", "s7", "s8", "s9", "s11", "s12", "s13", "s14", "s15", "s17", "s20", "s21"
]
CMAPSS_SETTINGS = ["setting_1", "setting_2"]


def engineer_ai4i_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes domain physics features for AI4I 2020 telemetry.
    All features represent legitimate sensor and operational information available at inference time.
    Standardizes column names to remove bracket characters ([ and ]) for model library compatibility.
    """
    df_feat = df.copy()

    # Standardize raw sensor names to snake_case without square brackets
    rename_dict = {
        "Air temperature [K]": "air_temperature_k",
        "Process temperature [K]": "process_temperature_k",
        "Rotational speed [rpm]": "rotational_speed_rpm",
        "Torque [Nm]": "torque_nm",
        "Tool wear [min]": "tool_wear_min"
    }
    df_feat = df_feat.rename(columns={k: v for k, v in rename_dict.items() if k in df_feat.columns})

    # 1. Thermal difference: Delta T = Process Temperature - Air Temperature
    df_feat["temp_diff_k"] = df_feat["process_temperature_k"] - df_feat["air_temperature_k"]

    # 2. Mechanical Power (kW) = (2 * pi * speed_rpm * torque_nm) / 60000
    df_feat["mechanical_power_kw"] = (
        2.0 * np.pi * df_feat["rotational_speed_rpm"] * df_feat["torque_nm"]
    ) / 60000.0

    # 3. Torque to Speed Ratio (load stress indicator)
    df_feat["torque_speed_ratio"] = df_feat["torque_nm"] / np.maximum(df_feat["rotational_speed_rpm"], 1.0)

    # 4. Tool Wear Risk Index: non-linear quadratic acceleration past 200 min
    df_feat["tool_wear_risk_index"] = (df_feat["tool_wear_min"] / 200.0) ** 2

    # 5. Encode product Type (L=Low quality/high volume, M=Medium, H=High)
    type_mapping = {"L": 0, "M": 1, "H": 2}
    if "Type" in df_feat.columns:
        df_feat["product_type_code"] = df_feat["Type"].map(type_mapping).fillna(0).astype(int)

    return df_feat


def prepare_ai4i_splits(
    df: pd.DataFrame,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Prepares stratified train, validation, and test sets for AI4I 2020 binary failure prediction.
    Strictly excludes failure-mode indicator columns (TWF, HDF, PWF, OSF, RNF) and row identifiers.
    """
    # Guardrail audit: Ensure target is present
    if AI4I_TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{AI4I_TARGET_COLUMN}' not found in DataFrame.")

    # 1. Feature Engineering
    df_engineered = engineer_ai4i_features(df)

    # 2. Drop leakage, identifier, and target columns
    cols_to_drop = [AI4I_TARGET_COLUMN] + AI4I_LEAKAGE_COLUMNS + AI4I_IDENTIFIER_COLUMNS
    if "Type" in df_engineered.columns:
        cols_to_drop.append("Type")  # Categorical string replaced by product_type_code

    feature_cols = [col for col in df_engineered.columns if col not in cols_to_drop]

    X = df_engineered[feature_cols].copy()
    y = df_engineered[AI4I_TARGET_COLUMN].astype(int).copy()

    # 3. Stratified Split: Train (70%), Val (15%), Test (15%)
    # First partition into (train+val, 85%) and (test, 15%)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    # Then partition (train+val) into train (70% total) and val (15% total)
    relative_val_size = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=relative_val_size, stratify=y_train_val, random_state=random_state
    )

    logger.info(
        f"AI4I dataset split completed: Train={len(X_train)} (Failures={y_train.sum()}), "
        f"Val={len(X_val)} (Failures={y_val.sum()}), Test={len(X_test)} (Failures={y_test.sum()}). "
        f"Features count={len(feature_cols)} (Leakage columns strictly excluded)."
    )

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
        "feature_names": feature_cols,
        "target_name": AI4I_TARGET_COLUMN
    }


def load_raw_cmapss_file(filepath: Path) -> pd.DataFrame:
    """Reads a NASA C-MAPSS space-delimited data file and assigns standard column headers."""
    column_names = (
        ["unit_number", "time_in_cycles", "setting_1", "setting_2", "setting_3"]
        + [f"s{i}" for i in range(1, 22)]
    )
    df = pd.read_csv(filepath, sep=r"\s+", header=None, names=column_names)
    return df


def engineer_cmapss_features(
    df: pd.DataFrame,
    window_size: int = 5
) -> pd.DataFrame:
    """
    Computes causal rolling features (mean and standard deviation) per engine unit.
    Preserves strict temporal ordering without using future cycles.
    """
    df_feat = df.copy()
    feature_cols = CMAPSS_SETTINGS + CMAPSS_INFORMATIVE_SENSORS

    # Groupby unit_number and apply causal rolling window
    grouped = df_feat.groupby("unit_number")[feature_cols]

    rolling_means = grouped.rolling(window=window_size, min_periods=1).mean().reset_index(level=0, drop=True)
    rolling_means.columns = [f"{col}_roll_mean" for col in feature_cols]

    rolling_stds = grouped.rolling(window=window_size, min_periods=1).std().fillna(0.0).reset_index(level=0, drop=True)
    rolling_stds.columns = [f"{col}_roll_std" for col in feature_cols]

    result = pd.concat([df_feat, rolling_means, rolling_stds], axis=1)
    return result


def prepare_cmapss_splits(
    train_file: Path,
    test_file: Optional[Path] = None,
    rul_file: Optional[Path] = None,
    max_rul_clip: float = 125.0,
    val_engine_ratio: float = 0.15,
    test_engine_ratio: float = 0.15,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Prepares engine-wise grouped train, validation, and test sets for NASA C-MAPSS turbofan RUL regression.
    Observations from the same engine never cross train/val/test boundaries.
    Applies standard piecewise linear RUL target capping (max_rul_clip = 125 cycles).
    """
    df_train_raw = load_raw_cmapss_file(train_file)

    # 1. Compute ground-truth RUL for run-to-failure training data
    max_cycles = df_train_raw.groupby("unit_number")["time_in_cycles"].transform("max")
    df_train_raw["raw_rul"] = max_cycles - df_train_raw["time_in_cycles"]
    # Piecewise linear target capping
    df_train_raw["rul"] = np.minimum(df_train_raw["raw_rul"], max_rul_clip)

    # 2. Engineer causal temporal features
    df_engineered = engineer_cmapss_features(df_train_raw)

    # 3. Grouped split by engine unit_number
    engine_units = df_engineered["unit_number"].unique()
    rng = np.random.RandomState(random_state)
    shuffled_engines = rng.permutation(engine_units)

    n_engines = len(shuffled_engines)
    n_test = int(np.round(n_engines * test_engine_ratio))
    n_val = int(np.round(n_engines * val_engine_ratio))
    n_train = n_engines - n_test - n_val

    train_engines = set(shuffled_engines[:n_train])
    val_engines = set(shuffled_engines[n_train:n_train + n_val])
    test_engines = set(shuffled_engines[n_train + n_val:])

    train_mask = df_engineered["unit_number"].isin(train_engines)
    val_mask = df_engineered["unit_number"].isin(val_engines)
    test_mask = df_engineered["unit_number"].isin(test_engines)

    # Input feature column selection: settings + 14 informative sensors + rolling statistics
    cols_to_exclude = ["unit_number", "time_in_cycles", "setting_3", "raw_rul", "rul"]
    # also exclude uninformative flat raw sensors: s1, s5, s6, s10, s16, s18, s19
    uninformative_raw = ["s1", "s5", "s6", "s10", "s16", "s18", "s19"]
    cols_to_exclude.extend(uninformative_raw)

    feature_cols = [c for c in df_engineered.columns if c not in cols_to_exclude]

    X_train = df_engineered.loc[train_mask, feature_cols].copy()
    y_train = df_engineered.loc[train_mask, "rul"].copy()

    X_val = df_engineered.loc[val_mask, feature_cols].copy()
    y_val = df_engineered.loc[val_mask, "rul"].copy()

    X_test_internal = df_engineered.loc[test_mask, feature_cols].copy()
    y_test_internal = df_engineered.loc[test_mask, "rul"].copy()

    # 4. Prepare official benchmark test set if test_file & rul_file are provided
    X_official_test = None
    y_official_test = None
    if test_file and rul_file and test_file.exists() and rul_file.exists():
        df_test_raw = load_raw_cmapss_file(test_file)
        df_test_eng = engineer_cmapss_features(df_test_raw)
        # Official test evaluation evaluates the final operational cycle of each engine
        last_cycles = df_test_eng.groupby("unit_number").last().reset_index()
        X_official_test = last_cycles[feature_cols].copy()

        df_rul = pd.read_csv(rul_file, header=None, names=["true_rul"])
        y_official_test = np.minimum(df_rul["true_rul"].values, max_rul_clip)

    logger.info(
        f"NASA C-MAPSS dataset split completed: Train={len(train_engines)} engines ({len(X_train)} rows), "
        f"Val={len(val_engines)} engines ({len(X_val)} rows), "
        f"Internal Test={len(test_engines)} engines ({len(X_test_internal)} rows). "
        f"Features count={len(feature_cols)}."
    )

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test_internal": X_test_internal,
        "y_test_internal": y_test_internal,
        "X_official_test": X_official_test,
        "y_official_test": y_official_test,
        "feature_names": feature_cols,
        "train_engines": list(train_engines),
        "val_engines": list(val_engines),
        "test_engines": list(test_engines),
        "max_rul_clip": max_rul_clip
    }
