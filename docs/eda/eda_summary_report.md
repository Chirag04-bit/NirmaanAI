# NirmaanAI — Master Exploratory Data Analysis (EDA) & Research-Integrity Synthesis

**Document Version**: 2.0.0 (Research-Integrity & Reproducibility Audited)  
**Phase**: Phase 3 — Data Understanding & Exploratory Data Analysis  
**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence Platform  
**Target MSME Verticals**: Textile & Precision Automotive Component Manufacturing  
**Academic Alignment**: Institute of Engineering & Management (IEM), Kolkata | Department of CSE (AI) | Group 59 | Guide: Prof. Kuntal Mondal  

---

## 1. Research & Methodological Framing

This document synthesizes exploratory data analysis (EDA) across all active empirical datasets in `C:\NIRMAAN AI\DATASET`. Every numerical value reported herein has been verified through executable code on the local dataset files.

> [!IMPORTANT]
> **Scientific Integrity & Causality Notice**:
> Observational and public benchmarks provide empirical distributions, correlation patterns, and baseline characteristics. They **do NOT** constitute causal validation of physical machinery behavior on a real factory floor. The proposed Machine 2 scenario is an operational engineering model; the empirical findings below provide **supporting evidence** for the design parameters of that scenario rather than formal causal proof.

---

## 2. Observed & Calculated Findings (Empirically Measured)

### 2.1. AI4I 2020 Predictive Maintenance (`01_AI4I_2020`)
- **Dimensions**: Exactly 10,000 instances $\times$ 14 columns.
- **Class Distribution**:
  - `Machine failure = 0`: 9,661 (96.61%)
  - `Machine failure = 1`: 339 (3.39%)
  - **Measured Imbalance Ratio**: **28.5 : 1**.
- **Failure Mode Breakdown (Count & Target Pearson Correlation)**:
  - `HDF` (Heat Dissipation Failure): 115 instances ($r = +0.5758$)
  - `OSF` (Overstrain Failure): 98 instances ($r = +0.5311$)
  - `PWF` (Power Failure): 95 instances ($r = +0.5228$)
  - `TWF` (Tool Wear Failure): 46 instances ($r = +0.3629$)
  - `RNF` (Random Failure): 19 instances ($r = +0.0045$)
- **Measured Thresholds & Physical Features**:
  - **Tool Wear in TWF**: When `TWF = 1`, Tool wear has a minimum of 198.0 min, mean of 216.37 min, and maximum of 253.0 min. **97.8%** of TWF instances (45 of 46) occur at Tool wear $\ge 200\text{ minutes}$. (For normal non-failure runs, mean Tool wear is 106.8 min).
  - **Temperature Difference in HDF**: For $\Delta T = T_{\text{process}} - T_{\text{air}}$, when `HDF = 1`, $\Delta T$ has a mean of 8.23 K and an exact maximum of **8.60 K** (115 of 115 instances, **100%**). In contrast, for non-HDF instances, mean $\Delta T$ is 10.02 K (range 7.6 K to 12.1 K).
  - **Torque & Rotational Speed**: Torque exhibits a $+0.1913$ correlation with failure; rotational speed exhibits a slight negative correlation ($-0.0442$).

---

### 2.2. NASA C-MAPSS Turbofan Engine Degradation (`02_NASA_CMAPSS`)
- **Dimensions**: 265,256 total sensor records (FD001 to FD004) across 707 engine units.
- **FD001 Measured Lifespan Statistics** (100 run-to-failure engines):
  - Minimum engine life: 128 cycles
  - Maximum engine life: 362 cycles
  - Mean lifespan: 206.3 cycles (median 199.0 cycles, std 46.3 cycles)
- **Sensor Drift Characteristics in FD001**:
  - **Degradation-Informative Sensors** (14 sensors with standard deviation $\ge 0.01$ and monotonic trend):
    `s2`, `s3`, `s4`, `s7`, `s8`, `s9`, `s11`, `s12`, `s13`, `s14`, `s15`, `s17`, `s20`, `s21`.
  - **Static / Non-Informative Sensors** (7 sensors with standard deviation $< 0.01$ under constant sea-level operating condition):
    `s1`, `s5`, `s6`, `s10`, `s16`, `s18`, `s19`.

---

### 2.3. UCI SECOM Semiconductor Process (`03_UCI_SECOM`)
- **Dimensions**: 1,567 rows $\times$ 592 columns (`Time` + 590 sensors + `Pass/Fail`).
- **Missingness Audit**: Exactly 41,951 missing cells across 538 feature columns.
  - 32 feature columns contain $>40\%$ missing values.
  - Exactly **116 columns** exhibit zero variance (constant values across all 1,567 rows).
