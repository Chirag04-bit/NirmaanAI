# NirmaanAI — Dataset-by-Dataset Preprocessing Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Strict Dataset-by-Dataset Cleaning, Preprocessing & Sampling  
**Status**: COMPLETE, ISOLATED & VERIFIED  

---

## 1. Executive Summary

This report documents the dataset-specific preprocessing transformations fitted strictly on training data across all 9 NirmaanAI manufacturing datasets.

**Strict Scientific Mandate**:
1. **FIT ON TRAIN ONLY**: All imputer statistics, scaler parameters ($\mu, \sigma$, medians, quantiles), and encodings are learned strictly from the training partition.
2. **TRANSFORM ON ALL**: Preprocessing transforms are subsequently evaluated on train, validation, and test partitions without recalculating parameters on validation or test sets.
3. **No Cross-Dataset Contamination**: Scalers and imputers are strictly isolated. No global parameters exist.

---

## 2. Dataset-by-Dataset Preprocessing Architectures

### 2.1. Dataset 01: UCI AI4I 2020 Predictive Maintenance
- **Split Method**: Stratified 70/15/15 (7,000 train, 1,500 val, 1,500 test).
- **Target**: `machine_failure` (binary, ~3.39% positive across all splits).
- **Scaling Method**: `StandardScaler`.
  - Scaled features: `air_temperature_k`, `process_temperature_k`, `rotational_speed_rpm`, `torque_nm`, `tool_wear_min`, `temp_diff_k`, `temp_ratio`, `mechanical_power_kw`, `torque_speed_ratio`, `torque_speed_product`, `tool_wear_risk_index`, `power_temp_ratio`, `product_type_encoded`.
  - Justification: Gaussian-like distribution of rotational speed and thermodynamic variables; standardization facilitates logistic regression, SVM, and neural baselines.
- **Pipeline Artifact**: `models/processed/ai4i/preprocessing_pipeline.pkl`.

### 2.2. Dataset 02: NASA C-MAPSS FD001 Turbofan Run-to-Failure
- **Split Method**: Engine-Grouped 70/15/15:
  - Train: Engines 1–70 (14,484 cycles)
  - Val: Engines 71–85 (3,091 cycles)
  - Test: Engines 86–100 (3,056 cycles)
  - Zero engine overlap between partitions.
- **Target**: `rul_clipped` (piecewise linear capped at 125 cycles).
- **Scaling Method**: `StandardScaler` fit strictly on the 14,484 training engine cycles across the 14 informative sensor channels and their causal rolling metrics.
- **Pipeline Artifact**: `models/processed/cmapss/preprocessing_pipeline.pkl`.

### 2.3. Dataset 03: UCI SECOM Semiconductor Manufacturing
- **Split Method**: Stratified 70/15/15 (1,096 train, 235 val, 236 test wafers).
- **Target**: `target_defect` (binary, ~6.64% defect rate).
- **Imputation**: `SimpleImputer(strategy='median')` fit strictly on training wafers.
- **Scaling Method**: `RobustScaler(quantile_range=(25.0, 75.0))`.
  - Justification: SECOM sensor channels exhibit heavy tails, multi-modal distributions, and high process kurtosis where traditional variance estimates are vulnerable to outlier inflation.
- **Pipeline Artifact**: `models/processed/secom/preprocessing_pipeline.pkl`.

### 2.4. Dataset 04: UCI Electricity Load Diagrams (Client MT_124)
- **Split Method**: Strictly Chronological 70/15/15:
  - Train: 18,279 hourly intervals (2012-01-08 to 2014-02-07)
  - Val: 3,917 hourly intervals (2014-02-08 to 2014-07-20)
  - Test: 3,917 hourly intervals (2014-07-21 to 2014-12-31)
  - $t_{\text{train}} < t_{\text{val}} < t_{\text{test}}$. Zero shuffling.
- **Target**: `power_kw` (Continuous hourly load).
- **Scaling Method**: `StandardScaler` fit strictly on the 18,279 training hours.
- **Pipeline Artifact**: `models/processed/electricity/preprocessing_pipeline.pkl`.

### 2.5. Dataset 05: Industrial IoT Simulator 2040
- **Task A (`failure`)**:
  - Target: `Failure_Within_7_Days` (Binary classification, ~6.0% failure rate).
  - Split: Stratified 70/15/15 (350,000 train, 75,000 val, 75,000 test).
  - Quarantined: `Remaining_Useful_Life_days`.
  - Scaler: `StandardScaler` fit on 350,000 training machines.
