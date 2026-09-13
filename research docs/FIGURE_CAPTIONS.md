# NirmaanAI — Research Paper Figure Captions
## Standardized Publication Captions with Epistemic Provenance and Methodological Caveats

---

### Dataset & Preprocessing Figures

#### Figure 1: Class Imbalance Profiles Across 5 Industrial Classification Tasks
- **File**: `figures/dataset/classification_class_distributions.png`
- **Title**: Training Set Class Distributions across 5 Industrial Classification Disciplines
- **Caption**: Empirical observation counts and class prevalence percentages across training partitions for (A) AI4I 2020 Machine Failure (3.4% failure), (B) UCI SECOM Wafer Defect (6.6% defect), (C) Industrial IoT 2040 7-Day Failure (6.0% failure), (D) Manufacturing Production Bottleneck (22.0% bottleneck), and (E) Manufacturing Defects Quality Control (16.0% defective). Highlights the severe class imbalance inherent to real-world industrial monitoring.
- **Dataset**: AI4I, SECOM, Industrial IoT, Manufacturing Production, Manufacturing Defects
- **Method**: Preprocessed training partition frequency auditing (`random_state=42`).
- **Demonstrates**: Multi-order-of-magnitude class imbalance requiring specialized PR-AUC optimization over naive accuracy.
- **Epistemic Status**: `OBSERVED` / `CONTROLLED_SYNTHETIC`
- **Limitation**: Discrete observation snapshots; operational failure frequencies vary dynamically across maintenance cycles.

#### Figure 2: Target Variable Distributions for Continuous Industrial Regression Tasks
- **File**: `figures/dataset/regression_target_distributions.png`
- **Title**: Target Density and Quantile Distributions across Continuous Regression Tasks
- **Caption**: Histograms and boxplots showing target density and distribution moments for (Left) NASA C-MAPSS FD001 Turbofan RUL with piecewise linear clipping at 125 flight cycles, (Center) Industrial IoT 2040 Fleet RUL across 350,000 training machines (range 0–1133 days), and (Right) UCI Steel Industry Active Power Demand in kW.
- **Dataset**: NASA C-MAPSS, Industrial IoT RUL, UCI Electricity Load
- **Method**: Distribution kernel histograms and boxplot percentile analysis.
- **Demonstrates**: Smooth unimodal power distributions versus plateau-clipped run-to-failure curves.
- **Epistemic Status**: `HIGH_FIDELITY_PHYSICS_SIMULATION` / `CONTROLLED_INDUSTRIAL_SIMULATOR` / `OBSERVED`
- **Limitation**: C-MAPSS RUL plateau at 125 cycles is an engineering convention where thermodynamic sensors cannot detect early micro-wear.

#### Figure 3: Cross-Dataset Training Partition Scales
- **File**: `figures/dataset/dataset_size_comparison.png`
- **Title**: Training Set Volume Comparison Across 10 Industrial Tasks (Logarithmic Scale)
- **Caption**: Comparison of training observation volume ranging from 700 dispatch orders (Manufacturing Production) to 350,000 distinct machines (Industrial IoT 2040), plotted on a logarithmic scale.
- **Dataset**: All 10 NirmaanAI tasks
- **Method**: Partition row count extraction from verified parquet files.
- **Demonstrates**: Broad scale diversity spanning small-sample observational logs to massive simulated machine fleets.
- **Epistemic Status**: `DERIVED`
- **Limitation**: Row volume does not directly equate to informational entropy or feature dimensionality.

#### Figure 4: Data Volume Optimization — Full Training vs Tuning Subsets
- **File**: `figures/preprocessing/tuning_subset_reduction.png`
- **Title**: Deterministic Computational Subsample Volume Reduction and Retention Ratios
- **Caption**: Training volume reduction achieved via deterministic, distribution-aware subsampling for high-volume datasets. Industrial IoT tasks were reduced to 105,000 rows (30.0% retention) using joint class/machine-type stratification, while time-series tasks utilized 50% chronological/stride windows.
- **Dataset**: Industrial IoT Failure, IoT RUL, Electricity, Textile, Synthetic Factory
- **Method**: Deterministic index-based subsampling (`src/data_preprocessing/tuning_subsample.py`).
- **Demonstrates**: Substantial computational reduction (4.12x speedup) with < 0.002% distribution drift.
- **Epistemic Status**: `CONTROLLED_COMPUTATIONAL_SUBSET`
- **Limitation**: Subsamples are computational aids for search only; final champions are retrained on full data.

---

### Classification Performance Figures