- **Target Distribution**:
  - `-1` (Pass): 1,463 (93.36%)
  - `+1` (Fail): 104 (6.64%)
  - **Measured Imbalance Ratio**: **14.07 : 1**.

---

### 2.4. Electricity Load Diagrams 2011–2014 (`04_ENERGY`)
- **Dimensions**: 140,257 timestamps (15-minute intervals spanning 2011-01-01 to 2014-12-31) $\times$ 371 columns.
- **Load Characteristics**:
  - 158 client profiles are active from timestamp 1 (2011-01-01); remaining meters are phased in over the 4-year period.
  - Active industrial client loads (e.g. `MT_124`, `MT_156`) exhibit strong 24-hour diurnal cyclicity, peaking during daytime operational hours.

---

### 2.5. Factory Sensor Simulator 2040 (`05_INDUSTRIAL_IOT`)
- **Dimensions**: Exactly 500,000 rows $\times$ 22 columns across 33 distinct machine types.
- **Target Distribution**:
  - `Failure_Within_7_Days = False`: 469,968 (93.99%)
  - `Failure_Within_7_Days = True`: 30,032 (6.01%)
  - **Measured Imbalance Ratio**: **15.65 : 1**.
- **Measured Telemetry by Failure Class**:
  - **Vibration**:
    - False (Healthy): Mean = 9.94 mm/s (std 5.00, median 9.95, 75th percentile 13.32 mm/s).
    - True (Impending Failure): Mean = **10.73 mm/s** (std 4.96, median 10.77, 75th percentile **14.12 mm/s**).
  - **Sound**:
    - False: Mean = 75.01 dB (std 9.99, range 18.2 to 120.7 dB).
    - True: Mean = 74.95 dB (std 9.96, range 27.8 to 115.6 dB).
    - *Finding*: Acoustic noise shows near-identical distributions across both classes in this synthetic dataset, indicating it carries minimal linear discriminative power on its own.
  - **Deterministic Leakage Verified**: The maximum `Remaining_Useful_Life_days` for `Failure_Within_7_Days = True` is **6.0 days**. RUL $\le 7.0$ perfectly determines the label.

---

### 2.6. Hybrid Manufacturing Categorical (`06_MANUFACTURING_PRODUCTION`)
- **Dimensions**: Exactly 1,000 job records $\times$ 13 columns.
- **Job Status Distribution**:
  - `Completed`: 673 (67.3%)
  - `Delayed`: 198 (19.8%)
  - `Failed`: 129 (12.9%)
- **Measured Dispatch Delay (`Start_Delay_min` = `Actual_Start` - `Scheduled_Start`)**:
  - For `Completed` jobs: Mean = -0.15 min (std 3.14 min, min -5.0 min, max +5.0 min).
  - For `Delayed` jobs: Mean = **20.15 min** (std 6.27 min, min **10.0 min**, max **30.0 min**).
  - For `Failed` jobs: `Actual_Start` is missing (`NaN`) because the jobs failed prior to dispatch.
  - *Finding*: In this dataset, 100% of jobs with start delays $\ge 10\text{ minutes}$ (198 of 198) resulted in `Delayed` status.

---

### 2.7. Manufacturing Defect Dataset (`08_MANUFACTURING_DEFECTS`)
- **Dimensions**: Exactly 3,240 records $\times$ 17 columns.
- **Defect Status Distribution**: `1` (Defect present): 2,723 (84.04%) | `0` (No defect): 517 (15.96%).
- **Measured Cost Differences**:
  - Non-defective runs (`0`): Mean ProductionCost = **₹12,158.88** (std ₹3,034.42).
  - Defective runs (`1`): Mean ProductionCost = **₹12,473.17** (std ₹3,074.78).
  - Difference: **+2.58%** increase in mean production cost on defective runs.
  - Mean DowntimePercentage is 2.49% for non-defective runs vs 2.50% for defective runs (0.65% relative difference).

---

## 3. Dataset Limitations

1. **Synthetic & Simulated Origins**:
   - `AI4I 2020`, `Factory Sensor Simulator 2040`, and `Hybrid Manufacturing` are synthetically generated datasets. While based on physical equations, their distributions reflect generative rules and cannot replace real factory sensor telemetry.
2. **Textile Domain Absence**:
   - None of the 7 empirical datasets originate from a textile loom or spinning mill. This gap will be addressed in Phase 5 via a dedicated synthetic MSME generator.
3. **Missing Raw Time-Series in 07_FACTORY_OEE_DOWNTIME**:
   - `archive (5).zip` contains only metadata and schema definitions; raw time-series CSVs are absent.

