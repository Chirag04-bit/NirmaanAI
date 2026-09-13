# NirmaanAI — Dataset-Wise Feature Extraction & Feature Engineering Research Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Pre-Model Tuning Feature Engineering & Scientific Leakage Audit  
**Status**: COMPLETE & VALIDATED (Immature/Ad-hoc Modeling Strictly Blocked)  
**Dataset Reference Checksum (`data/synthetic/auto_components/operational_losses.csv`)**: `34B12582B32D81E3121429C55EBF74E8` (VERIFIED MATCH)  

---

## 1. Objective

Before conducting any model hyperparameter tuning, neural architecture search, or threshold optimization across NirmaanAI's predictive engines, a rigorous, dataset-by-dataset feature extraction and engineering study was mandated.

### Core Scientific Principles:
1. **Physical & Domain Grounding**: Every engineered feature is derived from underlying mechanical, thermodynamic, electrical, or operational principles (e.g., ISO 10816 vibration severity, mechanical shaft power $P = 2\pi N\tau/60000$, thermal delta $\Delta T$, fluid depletion index).
2. **Strict Epistemic Isolation**: Datasets are never merged into an artificial multi-domain feature matrix. Each dataset functions inside its dedicated pipeline under `src/features/`.
3. **Zero Future Lookahead & Strict Causality**: For temporal and time-series datasets (NASA C-MAPSS FD001, UCI Electricity MT_124, Synthetic Factory, Textile Loom), every feature at time $t$ depends strictly on observations $t' \le t$. No centered rolling windows, no backwards back-filling.
4. **Leakage Elimination & Quarantine**: High-risk failure mode indicators (AI4I: `TWF`, `HDF`, `PWF`, `OSF`, `RNF`), surrogate labels, and post-event operational outcomes (actual completion delay, realized cycle ratio in prospective scheduling) are quarantined from predictor sets.
5. **Raw Dataset Immutability**: All source files under `C:\NIRMAAN AI\DATASET` remain unmodified.

---

## 2. Dataset Inventory & Profiling (Phase A & B)

| Dataset Key | Dataset Title & Source | Rows | Raw Cols | Mem (MB) | Granularity | Epistemic Nature | Primary Target Column(s) |
|---|---|---:|---:|---:|---|---|---|
| `ai4i` | UCI AI4I 2020 Predictive Maintenance | 10,000 | 14 | 1.1 | Per tool run | Real Physical Simulator | `machine_failure` (binary, 3.39%) |
| `cmapss` | NASA C-MAPSS Turbofan Engine FD001 | 20,631 | 26 | 4.1 | 1 Cycle (Run-to-failure) | High-Fidelity Physics Sim | `rul_clipped` (piecewise linear capped at 125) |
| `secom` | UCI SECOM Semiconductor Manufacturing | 1,567 | 592 | 7.1 | Per wafer batch | Real Fab In-Line Sensors | `target_defect` (binary, 6.64%) |
| `electricity` | UCI Electricity Load Diagrams (MT_124) | 26,113 | 2 | 0.8 | 1 Hour (resampled from 15m) | Real Smart Meter Grid | `power_kw` (continuous load) |
| `industrial_iot` | Factory Sensor Simulator 2040 | 500,000 | 22 | 84.0 | Per machine snapshot | Real-Scale Sensor Sim | `Failure_Within_7_Days`, `Remaining_Useful_Life_days` |
| `manufacturing_production` | Hybrid Manufacturing Discrete Schedule | 1,000 | 13 | 0.1 | Per production job | Real/Hybrid MES Execution | `Bottleneck_Risk` (binary, 32.7%) |
| `manufacturing_defects` | Manufacturing Process & Defect Quality | 3,240 | 17 | 0.4 | Per production batch | Real Quality Control Telemetry | `DefectStatus` (binary, 84.0%) |
| `textile` | Textile Loom Telemetry Synthetic | 43,200 | 13 | 4.3 | 1 Minute | CONTROLLED_SYNTHETIC | Multi-sensor Anomaly / Loom Stress |
| `synthetic_factory` | NirmaanAI Auto-Components Factory (M1–M5) | 43,200 | 13 | 4.3 | 1 Minute (30 days) | CONTROLLED_SYNTHETIC | Multi-station Anomaly / Controlled Degradation |

---

## 3. Detailed Dataset-by-Dataset Feature Engineering