#### Figures 5–9: Classification Confusion Matrices (Raw and Normalized)
- **Files**: `figures/classification/<task>_confusion_matrix.png`, `figures/classification/<task>_normalized_confusion_matrix.png`
- **Tasks**: `ai4i`, `secom`, `industrial_iot_failure`, `manufacturing_production`, `manufacturing_defects`
- **Title**: Single Blind Holdout Confusion Matrix under Validation-Frozen Operating Threshold
- **Caption**: Test set confusion matrices displaying true negatives, false positives, false negatives, and true positives, alongside normalized per-class recall matrices. Evaluated at optimal thresholds frozen on validation data.
- **Method**: Out-of-sample confusion matrix computation on untouched `test.parquet`.
- **Demonstrates**: Balanced operational recall (e.g. 50% defect recall in SECOM, 97.1% failure recall in IoT, 99.75% defect recall in Manufacturing Defects).
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: Evaluated on single frozen holdout partitions; operational false positive costs vary per factory.

#### Figures 10–14: Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Curves
- **Files**: `figures/classification/<task>_roc_curve.png`, `figures/classification/<task>_pr_curve.png`
- **Tasks**: `ai4i`, `secom`, `industrial_iot_failure`, `manufacturing_production`, `manufacturing_defects`
- **Title**: Holdout Test ROC and PR Trade-Off Curves with Empirical Baselines
- **Caption**: ROC and PR curves showing ranking discrimination across continuous probability thresholds. PR curves plot against horizontal dashed lines indicating empirical positive class prevalence floors.
- **Method**: Exact probability prediction on holdout test partitions using locked champion weights.
- **Demonstrates**: Substantial precision elevation above prevalence floors across all tasks (e.g. SECOM PR-AUC = 0.1964 vs 0.066 floor).
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: Convex hulls reflect model rank-ordering; operating point must be selected per business utility.

---

### Regression & Time-Series Figures

#### Figures 15–17: Regression Actual vs Predicted and Residual Distributions
- **Files**: `figures/regression/<task>_actual_vs_predicted.png`, `figures/regression/<task>_residual_distribution.png`
- **Tasks**: `cmapss`, `industrial_iot_rul`, `electricity`
- **Title**: Holdout Target Correlation and Error Residual Symmetry
- **Caption**: Actual vs predicted scatter plots with 1:1 perfect agreement reference lines, accompanied by residual distribution histograms and error moment statistics.
- **Method**: Continuous model inference on held-out test engines, machines, and chronological time windows.
- **Demonstrates**: Symmetric zero-centered residual distributions and tight target tracking ($R^2 \ge 0.900$ across all regression tasks).
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: Late-stage degradation variance expands near end-of-life where mechanical noise accelerates.

#### Figure 18: Electricity 7-Day Out-of-Sample Load Forecast
- **File**: `figures/temporal/electricity_actual_vs_forecast.png`
- **Title**: 15-Minute Cadence Industrial Power Demand Forecast vs Actual Telemetry
- **Caption**: Chronological comparison of actual active power consumption versus tuned XGBoost predictions across a representative 7-day holdout horizon (672 intervals), demonstrating tight phase alignment on daily shifts and weekend dips.
- **Dataset**: UCI Electricity Load
- **Method**: Multi-lag causal gradient boosted tree forecasting (`max_depth=8, lr=0.03`).
- **Demonstrates**: 6.27% out-of-sample WAPE tracking without future temporal leakage.
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: Exogenous weather factors and unplanned plant blackouts are not modeled in telemetry lags.

#### Figure 19: NASA C-MAPSS Turbofan Run-to-Failure Trajectories
- **File**: `figures/temporal/cmapss_engine_degradation_trajectories.png`
- **Title**: Predicted vs Actual RUL Across Representative Holdout Turbofan Engines
- **Caption**: Trajectory tracking of actual vs predicted remaining useful life across completely held-out engines (Units 86, 90, 95, 100) from healthy operation through catastrophic HPC failure.
- **Dataset**: NASA C-MAPSS FD001
- **Method**: Tuned XGBoost regression with 95 multi-window rolling degradation features.
- **Demonstrates**: Smooth degradation descent with RMSE of 13.08 cycles on unseen engines.
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: Constant operating conditions (sea level); does not model variable flight mission profiles.

---

### Anomaly & Scenario Figures

#### Figure 20: Textile Loom Telemetry Anomaly Degradation Contrast
- **File**: `figures/anomaly/textile_score_distribution.png`
- **Title**: PCA Subspace Reconstruction Anomaly Score Separation on Loom Telemetry
- **Caption**: Distribution of negative squared reconstruction error between nominal loom operation and controlled degradation validation tail. Pre-registered ADCR achieved 2.0618 on validation and 2.8024 on test (+141.1% gain over baseline).
- **Dataset**: Textile Weaving Loom Telemetry
- **Method**: 6-component PCA subspace orthogonal error modeling.
- **Demonstrates**: High signal-to-noise ratio separation without defect supervision.
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`
- **Limitation**: Assumes normal operations occupy a low-dimensional linear subspace manifold.

#### Figure 21: Machine M2 Controlled Degradation Scenario Timeline
- **File**: `figures/anomaly/synthetic_factory_m2_timeline.png`
- **Title**: Machine M2 Health Collapse and Anomaly Progression Across Decision Boundaries
- **Caption**: Temporal progression of Machine M2 health score (green) and anomaly score (red) across Days 17–23. Highlights the Day 18 degradation onset, the Jan 21 12:00 prospective decision cutoff, and the Jan 22 16:30 retrospective emergency maintenance event.
- **Dataset**: Synthetic Factory Multi-Station Telemetry
- **Method**: Isolation Forest multi-station anomaly tracking combined with Phase 13 Health Index.
- **Demonstrates**: Clear lead-time alerting prior to decision boundary; maintains strict prospective/retrospective quarantine.
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`
- **Limitation**: Controlled benchmark scenario; not empirical factory breakdown data.

