# NirmaanAI Master Dataset Registry

This document serves as the single source of truth for all datasets utilized within the NirmaanAI platform.

---

## 1. Master Dataset Inventory & Status

| Dataset ID & Name | Source Archive / Origin | License | Destination Folder | Rows | Cols | Primary Target | NirmaanAI Module | Preprocessing Status | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01_AI4I_2020** | UCI ML Repository (S. Matzka, 2020) | CC BY 4.0 | `DATASET/01_AI4I_2020/raw/` | 10,000 | 14 | `Machine failure` (0/1) | Phase 6 (Predictive Maintenance), Phase 11 (SHAP) | Pending (Phase 2) | Registered |
| **02_NASA_CMAPSS** | NASA Ames Prognostics (Saxena & Goebel, 2008) | Open Access / Public | `DATASET/02_NASA_CMAPSS/raw/CMaps/` | 265,256 | 26 | `RUL` (Cycles to failure) | Phase 6 (RUL Submodule), Phase 13 (Health Score) | Pending (Phase 2) | Registered |
| **03_UCI_SECOM** | UCI ML Repository (McCann & Johnston, 2008) | Open Access | `DATASET/03_UCI_SECOM/raw/` | 1,567 | 592 | `Pass/Fail` (-1 / +1) | Phase 7 (Anomaly Detection & Screening) | Pending (Phase 2) | Registered |
| **04_ENERGY** | UCI ML Repository (A. Trindade, 2015) | Open Access | `DATASET/04_ENERGY/raw/` | 140,257 | 371 | Load kW time-series | Phase 9 (Forecasting), Phase 14 (Loss Analysis) | Pending (Phase 2) | Registered |
| **05_INDUSTRIAL_IOT** | Kaggle Open Data (Factory Sensor Simulator 2040) | Public Domain (CC0) | `DATASET/05_INDUSTRIAL_IOT/raw/` | 500,000 | 22 | `Failure_Within_7_Days` | Phase 6 (PdM), Phase 7 (Anomaly), Phase 13 (Health) | Pending (Phase 2) | Registered |
| **06_MANUFACTURING_PRODUCTION** | Kaggle Open Data (Hybrid Manufacturing) | Open Access | `DATASET/06_MANUFACTURING_PRODUCTION/raw/` | 1,000 | 13 | `Job_Status` / Delays | Phase 8 (Bottlenecks), Phase 16 (Simulation) | Pending (Phase 2) | Registered |
| **07_FACTORY_OEE_DOWNTIME** | Kaggle Open Data (C. Grove) | CC0-1.0 | `DATASET/07_FACTORY_OEE_DOWNTIME/documentation/` | Metadata | - | OEE / Downtime Pareto | Phase 4 (Unified Schema Blueprint), Phase 5 (Synthetic) | Pending (Phase 2) | Schema Cataloged |
| **08_MANUFACTURING_DEFECTS** | Kaggle Open Data | Open Access | `DATASET/08_MANUFACTURING_DEFECTS/raw/` | 3,240 | 17 | `DefectStatus` (0/1) | Phase 10 (Inventory), Phase 14 (Financial Loss) | Pending (Phase 2) | Registered |
| **09_TEXTILE_MANUFACTURING** | Synthetic MSME Shop Floor Generator | Proprietary / Open | `DATASET/09_TEXTILE_MANUFACTURING/synthetic/` | TBD | TBD | Vibration $\rightarrow$ Cycle slowdown | Phase 5 (Synthetic Factory), Phase 8 (Bottleneck) | Planned (Phase 5) | Designed |
| **10_SYNTHETIC_FACTORY** | Integrated NirmaanAI Engine | Proprietary | `DATASET/10_SYNTHETIC_FACTORY/synthetic/` | Configurable | Schema | Multi-layer Factory State | Full Platform End-to-End Demonstration | Planned (Phase 5) | Designed |
| **11_MAINTENANCE_KNOWLEDGE** | Public MSME Equipment Manuals & SOPs | Public Domain / Fair Use | `DATASET/11_MAINTENANCE_KNOWLEDGE/raw/` | Text / PDF | Unstructured | Semantic Retrieval | Phase 19 (RAG Memory), Phase 20 (Copilot) | Planned (Phase 19) | Outlined |