### 3.1. Dataset 1: UCI AI4I 2020 Predictive Maintenance
- **File**: `DATASET/01_AI4I_2020/raw/ai4i2020.csv`
- **Predictor Objective**: Machine failure early warning prior to breakdown occurrence.
- **Engineered Features**:
  1. `temp_diff_k` ($\Delta T = T_{\text{process}} - T_{\text{air}}$): Thermodynamic dissipation gradient. Unit: Kelvin.
  2. `temp_ratio` ($T_{\text{process}} / T_{\text{air}}$): Relative thermal excitation.
  3. `mechanical_power_kw` ($P = \frac{2\pi \cdot \text{RPM} \cdot \tau}{60000}$): Instantaneous shaft mechanical power. Unit: kW.
  4. `torque_speed_ratio` ($\tau / \text{RPM}$): Heavy-load low-speed operational stress indicator.
  5. `torque_speed_product` ($\tau \cdot \text{RPM}$): Raw mechanical stress proxy.
  6. `tool_wear_risk_index` ($(\text{wear} / 240)^2$): Non-linear accelerated wear boundary approaching 240-minute service limit.
  7. `power_temp_ratio` ($P / \Delta T$): Specific mechanical energy dissipation efficiency.
  8. `product_type_encoded`: Ordinal quality grade encoding ($L=0, M=1, H=2$).
- **Leakage Quarantine**:
  - `UDI`, `Product ID`: Static arbitrary database identifiers.
  - `TWF` (Tool Wear Failure), `HDF` (Heat Dissipation Failure), `PWF` (Power Failure), `OSF` (Overstrain Failure), `RNF` (Random Failure): Direct failure cause labels; quarantined to prevent 100% trivial target leakage.

### 3.2. Dataset 2: NASA C-MAPSS FD001 Turbofan Run-to-Failure
- **File**: `DATASET/02_NASA_CMAPSS/raw/CMaps/train_FD001.txt`
- **Predictor Objective**: Remaining Useful Life (RUL) estimation under strictly causal conditions.
- **Target Construction**:
  - Raw RUL: $RUL_{e,c} = C_{\max,e} - c$.
  - Piecewise Linear RUL: $RUL^* = \min(RUL_{e,c}, 125)$ cycles (mitigating uninformative healthy baseline noise).
- **Constant Sensor Drops**:
  - `s1`, `s5`, `s10`, `s16`, `s18`, `s19` exhibited exactly zero variance across all engines and cycles; pruned immediately to prevent singular covariance matrices.
- **Engineered Temporal Features (14 Informative Channels $\times$ 5 Transforms = 70 Features + Cycle Norm)**:
  1. First difference: $\Delta s_i(c) = s_i(c) - s_i(c-1)$.
  2. Degradation delta from healthy baseline: $s_i(c) - \bar{s}_{i,\text{cycles 1..5}}$.
  3. Causal Rolling Mean (5 cycles): $\frac{1}{k}\sum_{j=0}^{k-1} s_i(c-j)$.
  4. Causal Rolling Mean (10 cycles): $\frac{1}{10}\sum_{j=0}^{9} s_i(c-j)$.
  5. Causal Rolling Standard Deviation (10 cycles): High-frequency flutter indicator.
  6. Cycle normalization: $c / 100.0$.

### 3.3. Dataset 3: UCI SECOM Semiconductor Manufacturing
- **File**: `DATASET/03_UCI_SECOM/raw/uci-secom.csv`
- **Predictor Objective**: In-line wafer defect classification under severe class imbalance ($104 / 1567 = 6.64\%$) and high dimensional sparsity.
- **Quality Analysis & Screening**:
  - Total raw sensor channels: 590.
  - Dropped for excessive missingness ($>50\%$ NaN): 28 channels (e.g., sensor_157, sensor_158, sensor_221).
  - Dropped for zero/near-zero variance ($\sigma^2 < 10^{-6}$): 126 channels.
  - Kept sensor channels: 436 channels.
  - Imputation Strategy: Domain-safe median imputation computed strictly per channel on retained features without row drops.

### 3.4. Dataset 4: UCI Electricity Load Diagrams (Client MT_124)
- **File**: `DATASET/04_ENERGY/raw/LD2011_2014.txt`
- **Predictor Objective**: Short-term and medium-term industrial power demand forecasting.
- **Temporal Resampling**: 15-minute raw interval resampled to 1-hour continuous electrical load (26,113 observations from 2012 to 2014).
- **Engineered Causal Features**:
  1. Calendar/Diurnal: `hour`, `day_of_week`, `is_weekend`, `month`, `is_peak_hours` (08:00–20:00).
  2. Harmonic representations: `hour_sin`, `hour_cos` ($2\pi h / 24$).
  3. Causal Lags: `lag_1h`, `lag_2h`, `lag_3h`, `lag_4h`, `lag_24h` (diurnal persistence), `lag_168h` (weekly seasonality).
  4. Causal Rolling Statistics (24-hour lookback): `rolling_mean_24h`, `rolling_std_24h`, `rolling_min_24h`, `rolling_max_24h`.
  5. Load Differences: `load_diff_1h` ($P_t - P_{t-1}$), `load_diff_24h` ($P_t - P_{t-24}$).

