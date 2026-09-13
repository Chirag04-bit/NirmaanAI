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
│   ├── db\                       # PostgreSQL & SQLAlchemy persistence models & seeder
│   └── utils\                    # Logging, config loaders, and reproducibility helpers
│
├── alembic\                      # Alembic schema migrations & versioned DDL
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
| **Phase 14** | Operational & Financial Loss Analysis (INR) | **COMPLETED** |
| **Phase 15** | Prescriptive Recommendation Engine | **COMPLETED** |
| **Phase 16** | Digital-Twin-Inspired What-If Simulation | **COMPLETED** |
| **Phase 17** | PostgreSQL Data Persistence & Production Layer | **VERIFIED (HOLD — ENV BLOCKED)** |
| **Phase 18** | FastAPI Asynchronous Backend Services | **VERIFIED (HOLD — ENV BLOCKED)** |
| **Phase 19** | Factory Knowledge Memory / Grounded RAG Engine | **COMPLETED & LOCKED** |
| **Phase 20** | Grounded AI Factory Copilot Subsystem | **COMPLETED & LOCKED** |
| **Phase 21** | React + Vite Executive Dashboard | **COMPLETED & LOCKED** |
| **Phase 22** | Full End-to-End System Integration | **COMPLETED & LOCKED (HOLD — ENV BLOCKED)** |
| **Phase 23** | Comprehensive Testing & Validation | Planned (Next Phase) |
| **Phase 24** | Dockerization & Deployment Packaging | Planned |
| **Phase 25** | Final Documentation & Research Packaging | Planned |

---

## Deployed Intelligence Subsystems (Phases 6–17)

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

### 9. Operational & Financial Loss Analysis (Phase 14)
- **First-Principles Derivation Core**: Translates physical machine telemetry, maintenance halts, tool wear scrap, and delayed production batches into quantified Indian Rupee (INR) metrics using configured MSME parameters from `factory_defaults.yaml` (Downtime: ₹4,500/hr, Base Electricity: ₹8.50/kWh, Peak: ₹12.50/kWh, Scrap: ₹350/kg, Rework: ₹280/hr, Bottleneck Margin: ₹320/unit).
- **Strict Epistemic Demarcation**: Systematically decomposes all financial outputs across `OBSERVED`, `DERIVED_FROM_OBSERVED`, `CONFIGURED_ASSUMPTION`, `PROJECTED_OPPORTUNITY_COST`, and `CONTROLLED_SYNTHETIC`. Prohibits pseudo-financial shortcuts ($₹ \ne f(\text{Health})$, $₹ \ne f(\text{SHAP})$, zero extra RCA loss).
- **Energy Cost vs Inefficiency**: Strict physical boundary between Total Energy Cost (operational expenditure) and Energy Inefficiency Loss (excess power consumption above rated machine design capacity). Peak tariff schedule (18:00–22:00) is recognized as an external utility schedule, never an equipment fault.
- **Anti-Double-Counting Safeguards**: Non-overlapping exposure calculation isolating downtime fixed overhead from running bottleneck throughput opportunity costs; independent cost-pool separation of raw material scrap from technician rework labor.
- **Controlled Machine 2 Scenario**: Full data-driven accounting of the spindle bearing failure chain, isolating ₹21,280 scrap loss, ₹2,660 rework labor, ₹1,675.83 energy inefficiency, ₹24,320 projected bottleneck opportunity cost during precursor degradation, and ₹11,670 single-event emergency stoppage loss (`MAINT_0003`).
- **Service Layer**: `FinancialLossService` exposing machine assessments ($M_1\text{--}M_5$), plant-wide aggregations, temporal causal queries ($t \le t_{\text{as\_of}}$), and reference reconciliation against `operational_losses.csv`.

