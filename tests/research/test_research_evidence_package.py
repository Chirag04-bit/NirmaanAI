"""
Tests for NirmaanAI Research Paper Evidence Package.
Verifies structure, integrity, immutability, metric consistency,
figure generation, tables, and reproducibility metadata.
"""

import json
import os
import subprocess
import hashlib
import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESEARCH_DOCS = os.path.join(PROJECT_ROOT, "research docs")


# =====================================================================
# 1. Directory Structure Tests
# =====================================================================

def test_research_docs_root_exists():
    assert os.path.isdir(RESEARCH_DOCS), "research docs directory must exist"


def test_required_subdirectories_exist():
    required_dirs = [
        "figures/dataset",
        "figures/preprocessing",
        "figures/model_comparison",
        "figures/classification",
        "figures/regression",
        "figures/anomaly",
        "figures/explainability",
        "figures/temporal",
        "figures/system",
        "figures/tuning",
        "tables/dataset_tables",
        "tables/model_tables",
        "tables/metric_tables",
        "tables/statistical_tables",
        "tables/system_tables",
        "data/dataset_statistics",
        "data/model_metrics",
        "data/predictions",
        "data/confusion_matrices",
        "data/curve_data",
        "data/explainability",
        "data/tuning",
        "data/system_metrics",
        "statistics",
        "metadata",
        "scripts",
    ]
    for rel_path in required_dirs:
        full_path = os.path.join(RESEARCH_DOCS, *rel_path.split("/"))
        assert os.path.isdir(full_path), f"Required directory missing: {rel_path}"


# =====================================================================
# 2. Master Narrative and Documentation Files Tests
# =====================================================================

def test_narrative_and_index_files_exist():
    required_files = [
        "RESEARCH_EVIDENCE_INDEX.md",
        "REPRODUCIBILITY.md",
        "FIGURE_CAPTIONS.md",
        "RESULTS_NUMBERS_FOR_PAPER.md",
    ]
    for filename in required_files:
        filepath = os.path.join(RESEARCH_DOCS, filename)
        assert os.path.isfile(filepath), f"Required file missing: {filename}"
        assert os.path.getsize(filepath) > 100, f"File appears too small: {filename}"


# =====================================================================
# 3. Master Tables (Tables 1-14 + Key Summary Tables)
# =====================================================================

@pytest.mark.parametrize("name,subfolder", [
    ("table1_dataset_characteristics", "dataset_tables"),
    ("table2_preprocessing_and_leakage", "dataset_tables"),
    ("table3_feature_engineering_summary", "dataset_tables"),
    ("table4_baseline_model_configurations", "model_tables"),
    ("table5_tuned_model_configurations", "model_tables"),
    ("table6_baseline_vs_tuned_validation", "model_tables"),
    ("table7_baseline_vs_tuned_test", "model_tables"),
    ("table8_classification_metrics", "metric_tables"),
    ("table9_regression_metrics", "metric_tables"),
    ("table10_anomaly_metrics", "metric_tables"),
    ("table11_explainability_top_features", "statistical_tables"),
    ("table12_nirmaanai_system_metrics", "system_tables"),
    ("table13_computational_efficiency_subsets", "statistical_tables"),
    ("table14_limitations_and_epistemic_status", "statistical_tables"),
])
def test_master_paper_tables_exist_and_readable(name, subfolder):
    csv_path = os.path.join(RESEARCH_DOCS, "tables", subfolder, f"{name}.csv")
    md_path = os.path.join(RESEARCH_DOCS, "tables", subfolder, f"{name}.md")

    assert os.path.isfile(csv_path), f"CSV table missing: {csv_path}"
    assert os.path.isfile(md_path), f"MD table missing: {md_path}"

    df = pd.read_csv(csv_path)
    assert len(df) > 0, f"Table {name}.csv is empty"


def test_required_auxiliary_tables_exist():
    aux_files = [
        ("dataset_summary.csv", os.path.join(RESEARCH_DOCS, "tables", "dataset_tables", "dataset_summary.csv")),
        ("dataset_summary.md", os.path.join(RESEARCH_DOCS, "tables", "dataset_tables", "dataset_summary.md")),
        ("dataset_summary.json", os.path.join(RESEARCH_DOCS, "tables", "dataset_tables", "dataset_summary.json")),
        ("baseline_vs_tuned.csv", os.path.join(RESEARCH_DOCS, "tables", "model_tables", "baseline_vs_tuned.csv")),
        ("baseline_vs_tuned.md", os.path.join(RESEARCH_DOCS, "tables", "model_tables", "baseline_vs_tuned.md")),
        ("final_model_matrix.csv", os.path.join(RESEARCH_DOCS, "tables", "model_tables", "final_model_matrix.csv")),
        ("final_model_matrix.md", os.path.join(RESEARCH_DOCS, "tables", "model_tables", "final_model_matrix.md")),
        ("regression_metrics.csv", os.path.join(RESEARCH_DOCS, "tables", "metric_tables", "regression_metrics.csv")),
        ("limitations.csv", os.path.join(RESEARCH_DOCS, "tables", "statistical_tables", "limitations.csv")),
        ("tuning_subset_statistics.csv", os.path.join(RESEARCH_DOCS, "data", "dataset_statistics", "tuning_subset_statistics.csv")),
    ]
    for name, path in aux_files:
        assert os.path.isfile(path), f"Auxiliary file missing: {path}"
        assert os.path.getsize(path) > 10, f"Auxiliary file empty: {path}"