### 3.5. Dataset 5: Industrial IoT Factory Simulator 2040
- **File**: `DATASET/05_INDUSTRIAL_IOT/raw/factory_sensor_simulator_2040.csv`
- **Predictor Objective**: Predictive maintenance classification and equipment longevity prediction across 500,000 records.
- **Engineered Features**:
  1. `thermal_deviation_c`: Deviation from nominal operating temperature ($T - 70^\circ\text{C}$).
  2. `vibration_severity_ratio`: Ratio against ISO 10816 Zone C boundary ($v / 2.8\,\text{mm/s}$).
  3. `fluid_depletion_index`: Combined lubrication and cooling depletion $((100 - \text{oil}) + (100 - \text{coolant})) / 2$.
  4. `thermo_vibration_stress`: Non-linear thermo-mechanical coupling ($T \cdot v / 100$).
  5. `hydraulic_pressure_deviation`: Deviation from nominal 150 bar hydraulic benchmark ($|P - 150|$).
  6. `error_rate_per_1k_hours`: Operational error velocity ($\text{errors} / (\text{hours}/1000 + 1)$).
  7. `coolant_thermal_efficiency`: Coolant heat absorption capability ($\Delta T / \text{flow}$).
- **Cross-Target Leakage Quarantine**:
  - `Failure_Within_7_Days` (Target for Classification) MUST NOT be used when predicting `Remaining_Useful_Life_days`.
  - `Remaining_Useful_Life_days` MUST NOT be used when predicting `Failure_Within_7_Days`.

### 3.6. Dataset 6: Manufacturing Production Discrete Scheduling
- **File**: `DATASET/06_MANUFACTURING_PRODUCTION/raw/hybrid_manufacturing_categorical.csv`
- **Predictor Objective**: Real-time bottleneck risk prediction ($327 / 1000 = 32.7\%$) at job dispatch time.
- **Prospective vs. Post-Event Quarantine**:
  - **Prospective Features (Allowed at Dispatch)**:
    - `planned_duration_min`: Scheduled execution duration.
    - `planned_energy_rate`: Scheduled energy demand intensity ($\text{energy} / \text{planned\_duration}$).
    - `is_night_shift`: Shift timing indicator.
    - `is_rush_order`: Priority flag.
    - `complexity_x_quantity`: Total planned mechanical workload.
  - **Post-Event Features (Quarantined to Diagnostic Audit Only)**:
    - `realized_start_delay_min` ($\text{actual\_start} - \text{scheduled\_start}$): Post-dispatch latency.
    - `realized_completion_delay_min` ($\text{actual\_end} - \text{scheduled\_end}$): Post-event delay.
    - `realized_cycle_ratio` ($\text{actual\_duration} / \text{planned\_duration}$): Realized operational distortion.
    - `Job_Status`: Post-run terminal execution state.

### 3.7. Dataset 7: Manufacturing Process & Defect Quality
- **File**: `DATASET/08_MANUFACTURING_DEFECTS/raw/manufacturing_defect_dataset.csv`
- **Predictor Objective**: Batch defect status prediction ($2723 / 3240 = 84.0\%$).
- **Engineered Features**:
  1. `cost_per_unit`: Financial production cost normalized by volume ($\text{Cost} / \text{Volume}$).
  2. `energy_per_unit_vol`: Specific energy consumption ($\text{Energy} / \text{Volume}$).
  3. `supply_chain_risk_index`: Combined supplier defect-rate interaction ($\text{SupplierRisk} \cdot \text{DefectRate}_{\text{supplier}}$).
  4. `maintenance_downtime_ratio`: Proportional maintenance burden ($\text{MaintHours} / \text{DowntimeHours}$).
  5. `labor_downtime_friction`: Operational inefficiency interaction ($\text{Downtime} \cdot (1 - \text{WorkerProd})$).
  6. `energy_cost_ratio`: Utility cost fraction ($\text{Energy} / \text{Cost}$).
  7. `quality_composite_indicator`: Multi-attribute quality score.

