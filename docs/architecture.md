# NirmaanAI System Architecture Specification

## 1. Executive Summary & Philosophy
**NirmaanAI** is designed as an AI-powered "Digital Factory Brain" built specifically for Indian Manufacturing MSMEs (initially focused on Textile and Precision Automotive Component manufacturing). 

Unlike conventional Enterprise Resource Planning (ERP) or Manufacturing Execution Systems (MES) that merely store operational logs, NirmaanAI transforms raw multi-source factory telemetry into actionable business and engineering decisions:
$$\text{Data} \longrightarrow \text{Prediction} \longrightarrow \text{Explanation} \longrightarrow \text{Financial Impact} \longrightarrow \text{Simulation} \longrightarrow \text{Recommendation} \longrightarrow \text{Human Action}$$

---

## 2. End-to-End Decision Flow

```
                      [ INDUSTRIAL DATA SOURCES ]
        (Machines / Telemetry, Job Logs, Energy, Inventory, Manual Notes)
                                     │
                                     ▼
                        [ DATA ENGINEERING LAYER ]
         (Cleaning, Synchronization, Unified Factory Schema, Storage)
                                     │
                                     ▼
                    [ ML & TIME-SERIES ANALYTICS LAYER ]
  ┌───────────────────────┬──────────────────────┬──────────────────────┐
  │ Predictive Maintenance│  Anomaly Detection   │ Bottleneck Prediction│
  │    (Failure & RUL)    │ (Sensors & Processes)│(Cycle Times & Queues)│
  └───────────────────────┴──────────────────────┴──────────────────────┘
                                     │
                                     ▼
                    [ EXPLAINABLE AI (XAI) & ROOT CAUSE ]
  ┌──────────────────────────────────────────────┬──────────────────────┐
  │        SHAP Feature Attribution              │ Root Cause Candidates│
  │    ("Vibration +38% above baseline")         │ (Bearing wear / Lube)│
  └──────────────────────────────────────────────┴──────────────────────┘
                                     │
                                     ▼
                 [ OPERATIONAL & FINANCIAL IMPACT ENGINE ]
  ┌──────────────────────────────────────────────┬──────────────────────┐
  │       Projected Downtime (Hours)             │ Financial Loss (INR) │
  │    ("2.5 hrs delay on Line 1")               │ ("₹11,250 downtime") │
  └──────────────────────────────────────────────┴──────────────────────┘
                                     │
                                     ▼
                [ DIGITAL-TWIN-INSPIRED WHAT-IF SIMULATION ]
  ┌─────────────────────────────────────────────────────────────────────┐
  │ Scenario: "Shift 40 units to Machine 3 and schedule lube on Shift C"│
  │ Outcome:  "Downtime avoided: 2.2 hrs; Net savings: ₹8,400"          │
  └─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                     [ SMART RECOMMENDATION ENGINE ]
  ┌─────────────────────────────────────────────────────────────────────┐
  │ Action:     Inspect spindle bearing & apply grease during 14:00 shift│
  │ Urgency:    HIGH | Confidence: 89% | Alternatives: Reroute queue    │
  └─────────────────────────────────────────────────────────────────────┘
                                     │
                ┌────────────────────┴────────────────────┐
                ▼                                         ▼
   [ AI FACTORY COPILOT (RAG) ]             [ UNIFIED EXECUTIVE DASHBOARD ]
  (Interactive grounded reasoning)         (React + Vite Visual Interface)
```

---

## 3. Layered Architectural Decomposition

### Layer 1: Data Engineering & Storage
- **Unified Factory Schema**: Relational schema normalizing:
  - `machines`: metadata, power ratings, cycle baselines.
  - `sensor_readings`: minutely/second telemetry (vibration, temp, RPM, torque).
  - `production_jobs`: scheduled vs actual start/finish, buffer queues.
  - `maintenance_records`: technician logs, component replacements, failure codes.
  - `inventory_items`: stock levels, safety stock thresholds, scrap rates.
  - `financial_parameters`: MSME downtime hourly cost, energy tariffs, rework cost.
- **Storage Tier**: PostgreSQL with relational indexing and time-series partitioning.

### Layer 2: Machine Learning & Analytics Core
- **Baseline-First Strategy**: Linear/Logistic baselines evaluated prior to Random Forest and XGBoost.
- **Predictive Maintenance**: Predict machine failure probability ($P(\text{failure})$ within 7 days) and Remaining Useful Life (RUL).
- **Anomaly Detection**: Unsupervised multivariate isolation of sensor drift (Isolation Forest, statistical Z-score thresholds).
- **Bottleneck Prediction**: Upstream/downstream queue congestion and cycle-time deviation identification.
- **Demand & Energy Forecasting**: 24-hour ahead energy load and production volume forecasting.

### Layer 3: Explainable AI & Root Cause Candidate Engine
- **SHAP (SHapley Additive exPlanations)**: Computes local and global feature attribution for every model inference.
- **Root Cause Candidate Generator**: Translates raw numerical attributions into factory terminology:
  - *Example*: High torque + high temperature $\rightarrow$ "Heat Dissipation Failure (HDF) / Insufficient Lubrication candidate".
  - *Academic Distinction*: Termed strictly as "contributing factor" and "root-cause candidate", never claiming absolute causal proof without physical verification.

### Layer 4: Operational & Financial Impact Engine
- Bridges algorithmic alerts to business metrics that Indian MSME plant managers act upon:
  $$\text{Downtime Loss (INR)} = \text{Downtime Duration (hrs)} \times \text{Hourly Downtime Rate (INR/hr)}$$
  $$\text{Energy Loss (INR)} = \Delta \text{Power (kWh)} \times \text{Tariff (INR/kWh)}$$
  $$\text{Scrap Loss (INR)} = \text{Scrapped Weight (kg)} \times \text{Material Cost Rate (INR/kg)}$$
- Clearly demarcates **Measured Data** vs **Configured Assumptions** vs **Illustrative Examples**.

### Layer 5: Digital-Twin-Inspired Simulation
- Evaluates discrete alternative operational decisions prior to execution:
  - Scenario A: Continue operating at full speed until failure (high downtime risk).
  - Scenario B: Reduce feed rate by 15% to extend tool life until shift end.
  - Scenario C: Immediate 30-minute planned pause for lubrication.

### Layer 6: Recommendation Engine & Copilot
- **Recommendation Formulation**:
  1. Concrete Action
  2. Justification & Evidence
  3. Operational & Financial Impact
  4. Decision Confidence
  5. Fallback Alternative
- **Factory Knowledge Memory (RAG)**: Retrieval-augmented memory over equipment manuals, SOPs, and historical incident logs.
- **Factory Copilot**: Natural language interface answering factory status queries grounded in live database state and vector documentation.

### Layer 7: Unified Frontend & APIs
- **FastAPI**: Asynchronous Python backend exposing structured REST endpoints.
- **React + Vite**: High-performance dashboard prioritizing actionable MSME decision cards, health scores, and root-cause breakdowns over ornamental charts.
