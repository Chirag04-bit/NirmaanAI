"""
NirmaanAI Feature Engineering Module: Manufacturing Process Defects
Dataset: Manufacturing Defect Dataset (3,240 industrial production batches)
Primary Task: Quality Defect Classification (DefectStatus: 0=Compliant, 1=Defective)

Enforces strict research integrity:
- Audits DefectRate for potential high-correlation target leakage.
- Derives unit-level economic and energy efficiency indicators (cost_per_unit, energy_intensity).
- Quantifies maintenance-to-downtime balance and supply chain friction factors.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config_loader import get_project_root
from src.utils.logger import logger

DEFECT_TARGET_COLUMN = "DefectStatus"


def extract_defect_features(
    data_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Extracts process, quality, and operational stability features for manufacturing defect analysis.
    """
    root = get_project_root()
    path = data_path or (root / "DATASET" / "08_MANUFACTURING_DEFECTS" / "raw" / "manufacturing_defect_dataset.csv")
    if not path.exists():
        path = root / "data" / "manufacturing_defects" / "manufacturing_defect_dataset.csv"

    if not path.exists():
        raise FileNotFoundError(f"Manufacturing defect dataset not found at {path}")

    logger.info(f"Extracting features for Manufacturing Defects from {path}")
    df_raw = pd.read_csv(path)
    df = df_raw.copy()

    # 1. Economic: Production cost per unit volume
    df["cost_per_unit"] = df["ProductionCost"] / np.maximum(df["ProductionVolume"], 1.0)

    # 2. Energy: Energy intensity per unit volume
    df["energy_per_unit_volume"] = df["EnergyConsumption"] / np.maximum(df["ProductionVolume"], 1.0)

    # 3. Reliability: Maintenance hours per downtime percentage point
    df["maintenance_downtime_ratio"] = df["MaintenanceHours"] / np.maximum(df["DowntimePercentage"], 0.1)

    # 4. Supply Chain Risk Index: Delivery delay interaction with stockout rate
    df["supply_chain_risk_index"] = df["DeliveryDelay"] * (df["StockoutRate"] / 100.0)

    # 5. Labor-Quality Friction Index: Inverted productivity multiplied by downtime
    df["operational_friction_index"] = (100.0 - df["WorkerProductivity"]) * (df["DowntimePercentage"] / 100.0)

    # 6. Additive Process Cost Share
    df["additive_cost_share"] = df["AdditiveMaterialCost"] / np.maximum(df["ProductionCost"], 1.0)

    # 7. Energy Quality Efficiency: Ratio of EnergyEfficiency to QualityScore
    df["energy_quality_factor"] = df["EnergyEfficiency"] / np.maximum(df["QualityScore"], 1.0)

    # Build Feature Dictionary
    records = []

    # Target
    records.append({
        "feature_name": DEFECT_TARGET_COLUMN,
        "original_columns": DEFECT_TARGET_COLUMN,
        "feature_type": "TARGET",
        "data_type": str(df[DEFECT_TARGET_COLUMN].dtype),
        "unit": "Binary (0=Compliant, 1=Defective)",
        "formula": "Ground truth defect label",
        "description": "Binary component inspection defect status",
        "dataset": "Manufacturing_Defects",
        "task": "Quality_Defect_Classification",
        "temporal_behavior": "POST_INSPECTION",
        "lookback": "None",
        "available_at_prediction_time": "NO",
        "leakage_status": "TARGET",
        "missing_rate": float(df[DEFECT_TARGET_COLUMN].isna().mean()),
        "variance": float(df[DEFECT_TARGET_COLUMN].var()),
        "unique_count": 2,
        "status": "TARGET",
        "removal_reason": "Supervised learning target label",
    })

    # Raw Columns
    raw_info = [
        ("ProductionVolume", "OPERATIONAL", "Units", "Total batch production volume count"),
        ("ProductionCost", "FINANCIAL", "INR / USD", "Total expenditure incurred for batch production"),
        ("SupplierQuality", "QUALITY", "Score (0-100)", "Incoming raw material supplier compliance index"),
        ("DeliveryDelay", "OPERATIONAL", "Days", "Inbound shipment delivery delay"),
        ("DefectRate", "QUALITY_METRIC", "Percentage", "Observed percentage of parts defective"),
        ("QualityScore", "QUALITY", "Score (0-100)", "Internal composite quality compliance rating"),
        ("MaintenanceHours", "MAINTENANCE", "Hours", "Total preventative and corrective maintenance labor hours"),
        ("DowntimePercentage", "OPERATIONAL", "Percentage", "Percentage of scheduled shift lost to stoppages"),
        ("InventoryTurnover", "SUPPLY_CHAIN", "Ratio", "Inventory velocity turnover ratio"),
        ("StockoutRate", "SUPPLY_CHAIN", "Percentage", "Frequency of raw material stockout events"),
        ("WorkerProductivity", "OPERATIONAL", "Score (0-100)", "Operational labor output efficiency score"),
        ("SafetyIncidents", "OPERATIONAL", "Count", "Workplace safety incidents logged during batch run"),
        ("EnergyConsumption", "ENERGY", "kWh", "Total electrical energy consumed by processing equipment"),
        ("EnergyEfficiency", "ENERGY", "Index", "Process energy efficiency rating"),
        ("AdditiveProcessTime", "PROCESS", "Minutes", "Duration of secondary additive processing"),
        ("AdditiveMaterialCost", "FINANCIAL", "Cost", "Direct material cost of additive manufacturing components"),
    ]
    for col, ftype, unit, desc in raw_info:
        # Check if DefectRate has high leakage risk
        leakage = "CONDITIONAL_HIGH_CORRELATION" if col == "DefectRate" else "SAFE"
        status = "REVIEW" if col == "DefectRate" else "KEEP"
        reason = "Extremely high correlation with DefectStatus; review to avoid proxy leakage" if col == "DefectRate" else "None"

        records.append({
            "feature_name": col,
            "original_columns": col,
            "feature_type": ftype,
            "data_type": str(df[col].dtype),
            "unit": unit,
            "formula": "Raw observation",
            "description": desc,
            "dataset": "Manufacturing_Defects",
            "task": "Quality_Defect_Classification",
            "temporal_behavior": "BATCH_RUN",
            "lookback": "Batch execution",
            "available_at_prediction_time": "YES",
            "leakage_status": leakage,
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()),
            "unique_count": int(df[col].nunique()),
            "status": status,
            "removal_reason": reason,
        })

    # Engineered Features
    eng_info = [
        ("cost_per_unit", "ProductionCost, ProductionVolume", "DERIVED_ECONOMIC", "Cost/Unit", "Unit production cost", "ProductionCost / ProductionVolume"),
        ("energy_per_unit_volume", "EnergyConsumption, ProductionVolume", "DERIVED_ENERGY", "kWh/Unit", "Specific energy consumption per unit", "EnergyConsumption / ProductionVolume"),
        ("maintenance_downtime_ratio", "MaintenanceHours, DowntimePercentage", "DERIVED_MAINTENANCE", "Hours/%", "Maintenance response per downtime percentage", "MaintenanceHours / DowntimePercentage"),
        ("supply_chain_risk_index", "DeliveryDelay, StockoutRate", "DERIVED_SUPPLY_CHAIN", "Index", "Compound inbound supply friction factor", "DeliveryDelay * StockoutRate"),
        ("operational_friction_index", "WorkerProductivity, DowntimePercentage", "DERIVED_OPERATIONAL", "Index", "Composite labor-downtime friction index", "(100 - Productivity) * Downtime"),
        ("additive_cost_share", "AdditiveMaterialCost, ProductionCost", "DERIVED_ECONOMIC", "Ratio", "Proportion of total cost in additive material", "AdditiveMaterialCost / ProductionCost"),
        ("energy_quality_factor", "EnergyEfficiency, QualityScore", "DERIVED_EFFICIENCY", "Ratio", "Energy efficiency normalized by quality score", "EnergyEfficiency / QualityScore"),
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
            "dataset": "Manufacturing_Defects",
            "task": "Quality_Defect_Classification",
            "temporal_behavior": "BATCH_RUN",
            "lookback": "Batch execution",
            "available_at_prediction_time": "YES",
            "leakage_status": "SAFE",
            "missing_rate": float(df[col].isna().mean()),
            "variance": float(df[col].var()),
            "unique_count": int(df[col].nunique()),
            "status": "KEEP",
            "removal_reason": "None (valid derived operational metric)",
        })

    feature_dict = pd.DataFrame(records)

    metadata = {
        "dataset_name": "Manufacturing_Defects",
        "total_batches": len(df),
        "total_columns": len(df.columns),
        "engineered_features_count": len(eng_info),
        "target_column": DEFECT_TARGET_COLUMN,
        "defect_count": int(df[DEFECT_TARGET_COLUMN].sum()),
        "defect_rate": float(df[DEFECT_TARGET_COLUMN].mean()),
        "status": "EXTRACTED_AND_AUDITED",
    }

    return df, feature_dict, metadata
