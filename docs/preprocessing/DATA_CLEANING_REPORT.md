# NirmaanAI — Dataset-by-Dataset Data Cleaning & Audit Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Strict Dataset-by-Dataset Cleaning, Preprocessing & Sampling  
**Status**: COMPLETE, ISOLATED & VERIFIED  

---

## 1. Overview & Core Philosophy

This report documents the independent audit, integrity verification, and cleaning actions executed on each of the 9 NirmaanAI datasets.

**Strict Architectural Mandate**:
- No generic or pooled cleaning functions were applied.
- Each dataset has different physical meanings, measurement units, temporal dynamics, and failure modes.
- True physical phenomena (such as controlled bearing flutter in Synthetic Factory, peak electrical demand loads, or run-to-failure degradation) were strictly preserved and never discarded as artificial statistical outliers.

---

## 2. Dataset-by-Dataset Cleaning Actions

### 2.1. Dataset 01: UCI AI4I 2020 Predictive Maintenance
- **Domain Task**: Machine failure binary classification.
- **Audit Findings**: 10,000 tool run rows, 0 duplicate records, 0 missing values.
- **Physical Bounds Audit**:
  - Air temperature: All observations within valid physical range $[295.3, 304.5]\,\text{K}$.
  - Process temperature: Valid range $[305.7, 313.8]\,\text{K}$.
  - Rotational speed: All speeds $> 0$ (range: $1168$ to $2886\,\text{RPM}$).
  - Torque: Strictly non-negative $[3.8, 76.6\,\text{Nm}]$.
- **Leakage Elimination**:
  - Quarantined identifiers: `UDI`, `Product ID`.
  - Quarantined failure breakdown modes: `TWF`, `HDF`, `PWF`, `OSF`, `RNF` (direct target leakage).
- **Cleaning Actions**: Quarantined 7 non-predictive columns; 0 rows removed. Clean dataset contains 10,000 rows $\times$ 15 columns.

### 2.2. Dataset 02: NASA C-MAPSS FD001 Turbofan Run-to-Failure
- **Domain Task**: Remaining Useful Life (RUL) continuous regression.
- **Audit Findings**: 20,631 cycles across 100 turbofan engines, 0 duplicate engine-cycle records, 0 missing values.
- **Temporal Trajectory Continuity**:
  - Verified monotonic cycle continuity per engine: Cycles increment strictly as $1, 2, \dots, C_{\max}$ with 0 trajectory breaks.
  - Zero-variance invariant sensors (`s1`, `s5`, `s10`, `s16`, `s18`, `s19`) removed during feature extraction.
- **Outlier Policy**: Sensor degradation trends and flutter are true physical wear signals; 0 records removed as outliers.
- **Target Construction**: Piecewise linear clipping applied at $RUL^* = \min(RUL, 125)$ cycles.

### 2.3. Dataset 03: UCI SECOM Semiconductor Manufacturing
- **Domain Task**: In-line wafer defect classification.
- **Audit Findings**: 1,567 wafers across 592 raw sensor channels.
- **High-Dimensional Pruning & Quality Verification**:
  - Features with $>50\%$ missing values: 28 channels removed.
  - Zero/near-zero variance channels ($\sigma^2 < 10^{-6}$): 126 channels removed.
  - Retained feature set: 436 informative sensor channels.
- **Missing Value Handling**: Median imputer fitted strictly on training partition; zero test leakage.
- **Outlier Policy**: Retained heavy tails and sensor spikes; handled via downstream `RobustScaler` (quantile-based).

### 2.4. Dataset 04: UCI Electricity Load Diagrams (Client MT_124)
- **Domain Task**: Hourly electrical load forecasting.
- **Audit Findings**: 26,113 continuous hourly observations (2012–2014), 0 duplicate timestamps, 0 missing values.
- **Physical Bounds Audit**:
  - Negative load records: Exactly 0.
  - Grid peak loads: Valid continuous industrial demand up to $900\,\text{kW}$.
- **Outlier Policy**: Peak loads correspond to diurnal shift operations and seasonal heating/cooling; 0 peaks removed.

### 2.5. Dataset 05: Industrial IoT Factory Simulator 2040
- **Domain Tasks**:
  1. Failure Classification (`Failure_Within_7_Days`)
  2. RUL Regression (`Remaining_Useful_Life_days`)