---

### Explainability & System Figures

#### Figures 22–23: Global SHAP Feature Importance Attribution
- **Files**: `figures/explainability/ai4i_shap_global_importance.png`, `figures/explainability/cmapss_shap_global_importance.png`
- **Title**: Global SHAP Feature Importance Ranking for Failure and RUL Attribution
- **Caption**: Mean absolute SHAP value rankings indicating feature contribution to model prediction variance. Top AI4I features include tool wear, rotational speed, and power; top C-MAPSS features are multi-window rolling averages of core sensors s4, s9, and s11.
- **Method**: TreeExplainer attribution on validated holdout sets.
- **Demonstrates**: Transparent model attribution aligned with thermodynamic and mechanical principles.
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: SHAP explains model prediction mechanics; it does NOT establish physical causal discovery.

#### Figure 24: NirmaanAI End-to-End System Architecture
- **File**: `figures/system/nirmaanai_e2e_pipeline_diagram.png`
- **Title**: Multimodal Manufacturing Intelligence System Architecture and Information Flow
- **Caption**: Comprehensive architectural schematic tracing data flow from raw telemetry ingestion and preprocessing through predictive/anomaly engines, decision intelligence (RCA, Health, Loss), and human-in-the-loop interaction layers.
- **Method**: System architectural design diagram.
- **Demonstrates**: Modular, governance-enforced integration linking statistical ML to operational shop-floor action.
- **Epistemic Status**: `SYSTEM_ARCHITECTURE`
- **Limitation**: Physical integration requires industrial edge gateways and standard OPC-UA protocols.

#### Figure 25: Phase 14 Operational and Financial Loss Analysis
- **File**: `figures/system/financial_impact_analysis.png`
- **Title**: Breakdown of Realized Downtime Losses, Gross Exposure, and Projected Savings (INR)
- **Caption**: Operational loss quantification across cell machines. Clearly distinguishes Realized Historical Loss (M2: INR 97,382; Plant: INR 1,48,500) from Gross Exposure (INR 1,81,582) and Projected Avoided Losses under optimal maintenance (INR 84,200).
- **Dataset**: Phase 14 Validated Loss Ledger
- **Method**: Activity-based costing model parameterization.
- **Demonstrates**: Actionable monetary translation of machine health and downtime.
- **Epistemic Status**: `DERIVED` / `PROJECTED`
- **Limitation**: Derived estimate based on configured labor/scrap parameters; not audited financial books.

#### Figure 26: Machine M2 Multi-Stage Degradation & Decision Support Timeline
- **File**: `figures/system/m2_integrated_case_study.png`
- **Title**: Multi-Stage Causal/Evidence Timeline for Machine M2 Case Study
- **Caption**: Integrated progression showing vibration surge $\to$ anomaly detection $\to$ cycle degradation $\to$ bottleneck alert $\to$ RCA attribution (MECHANICAL_LOAD) $\to$ health critical (26.88) $\to$ financial exposure (INR 97,382) $\to$ maintenance recommendation.
- **Method**: Cross-phase evidence alignment on controlled synthetic factory scenario.
- **Demonstrates**: Seamless cross-module synergy from sensory anomaly to dispatch recommendation.
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`
- **Limitation**: Evidence-aligned synthetic case study; does not constitute proven physical causality.

#### Figure 27: Master Multi-Task Model Performance Overview
- **File**: `figures/model_comparison/model_performance_master_figure.png`
- **Title**: Master Multi-Task Model Performance Overview Across 10 Industrial Disciplines
- **Caption**: Publication 3-panel comparison: (Panel A) Classification PR-AUC and ROC-AUC test performance, (Panel B) Regression RMSE and WAPE error metrics, and (Panel C) Anomaly detection ADCR and MASI separation ratios.
- **Method**: Multi-panel visualization respecting metric dimensional incompatibility.
- **Demonstrates**: Solid baseline performance across all 10 tasks with marked improvements on tuned candidates.
- **Epistemic Status**: `MODEL_OUTPUT`
- **Limitation**: Metric magnitudes across panels are fundamentally non-comparable.