---

## 4. Working Hypotheses for Modeling

1. **Hypothesis 1 (Thermal Dissipation Indicator)**:
   A combined feature $\text{Cooling\_Stress} = \text{Torque} \times \frac{1}{\max(\Delta T, 0.1)}$ will provide superior early warning for Heat Dissipation Failures compared to raw temperatures alone.
2. **Hypothesis 2 (Piece-wise Linear RUL Degradation)**:
   Turbofan degradation follows a stable baseline for the first $50\text{--}60\%$ of operating life, after which degradation accelerates exponentially.
3. **Hypothesis 3 (Secondary Bottleneck Queuing)**:
   Dispatch delays $> 10$ minutes on an upstream machine cause exponential queue growth at downstream buffer stages when machine utilization exceeds 85%.

---

## 5. External & Configured Operational Assumptions

The following operational and financial parameters are **configured MSME assumptions** (defined in `configs/factory_defaults.yaml`), not empirical dataset discoveries:
- **Downtime Cost Rate**: Set at **₹4,500.00 / hour** (heuristic MSME composite benchmark).
- **Base Electricity Tariff**: Set at **₹8.50 / kWh** (standard industrial tariff in India).
- **Peak Electricity Tariff Window**: Assumed as **18:00 to 22:00** at **₹12.50 / kWh** (state electricity board peak tariff structure).
- **Scrap Material Rate**: Assumed at **₹350.00 / kg**.
- **Factory Health Score Initial Weights**: Machine Health (0.35), Production Efficiency (0.25), Maintenance Condition (0.20), Energy Performance (0.10), Quality Yield (0.10) — *subject to calibration*.

---

## 6. Strict Data Leakage Guardrails

To preserve academic integrity, the following rules must be enforced across all preprocessing and model training code:

| Dataset | Leaking Column(s) | Mechanism | Mandated Preprocessing Action |
| :--- | :--- | :--- | :--- |
| `01_AI4I_2020` | `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | Component failure flags directly imply failure event | Drop from feature matrix $X$; reserve exclusively for root-cause multi-label diagnosis |
| `01_AI4I_2020` | `UDI` | Arbitrary row index | Drop completely |
| `02_NASA_CMAPSS`| Temporal run-to-failure series | Shuffling contiguous engine cycles between train/test | Split strictly by engine `unit_number` groups |
| `03_UCI_SECOM` | 41,951 missing entries | Imputation fitted globally across all data | Pipeline isolation: fit imputers and scalers strictly on $X_{\text{train}}$ |
| `05_INDUSTRIAL_IOT` | `Remaining_Useful_Life_days` | Values $\le 7.0$ deterministically define 7-day failure | Drop from feature matrix $X$ when predicting `Failure_Within_7_Days` |
| `06_MANUFACTURING_PRODUCTION` | `Actual_End` | Event occurs only after job execution | Exclude from scheduling dispatch inference |
| `08_MANUFACTURING_DEFECTS` | `DefectRate`, `QualityScore` | Post-inspection aggregated metrics | Exclude when predicting defect risk from pre-process parameters |

---

## 7. Implications for Phase 4 (Unified Factory Data Schema)

EDA findings confirm that isolated tables cannot capture manufacturing cause-and-effect. The Unified Factory Schema in Phase 4 must integrate:

1. **`machines`**: Baselines (Design Cycle Time, Baseline Power, Vibration thresholds: Normal $<3.8$ mm/s, Warning $3.8\text{--}5.5$ mm/s, Critical $\ge 5.5$ mm/s).
2. **`sensor_readings`**: High-frequency telemetry synchronized across Vibration, Temperature, RPM, Torque, and Power.
3. **`production_jobs`**: Job scheduling, assigned machines, start delays, queue lengths, and operation types.
4. **`maintenance_records`**: Component wear logs, technician notes, failure modes, and downtime hours.
5. **`financial_parameters`**: Machine downtime hourly cost (₹4,500/hr) and tariff rates (₹8.50/kWh base, ₹12.50/kWh peak).

### Supporting Evidence for the Machine 2 Scenario
The empirical data provides concrete evidence supporting the plausibility of Group 59's Machine 2 scenario:
- Sensor drift and wear accumulation occur prior to catastrophic stops (`AI4I`, `C-MAPSS`).
- Vibration shifts and dispatch delays correlate with elevated failure rates and job delays (`IoT`, `Hybrid`).
- Converting operational delays into downtime hours and multiplying by the MSME downtime tariff creates a concrete, actionable financial metric in Indian Rupees.
