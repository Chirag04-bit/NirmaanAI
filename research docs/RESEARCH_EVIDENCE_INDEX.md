# NirmaanAI — Research Paper Evidence Package Index
## Master Catalog of Publication Artifacts, Figures, Tables, and Data Files

---

### 1. Master Tables (`research docs/tables/`)

| Table # | Table Title | CSV Location | Markdown Location |
| :--- | :--- | :--- | :--- |
| **Table 1** | Master Dataset Characteristics & Task Taxonomy | `tables/dataset_tables/table1_dataset_characteristics.csv` | `table1_dataset_characteristics.md` |
| **Table 2** | Preprocessing, Feature Selection & Leakage Controls | `tables/dataset_tables/table2_preprocessing_and_leakage.csv` | `table2_preprocessing_and_leakage.md` |
| **Table 3** | Domain Feature Engineering Summary | `tables/dataset_tables/table3_feature_engineering_summary.csv` | `table3_feature_engineering_summary.md` |
| **Table 4** | Locked Baseline Benchmark Model Configurations | `tables/model_tables/table4_baseline_model_configurations.csv` | `table4_baseline_model_configurations.md` |
| **Table 5** | Final Tuned Champion Model Hyperparameters | `tables/model_tables/table5_tuned_model_configurations.csv` | `table5_tuned_model_configurations.md` |
| **Table 6** | Model Validation Results & Champion Selection | `tables/model_tables/table6_baseline_vs_tuned_validation.csv` | `table6_baseline_vs_tuned_validation.md` |
| **Table 7** | Single Blind Holdout Test Evaluation Results | `tables/model_tables/table7_baseline_vs_tuned_test.csv` | `table7_baseline_vs_tuned_test.md` |
| **Table 8** | Imbalanced Holdout Classification Metrics | `tables/metric_tables/table8_classification_metrics.csv` | `table8_classification_metrics.md` |
| **Table 9** | Holdout Regression Error Metrics | `tables/metric_tables/table9_regression_metrics.csv` | `table9_regression_metrics.md` |
| **Table 10** | Pre-Registered Anomaly Degradation Contrast (ADCR/MASI) | `tables/metric_tables/table10_anomaly_metrics.csv` | `table10_anomaly_metrics.md` |
| **Table 11** | Global SHAP Explainability Top Features | `tables/statistical_tables/table11_explainability_top_features.csv` | `table11_explainability_top_features.md` |
| **Table 12** | End-to-End System-Level Subsystem Metrics | `tables/system_tables/table12_nirmaanai_system_metrics.csv` | `table12_nirmaanai_system_metrics.md` |
| **Table 13** | Computational Subsampling Efficiency & Speedups | `tables/statistical_tables/table13_computational_efficiency_subsets.csv` | `table13_computational_efficiency_subsets.md` |
| **Table 14** | Methodological Limitations & Epistemic Audit | `tables/statistical_tables/table14_limitations_and_epistemic_status.csv` | `table14_limitations_and_epistemic_status.md` |

---

### 2. Publication Figures (`research docs/figures/`)

- **Dataset Distributions** (`figures/dataset/`):
  - `classification_class_distributions.png`: 5-panel training set class imbalance profiles.
  - `regression_target_distributions.png`: 3-panel histograms and boxplots for continuous targets.
  - `dataset_size_comparison.png`: Training partition row volume comparisons (log scale).
- **Preprocessing** (`figures/preprocessing/`):
  - `tuning_subset_reduction.png`: Full training rows vs tuning subset rows and retention ratios.
- **Classification** (`figures/classification/`):
  - `<task>_confusion_matrix.png`: Raw test set confusion matrices (5 tasks).
  - `<task>_normalized_confusion_matrix.png`: Per-class recall normalized matrices (5 tasks).
  - `<task>_roc_curve.png`: Receiver Operating Characteristic curves (5 tasks).
  - `<task>_pr_curve.png`: Precision-Recall curves against prevalence floors (5 tasks).
- **Regression** (`figures/regression/`):
  - `<task>_actual_vs_predicted.png`: Actual vs predicted scatter plots (3 tasks).
  - `<task>_residual_distribution.png`: Error residual distribution histograms (3 tasks).
  - `<task>_residual_vs_predicted.png`: Residuals vs predicted targets (3 tasks).
- **Temporal Telemetry** (`figures/temporal/`):
  - `electricity_actual_vs_forecast.png`: 7-day out-of-sample continuous power demand forecast.
  - `cmapss_engine_degradation_trajectories.png`: Unseen holdout engines run-to-failure curves.
- **Anomaly Detection** (`figures/anomaly/`):
  - `textile_score_distribution.png`: PCA anomaly score contrast between nominal and degradation.
  - `synthetic_factory_score_distribution.png`: Isolation Forest anomaly separation on pre-cutoff telemetry.
  - `synthetic_factory_m2_timeline.png`: Machine M2 health collapse and anomaly timeline (Days 17–23).
- **Explainability** (`figures/explainability/`):
  - `ai4i_shap_global_importance.png`: Top 10 global SHAP features for AI4I machine failure.
  - `cmapss_shap_global_importance.png`: Top 10 global SHAP degradation features for turbofan RUL.
- **Tuning & Comparison** (`figures/tuning/`, `figures/model_comparison/`):
  - `tuning_configurations_evaluated.png`: Bounded configurations evaluated per task (Total = 267).
  - `retained_vs_improved_models.png`: Scientific restraint distribution (5 accepted vs 5 retained).
  - `validation_improvement_bar_chart.png`: Validation relative improvement per task.
  - `test_improvement_bar_chart.png`: Single blind test holdout delta per task.
  - `model_performance_master_figure.png`: Master 3-panel publication overview figure.
- **System Architecture** (`figures/system/`):
  - `nirmaanai_e2e_pipeline_diagram.png`: Multimodal intelligence system architecture.
  - `factory_health_breakdown.png`: Phase 13 validated health scoring and machine status.
  - `financial_impact_analysis.png`: Phase 14 validated realized loss vs projected opportunity.
  - `m2_integrated_case_study.png`: Multi-stage causal/evidence timeline for Machine M2 case study.

---

### 3. Numerical Data & Curve Exports (`research docs/data/`)
- `curve_data/`: CSV points for all ROC and Precision-Recall curves.
- `confusion_matrices/`: JSON representations of raw and normalized confusion matrices.
- `dataset_statistics/`: Tuning subset reduction metrics and moment statistics.

---

### 4. Epistemic Status & Governance
- `metadata/epistemic_status_audit.csv`: Authoritative provenance reconciliation of all datasets and claims.
- `metadata/research_generation_manifest.json`: Cryptographic MD5 checksums, Git commit hash, and environment metadata.
- `FIGURE_CAPTIONS.md`: Full captions and caveats formatted for direct paper inclusion.
- `RESULTS_NUMBERS_FOR_PAPER.md`: Section 5 experimental narrative with exact validated figures.
- `REPRODUCIBILITY.md`: End-to-end reproduction commands.
