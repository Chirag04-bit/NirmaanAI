# NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Academic-green.svg)]()

---

## Academic & Institutional Identity

- **Institution**: Institute of Engineering & Management (IEM), Kolkata
- **Department**: Department of Computer Science & Engineering (Artificial Intelligence)
- **Project Group**: 59
- **Project Guide**: **PROF. KUNTAL MONDAL**
- **Initiative Alignment**: MSME Idea Hackathon 6.0 | Industry 4.0 & 5.0 | Make in India & Atmanirbhar Bharat

---

## Executive Summary

**NirmaanAI** is an AI-powered manufacturing intelligence and decision platform designed as a digital "Factory Brain" for Indian Manufacturing MSMEs. 

While conventional ERP and SCADA systems act as passive recording repositories, NirmaanAI actively analyzes machine telemetry, production schedules, vibration, and energy signals to deliver closed-loop decision support:

$$\mathbf{Telemetry} \longrightarrow \mathbf{Prediction} \longrightarrow \mathbf{Explanation} \longrightarrow \mathbf{Financial\ Impact\ (INR)} \longrightarrow \mathbf{Simulation} \longrightarrow \mathbf{Actionable\ Recommendation}$$

### Primary MSME Focus
- **Textile Manufacturing MSMEs** (Loom telemetry, motor vibration, cycle variation, power optimization).
- **Precision Automotive Component MSMEs** (CNC turning, VMC milling, tool wear degradation, scrap & rework minimization).

---

## Core Closed-Loop Pipeline

1. **Multi-Source Factory Telemetry**: Ingestion of machine vibration, operating temperatures, motor speeds, tool wear, energy load, and job logs.
2. **Predictive Maintenance & Anomaly Detection**: 7-day machine failure risk classification, Remaining Useful Life (RUL) estimation, and multivariate anomaly isolation.
3. **Explainable AI (XAI)**: SHAP-based feature attribution translating statistical outputs into physical factory symptoms.
4. **Root Cause Identification**: Attribution of failure and bottleneck candidates (e.g., Heat Dissipation Failure, Bearing Degradation, Overstrain).
5. **Operational & Financial Impact**: Translation of machine downtime, excess cycle times, and scrap into quantified Indian Rupee (INR) losses.
6. **Digital-Twin-Inspired What-If Simulation**: Scenario modeling to evaluate operational interventions prior to execution.
7. **Actionable Recommendation Engine**: Human-in-the-loop prescriptive maintenance and scheduling directives.
8. **AI Factory Copilot (RAG)**: LLM assistant grounded in shop-floor telemetry, historical failure records, and machinery SOPs.
9. **Unified Dashboard**: Real-time operational command center built with React and Vite.

---

## System Architecture

```
C:\NIRMAAN AI
│
├── DATASET\                      # Working master datasets (organized per module)
│
├── data\                         # Operational data partitions
│   ├── raw\                      # Raw ingested data
│   ├── processed\                # Cleaned, standardized arrays
│   ├── synthetic\                # MSME shop-floor synthetic generator outputs
│   └── external\                 # External benchmarks and tariffs
│
├── notebooks\                    # Exploratory data analysis (EDA) & research prototypes
│
├── src\                          # Production application source code
│   ├── data\                     # Ingestion, validation, and loaders
│   ├── features\                 # Feature engineering & scaling pipelines
│   ├── models\                   # ML models (Classification, Regression, Forecasting)
│   ├── explainability\           # SHAP explainability & attribution modules
│   ├── decision\                 # Health scores, loss calculators, recommendation rules
│   └── utils\                    # Logging, config loaders, and reproducibility helpers
│
├── models\                       # Serialized trained model weights & scalers
├── backend\                      # FastAPI backend application & API routes
├── frontend\                     # React + Vite dashboard web application
├── rag\                          # RAG document store, embeddings, and vector database
├── tests\                        # Unit, integration, and data validation test suites
├── docs\                         # Technical specifications, dataset registry, research notes
├── configs\                      # System and factory parameter configuration files
├── experiments\                  # Experiment tracking logs and evaluation artifacts
└── logs\                         # Application execution logs
```

