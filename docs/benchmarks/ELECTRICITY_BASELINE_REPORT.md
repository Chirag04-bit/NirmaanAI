# UCI Steel Industry Electricity Consumption Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `electricity`  
**Epistemic Status**: `REAL_INDUSTRIAL_TELEMETRY`  
**Task**: Hourly Power Consumption (kW) Time Series Forecasting (Client MT_124)  
**Target Column**: `power_kw`  
**Features Count**: 19 causal temporal, diurnal, cyclical, lag, and rolling features  
**Tuning Status**: `NOT_STARTED`

---

## 1. Chronological Partitioning (Causal Non-Overlapping Windows)

To prevent lookahead leakage in power grid demand forecasting, strictly ordered chronological splitting was utilized:

| Partition | Timeframe Coverage | Total Hours | Proportion | Leakage Safeguards |
|---|---|---|---|---|
| **Train** | Initial ~70% chronologically | 18,279 hours | 70% | Causal lags (t-1, t-2, t-3, t-4, t-24, t-168), backward rolling windows only |
| **Validation** | Intermediate ~15% window | 3,917 hours | 15% | Future window relative to train; past window relative to test |
| **Test (Holdout)** | Final ~15% chronologically | 3,917 hours | 15% | Final blind deployment simulation (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Evaluated on chronological validation window (3,917 hours):

| Candidate Model | Validation WAPE | Validation MAE (kW) | Validation RMSE (kW) | Validation R² |
|---|---|---|---|---|
| **XGBoost_Regressor** | **0.0652** | **18.80** | **26.15** | **0.9610** |
| Random_Forest_Regressor | 0.0694 | 20.02 | 27.84 | 0.9558 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `XGBoost_Regressor`
- **Primary Metric**: Validation WAPE = `0.0652` (6.52%)
- **Secondary Metric**: Validation MAE = `18.80 kW`
- **Rationale**: Gradient boosted trees excel on non-linear multi-period interactions between calendar features (`is_peak_hours`, cyclical `hour_sin`/`hour_cos`) and autoregressive load deviations.

---

## 4. Final Blind Holdout Evaluation (Test Set)

Evaluated **exactly once** on final test window (3,917 hours):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **WAPE** | **0.0663 (6.63%)** | Extremely accurate industrial energy demand forecast |
| **MAE** | **19.83 kW** | Under 20 kW mean deviation on industrial furnace plant loads |
| **RMSE** | **27.04 kW** | Tight bound on large load spike variances |
| **R²** | **0.9580** | 95.8% of consumption variability captured prospectively |
| **sMAPE** | **0.0779 (7.79%)** | Consistent symmetry across peak and off-peak tariffs |

---

## 5. Artifacts Locked

- `models/benchmarks/electricity/model_comparison.csv`
- `models/benchmarks/electricity/validation_metrics.json`
- `models/benchmarks/electricity/final_test_metrics.json`
- `models/benchmarks/electricity/training_config.json`
- `models/benchmarks/electricity/benchmark_metadata.json`
- `models/benchmarks/electricity/locked_baseline_model.joblib`
