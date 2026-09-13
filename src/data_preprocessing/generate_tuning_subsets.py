"""
NirmaanAI — Tuning Subsets Generation Script
===========================================
Generates deterministic computational tuning subsets for high-volume datasets
and compiles representativeness audits and metadata.
"""

import os
import json
from datetime import datetime, timezone
import pandas as pd

from src.data_preprocessing.tuning_subsample import (
    deterministic_stratified_classification_sample,
    deterministic_distribution_aware_regression_sample,
    deterministic_chronological_window_sample,
    deterministic_temporal_stride_sample,
    compute_representativeness_audit,
    calculate_file_md5,
)

BASE_DIR = r"C:\NIRMAAN AI"
OUTPUT_BASE = os.path.join(BASE_DIR, "models", "tuning_subsets")


def generate_industrial_iot_failure_subset():
    task_name = "industrial_iot_failure"
    source_path = os.path.join(BASE_DIR, "models", "processed", "industrial_iot", "failure", "train.parquet")
    output_dir = os.path.join(OUTPUT_BASE, task_name)
    os.makedirs(output_dir, exist_ok=True)
    out_parquet = os.path.join(output_dir, "train_subsample.parquet")

    full_df = pd.read_parquet(source_path)
    # Target size: 105,000 rows (30.0% retention)
    subset_df = deterministic_stratified_classification_sample(
        df=full_df,
        target_col="Failure_Within_7_Days",
        stratify_cols=["Machine_Type_encoded"],
        target_rows=105000,
        random_state=42
    )

    subset_df.to_parquet(out_parquet, index=False)

    audit = compute_representativeness_audit(
        full_df=full_df,
        subset_df=subset_df,
        target_col="Failure_Within_7_Days",
        cat_cols=["Machine_Type_encoded"]
    )
    with open(os.path.join(output_dir, "representativeness_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    meta = {
        "dataset_name": "industrial_iot_failure",
        "dataset_version": "1.0.0",
        "source_rows": len(full_df),
        "source_partition": "train.parquet",
        "subset_rows": len(subset_df),
        "retention_ratio": round(len(subset_df) / len(full_df), 4),
        "sampling_method": "deterministic_stratified_joint_class_and_machine_type",
        "sampling_seed": 42,
        "target_column": "Failure_Within_7_Days",
        "class_distribution_before": audit["target_distribution"]["full_proportions"],
        "class_distribution_after": audit["target_distribution"]["subset_proportions"],
        "categorical_distribution_audit": audit["categorical_distributions"],
        "numerical_distribution_audit": {
            k: {
                "full_mean": v["full_mean"],
                "subset_mean": v["subset_mean"],
                "mean_abs_diff": v["mean_abs_diff"],
                "ks_statistic": v["ks_statistic"],
                "ks_p_value": v["ks_p_value"]
            } for k, v in list(audit["numerical_moments"].items())[:5]
        },
        "temporal_constraints": "None (Cross-sectional fleet snapshot; single observation per machine)",
        "scenario_constraints": "None",
        "excluded_columns": ["Machine_ID", "Remaining_Useful_Life_days"],
        "leakage_controls": "Strict isolation: Machine_ID dropped; cross-target RUL quarantined; sampled strictly from training partition only.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "post-phase-25-subsample-v1",
        "source_checksum": calculate_file_md5(source_path),
        "subset_checksum": calculate_file_md5(out_parquet),
        "epistemic_status": "CONTROLLED_COMPUTATIONAL_SUBSET"
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {task_name}: {len(subset_df)} rows ({meta['retention_ratio']*100:.1f}%)")


def generate_industrial_iot_rul_subset():
    task_name = "industrial_iot_rul"
    source_path = os.path.join(BASE_DIR, "models", "processed", "industrial_iot", "rul", "train.parquet")
    output_dir = os.path.join(OUTPUT_BASE, task_name)
    os.makedirs(output_dir, exist_ok=True)
    out_parquet = os.path.join(output_dir, "train_subsample.parquet")

    full_df = pd.read_parquet(source_path)
    # Target size: 105,000 rows (30.0% retention)
    subset_df = deterministic_distribution_aware_regression_sample(
        df=full_df,
        target_col="Remaining_Useful_Life_days",
        stratify_cols=["Machine_Type_encoded"],
        n_bins=10,
        target_rows=105000,
        random_state=42
    )

    subset_df.to_parquet(out_parquet, index=False)

    audit = compute_representativeness_audit(
        full_df=full_df,
        subset_df=subset_df,
        target_col="Remaining_Useful_Life_days",
        cat_cols=["Machine_Type_encoded"]
    )
    with open(os.path.join(output_dir, "representativeness_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    meta = {
        "dataset_name": "industrial_iot_rul",
        "dataset_version": "1.0.0",
        "source_rows": len(full_df),
        "source_partition": "train.parquet",
        "subset_rows": len(subset_df),
        "retention_ratio": round(len(subset_df) / len(full_df), 4),
        "sampling_method": "deterministic_distribution_aware_decile_binned_regression",
        "sampling_seed": 42,
        "target_column": "Remaining_Useful_Life_days",
        "class_distribution_before": audit["target_distribution"],
        "class_distribution_after": audit["target_distribution"],
        "categorical_distribution_audit": audit["categorical_distributions"],
        "numerical_distribution_audit": {
            k: {
                "full_mean": v["full_mean"],
                "subset_mean": v["subset_mean"],
                "mean_abs_diff": v["mean_abs_diff"],
                "ks_statistic": v["ks_statistic"],
                "ks_p_value": v["ks_p_value"]
            } for k, v in list(audit["numerical_moments"].items())[:5]
        },
        "temporal_constraints": "None (Cross-sectional fleet snapshot; exactly one record per Machine_ID; zero longitudinal sequence)",
        "scenario_constraints": "None",
        "excluded_columns": ["Machine_ID", "Failure_Within_7_Days"],
        "leakage_controls": "Strict isolation: Machine_ID dropped; cross-target Failure_Within_7_Days quarantined; sampled strictly from training partition only.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "post-phase-25-subsample-v1",
        "source_checksum": calculate_file_md5(source_path),
        "subset_checksum": calculate_file_md5(out_parquet),
        "epistemic_status": "CONTROLLED_COMPUTATIONAL_SUBSET"
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {task_name}: {len(subset_df)} rows ({meta['retention_ratio']*100:.1f}%)")


def generate_electricity_subset():
    task_name = "electricity"
    source_path = os.path.join(BASE_DIR, "models", "processed", "electricity", "train.parquet")
    output_dir = os.path.join(OUTPUT_BASE, task_name)
    os.makedirs(output_dir, exist_ok=True)
    out_parquet = os.path.join(output_dir, "train_subsample.parquet")

    full_df = pd.read_parquet(source_path)
    # Contiguous chronological window: last 50% of the training partition
    subset_df = deterministic_chronological_window_sample(
        df=full_df,
        timestamp_col="timestamp",
        target_fraction=0.5
    )

    subset_df.to_parquet(out_parquet, index=False)

    audit = compute_representativeness_audit(
        full_df=full_df,
        subset_df=subset_df,
        target_col="power_kw"
    )
    with open(os.path.join(output_dir, "representativeness_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    meta = {
        "dataset_name": "electricity",
        "dataset_version": "1.0.0",
        "source_rows": len(full_df),
        "source_partition": "train.parquet",
        "subset_rows": len(subset_df),
        "retention_ratio": round(len(subset_df) / len(full_df), 4),
        "sampling_method": "deterministic_contiguous_chronological_window",
        "sampling_seed": 42,
        "target_column": "power_kw",
        "class_distribution_before": audit["target_distribution"],
        "class_distribution_after": audit["target_distribution"],
        "categorical_distribution_audit": {},
        "numerical_distribution_audit": {
            k: {
                "full_mean": v["full_mean"],
                "subset_mean": v["subset_mean"],
                "mean_abs_diff": v["mean_abs_diff"],
                "ks_statistic": v["ks_statistic"],
                "ks_p_value": v["ks_p_value"]
            } for k, v in list(audit["numerical_moments"].items())[:5]
        },
        "temporal_constraints": "Strict chronological continuity preserved. Zero random shuffling. Causal lags intact.",
        "scenario_constraints": "None",
        "excluded_columns": [],
        "leakage_controls": "Chronological windowing strictly from training timeline. Future validation and test partitions remain completely untouched.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "post-phase-25-subsample-v1",
        "source_checksum": calculate_file_md5(source_path),
        "subset_checksum": calculate_file_md5(out_parquet),
        "epistemic_status": "CONTROLLED_COMPUTATIONAL_SUBSET"
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {task_name}: {len(subset_df)} rows ({meta['retention_ratio']*100:.1f}%)")


def generate_textile_subset():
    task_name = "textile"
    source_path = os.path.join(BASE_DIR, "models", "processed", "textile", "train.parquet")
    output_dir = os.path.join(OUTPUT_BASE, task_name)
    os.makedirs(output_dir, exist_ok=True)
    out_parquet = os.path.join(output_dir, "train_subsample.parquet")

    full_df = pd.read_parquet(source_path)
    # Stride of 2 across machines preserving multi-loom balance and temporal ordering
    subset_df = deterministic_temporal_stride_sample(
        df=full_df,
        stride=2,
        group_col="machine_id",
        timestamp_col="timestamp"
    )

    subset_df.to_parquet(out_parquet, index=False)

    audit = compute_representativeness_audit(
        full_df=full_df,
        subset_df=subset_df,
        target_col=None,
        cat_cols=["machine_id"]
    )
    with open(os.path.join(output_dir, "representativeness_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    meta = {
        "dataset_name": "textile",
        "dataset_version": "1.0.0",
        "source_rows": len(full_df),
        "source_partition": "train.parquet",
        "subset_rows": len(subset_df),
        "retention_ratio": round(len(subset_df) / len(full_df), 4),
        "sampling_method": "deterministic_synchronized_temporal_stride",
        "sampling_seed": 42,
        "target_column": None,
        "class_distribution_before": {},
        "class_distribution_after": {},
        "categorical_distribution_audit": audit["categorical_distributions"],
        "numerical_distribution_audit": {
            k: {
                "full_mean": v["full_mean"],
                "subset_mean": v["subset_mean"],
                "mean_abs_diff": v["mean_abs_diff"],
                "ks_statistic": v["ks_statistic"],
                "ks_p_value": v["ks_p_value"]
            } for k, v in list(audit["numerical_moments"].items())[:5]
        },
        "temporal_constraints": "Strict chronological alignment preserved per loom. Zero cross-time shuffling.",
        "scenario_constraints": "Nominal loom operating manifold preserved across all machine IDs.",
        "excluded_columns": [],
        "leakage_controls": "Sampled exclusively from nominal training partition. Validation and test degradation intervals remain untouched.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "post-phase-25-subsample-v1",
        "source_checksum": calculate_file_md5(source_path),
        "subset_checksum": calculate_file_md5(out_parquet),
        "epistemic_status": "CONTROLLED_COMPUTATIONAL_SUBSET"
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {task_name}: {len(subset_df)} rows ({meta['retention_ratio']*100:.1f}%)")


def generate_synthetic_factory_subset():
    task_name = "synthetic_factory"
    source_path = os.path.join(BASE_DIR, "models", "processed", "synthetic_factory", "train.parquet")
    output_dir = os.path.join(OUTPUT_BASE, task_name)
    os.makedirs(output_dir, exist_ok=True)
    out_parquet = os.path.join(output_dir, "train_subsample.parquet")

    full_df = pd.read_parquet(source_path)
    # Stride of 2 across machines preserving synchronized M1-M5 station telemetry
    subset_df = deterministic_temporal_stride_sample(
        df=full_df,
        stride=2,
        group_col="machine_id",
        timestamp_col="timestamp"
    )

    subset_df.to_parquet(out_parquet, index=False)

    audit = compute_representativeness_audit(
        full_df=full_df,
        subset_df=subset_df,
        target_col=None,
        cat_cols=["machine_id"]
    )
    with open(os.path.join(output_dir, "representativeness_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    meta = {
        "dataset_name": "synthetic_factory",
        "dataset_version": "1.0.0",
        "source_rows": len(full_df),
        "source_partition": "train.parquet",
        "subset_rows": len(subset_df),
        "retention_ratio": round(len(subset_df) / len(full_df), 4),
        "sampling_method": "deterministic_synchronized_multi_station_temporal_stride",
        "sampling_seed": 42,
        "target_column": None,
        "class_distribution_before": {},
        "class_distribution_after": {},
        "categorical_distribution_audit": audit["categorical_distributions"],
        "numerical_distribution_audit": {
            k: {
                "full_mean": v["full_mean"],
                "subset_mean": v["subset_mean"],
                "mean_abs_diff": v["mean_abs_diff"],
                "ks_statistic": v["ks_statistic"],
                "ks_p_value": v["ks_p_value"]
            } for k, v in list(audit["numerical_moments"].items())[:5]
        },
        "temporal_constraints": "Synchronized 10-minute cadence preserved across M1-M5 stations up to training cutoff 2026-01-15.",
        "scenario_constraints": "M2 degradation event occurs downstream in Days 18-21 (validation/retrospective holdout). Training baseline represents pure nominal factory operating envelope.",
        "excluded_columns": [],
        "leakage_controls": "Sampled exclusively from pre-cutoff training partition. MAINT_0003 and Days 18-21 scenario rows remain strictly outside prospective training.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "post-phase-25-subsample-v1",
        "source_checksum": calculate_file_md5(source_path),
        "subset_checksum": calculate_file_md5(out_parquet),
        "epistemic_status": "CONTROLLED_COMPUTATIONAL_SUBSET"
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {task_name}: {len(subset_df)} rows ({meta['retention_ratio']*100:.1f}%)")


def generate_manifest():
    manifest_path = os.path.join(OUTPUT_BASE, "tuning_subsets_manifest.json")
    manifest = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": "NirmaanAI Data Volume Optimization & Tuning Subsample Registry",
        "epistemic_status": "CONTROLLED_COMPUTATIONAL_SUBSET",
        "canonical_data_policy": "Canonical datasets remain 100% full and immutable in models/processed/. Subsets are computational aids only.",
        "optimized_datasets": {
            "industrial_iot_failure": {
                "status": "SUBSET_GENERATED",
                "full_train_rows": 350000,
                "subset_train_rows": 105000,
                "retention_pct": 30.0,
                "strategy": "Deterministic stratified joint class & machine type sampling",
                "location": "models/tuning_subsets/industrial_iot_failure/"
            },
            "industrial_iot_rul": {
                "status": "SUBSET_GENERATED",
                "full_train_rows": 350000,
                "subset_train_rows": 105000,
                "retention_pct": 30.0,
                "strategy": "Deterministic decile-binned distribution-aware regression sampling",
                "location": "models/tuning_subsets/industrial_iot_rul/"
            },
            "electricity": {
                "status": "SUBSET_GENERATED",
                "full_train_rows": 18279,
                "subset_train_rows": 9140,
                "retention_pct": 50.0,
                "strategy": "Deterministic contiguous chronological window",
                "location": "models/tuning_subsets/electricity/"
            },
            "textile": {
                "status": "SUBSET_GENERATED",
                "full_train_rows": 30240,
                "subset_train_rows": 15120,
                "retention_pct": 50.0,
                "strategy": "Deterministic synchronized temporal stride (stride=2 across looms)",
                "location": "models/tuning_subsets/textile/"
            },
            "synthetic_factory": {
                "status": "SUBSET_GENERATED",
                "full_train_rows": 20415,
                "subset_train_rows": 10210,
                "retention_pct": 50.0,
                "strategy": "Deterministic synchronized multi-station temporal stride (stride=2 across M1-M5)",
                "location": "models/tuning_subsets/synthetic_factory/"
            }
        },
        "non_reduced_datasets": {
            "ai4i": {
                "status": "KEPT_FULL",
                "full_train_rows": 7000,
                "reason": "Dataset size is already compact (7,000 train rows); volume reduction provides negligible gain while risking rare failure mode representation."
            },
            "cmapss": {
                "status": "KEPT_FULL",
                "full_train_rows": 14130,
                "reason": "Engine-grouped physics trajectories must preserve complete run-to-failure curves across all 70 training engines (14,130 rows)."
            },
            "secom": {
                "status": "KEPT_FULL",
                "full_train_rows": 1096,
                "reason": "Wafer defect dataset is already small (1,096 train rows) with only 6.6% defect prevalence."
            },
            "manufacturing_production": {
                "status": "KEPT_FULL",
                "full_train_rows": 700,
                "reason": "Production dispatch log contains only 700 training rows; reduction would severely degrade ranking quality."
            },
            "manufacturing_defects": {
                "status": "KEPT_FULL",
                "full_train_rows": 2268,
                "reason": "Batch quality dataset contains 2,268 training rows; highly compact and fast to train."
            }
        }
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print("Generated manifest at", manifest_path)


if __name__ == "__main__":
    generate_industrial_iot_failure_subset()
    generate_industrial_iot_rul_subset()
    generate_electricity_subset()
    generate_textile_subset()
    generate_synthetic_factory_subset()
    generate_manifest()