### 10. Operational Recommendation Engine (Phase 15)
- **Evidence-Grounded Prescriptive Engine**: Generates transparent, deterministic operational recommendations using a closed 26-action taxonomy across 5 operational categories (`PREVENTIVE_MAINTENANCE`, `PROCESS_OPTIMIZATION`, `INVENTORY_REPLENISHMENT`, `QUALITY_CONTROL`, `ENERGY_MANAGEMENT`).
- **Multi-Signal Rule Activation**: Evaluates Phase 6 failure probability ($\tau=0.91$), Phase 7 PCA anomaly ($\tau=0.24050$), Phase 13 health state (`CRITICAL`, `DEGRADED`, `WATCH`), and Phase 10 inventory contracts (ROP $1.367$, SS $1.134$).
- **Priority & Urgency Matrix**: Actionable ranking across Priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and Urgency (`IMMEDIATE`, `SCHEDULED`, `DEFERRED`) with full physical evidence references.
- **Service Layer**: `RecommendationService` exposing single-machine evaluation, plant-wide filtering, and reproducible rule execution.

### 11. What-If / Digital-Twin-Inspired Simulation Engine (Phase 16)
- **Counterfactual Decision Support**: Evaluates "what would likely happen if a proposed intervention were executed" prior to shop-floor commitment.
- **Strict Temporal Demarcation**: Decision cutoff fixed strictly at `2026-01-21T12:00:00Z`. Retrospective evaluation against Day-22 synthetic ground truth (`MAINT_0003`, 2026-01-22T16:30:00Z).
- **Counterfactual Net Benefit**: Quantifies avoided breakdown losses (₹9,420 avoided loss: ₹9,000 downtime + ₹420 emergency labor) offset by planned service downtime and technician labor (₹2,390), yielding a net counterfactual benefit of **₹7,030**.
- **Epistemic Integrity**: Diagnostic KPIs under intervention (`failure_probability`, `anomaly_score`, `health_score`) are explicitly governed as `NOT_PROJECTABLE` without an empirical physics twin.
- **Service Layer**: `SimulationService` providing scenario generation, comparative cost-benefit evaluation, and markdown executive briefings.

### 12. PostgreSQL Persistence & Production Data Layer (Phase 17)
- **19 Phase 17 Persistence Tables**: Full declarative SQLAlchemy 2.0 schema spanning Core Factory, Operations/Telemetry, and AI/Decision Intelligence.
- **Normalized Simulation Storage**: Dedicated queryable columns for counterfactual metrics and net financial benefit (`net_counterfactual_benefit_inr`, `projected_avoided_breakdown_loss_inr`), eliminating reliance on opaque JSON blobs.
- **Financial Semantic Separation**: Database-level distinction between Realized Loss (₹73,062.28), Baseline Opportunity Cost (₹24,320.00), Gross Financial Exposure (₹97,382.28), and Avoided Opportunity Cost (₹19,520.00).
- **Alembic Migration & Deterministic Seeding**: Reproducible versioned DDL migrations and idempotent database seeder preserving complete upstream provenance and temporal causality.

### 13. FastAPI Asynchronous Backend Services (Phase 18)
- **17 Domain APIRouters**: Production REST API exposing factory topology, live telemetry streams, predictive maintenance alerts, SHAP explanations, RCA fault trees, and prescriptive interventions.
- **Strict Pydantic v2 Contracts**: Full request/response validation with zero untyped JSON blobs, OpenAPI 3.1 documentation (`/docs`, `/redoc`), and robust CORS configuration.
- **Zero-Latency In-Memory Execution**: Seamless fallback to cached in-process intelligence when database persistence is offline.

### 14. Factory Knowledge Memory & Grounded RAG Engine (Phase 19)
- **278 Knowledge Chunks Indexed**: Comprehensive cross-phase technical knowledge base with complete heading hierarchy (`H1 > H2 > H3`), SHA-256 checksums, and source traceability.
- **Deterministic Dense Representation**: Unit-normalized 256-dimensional TF-IDF/SVD vector space ($0.70 \cdot \text{Dense} + 0.30 \cdot \text{Keyword}$) $\times W_{\text{authority}}$ with exact cosine dot-product indexing.
- **Strict Temporal Governance**: Authoritative cutoff locked at `2026-01-21T12:00:00Z`. Isolates post-cutoff synthetic ground truth event `MAINT_0003` from prospective queries to prevent future knowledge leakage.
- **8-Class Epistemic Taxonomy**: Rigorous tracking of `OBSERVED`, `DERIVED`, `MODEL_OUTPUT`, `CONTROLLED_SYNTHETIC`, `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`, `PROJECTED`, `NOT_PROJECTABLE`, and `UNKNOWN`.
- **Anti-Hallucination Guardrails**: Rejects queries targeting unknown assets (`M99`, `FAC_99`), ungrounded events, or unprojectable causal metrics with `NO_SUFFICIENT_EVIDENCE`.