- **Task B (`rul`)**:
  - Target: `Remaining_Useful_Life_days` (Continuous regression, mean ~452 days).
  - Split: Random 70/15/15 (350,000 train, 75,000 val, 75,000 test).
  - Quarantined: `Failure_Within_7_Days`.
  - Scaler: `StandardScaler` fit on 350,000 training machines.
- **Pipeline Artifacts**:
  - `models/processed/industrial_iot/failure/preprocessing_pipeline.pkl`
  - `models/processed/industrial_iot/rul/preprocessing_pipeline.pkl`

### 2.6. Dataset 06: Manufacturing Production Discrete Scheduling
- **Split Method**: Job-Sequence Chronological 70/15/15 (700 train, 150 val, 150 test jobs).
- **Target**: `target_is_bottleneck` (~32.7% positive).
- **Prospective Feature Scaling**: `StandardScaler` fit strictly on 700 training jobs across dispatch-available variables (`planned_duration_min`, `planned_energy_rate`, `machine_unavailability_pct`, etc.).
- **Pipeline Artifact**: `models/processed/manufacturing_production/preprocessing_pipeline.pkl`.

### 2.7. Dataset 07: Manufacturing Process & Defect Quality
- **Split Method**: Stratified 70/15/15 (2,268 train, 486 val, 486 test batches).
- **Target**: `DefectStatus` (Binary: 84.0% defective batches, 16.0% pass batches).
- **Scaling Method**: `StandardScaler` fit strictly on 2,268 training batches across physical, process, and supplier risk indices.
- **Pipeline Artifact**: `models/processed/manufacturing_defects/preprocessing_pipeline.pkl`.

### 2.8. Dataset 08: Textile Manufacturing Loom Telemetry
- **Split Method**: Per-Machine Chronological 70/15/15:
  - Within each loom (TX01–TX05): First 70% train (30,240 ticks total), next 15% val (6,480 ticks total), final 15% test (6,480 ticks total).
- **Scaling Method**: `StandardScaler` fit strictly on the 30,240 training ticks.
- **Pipeline Artifact**: `models/processed/textile/preprocessing_pipeline.pkl`.

### 2.9. Dataset 09: Synthetic Factory Auto-Components (Master Scenario)
- **Split Method**: Temporal Decision Cutoff Partition:
  - Train: Pre-cutoff early baseline (first 70% of pre-cutoff timeline per station: 20,415 ticks)
  - Val: Pre-cutoff emerging degradation (remaining 30% of pre-cutoff timeline: 8,750 ticks)
  - Test: Post-cutoff evaluation window (14,035 ticks containing Day 21 incident and recovery)
- **Scaling Method**: `StandardScaler` fit strictly on the 20,415 pre-cutoff baseline training ticks.
- **Pipeline Artifact**: `models/processed/synthetic_factory/preprocessing_pipeline.pkl`.

---

## 3. Preprocessing Verification Matrix

| Dataset | Split Method | Scaler Type | Fit Scope | Transform Scope | Preprocessing Pipeline Status |
|---|---|---|---|---|---|
| **AI4I 2020** | Stratified 70/15/15 | `StandardScaler` | Train Only (7k) | Train, Val, Test | SERIALIZED & VERIFIED |
| **NASA C-MAPSS** | Engine-Grouped 70/15/15 | `StandardScaler` | Train Engines (1–70) | Train, Val, Test | SERIALIZED & VERIFIED |
| **UCI SECOM** | Stratified 70/15/15 | `RobustScaler` + `SimpleImputer` | Train Only (1,096) | Train, Val, Test | SERIALIZED & VERIFIED |
| **UCI Electricity** | Chronological 70/15/15 | `StandardScaler` | Train Hours (18.2k) | Train, Val, Test | SERIALIZED & VERIFIED |
| **Industrial IoT (Failure)** | Stratified 70/15/15 | `StandardScaler` | Train Only (350k) | Train, Val, Test | SERIALIZED & VERIFIED |
| **Industrial IoT (RUL)** | Random 70/15/15 | `StandardScaler` | Train Only (350k) | Train, Val, Test | SERIALIZED & VERIFIED |
| **Production** | Job-Sequence 70/15/15 | `StandardScaler` | Train Only (700) | Train, Val, Test | SERIALIZED & VERIFIED |
| **Defects** | Stratified 70/15/15 | `StandardScaler` | Train Only (2,268) | Train, Val, Test | SERIALIZED & VERIFIED |
| **Textile** | Per-Machine Chronological | `StandardScaler` | Train Only (30.2k) | Train, Val, Test | SERIALIZED & VERIFIED |
| **Synthetic Factory** | Temporal Decision Cutoff | `StandardScaler` | Train Baseline (20.4k) | Train, Val, Test | SERIALIZED & VERIFIED |
