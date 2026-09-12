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
| **Phase 9** | Production & Energy Forecasting | Planned |
| **Phase 10** | Smart Inventory Intelligence | Planned |
| **Phase 11** | Explainable AI & SHAP Feature Attribution | Planned |
| **Phase 12** | Root Cause Analysis Engine | Planned |
| **Phase 13** | Composite Factory Health Score | Planned |
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

## Deployed Intelligence Subsystems (Phases 6–8)

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

# Run complete system test suite (61 tests across Phases 0-8)
python -m pytest tests/ -v

# Train / Evaluate individual intelligence subsystems
python -m src.models.train_pdm         # Phase 6: Predictive Maintenance
python -m src.models.train_anomaly     # Phase 7: Anomaly Detection
python -m src.models.train_bottleneck  # Phase 8: Bottleneck Prediction
```