- **Audit Findings**: 500,000 machine records, 0 duplicates, minor missing values in engineered coolant thermal efficiency (imputed via training median).
- **Strict Cross-Target Quarantine**:
  - `failure` pipeline: Drops `Remaining_Useful_Life_days` and `Machine_ID`.
  - `rul` pipeline: Drops `Failure_Within_7_Days` and `Machine_ID`.
- **Categorical Encoding**: `Machine_Type` encoded into integer representation; boolean supervision and error flags cast to integer.

### 2.6. Dataset 06: Manufacturing Production Discrete Scheduling
- **Domain Task**: Prospective bottleneck prediction at job dispatch time.
- **Audit Findings**: 1,000 production jobs, 0 duplicates, 0 missing values.
- **Prospective vs. Diagnostic Quarantine**:
  - Excluded post-event delay metrics: `realized_start_delay_min`, `realized_completion_delay_min`, `realized_cycle_ratio`, `Job_Status`, `Actual_Start`, `Actual_End`.
  - Retained prospective dispatch variables: `planned_duration_min`, `planned_energy_rate`, `machine_unavailability_pct`, `material_intensity`, `operation_type_code`, `machine_id_encoded`.

### 2.7. Dataset 07: Manufacturing Process & Defect Quality
- **Domain Task**: Batch defect quality classification.
- **Audit Findings**: 3,240 production batches, 0 duplicates, 0 missing values.
- **Categorical Encoding**: `SupplierQuality` mapped to ordinal values (`Low`=0, `Medium`=1, `High`=2).
- **Outlier Policy**: Extreme cost or volume batches correspond to specialized heavy industrial runs; all 3,240 rows retained.

### 2.8. Dataset 08: Textile Manufacturing Loom Telemetry
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`.
- **Audit Findings**: 43,200 sensor ticks (1-minute intervals across 5 looms: TX01–TX05), 0 duplicate records.
- **Outlier Policy**: High vibration and temperature spikes represent simulated yarn breakages and bearing strain; 0 rows pruned.

### 2.9. Dataset 09: Synthetic Factory Auto-Components (Master Scenario)
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`.
- **Audit Findings**: 43,200 sensor ticks across 5 stations (M1 CNC Lathe, M2 VMC Milling, M3 Grinder, M4 Inspection, M5 Assembly).
- **Scenario Integrity**:
  - Controlled M2 bearing degradation (Days 18–21) strictly retained.
  - Decision cutoff at `2026-01-21 12:00:00 UTC` applied to partition prospective training data from future post-incident recovery.
  - Quarantined retrospective ground truth `MAINT_0003` (`2026-01-22 16:30 UTC`).

---

## 3. Summary Audit Matrix

| Dataset | Raw Rows | Cleaned Rows | Raw Cols | Cleaned Cols | Duplicates Pruned | Quarantined / Excluded Cols |
|---|---:|---:|---:|---:|---:|---|
| **AI4I 2020** | 10,000 | 10,000 | 22 | 15 | 0 | 7 (`UDI`, `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, `RNF`) |
| **NASA C-MAPSS** | 20,631 | 20,631 | 99 | 99 | 0 | 0 (Constant sensors dropped in feature extraction) |
| **UCI SECOM** | 1,567 | 1,567 | 437 | 437 | 0 | 0 (154 uninformative channels dropped in feature extraction) |
| **UCI Electricity** | 26,113 | 26,113 | 21 | 21 | 0 | 0 (Strict backward-looking lags preserved) |
| **Industrial IoT (Failure)** | 500,000 | 500,000 | 29 | 28 | 0 | 2 (`Machine_ID`, `Remaining_Useful_Life_days`) |
| **Industrial IoT (RUL)** | 500,000 | 500,000 | 29 | 28 | 0 | 2 (`Machine_ID`, `Failure_Within_7_Days`) |
| **Production** | 1,000 | 1,000 | 29 | 15 | 0 | 14 (Post-event delays, actual completion, string dates) |
| **Defects** | 3,240 | 3,240 | 24 | 24 | 0 | 0 (Ordinal encoding applied) |
| **Textile** | 43,200 | 43,200 | 20 | 20 | 0 | 0 (`CONTROLLED_SYNTHETIC` preserved) |
| **Synthetic Factory** | 43,200 | 43,200 | 25 | 25 | 0 | 0 (Scenario degradation preserved) |
