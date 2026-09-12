"""
NirmaanAI Inventory Optimization Pipeline & Training Script
Phase 10: Smart Inventory Intelligence

Executes end-to-end inventory optimization and maintenance coupling evaluation:
1. Loads catalog from inventory_items.csv.
2. Derives daily SKU consumption rates from production_jobs.csv.
3. Computes demand statistics (d_mean, sigma_d).
4. Solves deterministic Operations Research models:
   - Dynamic Safety Stock (Z=1.645 for 95% raw material, Z=2.326 for 99% critical spare)
   - Reorder Point (ROP)
   - Economic Order Quantity (EOQ - Wilson-Harris model)
   - Days of Supply (DoS)
   - Shortage risk classification
5. Evaluates Machine 2 Predictive Maintenance-Spare Coupling:
   - Empirical AI4I decision threshold (0.91)
   - Configured synthetic vibration trigger (3.80 mm/s)
   - Bearing lead time (7 days) physical constraint evaluation
6. Persists artifacts and metadata under models/inventory_intelligence/

RESEARCH INTEGRITY:
- Pure deterministic Operations Research models.
- Clearly distinguishes empirical data, derived synthetic consumption, and simulation parameters.
- Preserves AI4I decision threshold at 0.91 (strict Phase 6 semantics).
- Acknowledges physical 7-day lead-time constraints.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import joblib
import pandas as pd

from src.features.inventory_features import (
    CONFIGURED_BOM_MAP,
    compute_sku_demand_statistics,
    derive_daily_sku_consumption,
    load_inventory_catalog,
)
from src.models.inventory_optimizer import InventoryOptimizer
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


def run_inventory_pipeline() -> Dict[str, Any]:
    """Runs the complete inventory intelligence and OR optimization pipeline."""
    root = get_project_root()
    output_dir = root / "models" / "inventory_intelligence"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Starting Phase 10: Smart Inventory Intelligence Pipeline ---")

    # 1. Load catalog & derive synthetic consumption
    df_catalog = load_inventory_catalog()
    df_daily_consumption = derive_daily_sku_consumption()
    demand_stats = compute_sku_demand_statistics(df_daily_consumption)

    optimizer = InventoryOptimizer(default_annual_working_days=312)

    # 2. Audit each SKU in the catalog
    sku_audit_records: List[Dict[str, Any]] = []

    for _, row in df_catalog.iterrows():
        sku_id = str(row["sku_id"])
        current_stock = float(row["current_stock"])
        unit_cost = float(row["unit_cost"])

        if sku_id in CONFIGURED_BOM_MAP:
            bom_cfg = CONFIGURED_BOM_MAP[sku_id]
        else:
            # Fallback configuration if SKU not in BOM map
            bom_cfg = {
                "category": str(row.get("category", "GENERAL")),
                "lead_time_days": float(row.get("lead_time_days", 5.0)),
                "lead_time_std_days": 1.0,
                "service_level_target": 0.95,
                "order_setup_cost_inr": 1500.0,
                "annual_holding_rate": 0.20
            }

        sku_stats = demand_stats.get(sku_id, {
            "d_mean": 0.0,
            "sigma_d": 0.0,
            "min_daily": 0.0,
            "max_daily": 0.0,
            "days_observed": 0
        })

        audit = optimizer.audit_sku_inventory(
            sku_id=sku_id,
            current_stock=current_stock,
            unit_cost=unit_cost,
            demand_stats=sku_stats,
            bom_config=bom_cfg
        )
        sku_audit_records.append(audit)

    df_summary = pd.DataFrame(sku_audit_records)
    summary_csv_path = output_dir / "sku_optimization_summary.csv"
    df_summary.to_csv(summary_csv_path, index=False)
    logger.info(f"Saved SKU optimization summary table to: {summary_csv_path}")

    # 3. Evaluate Machine 2 Maintenance-Spare Coupling
    # Extract M2 spindle bearing current stock
    bearing_row = df_catalog[df_catalog["sku_id"] == "SKU_SPINDLE_BEARING_M2"]
    bearing_stock = float(bearing_row["current_stock"].iloc[0]) if len(bearing_row) > 0 else 1.0

    # Scenario A: Empirical Failure Alert (Phase 6 threshold = 0.91)
    coupling_empirical_alert = optimizer.evaluate_machine2_maintenance_coupling(
        failure_prob=0.925,
        vibration_mms=2.45,
        sku_spindle_stock=bearing_stock,
        lead_time_days=7.0,
        decision_threshold=0.91,
        synthetic_vibration_trigger=3.80
    )

    # Scenario B: Configured Synthetic Vibration Alert (vib >= 3.80 mm/s)
    coupling_vibration_alert = optimizer.evaluate_machine2_maintenance_coupling(
        failure_prob=0.450,
        vibration_mms=4.15,
        sku_spindle_stock=bearing_stock,
        lead_time_days=7.0,
        decision_threshold=0.91,
        synthetic_vibration_trigger=3.80
    )

    # Scenario C: Normal Operation (No alert)
    coupling_normal = optimizer.evaluate_machine2_maintenance_coupling(
        failure_prob=0.120,
        vibration_mms=1.80,
        sku_spindle_stock=bearing_stock,
        lead_time_days=7.0,
        decision_threshold=0.91,
        synthetic_vibration_trigger=3.80
    )

    # Scenario D: Depleted Warehouse Stock (0.0 bearings)
    coupling_depleted = optimizer.evaluate_machine2_maintenance_coupling(
        failure_prob=0.940,
        vibration_mms=4.20,
        sku_spindle_stock=0.0,
        lead_time_days=7.0,
        decision_threshold=0.91,
        synthetic_vibration_trigger=3.80
    )

    coupling_results = {
        "scenario_a_empirical_alert": coupling_empirical_alert,
        "scenario_b_synthetic_vibration_alert": coupling_vibration_alert,
        "scenario_c_normal_operation": coupling_normal,
        "scenario_d_depleted_stock_alert": coupling_depleted
    }

    # 4. Save Joblib Artifact
    optimizer_bundle = {
        "optimizer": optimizer,
        "sku_summary": df_summary,
        "coupling_results": coupling_results,
        "demand_stats": demand_stats,
        "bom_map": CONFIGURED_BOM_MAP
    }
    joblib_path = output_dir / "inventory_optimizer.joblib"
    joblib.dump(optimizer_bundle, joblib_path)
    logger.info(f"Saved InventoryOptimizer bundle to: {joblib_path}")

    # 5. Build Metadata
    metadata: Dict[str, Any] = {
        "subsystem": "Smart Inventory Intelligence & Operations Research",
        "phase": "Phase 10",
        "methodology": "Deterministic Operations Research & Statistical Inventory Control",
        "data_sources": {
            "inventory_catalog": "DATASET/10_SYNTHETIC_FACTORY/synthetic/inventory_items.csv",
            "production_jobs": {
                "path": "DATASET/10_SYNTHETIC_FACTORY/synthetic/production_jobs.csv",
                "total_jobs_in_dataset": 300,
                "machines": ["M1", "M2", "M3", "M4", "M5"],
                "jobs_per_machine": 60,
                "jobs_on_sku_consuming_machines": 180,
                "sku_consuming_machines": ["M1", "M2", "M3"],
                "md5_checksum": "52db0b6292e4cff0a547b40c0b97d9a4"
            },
            "maintenance_records": {
                "path": "DATASET/10_SYNTHETIC_FACTORY/synthetic/maintenance_records.csv",
                "nature": "CONFIGURED SYNTHETIC SPARE-CONSUMPTION RELATIONSHIP"
            },
            "consumption_derivation": "CONFIGURED SYNTHETIC SIMULATION RELATIONSHIP (Bills of Materials)",
            "empirical_source_data_modified": False
        },
        "simulation_assumptions": {
            "annual_working_days": 312,
            "raw_material_service_level": 0.95,
            "raw_material_z_score": 1.645,
            "critical_spare_service_level": 0.99,
            "critical_spare_z_score": 2.326,
            "holding_cost_rate": "0.15 - 0.22 depending on SKU category",
            "order_setup_costs": "₹800 - ₹3500 depending on SKU vendor logistics"
        },
        "mathematical_core": {
            "safety_stock_formula": "SS = Z * sqrt(L_mean * sigma_d^2 + d_mean^2 * sigma_L^2)",
            "reorder_point_formula": "ROP = (d_mean * L_mean) + SS",
            "economic_order_quantity_formula": "EOQ = sqrt((2 * D * S) / H)",
            "days_of_supply_formula": "DoS = Current_Stock / d_mean"
        },
        "machine2_maintenance_coupling": {
            "bearing_sku": "SKU_SPINDLE_BEARING_M2",
            "empirical_decision_threshold": 0.91,
            "synthetic_vibration_trigger_mms": 3.80,
            "configured_vendor_lead_time_days": 7.0,
            "lead_time_std_days": 2.0,
            "transit_time_caveat": "Emergency procurement does NOT eliminate physical transit lead time.",
            "coupling_scenarios_evaluated": coupling_results
        },
        "sku_inventory_audit_table": sku_audit_records
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Exported Phase 10 inventory metadata to: {metadata_path}")

    return metadata


if __name__ == "__main__":
    run_inventory_pipeline()