# =====================================================================
# 4. Metric Consistency Tests
# =====================================================================

def test_metric_consistency_with_tuned_artifacts():
    summary_path = os.path.join(PROJECT_ROOT, "models", "tuned", "global_tuning_summary.json")
    with open(summary_path, "r") as f:
        global_summary = json.load(f)

    bvt_csv = os.path.join(RESEARCH_DOCS, "tables", "model_tables", "baseline_vs_tuned.csv")
    bvt_df = pd.read_csv(bvt_csv)

    for task_key, task_data in global_summary["tasks"].items():
        row = bvt_df[bvt_df["Task Identifier"] == task_key]
        assert len(row) == 1, f"Expected 1 row for {task_key} in baseline_vs_tuned.csv"
        row = row.iloc[0]

        expected_base_val = task_data["baseline_val_score"]
        reported_base_val = float(row["Baseline Val"])
        assert abs(expected_base_val - reported_base_val) < 1e-4

        expected_tuned_val = task_data["tuned_val_score"]
        reported_tuned_val = float(row["Tuned Val"])
        assert abs(expected_tuned_val - reported_tuned_val) < 1e-4

        expected_val_abs = task_data["val_abs_improvement"]
        reported_val_abs = float(row["Val Abs Imprv"])
        assert abs(expected_val_abs - reported_val_abs) < 1e-4


def test_final_model_matrix_matches_approved_selections():
    fmm_csv = os.path.join(RESEARCH_DOCS, "tables", "model_tables", "final_model_matrix.csv")
    fmm_df = pd.read_csv(fmm_csv)
    
    expected_models = {
        "ai4i": "Random_Forest_Natural",
        "cmapss": "XGB_n150_d6_lr0.03",
        "secom": "XGB_d4_lr0.08_col0.5_spw10_Nat",
        "electricity": "XGB_n200_d8_lr0.03_mcw1",
        "industrial_iot_failure": "Logistic_Regression_Sampled",
        "industrial_iot_rul": "XGBoost_Regressor",
        "manufacturing_production": "Random_Forest_Weighted",
        "manufacturing_defects": "RF_n100_dNone_l4",
        "textile": "PCA_comp6",
        "synthetic_factory": "Isolation_Forest",
    }

    for task, model_name in expected_models.items():
        match = fmm_df[fmm_df["Task"] == task]
        assert len(match) == 1, f"Missing task {task} in final_model_matrix"
        assert match.iloc[0]["Final Selected Model"] == model_name, f"Mismatch for {task}: {match.iloc[0]['Final Selected Model']} != {model_name}"


# =====================================================================
# 5. Figure Existence and Quality Tests
# =====================================================================

