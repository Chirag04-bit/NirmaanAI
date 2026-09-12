# NirmaanAI Master Dataset Registry

This document serves as the formal and verified catalog of all data assets utilized, planned, or referenced in the NirmaanAI platform.

---

## 1. Classification Overview

To maintain scientific integrity and prevent fabricated claims, datasets are partitioned into five mutually exclusive categories:
1. **LOCALLY PRESENT (RAW DATA AVAILABLE)**: Datasets physically verified and present in `C:\Users\user\OneDrive\Desktop\NIRMAAN\DATASET`.
2. **SCHEMA-ONLY / METADATA RESOURCE**: Datasets where schemas, READMEs, or parameters exist, but raw operational CSV/records are unavailable locally.
3. **PLANNED SYNTHETIC GENERATION**: Datasets to be mathematically simulated in future phases using domain rules and reproducible seeds.
4. **PLANNED KNOWLEDGE / RAG CORPUS**: Unstructured technical manuals, SOPs, and troubleshooting records to be curated in Phase 19.
5. **RECOMMENDED / EXTERNAL CANDIDATES**: Relevant external benchmarks not currently present locally (require explicit user approval before downloading).

---

## 2. Master Dataset Catalog

### Category A: Locally Present Datasets (Raw Data Verified)
*Source location: `C:\Users\user\OneDrive\Desktop\NIRMAAN\DATASET`*

| ID | Dataset Name | Source Archive | License | Verified Rows | Verified Cols | Primary Target | NirmaanAI Module | Ingestion Plan |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **AI4I 2020 Predictive Maintenance** | `ai4i+2020+predictive+maintenance+dataset.zip` & `archive.zip` | CC BY 4.0 | 10,000 | 14 | `Machine failure` (0/1) | Phase 6 (PdM), Phase 11 (SHAP), Phase 12 (Root Cause) | Copy & unpack into `DATASET/01_AI4I_2020/raw/` in Phase 2 |
| **02** | **NASA C-MAPSS Turbofan Degradation** | `archive (1).zip` | NASA Open Data | 265,256 (all 4 subsets) | 26 | `RUL` (Remaining Useful Life in cycles) | Phase 6 (RUL Submodule), Phase 13 (Health Score) | Copy & unpack into `DATASET/02_NASA_CMAPSS/raw/` in Phase 2 |
| **03** | **UCI SECOM Semiconductor Process** | `archive (2).zip` (`uci-secom.csv`) & `secom.zip` | Open Access | 1,567 | 592 | `Pass/Fail` (-1 / +1) | Phase 7 (Anomaly Detection & Multi-Sensor Screening) | Copy & unpack into `DATASET/03_UCI_SECOM/raw/` in Phase 2 |
| **04** | **Electricity Load Diagrams 2011-2014** | `electricityloaddiagrams20112014.zip` | Open Access | 140,257 | 371 | Load kW time-series (15-min intervals) | Phase 9 (Energy Forecasting), Phase 14 (Financial Loss) | Copy & unpack into `DATASET/04_ENERGY/raw/` in Phase 2 |
| **05** | **Factory Sensor Simulator 2040** | `archive (3).zip` | CC0 Public Domain | 500,000 | 22 | `Failure_Within_7_Days` (0/1) | Phase 6 (PdM), Phase 7 (Anomaly), Phase 13 (Health) | Copy & unpack into `DATASET/05_INDUSTRIAL_IOT/raw/` in Phase 2 |
| **06** | **Hybrid Manufacturing Categorical** | `archive (6).zip` | Open Access | 1,000 | 13 | `Job_Status` ('Completed', 'Delayed', 'Failed') | Phase 8 (Bottleneck Prediction), Phase 16 (Simulation) | Copy & unpack into `DATASET/06_MANUFACTURING_PRODUCTION/raw/` in Phase 2 |
| **08** | **Manufacturing Defect Dataset** | `archive (4).zip` | Open Access | 3,240 | 17 | `DefectStatus` (0/1) | Phase 10 (Inventory Intelligence), Phase 14 (Loss Analysis) | Copy & unpack into `DATASET/08_MANUFACTURING_DEFECTS/raw/` in Phase 2 |

---