### 3.8. Dataset 8: Textile Loom Telemetry (Synthetic)
- **File**: `DATASET/09_TEXTILE_MANUFACTURING/synthetic/sensor_readings.csv`
- **Predictor Objective**: High-speed weaving loom mechanical anomaly tracking.
- **Epistemic Status**: `CONTROLLED_SYNTHETIC` (explicitly tagged to prevent real-world overclaiming).
- **Engineered Features**:
  1. `temp_diff_c`: Thermodynamic gradient ($T_{\text{loom}} - T_{\text{ambient}}$).
  2. `vibration_norm`: Acceleration deviation against nominal 2.0 mm/s.
  3. `vibration_roll_mean_5`: Causal rolling mean across 5 ticks.
  4. `vibration_roll_max_15`: Causal rolling peak across 15 ticks.
  5. `power_rpm_ratio`: Electromechanical torque impedance proxy.
  6. `acoustic_vibration_stress`: Vibro-acoustic coupled strain ($v \cdot \text{dB}$).

### 3.9. Dataset 9: Synthetic Factory Auto-Components (Master Scenario)
- **File**: `DATASET/10_SYNTHETIC_FACTORY/synthetic/sensor_readings.csv`
- **Predictor Objective**: Multi-station manufacturing cell degradation early warning (M1 CNC Lathe, M2 VMC Milling, M3 Grinder, M4 Inspection, M5 Assembly).
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`.
- **Temporal Quarantine & Scenario Integrity**:
  - Temporal Decision Cutoff: `2026-01-21 12:00:00 UTC` (Day 21).
  - Pre-cutoff records: 29,165 sensor ticks (Healthy baseline & emerging subtle degradation).
  - Post-cutoff records: 14,035 sensor ticks (Emergency breakdown & post-event recovery).
  - Scenario Quarantine: Maintenance event `MAINT_0003` (M2 bearing failure on Day 21) is quarantined to prevent model lookahead leakage.
- **Engineered Features**:
  1. `temp_diff_c`: Machine vs ambient temperature differential.
  2. `vibration_severity_ratio`: ISO 10816 Zone C ratio ($v / 2.8$).
  3. `vibration_roll_mean_5`: Station-isolated causal rolling mean (5 ticks).
  4. `vibration_roll_std_15`: Station-isolated rolling vibration flutter (15 ticks).
  5. `vibration_roll_max_15`: Station-isolated rolling peak shock (15 ticks).
  6. `power_speed_ratio`: Mechanical impedance ($P / \text{RPM}$).
  7. `mech_thermal_stress`: Combined stress tensor ($T \cdot v$).
  8. `fluid_health_index`: Lubricant + coolant composite score ($(\text{oil} + \text{coolant}) / 2$).
  9. `tool_wear_risk`: Non-linear quadratic tool wear fatigue indicator ($(\text{wear} / 240)^2$).
  10. `is_pre_decision_cutoff`: Strict binary marker separating prospectively available records from post-incident future telemetry.

---

## 4. Comprehensive Feature Leakage Audit

| Dataset | Column Name | Raw / Derived | Classification | Risk Level | Mitigation / Policy |
|---|---|---|---|---|---|
| AI4I | `UDI` | Raw | IDENTIFIER | High | DROPPED / QUARANTINED |
| AI4I | `Product ID` | Raw | IDENTIFIER | High | DROPPED / QUARANTINED |
| AI4I | `TWF` | Raw | TARGET_LEAKAGE | Critical | EXCLUDED from predictor set (Specific failure mode) |
| AI4I | `HDF` | Raw | TARGET_LEAKAGE | Critical | EXCLUDED from predictor set (Specific failure mode) |
| AI4I | `PWF` | Raw | TARGET_LEAKAGE | Critical | EXCLUDED from predictor set (Specific failure mode) |
| AI4I | `OSF` | Raw | TARGET_LEAKAGE | Critical | EXCLUDED from predictor set (Specific failure mode) |
| AI4I | `RNF` | Raw | TARGET_LEAKAGE | Critical | EXCLUDED from predictor set (Specific failure mode) |
| C-MAPSS | `rul_raw` | Derived | TARGET | Critical | Used ONLY as supervisory label; never as input feature |
| C-MAPSS | Future cycles | Temporal | FUTURE_LEAKAGE | Critical | All rolling calculations strictly restricted to $t \le c$ |
| SECOM | Constant channels | Raw | CONSTANT | Medium | 126 zero-variance channels pruned |
| SECOM | Sensor channels $>50\%$ NaN | Raw | UNUSABLE | High | 28 channels pruned before modeling |
| Electricity | Forward load ($t+k$) | Temporal | FUTURE_LEAKAGE | Critical | Only backward lags ($\ge 1\text{h}$) and past rolling windows used |
| Industrial IoT | `Failure_Within_7_Days` | Raw | TARGET | Critical | Quarantined when training RUL regression model |
| Industrial IoT | `Remaining_Useful_Life_days` | Raw | TARGET | Critical | Quarantined when training Failure classification model |
| Production | `realized_start_delay_min` | Derived | POST_EVENT_ONLY | Critical | Excluded from dispatch-time bottleneck predictor |
| Production | `realized_completion_delay_min`| Derived | POST_EVENT_ONLY | Critical | Excluded from dispatch-time bottleneck predictor |
| Production | `realized_cycle_ratio` | Derived | POST_EVENT_ONLY | Critical | Excluded from dispatch-time bottleneck predictor |
| Production | `Job_Status` | Raw | POST_EVENT_ONLY | High | Terminal status excluded from early warning models |
| Synthetic Factory | Future telemetry ($>21\text{d}$) | Temporal | SCENARIO_LEAKAGE | Critical | Guarded by `is_pre_decision_cutoff` flag |
| Synthetic Factory | `MAINT_0003` | Metadata | FUTURE_LEAKAGE | Critical | Quarantined during training to emulate blind detection |

---

## 5. Temporal Causality Audit

To strictly guarantee zero temporal leakage:
1. **Window Alignment**: All rolling windows (`rolling_mean`, `rolling_std`, `rolling_max`, `rolling_min`) are right-aligned. For any record at timestamp or cycle $t$, window spans $[t - W + 1, t]$.
2. **First Valid Timestamp**: For initial intervals where $t < W$, standard expanding aggregations with minimum periods of 1 are applied, preventing artificial NaN drops while eliminating forward bias.
3. **Difference Formulations**: All difference operations are defined as $\Delta x_t = x_t - x_{t-1}$.
4. **Grouped Isolation**: For multi-entity datasets (C-MAPSS 100 engines, Synthetic Factory 5 stations, Textile 5 looms), rolling windows are partitioned strictly by entity ID. Telemetry from Engine $A$ is never rolled across Engine $B$.

---

## 6. Feature Scaling Guidance for Downstream Modeling

| Downstream Model Class | Scaling Recommendation | Method Justification |
|---|---|---|
| Tree-based Ensembles (XGBoost, LightGBM, Random Forest) | None (Raw numericals) | Invariant to monotonic affine scaling; preserves exact physical thresholds ($T = 70^\circ\text{C}$, ISO $v = 2.8\,\text{mm/s}$) |
| Linear / Regularized Models (ElasticNet, Logistic Regression) | `StandardScaler` or `RobustScaler` | Required for isotropic $L_1/L_2$ penalties; `RobustScaler` advised for SECOM & Industrial IoT due to heavy tails |
| Deep Learning / Temporal Recurrent Nets (LSTM, GRU, Transformers) | `MinMaxScaler([0, 1])` or `StandardScaler` | Prevents gradient explosion across unscaled RPM ($10^3$) vs $\Delta T$ ($10^1$) channels |
| Distance / Clustering Algorithms (KNN, Isolation Forest, PCA) | `StandardScaler` | Essential to prevent large-magnitude features from dominating Euclidean metric space |

---

## 7. Artifact Registry & Storage Locations

Feature artifacts are stored under `models/features/<dataset_key>/`:
1. `models/features/ai4i/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
2. `models/features/cmapss/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
3. `models/features/secom/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
4. `models/features/electricity/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
5. `models/features/industrial_iot/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
6. `models/features/manufacturing_production/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
7. `models/features/manufacturing_defects/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
8. `models/features/textile/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)
9. `models/features/synthetic_factory/` (`feature_dictionary.csv`, `extracted_features.parquet`, `metadata.json`)

---

## 8. Verification & Test Suite Summary

- **Feature Extraction Test Suite**: `tests/test_feature_extraction.py` (11 unit & integration tests) — **11 PASSED**
- **Project Full Regression Suite**: `pytest tests/ -q` — **364 PASSED**, 2 skipped, 0 failed (100% GREEN)
- **Dataset Immutability Checksum**: `data/synthetic/auto_components/operational_losses.csv` matches `34B12582B32D81E3121429C55EBF74E8`
- **Model Tuning Prohibition**: No models tuned, no hyperparameters searched, no locked metrics altered. Feature engineering study is cleanly finished and awaiting explicit user instructions.