---

## Master Phase Roadmap

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 0** | Project Audit & Existing Work Inspection | **COMPLETED** |
| **Phase 1** | Project Foundation & Scaffolding | **COMPLETED** |
| **Phase 2** | Dataset Collection & Organization | **COMPLETED** |
| **Phase 3** | Data Understanding & Exploratory Data Analysis (EDA) | **COMPLETED** |
| **Phase 4** | Unified Factory Data Schema | **COMPLETED** |
| **Phase 5** | Synthetic Factory Dataset Generator | **COMPLETED** |
| **Phase 6** | Predictive Maintenance (Failure Classification & RUL Regression) | **COMPLETED** |
| **Phase 7** | Multi-Sensor Anomaly Detection (Unsupervised PCA & Baseline Benchmark) | **COMPLETED** |
| **Phase 8** | Production Bottleneck Prediction & Flow Intelligence | **COMPLETED** |
| **Phase 9** | Production & Energy Forecasting | **COMPLETED** |
| **Phase 10** | Smart Inventory Intelligence | **COMPLETED** |
| **Phase 11** | Explainable AI & SHAP Feature Attribution | **COMPLETED** |
| **Phase 12** | Root Cause Analysis Engine | **COMPLETED** |
| **Phase 13** | Composite Factory Health Score | **COMPLETED** |
| **Phase 14** | Operational & Financial Loss Analysis (INR) | Planned |
| **Phase 15** | Prescriptive Recommendation Engine | Planned |
| **Phase 16** | Digital-Twin-Inspired What-If Simulation | Planned |
| **Phase 17** | PostgreSQL Relational Database Layer | Planned |
| **Phase 18** | FastAPI Asynchronous Backend Services | Planned |
| **Phase 19** | Factory Knowledge Memory (RAG Ingestion) | Planned |
| **Phase 20** | Grounded AI Factory Copilot | Planned |
| **Phase 21** | React + Vite Executive Dashboard | Planned |
| **Phase 22** | Full End-to-End System Integration | Planned |
| **Phase 23** | Comprehensive Testing & Validation | Planned |
| **Phase 24** | Dockerization & Deployment Packaging | Planned |
| **Phase 25** | Final Documentation & Research Packaging | Planned |

---

## Deployed Intelligence Subsystems (Phases 6–12)

### 1. Predictive Maintenance (Phase 6)
- **Failure Classification**: XGBoost Champion (Precision: 0.9545, Recall: 0.8235, F1: 0.8842, ROC-AUC: 0.9831) on AI4I 2020. Strict leakage exclusion of tool wear modes and identifiers.
- **RUL Regression**: Random Forest Champion (RMSE: 18.11 cycles, MAE: 13.21, $R^2$: 0.7957) on NASA C-MAPSS FD001. Grouped engine unit splitting and causal 5-cycle rolling statistics.
- **Service Layer**: `PredictiveMaintenanceService` exposing failure risk probabilities and remaining cycle estimates.

### 2. Multi-Sensor Anomaly Detection (Phase 7)
- **Unsupervised Telemetry Monitoring**: PCA Reconstruction Error Champion (F1: 0.9859, Precision: 0.9722, Recall: 1.0000, PR-AUC: 0.9965) trained on unpolluted reference normal operations (Days 1–15).
- **Threshold Calibration**: 99th percentile validation calibration yielding an observed 1.04% false-positive rate.
- **Early Warning**: Detected 1/1 true synthetic degradation event with 106.5 hours (4.44 days) early warning lead time.
- **Service Layer**: `AnomalyDetectionService` maintaining causal rolling buffers and top-contributing sensor diagnostics.

