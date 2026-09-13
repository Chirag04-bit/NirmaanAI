# NASA C-MAPSS FD001 Turbofan RUL Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `cmapss`  
**Epistemic Status**: `HIGH_FIDELITY_PHYSICS_SIMULATION`  
**Task**: Remaining Useful Life (RUL) Continuous Regression  
**Target Column**: `rul_clipped` (Piecewise linear threshold cap at 125 cycles)  
**Features Count**: 95 sensor telemetry, rolling stats, and engineered physics features  
**Group Unit**: `unit_number` (Turbofan Engine ID)  
**Tuning Status**: `NOT_STARTED`

---

## 1. Engine-Grouped Partitioning

To avoid auto-correlated temporal leakage across consecutive cycles of the same engine, dataset splitting was performed strictly by engine unit identifier:

| Partition | Engines Included | Total Engines | Total Operational Cycles | Target RUL Cap |
|---|---|---|---|---|
| **Train** | Engines 1–70 | 70 | 14,130 | 125 cycles |
| **Validation** | Engines 71–85 | 15 | 3,210 | 125 cycles |
| **Test (Holdout)** | Engines 86–100 | 15 | 3,291 | 125 cycles |

Zero engines overlap across partitions.

---

## 2. Experimental Candidate Baselines

Two model families were fitted on the training engines (14,130 cycles) and evaluated on validation engines (3,210 cycles):

| Candidate Model | Validation RMSE (cycles) | Validation MAE (cycles) | Validation R² | Validation WAPE |
|---|---|---|---|---|
| **XGBoost_Regressor** | **12.90** | **9.16** | **0.9032** | **0.1028** |
| Random_Forest_Regressor | 14.28 | 10.18 | 0.8814 | 0.1143 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `XGBoost_Regressor`
- **Primary Metric**: Validation RMSE = `12.90` cycles
- **Secondary Metric**: Validation MAE = `9.16` cycles
- **Rationale**: Gradient boosting effectively captured the subtle exponential decay and degradation signatures across sensors S2, S3, S4, S7, S8, S11, S12, S15 with superior residual convergence over bagged decision trees.

---

## 4. Final Blind Holdout Evaluation (Test Engines 86–100)

The champion was evaluated **exactly once** on the holdout test engines (3,291 cycles):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **RMSE** | **13.33 cycles** | Sub-14 cycle typical error on completely unseen jet engines |
| **MAE** | **9.70 cycles** | Mean absolute estimation error under 10 flight cycles |
| **R²** | **0.8965** | 89.65% of degradation variance accounted for |
| **WAPE** | **0.1089** | Weighted absolute percentage error under 11% |
| **sMAPE** | **0.1581** | Symmetric mean error of 15.8% |

---

## 5. Artifacts Locked

- `models/benchmarks/cmapss/model_comparison.csv`
- `models/benchmarks/cmapss/validation_metrics.json`
- `models/benchmarks/cmapss/final_test_metrics.json`
- `models/benchmarks/cmapss/training_config.json`
- `models/benchmarks/cmapss/benchmark_metadata.json`
- `models/benchmarks/cmapss/locked_baseline_model.joblib`
