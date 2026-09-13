# Synthetic Factory Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `synthetic_factory`  
**Epistemic Status**: `CONTROLLED_SYNTHETIC`  
**Task**: Multi-Station Factory Health Index & Anomaly Detection (Stations M1–M5)  
**Features Count**: 20 cross-station vibration, thermal, acoustic, and stress telemetry features  
**Isolation Condition**: Trained strictly on pre-decision cutoff (`2026-01-21 12:00 UTC`), isolating `MAINT_0003` from training baseline  
**Tuning Status**: `NOT_STARTED`

---

## 1. Multi-Station Partitioning

The synthetic factory dataset captures multi-station assembly operations across machines M1 through M5. The model was trained strictly on nominal operations prior to the decision cutoff:

| Partition | Timeframe / Filter | Total Observations | Machines Covered |
|---|---|---|---|
| **Train** | Pre-Decision Cutoff (Nominal) | 20,415 | M1, M2, M3, M4, M5 |
| **Validation** | Intermediate Validation Window | 8,750 | M1, M2, M3, M4, M5 |
| **Test (Holdout)** | Post-Cutoff / Holdout Window | 14,035 | M1, M2, M3, M4, M5 (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Evaluated on `val.parquet` (8,750 observations):

| Candidate Model | Mean Anomaly Score | Std Anomaly Score | 95th Percentile | Min Anomaly Score |
|---|---|---|---|---|
| **Isolation_Forest_Detector** | **-0.5417** | **0.0461** | **-0.4901** | **-0.7120** |
| PCA_Reconstruction_Detector | -0.1820 | 0.0580 | -0.0810 | -0.8450 |
| Robust_ZScore_Detector | -2.1050 | 1.1200 | -1.0500 | -8.9100 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `Isolation_Forest_Detector`
- **Primary Metric**: Anomaly score distribution stability (Mean = `-0.5417`, Std = `0.0461`)
- **Rationale**: Isolation Forest effectively separates anomalous deviations across coupled physical interactions (e.g. `mech_thermal_stress`, `vibration_severity_ratio`, `fluid_health_index`) without station-specific scale bias.

---

## 4. Final Blind Holdout Evaluation (Test Set)

Evaluated **exactly once** on `test.parquet` (14,035 observations):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **Mean Anomaly Score** | **-0.5336** | Close match with pre-cutoff nominal baseline |
| **Std Anomaly Score** | **0.0452** | Consistent dispersion across normal and degrading cycles |
| **95th Percentile Score** | **-0.4873** | Robust operational ceiling |
| **5th Percentile Score** | **-0.6169** | High-sensitivity alert threshold for factory health degradation |
| **Minimum Score (Peak Anomaly)**| **-0.7198** | Acute anomaly successfully identified |

---

## 5. Artifacts Locked

- `models/benchmarks/synthetic_factory/model_comparison.csv`
- `models/benchmarks/synthetic_factory/validation_metrics.json`
- `models/benchmarks/synthetic_factory/final_test_metrics.json`
- `models/benchmarks/synthetic_factory/training_config.json`
- `models/benchmarks/synthetic_factory/benchmark_metadata.json`
- `models/benchmarks/synthetic_factory/locked_baseline_model.joblib`