def test_all_publication_figures_exist_and_non_empty():
    required_figures = [
        # Dataset
        "figures/dataset/classification_class_distributions.png",
        "figures/dataset/regression_target_distributions.png",
        "figures/dataset/dataset_size_comparison.png",
        # Preprocessing
        "figures/preprocessing/tuning_subset_reduction.png",
        # Model comparison
        "figures/model_comparison/model_performance_master_figure.png",
        # Classification (4 per task * 5 tasks = 20)
        "figures/classification/ai4i_confusion_matrix.png",
        "figures/classification/ai4i_normalized_confusion_matrix.png",
        "figures/classification/ai4i_roc_curve.png",
        "figures/classification/ai4i_pr_curve.png",
        "figures/classification/secom_confusion_matrix.png",
        "figures/classification/secom_normalized_confusion_matrix.png",
        "figures/classification/secom_roc_curve.png",
        "figures/classification/secom_pr_curve.png",
        "figures/classification/industrial_iot_failure_confusion_matrix.png",
        "figures/classification/industrial_iot_failure_normalized_confusion_matrix.png",
        "figures/classification/industrial_iot_failure_roc_curve.png",
        "figures/classification/industrial_iot_failure_pr_curve.png",
        "figures/classification/manufacturing_production_confusion_matrix.png",
        "figures/classification/manufacturing_production_normalized_confusion_matrix.png",
        "figures/classification/manufacturing_production_roc_curve.png",
        "figures/classification/manufacturing_production_pr_curve.png",
        "figures/classification/manufacturing_defects_confusion_matrix.png",
        "figures/classification/manufacturing_defects_normalized_confusion_matrix.png",
        "figures/classification/manufacturing_defects_roc_curve.png",
        "figures/classification/manufacturing_defects_pr_curve.png",
        # Regression (4 per task * 3 tasks = 12)
        "figures/regression/cmapss_actual_vs_predicted.png",
        "figures/regression/cmapss_residual_distribution.png",
        "figures/regression/cmapss_residual_vs_predicted.png",
        "figures/regression/cmapss_error_histogram.png",
        "figures/regression/industrial_iot_rul_actual_vs_predicted.png",
        "figures/regression/industrial_iot_rul_residual_distribution.png",
        "figures/regression/industrial_iot_rul_residual_vs_predicted.png",
        "figures/regression/industrial_iot_rul_error_histogram.png",
        "figures/regression/electricity_actual_vs_predicted.png",
        "figures/regression/electricity_residual_distribution.png",
        "figures/regression/electricity_residual_vs_predicted.png",
        "figures/regression/electricity_error_histogram.png",
        # Anomaly
        "figures/anomaly/textile_score_distribution.png",
        "figures/anomaly/synthetic_factory_score_distribution.png",
        "figures/anomaly/synthetic_factory_m2_timeline.png",
        # Temporal
        "figures/temporal/electricity_actual_vs_forecast.png",
        "figures/temporal/cmapss_engine_degradation_trajectories.png",
        # Explainability
        "figures/explainability/ai4i_shap_global_importance.png",
        "figures/explainability/cmapss_shap_global_importance.png",
        # System
        "figures/system/nirmaanai_e2e_pipeline_diagram.png",
        "figures/system/factory_health_breakdown.png",
        "figures/system/financial_impact_analysis.png",
        "figures/system/m2_integrated_case_study.png",
        # Tuning
        "figures/tuning/validation_improvement_bar_chart.png",
        "figures/tuning/test_improvement_bar_chart.png",
        "figures/tuning/tuning_configurations_evaluated.png",
        "figures/tuning/retained_vs_improved_models.png",
    ]

    assert len(required_figures) == 52, f"Expected 52 figures, got {len(required_figures)}"

    for rel_path in required_figures:
        full_path = os.path.join(RESEARCH_DOCS, *rel_path.split("/"))
        assert os.path.isfile(full_path), f"Figure missing: {rel_path}"
        file_size = os.path.getsize(full_path)
        assert file_size > 5000, f"Figure too small ({file_size} bytes): {rel_path}"


# =====================================================================
# 6. Epistemic Status and Manifest Tests
# =====================================================================

def test_epistemic_status_audit_validity():
    audit_path = os.path.join(RESEARCH_DOCS, "metadata", "epistemic_status_audit.csv")
    assert os.path.isfile(audit_path), "epistemic_status_audit.csv missing"
    df = pd.read_csv(audit_path)
    assert len(df) >= 10, "Epistemic status audit should cover all key components"

    valid_statuses = {
        "OBSERVED",
        "DERIVED",
        "MODEL_OUTPUT",
        "CONTROLLED_SYNTHETIC",
        "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH",
        "PROJECTED",
        "NOT_PROJECTABLE",
        "UNKNOWN",
        "REAL_PHYSICAL_SIMULATOR",
        "REAL_SEMICONDUCTOR_INLINE_SENSORS",
        "HIGH_FIDELITY_PHYSICS_SIMULATION",
        "REAL_INDUSTRIAL_TELEMETRY",
        "CONTROLLED_INDUSTRIAL_SIMULATOR",
        "PROSPECTIVE_DISPATCH_RECORD",
        "REAL_MANUFACTURING_METRICS",
        "REAL_WORLD_OBSERVATIONAL",
    }
    for status in df["Epistemic Status"]:
        for part in status.split("/"):
            part = part.strip()
            assert part in valid_statuses, f"Invalid epistemic status: {part}"


def test_research_manifest_validity():
    manifest_path = os.path.join(RESEARCH_DOCS, "metadata", "research_generation_manifest.json")
    assert os.path.isfile(manifest_path), "research_generation_manifest.json missing"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert "generated_at" in manifest
    assert "git" in manifest
    assert "governance_and_integrity" in manifest
    assert "research_evidence_counts" in manifest
    assert manifest["research_evidence_counts"]["total_figures"] == 52


# =====================================================================
# 7. Absolute Safety & Immutability Tests
# =====================================================================

def test_operational_losses_checksum_unchanged():
    csv_path = os.path.join(PROJECT_ROOT, "data", "synthetic", "auto_components", "operational_losses.csv")
    with open(csv_path, "rb") as f:
        h = hashlib.md5(f.read()).hexdigest().upper()
    assert h == "34B12582B32D81E3121429C55EBF74E8", f"Checksum mismatch: {h}"


def test_immutable_directories_unchanged_in_git():
    cmd = ["git", "status", "--porcelain", "models/benchmarks", "models/tuned", "models/processed"]
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    assert res.returncode == 0
    assert res.stdout.strip() == "", f"Immutable model directories modified in git:\n{res.stdout}"
