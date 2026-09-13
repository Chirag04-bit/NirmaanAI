# NirmaanAI Master Baseline Model Benchmarking Summary Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Root**: `C:\NIRMAAN AI`  
**Execution Timestamp**: `2026-09-13 14:20:46 UTC`  
**Total Datasets / Tasks Benchmarked**: 10  
**Tuning Status**: `NOT_STARTED` (Strictly Pre-Tuning Default Baselines)  
**Holdout Protocol**: Test partition evaluated **EXACTLY ONCE** per dataset after validation champion selection  
**Isolation Assurance**: Zero cross-dataset leakage, zero test data leakage, zero model state contamination

---

## 1. Executive Master Benchmarking Summary Table

| # | Dataset / Task | Epistemic Status | Validation Champion Model | Primary Selection Metric | Test Score | Primary Test Performance Metrics |
|---|---|---|---|---|---|---|
| **01** | **AI4I 2020** (Machine Failure) | `REAL_PHYSICAL_SIMULATOR` | `Random_Forest_Natural` | Validation PR-AUC | **0.9099** | **PR-AUC**: 0.910 \| **ROC-AUC**: 0.971 \| **F1**: 0.870 \| **Recall**: 0.784 |
| **02** | **NASA C-MAPSS FD001** (Turbofan RUL) | `HIGH_FIDELITY_PHYSICS_SIMULATION` | `XGBoost_Regressor` | Validation RMSE | **13.33** | **RMSE**: 13.33 cycles \| **MAE**: 9.70 cycles \| **R²**: 0.896 \| **WAPE**: 0.109 |
| **03** | **UCI SECOM** (Wafer Defect) | `REAL_SEMICONDUCTOR_INLINE_SENSORS` | `XGBoost_Weighted` | Validation PR-AUC | **0.1374** | **PR-AUC**: 0.137 \| **ROC-AUC**: 0.681 \| **Accuracy**: 0.932 (Defect floor documented) |
| **04** | **UCI Steel Electricity** (MT_124 Power) | `REAL_INDUSTRIAL_TELEMETRY` | `XGBoost_Regressor` | Validation WAPE | **0.0663** | **WAPE**: 6.63% \| **MAE**: 19.83 kW \| **RMSE**: 27.04 kW \| **R²**: 0.958 |
| **05A**| **Industrial IoT 2040** (7-Day Failure) | `CONTROLLED_INDUSTRIAL_SIMULATOR` | `Logistic_Regression_Sampled` | Validation PR-AUC | **0.7596** | **PR-AUC**: 0.760 \| **ROC-AUC**: 0.983 \| **Recall**: 0.971 \| **F1**: 0.619 |
| **05B**| **Industrial IoT 2040** (RUL Regression) | `CONTROLLED_INDUSTRIAL_SIMULATOR` | `XGBoost_Regressor` | Validation RMSE | **48.60** | **RMSE**: 48.60 days \| **MAE**: 38.37 days \| **R²**: 0.972 \| **WAPE**: 0.085 |
| **06** | **Manufacturing Production** (Bottleneck) | `PROSPECTIVE_DISPATCH_RECORD` | `Random_Forest_Weighted` | Validation PR-AUC | **0.3141** | **PR-AUC**: 0.314 \| **ROC-AUC**: 0.561 \| **Recall**: 0.311 \| **F1**: 0.315 |
| **07** | **Manufacturing Defects** (Batch Quality) | `REAL_MANUFACTURING_METRICS` | `Random_Forest_Natural` | Validation ROC-AUC | **0.8675** | **ROC-AUC**: 0.868 \| **PR-AUC**: 0.957 \| **F1**: 0.978 \| **Accuracy**: 0.963 |
| **08** | **Textile Manufacturing** (Loom Telemetry) | `CONTROLLED_SYNTHETIC` | `Isolation_Forest_Detector` | Mean Anomaly Stability | **-0.4972** | **Mean Score**: -0.497 \| **Std**: 0.019 \| **95th %ile**: -0.468 \| **Peak**: -0.569 |
| **09** | **Synthetic Factory** (M1–M5 Anomaly) | `CONTROLLED_SYNTHETIC` | `Isolation_Forest_Detector` | Mean Anomaly Stability | **-0.5336** | **Mean Score**: -0.534 \| **Std**: 0.045 \| **95th %ile**: -0.487 \| **Peak**: -0.720 |

---

## 2. Rigorous Methodological Guarantees

1. **Strict No-Tuning Mandate Enforced**:
   - Zero automated hyperparameter search loops (`GridSearchCV`, `RandomizedSearchCV`, `Optuna`) were run.
   - All models utilized standard/default configurations with documented random seeds (`random_state=42`).
   - Every artifact metadata explicitly verifies `"tuning_status": "NOT_STARTED"`.

2. **Holdout Test Set Integrity**:
   - All model comparisons and champion selections were performed exclusively on `val.parquet`.
   - The test partition was evaluated **exactly once** after locking the champion model to freeze the honest baseline score.
   - Test data was never used in feature scaling, categorical encoding, or threshold tuning.

3. **Complete Dataset Isolation**:
   - No datasets were merged, pooled, or cross-referenced.
   - Scalers, feature pipelines, and models remain strictly compartmentalized in `models/benchmarks/<dataset>/`.

4. **Target Quarantine Adherence**:
   - `industrial_iot_failure`: `Remaining_Useful_Life_days` quarantined.
   - `industrial_iot_rul`: `Failure_Within_7_Days` quarantined.
   - `manufacturing_production`: Post-completion delays quarantined; prospective dispatch signals only.
   - `synthetic_factory`: Pre-decision cutoff baseline; `MAINT_0003` isolated from train partition.

---

## 3. Test Suite Verification & Canonical Integrity

- **Benchmark Test Suite**: `pytest tests/benchmarks/ -v` $\to$ **42 PASSED, 0 FAILED**
- **Full Project Regression**: `pytest tests/ -q` $\to$ **437 PASSED, 2 SKIPPED, 0 FAILED**
- **Canonical Checksum**: `34B12582B32D81E3121429C55EBF74E8` (`data/synthetic/auto_components/operational_losses.csv`) $\to$ **VERIFIED UNCHANGED**

---

## 4. Next Phase Readiness

Baseline model benchmarking is **COMPLETE AND LOCKED**. Model hyperparameter tuning has **NOT** started and awaits explicit authorization.