### 15. Grounded AI Factory Copilot Subsystem (Phase 20)
- **Controlled Decision-Support Interface**: Natural-language query interface returning structured, evidence-grounded answers with verbatim citations and confidence metrics.
- **15 Deterministic Operational Intents**: Rule-based intent classification covering health checks, degradation causes, recommendations, inventory availability, financial exposure, and what-if simulation results.
- **Source Authority & Financial Grounding**: Enforces authoritative Phase 14 financials (Realized Loss ₹73,062.28, Opportunity ₹24,320.00, Gross Exposure ₹97,382.28) while automatically filtering out superseded draft figures (₹92,582.28).
- **Counterfactual Limitation Protection**: Rejects uncomputable post-intervention failure probabilities with explicit `NOT_PROJECTABLE` limitations.
- **100% Benchmark Accuracy**: Evaluated across 14 domain and negative test cases with 100% positive accuracy and 100% negative refusal rate. Exposed via `POST /api/v1/copilot/ask`.

### 16. Executive Factory Dashboard (Phase 21)
- **React 19 + Vite 6 Architecture**: Modern, responsive single-page operational command center with sub-second HMR and 170ms production builds.
- **Industrial Vanilla CSS Design System**: Bespoke dark-mode glassmorphic theme with CSS custom properties, responsive grids, micro-animations, and Google Fonts (`Outfit`, `Inter`, `JetBrains Mono`).
- **Fleet Intelligence & Diagnostic Drilldowns**: Radial SVG health gauges for M1–M5, real-time sensor waveforms, SHAP feature attribution waterfalls, and Root Cause Analysis (RCA) diagnostic trees.
- **Smart Inventory & Buffer Management**: Live SKU tracking with safety stock breach alerts (`SKU_SPINDLE_BEARING_M2`) and one-click expedited procurement triggers.
- **Interactive Digital Twin What-If Studio**: Scenario comparison matrix (Scenarios A through E) with dynamic counterfactual financial exposure reduction charts.
- **Embedded Grounded Copilot Interface**: Interactive decision-support assistant with quick-verification chips, verbatim citations, epistemic badges, and explicit boundary guardrails.

---

## Setup & Getting Started

### Prerequisites
- Python 3.14+ (or Python 3.10+)
- PostgreSQL 15+ (optional for production persistence; SQLite supported in-memory for testing)
- Node.js v20+ & npm
- Git

### Installation
```powershell
# Clone or navigate to workspace
cd "C:\NIRMAAN AI"

# Install Python dependencies
pip install -r requirements.txt

# Run complete system test suite (328 tests across Phases 0-20)
python -m pytest tests/ -q

# Run Phase 19 Knowledge Memory / RAG tests
python -m pytest tests/test_knowledge_rag.py -v

# Run Phase 20 AI Factory Copilot tests
python -m pytest tests/test_copilot.py -v

# Run targeted database persistence tests
python -m pytest tests/test_database.py -v

# Apply database migrations (PostgreSQL / SQLite)
python -m alembic upgrade head

# Seed database with deterministic historical factory data
python -m src.db.seed.seeder

# Train / Evaluate individual intelligence subsystems
python -m src.models.train_pdm                 # Phase 6: Predictive Maintenance
python -m src.models.train_anomaly             # Phase 7: Anomaly Detection
python -m src.models.train_bottleneck          # Phase 8: Bottleneck Prediction
python -m src.models.train_forecaster          # Phase 9: Production & Energy Forecasting
python -m src.models.train_inventory           # Phase 10: Smart Inventory Intelligence
python -m src.models.train_explainability      # Phase 11: Explainable AI & SHAP
python -m src.models.evaluate_rca              # Phase 12: Root Cause Analysis
python -m src.models.evaluate_health           # Phase 13: Factory Health Score
python -m src.decision.loss_service            # Phase 14: Financial Loss Accounting
python -m src.models.evaluate_recommendations  # Phase 15: Recommendation Engine
python -m src.models.evaluate_simulation       # Phase 16: What-If Simulation
```
