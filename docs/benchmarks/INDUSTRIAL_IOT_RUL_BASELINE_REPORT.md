# Industrial IoT 2040 Remaining Useful Life (RUL) Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `industrial_iot_rul`  
**Epistemic Status**: `CONTROLLED_INDUSTRIAL_SIMULATOR`  
**Task**: Remaining Useful Life Continuous Regression in Days  
**Target Column**: `Remaining_Useful_Life_days` (Mean: ~452 days, Range: 0 to 1,000+ days)  
**Features Count**: 26 telemetry and degradation features  
**Quarantined Columns**: `Failure_Within_7_Days` (Zero target leakage), `Machine_ID` (Zero entity leakage)  
**Tuning Status**: `NOT_STARTED`

---

## 1. Scale & Entity Split Verification

Splitting strictly by independent machines:

| Partition | Total Machines | Mean RUL (days) | Min RUL | Max RUL | Leakage Safeguards |
|---|---|---|---|---|---|
| **Train** | 350,000 | 452.6 | 0.0 | 1095.0 | Zero entity overlap; `Failure_Within_7_Days` quarantined |
| **Validation** | 75,000 | 452.9 | 0.0 | 1095.0 | Completely disjoint equipment population |
| **Test (Holdout)** | 75,000 | 452.4 | 0.0 | 1095.0 | Final Blind Evaluation (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Evaluated on validation machines (75,000 rows):

| Candidate Model | Validation RMSE (days) | Validation MAE (days) | Validation R² | Validation WAPE |
|---|---|---|---|---|
| **XGBoost_Regressor** | **48.49** | **38.26** | **0.9717** | **0.0845** |
| Random_Forest_Regressor | 52.18 | 41.35 | 0.9672 | 0.0913 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `XGBoost_Regressor`
- **Primary Metric**: Validation RMSE = `48.49` days
- **Secondary Metric**: Validation MAE = `38.26` days
- **Rationale**: Gradient boosting efficiently handled multi-variate non-linear interactions across `Operational_Hours`, `Vibration_mms`, and `fluid_depletion_index`, scaling gracefully across 350,000 machines.

---

## 4. Final Blind Holdout Evaluation (Test Machines)

Evaluated **exactly once** on `test.parquet` (75,000 independent machines):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **R²** | **0.9716** | 97.16% of equipment lifetime variance explained |
| **MAE** | **38.37 days** | ~1.2 month average error margin over multiple years of asset life |
| **RMSE** | **48.60 days** | Tight dispersion without extreme outlier misses |
| **WAPE** | **0.0848 (8.48%)** | Mean relative error under 8.5% plant-wide |
| **sMAPE** | **0.2594 (25.9%)** | Consistent across aging and newly commissioned machines |

---

## 5. Artifacts Locked

- `models/benchmarks/industrial_iot_rul/model_comparison.csv`
- `models/benchmarks/industrial_iot_rul/validation_metrics.json`
- `models/benchmarks/industrial_iot_rul/final_test_metrics.json`
- `models/benchmarks/industrial_iot_rul/training_config.json`
- `models/benchmarks/industrial_iot_rul/benchmark_metadata.json`
- `models/benchmarks/industrial_iot_rul/locked_baseline_model.joblib`