### Category B: Archive / Schema-Only Resource (Raw Data Unavailable Locally)
| ID | Dataset Name | Source Archive | License | Available Assets | Missing Assets | Intended Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **07** | **Factory OEE & Downtime Starter** | `archive (5).zip` | CC0-1.0 | `README.md`, `LICENSE`, `dataset-metadata.json`, `cover.png` | `factory_synth_minutely.csv`, `oee_by_day.csv`, `oee_by_shift.csv`, `downtime_pareto.csv`, `spc_xbar_r.csv` | Blueprint for Phase 4 Unified Schema and Phase 5 OEE calculations |

*Audit Note: The raw time-series CSVs were not packaged in this archive. It will be treated strictly as a schema and metric specification document.*

---

### Category C: Planned Synthetic Datasets (To Be Generated)
| ID | Planned Dataset Name | Target Vertical | Generation Phase | Synthetic Mechanism | Operational Purpose | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **09** | **Textile MSME Shop Floor Dataset** | Textile Weaving / Spinning MSME | Phase 5 | Mathematical degradation curves + noise | Simulates loom motor vibration rise $\rightarrow$ cycle slowdown $\rightarrow$ line bottleneck $\rightarrow$ rupee loss | Planned (Phase 5) |
| **10** | **Integrated Factory Digital Twin Dataset** | Discrete Auto-Components MSME | Phase 5 | Interconnected multi-machine queue simulator | End-to-end integration across telemetry, maintenance, inventory, and finance | Planned (Phase 5) |

*Audit Note: These datasets do not yet exist. They will be generated strictly in Phase 5 with fully documented equations and reproducible random seeds.*

---

### Category D: Planned Maintenance & Knowledge Corpora (To Be Curated)
| ID | Resource Name | Target Equipment | Target Phase | Document Types | Purpose | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **11** | **Factory Maintenance Knowledge Corpus** | CNC Turning, VMC Milling, Textile Looms | Phase 19 | Machine operation manuals, SOPs, troubleshooting guides | Vector indexing for RAG Factory Memory & AI Copilot | Planned (Phase 19) |

*Audit Note: Equipment SOPs and manuals will be curated and placed in `C:\NIRMAAN AI\rag\documents\` in Phase 19.*

---

### Category E: Recommended External Candidates (Not Present - Approval Required)
If empirical gaps arise during Phase 6–10, candidates (such as CNC milling tool wear datasets from Kaggle/UCI) will be formally proposed via a `DATASET ADDITION PROPOSAL` and will not be downloaded without explicit user approval.

---

## 3. Data Leakage Guardrails for Local Datasets

1. **AI4I 2020 (`01_AI4I_2020`)**:
   - Failure mode indicators (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) directly imply `Machine failure = 1`.
   - *Guardrail*: Mask all failure mode columns when training binary failure prediction models. Use them solely for root-cause multi-label diagnosis. Drop `UDI` index.

2. **NASA C-MAPSS (`02_NASA_CMAPSS`)**:
   - Run-to-failure multi-cycle degradation.
   - *Guardrail*: Do not perform random row-level train-test splits. Split strictly by `unit_number` engine trajectories to prevent temporal train-test leakage.

3. **UCI SECOM (`03_UCI_SECOM`)**:
   - 590 sensors with 41,951 missing entries.
   - *Guardrail*: Imputation, standardization, and variance thresholding must be fit exclusively on training folds.

4. **Factory Sensor Simulator 2040 (`05_INDUSTRIAL_IOT`)**:
   - `Remaining_Useful_Life_days` deterministically leaks `Failure_Within_7_Days` when $\le 7$.
   - *Guardrail*: Exclude `Remaining_Useful_Life_days` when predicting failure within the 7-day operational window.

5. **Hybrid Manufacturing (`06_MANUFACTURING_PRODUCTION`)**:
   - `Actual_End` occurs after job termination.
   - *Guardrail*: Exclude `Actual_End` and downstream post-job flags at scheduling inference time.

6. **Manufacturing Defects (`08_MANUFACTURING_DEFECTS`)**:
   - `DefectRate` and `QualityScore` are post-production inspection outcomes.
   - *Guardrail*: Segregate operational equipment parameters from inspection quality metrics.