### 3. Bottleneck Prediction & Flow Intelligence (Phase 8)
- **Production Flow Forecasting**: Domain-informed heuristic flow baseline predicting upcoming job bottlenecks and cycle time expansions at dispatch time ($t \le t_{\text{scheduled\_start}}$).
- **Zero-Lookahead Feature Engineering**: Strictly causal prior cycle ratios, dispatch delays, and 1-hour pre-dispatch sensor telemetry.
- **Cold-Start Integrity**: Explicitly accounts for zero positive bottleneck cases during initial nominal operations, demonstrating why domain physical priors are essential prior to historical failure accumulation.
- **Service Layer**: `BottleneckService` evaluating real-time line states (`NOMINAL_FLOW`, `MODERATE_CONGESTION`, `CRITICAL_BOTTLENECK`) and identifying active constraint stations.

### 4. Production & Energy Forecasting (Phase 9)
- **Empirical Grid Load Benchmark**: XGBoost Champion on UCI Electricity Load (Client `MT_124`, 1-hour resolution) achieving RMSE of 26.23 kW, WAPE of 6.50%, and $R^2$ of 0.9605 across 26,281 chronological timestamps.
- **Shop-Floor Plant Power & Tariff Costing**: Multi-machine active power demand forecasting coupled with Indian MSME tariff rules (Base ₹8.50/kWh, Peak ₹12.50/kWh during 18:00–22:00) with 0.01% financial cost estimation error over holdout test data.
- **Production Throughput**: Causal daily completed unit volume forecasting (Ridge Champion: 10.52 units RMSE, 0.77% WAPE, $R^2 = 0.9938$).
- **Service Layer**: `ForecastingService` providing multi-horizon power forecasting, shift-level electricity expenditure projections (INR), and peak tariff operational alerts.

### 5. Smart Inventory Intelligence & Operations Research (Phase 10)
- **Operations Research Optimization Core**: Deterministic dynamic Safety Stock ($SS = Z \sqrt{\bar{L} \sigma_d^2 + \bar{d}^2 \sigma_L^2}$), Reorder Point ($ROP = \bar{d} \bar{L} + SS$), Economic Order Quantity ($EOQ = \sqrt{2DS/H}$), and Days of Supply ($DoS = \text{Current Stock}/\bar{d}$) with $Z=1.645$ (95% standard raw materials) and $Z=2.326$ (99% critical spares/tooling).
- **Machine 2 Maintenance-Spare Coupling**: Direct operational coupling between Phase 6 failure alerts (empirical threshold $\tau=0.91$) or synthetic vibration excursions ($\ge 3.80\text{ mm/s}$) and `SKU_SPINDLE_BEARING_M2` stock levels. Identifies constrained maintenance when 7-day vendor replenishment lead time cannot arrive before required servicing.
- **Five-Tier Shortage Risk Model**: Actionable categorization across `OUT_OF_STOCK`, `CRITICAL_DEFICIT`, `REORDER_NOW`, `OPTIMAL_BUFFER`, and `SURPLUS_INVENTORY`.
- **Service Layer**: `InventoryService` exposing single-SKU audits, plant-wide working capital summaries (INR), and machine maintenance-spare evaluations.

### 6. Explainable AI & SHAP Feature Attribution (Phase 11)
- **Model Attribution Core**: Exact TreeExplainer integration attributing AI4I XGBoost equipment alerts in additive log-odds margin space ($|\text{margin} - (\text{base} + \sum \text{SHAP})| = 0.0$) with calibrated logistic sigmoid mapping to probability, preserving Phase 6 decision threshold $\tau = 0.91$.
- **NASA C-MAPSS RUL Attribution**: Random Forest TreeExplainer attributing remaining life in operational cycles (base value $\approx 86.52\text{ cycles}$; top degradation drivers: LPT exhaust temperature `s4_roll_mean` and physical core speed `s9_roll_mean`).
- **Four-Quadrant Local Audits**: Systematic analysis of actual holdout test samples across True Positives, True Negatives, False Positives (high tool wear survival), and False Negatives (moderate tool wear suppression).
- **Machine 2 Synthetic Investigation**: Evaluates model feature sensitivity on simulated digital twin telemetry with explicit distribution-shift notices and strict causality disclaimers (model attribution $\neq$ physical causality).
- **Service Layer**: `ExplanationService` generating human-readable manufacturing narratives and Pydantic v2 schemas for real-time attribution without model retraining.