---

## 2. Dataset Detailed Profiles & Leakage Guardrails

### 01_AI4I_2020 Predictive Maintenance
- **File**: `ai4i2020.csv`
- **Rows**: 10,000 | **Columns**: 14
- **Primary Features**: `Type`, `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, `Tool wear [min]`
- **Targets**: `Machine failure` (3.39% positive class), `TWF`, `HDF`, `PWF`, `OSF`, `RNF`
- **Critical Leakage Guardrail**: Component failure flags (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) directly imply `Machine failure = 1`. They must strictly be excluded when training binary failure prediction models. `UDI` is an arbitrary row index and must be dropped.

### 02_NASA_CMAPSS Turbofan Engine Degradation
- **Files**: `train_FD001.txt` .. `train_FD004.txt`, `test_FD001.txt` .. `test_FD004.txt`, `RUL_FD001.txt` .. `RUL_FD004.txt`
- **Total Sensor Records**: 265,256 rows across 4 operating regimes
- **Features**: 3 operational settings + 21 sensor measurements per time cycle
- **Target**: Remaining Useful Life (`RUL`) in operating cycles
- **Critical Leakage Guardrail**: Unit trajectories are time-dependent run-to-failure series. Data splits must be performed on engine `unit_number` groups rather than random shuffling to prevent temporal train-test leakage.

### 03_UCI_SECOM Semiconductor Process
- **File**: `uci-secom.csv`
- **Rows**: 1,567 | **Columns**: 592 (`Time`, 590 sensors, `Pass/Fail`)
- **Target**: `Pass/Fail` (-1 = Pass [93.36%], 1 = Fail [6.64%])
- **Critical Leakage Guardrail**: High missingness (41,951 nulls across 538 features). Missing value imputation and low-variance feature selection must strictly be fitted on training folds only.

### 04_ENERGY (Electricity Load Diagrams 2011-2014)
- **File**: `LD2011_2014.txt`
- **Rows**: 140,257 timestamps (15-minute intervals) | **Columns**: 371
- **Target**: Electrical power consumption (kW)
- **Critical Leakage Guardrail**: Time-series cross-validation (rolling forward-chaining) without random temporal shuffling.

### 05_INDUSTRIAL_IOT (Factory Sensor Simulator 2040)
- **File**: `factory_sensor_simulator_2040.csv`
- **Rows**: 500,000 | **Columns**: 22
- **Features**: Vibration, temperature, sound, oil level, coolant level, power consumption, operational hours
- **Targets**: `Failure_Within_7_Days` (Binary, 6.0% positive), `Remaining_Useful_Life_days` (Continuous)
- **Critical Leakage Guardrail**: `Remaining_Useful_Life_days` deterministically leaks `Failure_Within_7_Days` for values $\le 7$. It must be dropped when training classification models for the 7-day failure window.

### 06_MANUFACTURING_PRODUCTION (Hybrid Manufacturing Categorical)
- **File**: `hybrid_manufacturing_categorical.csv`
- **Rows**: 1,000 | **Columns**: 13
- **Features**: `Job_ID`, `Machine_ID`, `Operation_Type`, `Processing_Time`, `Scheduled_Start`, `Actual_Start`
- **Targets**: `Job_Status` ('Completed', 'Delayed', 'Failed')
- **Critical Leakage Guardrail**: `Actual_End` occurs after job termination and cannot be used at scheduling time.

### 08_MANUFACTURING_DEFECTS
- **File**: `manufacturing_defect_dataset.csv`
- **Rows**: 3,240 | **Columns**: 17
- **Features**: `ProductionVolume`, `ProductionCost`, `SupplierQuality`, `DeliveryDelay`, `MaintenanceHours`, `DowntimePercentage`, `InventoryTurnover`, `StockoutRate`
- **Target**: `DefectStatus` (1: 84.04%, 0: 15.96%)
- **Critical Leakage Guardrail**: Post-inspection metrics (`DefectRate`, `QualityScore`) must be segregated from operational predictors.