### 7. Root Cause Analysis Engine (Phase 12)
- **Evidence-Based RCA Core**: Fuses heterogeneous signals from Phase 6 (prediction $\tau=0.91$), Phase 7 (anomaly score $\tau=0.2405$), Phase 8 (cycle ratio & bottleneck state), Phase 10 (spare availability), and Phase 11 (SHAP feature attribution).
- **Controlled Taxonomy & Machine Baselines**: 13 operational candidate cause categories normalized against machine-specific operating baselines (M1–M5) to account for distribution mismatch.
- **Temporal Precedence & Causal Ordering**: Verifies precursor progression ($t_0 \le t_1 \le t_2 \le t_3$) with strict lookahead leakage exclusion ($t \le t_{\text{event}}$).
- **Contradiction Penalties & Negative Control**: Explicitly penalizes candidate causes when expected physical indicators are nominal, demonstrating that SHAP model attribution alone does NOT constitute root cause analysis.
- **Service Layer**: `RootCauseAnalysisService` providing deterministic event analysis, controlled synthetic degradation scenario reconstruction, and human-readable audit reports with strict scientific disclaimers.

### 8. Factory Health Score Subsystem (Phase 13)
- **Multi-Signal Operational Health Core**: Deterministic, bounded ($0\text{--}100$) health score aggregating 6 validated dimensions: Predictive Failure Risk ($0.25$), Multi-Sensor Anomaly Health ($0.20$), Production Flow & Bottleneck ($0.20$), Energy Deviation ($0.10$), Maintenance & Spare Context ($0.10$), and Diagnostic Consistency ($0.15$).
- **Double-Counting Safeguards**: SHAP is strictly assigned $0.00$ weight in scoring (exclusive to explanatory diagnostics); RCA acts as an operational diagnostic-severity modifier rather than re-penalizing raw sensor telemetry.
- **Factory-Level Aggregation & Critical Asset Constraint**: Equal baseline weighting ($0.20$ per machine for M1–M5) with $\arg\min_m H_m$ isolation. Automatic plant status override caps factory health at `WATCH` if any machine is `CRITICAL`, preventing healthy machines from masking active station breakdowns.
- **Dynamic Renormalization & Missing Data**: Explicit coverage tracking with proportional weight renormalization for partial evidence ($[40\%, 99.9\%]$) and hard override to `INSUFFICIENT_DATA` (score $0.0$, `LOW` confidence) when coverage $< 40\%$.
- **Temporal Causal Filtering**: Strictly causal $H(t) \le t$ evaluation preventing future maintenance leakage or lookahead bias.
- **Service Layer**: `FactoryHealthService` exposing machine assessments, plant-wide aggregations, historical trend evaluations, and human-readable markdown reports.

---

## Setup & Getting Started

### Prerequisites
- Python 3.14+ (or Python 3.10+)
- Node.js v20+ & npm
- Git

### Installation
```powershell
# Clone or navigate to workspace
cd "C:\NIRMAAN AI"

# Install Python dependencies
pip install -r requirements.txt

# Run complete system test suite (143 tests across Phases 0-13)
python -m pytest tests/ -v

# Train / Evaluate individual intelligence subsystems
python -m src.models.train_pdm            # Phase 6: Predictive Maintenance
python -m src.models.train_anomaly        # Phase 7: Anomaly Detection
python -m src.models.train_bottleneck     # Phase 8: Bottleneck Prediction
python -m src.models.train_forecaster     # Phase 9: Production & Energy Forecasting
python -m src.models.train_inventory      # Phase 10: Smart Inventory Intelligence
python -m src.models.train_explainability # Phase 11: Explainable AI & SHAP
python -m src.models.evaluate_rca         # Phase 12: Root Cause Analysis
python -m src.models.evaluate_health      # Phase 13: Factory Health Score
```
