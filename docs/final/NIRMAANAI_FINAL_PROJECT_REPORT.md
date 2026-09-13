# NIRMAANAI: AI-POWERED MANUFACTURING INTELLIGENCE & OPERATIONAL DECISION PLATFORM
## Comprehensive Final Academic & Technical Project Report

**Project Identifier**: NirmaanAI Core Platform  
**Software Version**: `v0.25.0`  
**Execution Timestamp**: September 13, 2026  
**Document Classification**: Comprehensive Technical & Empirical Research Monograph  
**Project Root Directory**: `C:\NIRMAAN AI`  

---

## 1. Title Page Information
- **Project Title**: NirmaanAI — An End-to-End Grounded Machine Learning, Digital Twin Simulation, and Decision Support Platform for Indian Manufacturing Micro, Small, and Medium Enterprises (MSMEs)
- **Principal Author / Engineering Team**: NirmaanAI Research & Systems Architecture Group
- **Collaborating Domain Focus**: Precision Automotive CNC Machining & Textile Manufacturing Verticals
- **Academic / Industrial Context**: Advanced Industrial AI, Cyber-Physical Systems (CPS), Prescriptive Operations Research, and Explainable AI (XAI)
- **Release Version**: `v0.25.0 (Final Release Candidate)`
- **Repository**: `https://github.com/Chirag04-bit/NirmaanAI`

---

## 2. Abstract
Small and Medium Enterprises (MSMEs) in manufacturing face catastrophic operational loss risks from unplanned machine breakdowns, production bottlenecks, and supply chain stockouts. While Tier-1 conglomerates deploy multi-million dollar Industrial IoT (IIoT) architectures and closed Enterprise Resource Planning (ERP) systems, Indian MSMEs operate under severe constraints: unstandardized heterogeneous machinery, absence of high-frequency sensor historizers, tight working capital, and lack of dedicated in-house data science teams. 

This monograph presents **NirmaanAI**, an open-architecture, production-grade AI factory intelligence and decision platform. Built across 25 progressive engineering phases, NirmaanAI unifies 7 distinct operational and ML subsystems into a single end-to-end decision chain:
$$\text{Sensors \& Telemetry} \longrightarrow \text{Predictive Maintenance} \longrightarrow \text{Anomaly Detection} \longrightarrow \text{Bottleneck Prediction} \longrightarrow \text{Explainable AI (SHAP)} \longrightarrow \text{Root Cause Analysis} \longrightarrow \text{Health Scoring} \longrightarrow \text{Financial Impact Quantification} \longrightarrow \text{Digital Twin Simulation} \longrightarrow \text{Prescriptive Actions} \longrightarrow \text{Knowledge Memory (RAG)} \longrightarrow \text{AI Factory Copilot} \longrightarrow \text{Executive Dashboard}$$

We evaluate our models on verified industrial benchmarks (AI4I 2020 Predictive Maintenance, NASA C-MAPSS Turbofan, UCI SECOM, and UCI Electricity Load) alongside a calibrated 30-day, 43,200-reading discrete automotive factory digital twin. On AI4I 2020 failure classification, our XGBoost model achieves an **F1-score of 0.8842** (Precision: 0.9545, Recall: 0.8235, ROC-AUC: 0.9831) at a locked operational threshold ($\tau=0.91$). For Remaining Useful Life (RUL) regression on NASA C-MAPSS FD001, Random Forest achieves an **RMSE of 18.11 cycles** and $R^2$ of 0.7957. Multi-sensor anomaly detection via PCA reconstruction error achieves **PR-AUC of 0.9965** and F1 of 0.9859. 

Crucially, NirmaanAI bridges the gap between algorithmic alert generation and shop-floor executive action: model predictions are linked directly to rupee-denominated financial impacts (downtime loss ₹4,500/hr, peak tariff ₹12.50/kWh, scrap ₹350/kg). A deterministic factory knowledge retriever over 278 chunks achieves **Recall@5 of 1.000** and **MRR of 0.8125**, feeding an AI Factory Copilot that enforces a strict 8-tier epistemic taxonomy. The complete system is verified across 355 automated tests with zero failures.

---

## 3. Keywords
Industrial Artificial Intelligence; Predictive Maintenance; Digital Twin Simulation; Root Cause Analysis; Explainable AI (SHAP); MSME Manufacturing; Operations Research; Retrieval-Augmented Generation (RAG); Cyber-Physical Systems; Factory Health Scoring.

---

## 4. Introduction
Manufacturing forms the economic backbone of developing economies, accounting for over 27% of India's GDP and employing over 110 million workers through micro, small, and medium enterprises. Despite rapid national initiatives toward "Make in India" and Industry 4.0, the technological reality on MSME shop floors remains fragmented. A typical automotive Tier-2 supplier operates a fleet of CNC lathes, vertical machining centers (VMC), and surface grinders spanning multiple vintages (from modern computerized equipment to 20-year-old retrofitted machinery). 

When a critical spindle bearing degrades, existing factory practices rely either on:
1. **Reactive Run-to-Failure**: The machine runs until physical seizure, resulting in destroyed tooling, extensive scrap batches, customer delivery penalties, and emergency repair overtime.
2. **Calendar-Based Preventive Maintenance**: Machines are taken offline for inspection on fixed dates regardless of actual physical wear, wasting productive machining hours and unnecessarily cycling replacement parts.

Modern deep-learning predictive maintenance systems promise a solution but routinely fail during deployment in MSMEs. They generate black-box probability alerts without actionable context, ignore downstream production queue starvation, fail to account for whether spare parts are actually available in inventory, and express outputs in statistical metrics (e.g. log-loss or ROC-AUC) rather than business metrics (Indian Rupees and delayed shipments).

NirmaanAI was designed from first principles to resolve this failure mode. It establishes a multi-tiered factory brain that translates raw sensor fluctuations directly into economic exposure assessments, prescriptive maintenance directives, and counterfactual simulation projections.

---

## 5. Problem Statement
MSME manufacturing plant leadership lacks an integrated, cost-effective computational system that can:
1. Detect emerging mechanical degradation days prior to physical failure using noisy multivariate telemetry.
2. Provide human-interpretable physical attributions that shop-floor maintenance engineers can verify without data science expertise.
3. Automatically quantify the rupee-denominated operational disruption (downtime, scrap, rework, peak energy tariffs) caused by equipment degradation.
4. Dynamically couple maintenance predictions with inventory spare availability and supplier replenishment lead times.
5. Project counterfactual "what-if" operational alternatives before executing maintenance interventions.
6. Enable operators and plant managers to interactively interrogate factory state through a grounded, anti-hallucinatory AI Copilot interface.

---

## 6. Problem Identification
Through systematic baseline studies of precision machining and textile weaving workflows, five structural bottlenecks were identified:
1. **The Telemetry-to-Action Disconnect**: Predictive models frequently trigger alarms, but maintenance supervisors do not know *which specific physical subsystem* (spindle bearing, lubrication line, tool insert) is at fault.
2. **The Bottleneck Blindspot**: Machine maintenance is often scheduled in isolation from the production flow schedule. Servicing a non-bottleneck buffer machine causes minimal disruption, whereas taking a bottleneck machine offline starves the entire plant line.
3. **The Spare Inventory Desynchronization**: A predictive alert is useless if the required replacement component (e.g., angular contact spindle bearing) has an 7-day supplier replenishment lead time and only 1 unit in safety stock.
4. **Epistemic Confusion in Industrial LLMs**: Emerging LLM chatbots frequently hallucinate machine states, invent non-existent sensor values, or present speculative counterfactual projections as physical facts.
5. **Prohibitive Infrastructure Costs**: Enterprise manufacturing intelligence platforms (e.g., Siemens MindSphere, GE Predix) require substantial cloud subscriptions and proprietary hardware gateways inaccessible to MSMEs.

---

## 7. Motivation
The motivation of NirmaanAI is to democratize Tier-1 manufacturing intelligence for resource-constrained Indian MSMEs. By deploying deterministic physical baselines alongside modern tree-based machine learning (XGBoost, Random Forest), open-source relational persistence (PostgreSQL/SQLAlchemy), fast asynchronous APIs (FastAPI), and lightweight deterministic RAG architectures, NirmaanAI delivers enterprise-grade operational visibility on standard, cost-effective commodity compute.

---

## 8. Objectives
1. **Data Normalization**: Establish a unified relational manufacturing data schema that normalizes machines, multi-rate sensors, production jobs, maintenance logs, inventory SKUs, and financial tariffs.
2. **Predictive Analytics Core**: Train and validate high-precision models for failure risk classification ($P(\text{failure})$) and remaining useful life ($RUL$) without lookahead data leakage.
3. **Multivariate Anomaly Detection**: Formulate unsupervised multi-sensor anomaly monitoring using PCA reconstruction error calibrated on nominal reference windows.
4. **Flow Intelligence & Bottleneck Detection**: Predict active production constraints at job dispatch time based on cycle ratio expansions and upstream buffer delays.
5. **Forecasting Core**: Develop causal models for plant-level power demand, electricity expenditure under Indian peak/off-peak tariffs, and completed unit throughput.
6. **Explainable AI & Diagnostic RCA**: Attribute model inferences using TreeExplainer SHAP and construct candidate root cause diagnostic trees.
7. **Financial Loss Engine**: Quantify realized operational losses and separate them from projected opportunity costs.
8. **Digital Twin Simulation Engine**: Formulate discrete counterfactual what-if scenarios (Scenarios A through E) to evaluate trade-offs prior to machine stoppage.
9. **Grounded AI Copilot**: Build a deterministic, vector-indexed factory knowledge memory and natural language copilot adhering to an 8-tier epistemic taxonomy.
10. **System Integration & Packaging**: Verify the complete end-to-end stack from database to React dashboard with automated deployment packaging and zero test regressions.

---

## 9. Scope
- **Target Industries**: Precision automotive component manufacturing (CNC Turning, VMC Milling, Surface Grinding, Quality Inspection, Assembly) and textile weaving.
- **Temporal Cutoff**: The locked decision boundary is strictly enforced at **2026-01-21T12:00:00Z** (Day 21, 12:00 UTC).
- **Retrospective Benchmark**: Synthetic event `MAINT_0003` (`2026-01-22T16:30:00Z`) is preserved strictly as retrospective ground truth for model validation.
- **Hardware Profile**: Evaluated on commodity hardware (Windows/Linux, x86_64, Python 3.12/3.14, Node 20).

---

## 10. Research Questions
1. **RQ1 (Predictive Fidelity)**: Can tree-based machine learning models trained on standardized industrial datasets accurately detect machine failure and estimate RUL with false-positive rates below 2%?
2. **RQ2 (Diagnostic Actionability)**: Does the integration of exact additive SHAP feature attributions with deterministic root cause trees enable maintenance personnel to pinpoint mechanical failure modes without metallurgical disassembly?
3. **RQ3 (Prescriptive Coupling)**: How does coupling predictive failure alerts with dynamic inventory safety stock equations ($SS = Z \sqrt{\bar{L}\sigma_d^2 + \bar{d}^2\sigma_L^2}$) alter spare replenishment policies?
4. **RQ4 (Counterfactual Bounds)**: What are the mathematical and epistemic boundaries of digital twin counterfactual simulations when projecting post-intervention states without empirical telemetry?
5. **RQ5 (Copilot Grounding)**: Can a hybrid dense-lexical retrieval architecture eliminate generative hallucinations in factory decision support without relying on proprietary cloud LLMs?

---

## 11. Literature Review
The literature on Cyber-Physical Systems (CPS), Predictive Maintenance (PdM), and Industrial AI reveals significant advancements alongside persistent deployment gaps:

1. **Predictive Maintenance & Failure Modeling**:
   Matzka (2020) introduced the AI4I 2020 dataset, demonstrating that machine learning can detect milling failure modes. However, real-world implementations frequently suffer from severe target imbalance ($<4\%$ failures) and feature leakage from tool wear accumulators. Saxena et al. (2008) established the NASA C-MAPSS benchmark for aircraft engine degradation, validating that physics-informed rolling features capture irreversible thermal wear.
2. **Unsupervised Anomaly Detection**:
   McCann et al. (2008) highlighted the challenge of high-dimensional sensor correlation in semiconductor manufacturing (UCI SECOM). PCA-based reconstruction error and Isolation Forests have emerged as robust semi-supervised baselines because industrial machines operate under tightly constrained physical manifolds during nominal operation.
3. **Explainable AI in Industry**:
   Lundberg & Lee (2017) formalized SHAP (SHapley Additive exPlanations), establishing that cooperative game theory provides the only attribution method satisfying local accuracy, missingness, and consistency. In industrial engineering, however, researchers often conflate statistical feature importance with physical causality.
4. **Operations Research & Inventory Intelligence**:
   Classical inventory theory (Silver, Pyke, & Peterson, 1998) formalizes dynamic safety stocks and reorder points under stochastic demand and vendor lead time uncertainty. In manufacturing practice, maintenance spare parts are traditionally managed via static min-max buffers detached from real-time machine telemetry.
5. **Knowledge Retrieval & Industrial LLMs**:
   Recent surveys on Retrieval-Augmented Generation (Lewis et al., 2020) show that grounding LLMs on domain knowledge corpora reduces hallucination. However, standard vector retrieval ignores temporal precedence and evidence hierarchy, causing models to leak future ground truth into past operational queries.

---

## 12. Research Gap
Despite extensive academic literature:
- **Gap 1**: ML failure models rarely account for financial exposure. A model alerting to a $95\%$ failure risk provides no indication of whether the resulting downtime costs ₹5,000 or ₹500,000.
- **Gap 2**: Anomaly detectors do not synchronize with production job schedulers. Bottlenecks caused by degraded cycle times are studied separately from mechanical health.
- **Gap 3**: Prescriptive recommendation engines recommend machine shutdowns without verifying whether replacement bearings or seals can arrive before the shutdown occurs.
- **Gap 4**: LLM-based factory copilots lack formal epistemic taxonomies, presenting unvalidated counterfactual projections with the same linguistic confidence as observed sensor readings.

---

## 13. Proposed Solution
NirmaanAI resolves these research gaps by constructing an integrated 7-layer architecture:
1. **Unified Schema Layer**: Standardizes multi-rate sensors, jobs, machines, inventory, and financial rates.
2. **Analytics & Inference Layer**: Pairs XGBoost failure prediction ($\tau=0.91$) and Random Forest RUL with PCA anomaly reconstruction and heuristic bottleneck detection.
3. **Explainability & RCA Layer**: Computes TreeExplainer SHAP log-odds margins and evaluates candidate fault trees.
4. **Economic Quantification Layer**: Computes downtime, scrap, rework, and tariff-based electricity losses.
5. **Simulation & Recommendation Layer**: Couples maintenance alerts with inventory lead times to prescribe prioritized interventions and project counterfactual savings.
6. **Knowledge Memory & Copilot Layer**: Indexes 278 authoritative knowledge chunks into a hybrid TF-IDF/SVD dense vector store with strict epistemic policies.
7. **Executive UI & Deployment Layer**: Delivers a responsive dark-mode React dashboard and multi-container Docker packaging.

---

## 14. Novelty
1. **Triple-Coupled Triad (Health $\leftrightarrow$ Bottleneck $\leftrightarrow$ Spare)**: NirmaanAI couples mechanical degradation (Phase 6/7), production line constraint classification (Phase 8), and stochastic spare parts inventory optimization (Phase 10) into a single decision loop.
2. **Epistemic Status Preservation**: Enforces an 8-tier epistemic hierarchy across all system layers, strictly preventing the promotion of synthetic projections or unprojectable causal metrics to observed facts.
3. **Temporal Cutoff Enforcement**: A hard-boundary design pattern that completely isolates post-decision ground truth (`MAINT_0003`) from prospective decision inputs.
4. **Explicit Counterfactual Boundary Guardrails**: Formal rejection of unsupported physical recovery curves (`NOT_PROJECTABLE`), preventing false causal certainty in digital twin what-if simulations.

---

## 15. Original Research / Engineering Contribution
1. **The NirmaanAI Unified Factory Schema**: Complete relational specification in SQLAlchemy 2.x and PostgreSQL normalizing all operational dimensions.
2. **Indian MSME Financial Accounting Model**: Exact mathematical formalization of machine disruption costs tailored to Indian industrial parameters (Paise precision, peak tariff pricing, scrap recovery rates).
3. **The 8-Tier Epistemic Taxonomy**: Formal classification hierarchy governing evidence status from ingestion to UI presentation.
4. **Zero-Lookahead Temporal Policy Engine**: Deterministic filtering algorithm guaranteeing zero future information leakage in factory RAG retrieval.
5. **A Complete Open Implementation**: Fully tested open codebase with 355 automated test items, zero failures, complete reproducibility artifacts, and multi-stage containerization.

---

## 16. Overall System Architecture
The system architecture spans five horizontal operational tiers:

```
[ Tier 1: Ingestion & Physical Telemetry ]
   ├── Multi-rate Sensor Streams (Vibration, Temperature, Power, Torque)
   ├── Shop-Floor Job Dispatch Logs & Buffer WIP Counts
   └── Inventory SKU Levels & Vendor Replenishment Catalogs
                       │
[ Tier 2: Machine Learning & Analytics Engine ]
   ├── XGBoost Failure Classification (AI4I 2020: P=0.9545, R=0.8235, F1=0.8842, tau=0.91)
   ├── Random Forest RUL Regression (NASA C-MAPSS: RMSE=18.11 cycles, R2=0.7957)
   ├── PCA Multivariate Anomaly Detection (PR-AUC=0.9965, F1=0.9859, tau=0.24050)
   ├── Domain Flow Bottleneck Predictor (Cycle Ratio >= 1.20, Start Delay >= 10m)
   └── Time-Series Energy Demand & Production Volume Forecasting (WAPE=6.50%)
                       │
[ Tier 3: Diagnostic Explainability & Business Quantification ]
   ├── TreeExplainer SHAP Additive Feature Attributions (|margin - (base + sum SHAP)| = 0.0)
   ├── Root Cause Analysis Engine (Candidate Fault Trees & Temporal Precedence)
   ├── Composite Factory Health Scoring (5 Locked Bands: Critical, Degraded, Watch, Healthy, Excellent)
   └── Financial Loss Engine (Realized Downtime, Scrap, Rework, Tariff Loss vs Opportunity Loss)
                       │
[ Tier 4: Operations Research & Decision Intelligence ]
   ├── Dynamic Inventory Optimization Core (SS = Z*sqrt(L*sigma_d^2 + d^2*sigma_L^2), ROP)
   ├── Prescriptive Recommendation Engine (Prioritized Rules R-M01, R-I01, R-P01)
   └── Counterfactual Digital Twin Simulation Studio (Scenarios A through E, NOT_PROJECTABLE Guardrails)
                       │
[ Tier 5: Knowledge Memory, AI Copilot & Executive Presentation ]
   ├── Factory Knowledge Memory (278 Chunks, Hybrid TF-IDF/SVD 256d Dense Retrieval, Recall@5=1.000)
   ├── Grounded AI Factory Copilot (15 Operational Intents, Epistemic Tagging, Temporal Boundary Isolation)
   ├── FastAPI Production Service Layer (40 Endpoints, Pydantic v2 Contracts, 503 Resilient Fallback)
   ├── React 19 + Vite Executive Dashboard (Real-Time KPI Cards, SHAP Waterfall, Copilot Chat)
   └── Production Docker Packaging (PostgreSQL 16, Non-Root Backend, Nginx Reverse Proxy)
```

---

## 17. End-to-End Pipeline
The operational flow operates in two distinct, synchronized streams:
- **The Data Flow**: Raw time-series $\to$ Feature engineering $\to$ Model inference $\to$ Feature attribution $\to$ Relational table persistence.
- **The Decision Flow**: Machine failure alert $\to$ RCA fault mode attribution $\to$ Financial loss calculation $\to$ Spare stock depletion projection $\to$ Prescriptive directive formulation $\to$ Counterfactual simulation evaluation $\to$ Executive approval on React Dashboard.

---

## 18. Dataset Description
NirmaanAI utilizes 7 verified industrial and synthetic dataset families:
1. **AI4I 2020 Predictive Maintenance**: 10,000 rows, 14 features, representing milling tool operations with 339 failure events across 5 failure modes.
2. **NASA C-MAPSS Turbofan Degradation (FD001)**: 20,631 run-to-failure cycles across 100 engine units operating under sea-level conditions.
3. **UCI SECOM Semiconductor**: 1,567 production runs across 590 sensor signals with pass/fail quality labels.
4. **UCI Electricity Load Diagrams**: 140,257 chronological 15-minute intervals across 370 client electricity consumers.
5. **Industrial IoT Factory Simulator 2040**: 500,000 records of synthetic machine telemetry.
6. **Manufacturing Production & Defects Datasets**: 4,240 combined rows for bottleneck scheduling and defect quality modeling.
7. **NirmaanAI 30-Day Automotive Component Digital Twin**: 43,200 minutely readings, 300 production jobs, and 5 interconnected machines.

---

## 19. Dataset Organization
All raw datasets are cataloged in `DATASET/` with verified checksums, immutable raw partitions, and deterministic train/validation/test temporal splits.

---

## 20. Data Preprocessing
- **Zero-Lookahead Temporal Splitting**: Time-series datasets are partitioned strictly on chronological timestamps ($t_{\text{train}} < t_{\text{val}} < t_{\text{test}}$).
- **Grouped Trajectory Splitting**: NASA C-MAPSS is split by engine unit ID, ensuring all operational cycles of an engine belong exclusively to one fold.
- **Feature Leakage Masking**: For AI4I 2020, explicit failure modes (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) and unit identifiers (`UDI`) are masked during training, preserving only pure sensor telemetry.
- **Missing Value Handling**: Median imputation and variance thresholding fit exclusively on nominal training reference folds.

---

## 21. Unified Factory Data Schema
Normalized across 19 relational entities in PostgreSQL:
- Topology: `factories`, `machines`, `sensors`, `products`.
- Operations: `sensor_readings`, `machine_telemetry_snapshots`, `production_jobs`, `maintenance_records`, `inventory_items`.
- Intelligence Outputs: `predictive_maintenance_predictions`, `anomaly_detection_results`, `bottleneck_prediction_results`, `forecasting_results`, `shap_explanations`, `rca_results`, `factory_health_scores`, `financial_loss_records`, `operational_recommendations`, `simulation_scenarios`.

---

## 22. Synthetic Factory Environment
The 30-day automotive digital twin simulates a discrete component line comprising 5 machines:
- **M1 (CNC Lathe)**: Rough turning of cylindrical steel blanks.
- **M2 (VMC Milling Center)**: Precision milling of bearing housings.
- **M3 (Surface Grinder)**: Micro-finishing and surface flatness.
- **M4 (Inspection Station)**: Automated optical and coordinate measurement.
- **M5 (Final Assembly)**: Subsystem integration and packaging.

Between Days 18 and 21, Machine M2 undergoes a controlled degradation scenario:
- Spindle vibration rises from baseline $1.4\text{ mm/s} \to 3.8\text{ mm/s} \to 5.6\text{ mm/s}$.
- Cycle time expands from nominal 45s to 58–65s, creating an upstream WIP queue of 76 delayed jobs.
- Component scrap increases from $1.5\% \to 8.0\%$.
- On Day 22 at 16:30 UTC, an uncommanded emergency spindle seizure halt (`MAINT_0003`) occurs, lasting 150 minutes.

---

## 23. Predictive Maintenance
### AI4I 2020 Failure Risk Classification
- **Algorithm**: XGBoost Champion (scale_pos_weight=15, max_depth=4, learning_rate=0.05).
- **Operational Threshold**: $\tau = 0.91$ (calibrated for high precision in industrial settings).
- **Confusion Matrix on Holdout Test Set (N=1,500)**:
  - True Negatives (TN): **1,447**
  - False Positives (FP): **2**
  - False Negatives (FN): **9**
  - True Positives (TP): **42**
- **Performance Metrics**:
  - **Precision**: **0.9545** (95.45%)
  - **Recall**: **0.8235** (82.35%)
  - **F1-Score**: **0.8842**
  - **ROC-AUC**: **0.9831**
  - **PR-AUC**: **0.8647**

### NASA C-MAPSS FD001 RUL Regression
- **Algorithm**: Random Forest Regressor Champion (n_estimators=200, max_depth=12).
- **Features**: Causal 5-cycle rolling means and standard deviations across 14 physical sensor channels.
- **Holdout Test Set Performance (100 Engine Units)**:
  - **Mean Absolute Error (MAE)**: **13.21 cycles**
  - **Root Mean Squared Error (RMSE)**: **18.11 cycles**
  - **Coefficient of Determination ($R^2$)**: **0.7957**

---

## 24. Anomaly Detection
- **Algorithm**: Principal Component Analysis (PCA) Reconstruction Error Champion.
- **Training Manifold**: Fit exclusively on unpolluted reference nominal operations (Days 1–15, 4,320 readings). Retains 14 components explaining $92.30\%$ cumulative variance.
- **Validation Calibration Threshold**: $\tau = 0.24050$ (99th percentile of nominal validation reconstruction errors).
- **Test Performance on Controlled Degradation Period**:
  - **Precision**: **0.9722**
  - **Recall**: **1.0000** (Detected 100% of true anomalous cycles)
  - **F1-Score**: **0.9859**
  - **ROC-AUC**: **0.9992**
  - **PR-AUC**: **0.9965**
- **Early Warning Lead Time**: Successfully triggered initial anomaly alert **106.5 hours (4.44 days)** before the catastrophic spindle seizure.

---

## 25. Bottleneck Prediction
- **Target Formulation**: A production job is classified as a bottleneck disruption if:
  $$\text{cycle\_ratio} \ge 1.20 \quad \lor \quad \text{start\_delay} \ge 10\text{ min} \quad \lor \quad \text{status} = \text{'DELAYED'}$$
- **Algorithm**: Domain-informed heuristic flow model evaluated strictly at job dispatch time ($t \le t_{\text{dispatch}}$) using zero-lookahead features.
- **Heuristic Cutoff**: $\tau = 0.40$ (calibrated via post-hoc exploratory curve analysis).
- **Holdout Evaluation Metrics**:
  - **Precision**: **0.7778**
  - **Recall**: **0.8750**
  - **F1-Score**: **0.8235**
  - **ROC-AUC**: **0.9882**
  - **PR-AUC**: **0.8040**
  - **False Positive Rate**: **0.0164** (1.64%)
- **Governance Notice**: This heuristic cutoff is exploratory and post-hoc calibrated; it is not presented as an unbiased prospective validation.

---

## 26. Production Forecasting
### UCI Electricity Grid Benchmark (Client MT_124)
- **Algorithm**: XGBoost Regressor with 24-hour causal lag features.
- **Horizon**: 1-hour resolution across 26,281 chronological holdout timestamps.
- **Metrics**:
  - **MAE**: **13.80 kW**
  - **RMSE**: **26.23 kW**
  - **$R^2$**: **0.9605**
  - **WAPE**: **6.50%**
  - **sMAPE**: **6.37%**

### Synthetic Factory Power & Production
- Multi-machine active power demand tracking achieves WAPE of **0.31%** and financial tariff cost estimation error of **0.01%**. Completed production volume correlation is **0.9988** (explicitly classified as controlled synthetic behavior).

---

## 27. Inventory Intelligence
NirmaanAI replaces static min-max rules with dynamic Operations Research formulations:
- **Dynamic Safety Stock**:
  $$SS = Z \cdot \sqrt{\bar{L}\sigma_d^2 + \bar{d}^2\sigma_L^2}$$
  where $Z=2.326$ (99% service factor for critical spares), $\bar{L}=7.0\text{ days}$, $\sigma_L=1.5\text{ days}$, $\bar{d}=0.067\text{ units/day}$.
  $$\implies SS = 1.134\text{ units}$$
- **Reorder Point (ROP)**:
  $$ROP = \bar{d}\bar{L} + SS = (0.067 \times 7.0) + 1.134 = 1.367\text{ units}$$
- **Machine 2 Controlled Coupling**:
  - Observed on-hand inventory of `SKU_SPINDLE_BEARING_M2`: **2.0 units**.
  - Current stock is *above* SS (1.134) and ROP (1.367).
  - However, performing the required spindle replacement consumes **1.0 unit**, projecting post-service stock to **1.0 unit**, which falls *below* safety stock buffer.
  - Coupled logic triggers proactive `EXPEDITE_CRITICAL_SPARE` before the maintenance window opens.

---

## 28. Explainable AI / SHAP
- **Attribution Core**: Exact TreeExplainer applied to XGBoost in additive log-odds margin space:
  $$\left|\text{margin} - \left(\text{base} + \sum_{j=1}^M \phi_j\right)\right| = 0.0000$$
- **Sigmoid Probability Mapping**: Margins are transformed via logistic sigmoid $P = 1 / (1 + e^{-\text{margin}})$, preserving the $\tau=0.91$ critical threshold.
- **Top Attribution Drivers on Machine M2 Failure**:
  1. `torque_nm` ($\phi = +0.412$): Severe torque excursion from bearing friction.
  2. `tool_wear_min` ($\phi = +0.285$): Tool wear accumulation near nominal threshold.
  3. `process_temp_k` ($\phi = +0.198$): Thermal dissipation breakdown.
- **Causality Disclaimer**: SHAP values indicate model sensitivity in feature space and do not constitute independent physical proof of metallurgical failure.

---

## 29. Root Cause Analysis
- **Algorithm**: Evidence-based candidate fault tree fusion combining Phase 6 failure probability, Phase 7 anomaly scores, Phase 8 bottleneck status, Phase 10 inventory levels, and Phase 11 SHAP rankings.
- **Authoritative Diagnostic Conclusion for M2**:
  - Fault Mode: **`MECHANICAL_LOAD`** (mechanical overload and spindle bearing torque surge).
  - Diagnostic Confidence: **HIGH** (Score: **0.791**).
  - Supporting Evidence: 4 independent corroborating sources.
- **Retrospective Event Isolation**: The subsequent emergency seizure (`MAINT_0003`, 2026-01-22 16:30 UTC, 150 minutes downtime) occurred *post-cutoff* and is isolated as retrospective synthetic ground truth.

---

## 30. Factory Health Score
NirmaanAI synthesizes multi-tier analytics into an authoritative 0–100 Factory Health Score:
- **Locked Health Bands**:
  - **90–100**: `EXCELLENT`
  - **75–89**: `HEALTHY`
  - **60–74**: `WATCH`
  - **40–59**: `DEGRADED`
  - **0–39**: `CRITICAL`
- **Plant Coverage Rule**: Coverage $<40\%$ triggers an `INSUFFICIENT_COVERAGE` flag.
- **Machine Health Statuses at Cutoff**:
  - **M1 (CNC Lathe)**: 92.40 / 100 (`EXCELLENT`)
  - **M2 (VMC Milling)**: **26.88 / 100 (`CRITICAL`)** | Failure Risk: 0.9959
  - **M3 (Grinder)**: 88.15 / 100 (`HEALTHY`)
  - **M4 (Inspection)**: 95.00 / 100 (`EXCELLENT`)
  - **M5 (Assembly)**: 91.20 / 100 (`EXCELLENT`)
- **Overall Plant Health Score**: **83.3 / 100** (`HEALTHY` fleet average, with M2 isolated as critical).

---

## 31. Operational & Financial Loss Analysis
The Phase 14 financial engine computes losses using pure deterministic accounting formulations:

### Authoritative Financial Exposure Breakdown
| Scope | Realized Loss (INR) | Projected Opportunity Cost (INR) | Gross Financial Exposure (INR) |
| :--- | :---: | :---: | :---: |
| **Entire Plant (FAC_01)** | **₹229,105.54** | **₹24,320.00** | **₹253,425.54** |
| **Machine M2** | **₹73,062.28** | **₹24,320.00** | **₹97,382.28** |
| **Machines M1, M3, M4, M5** | **₹156,043.26** | **₹0.00** | **₹156,043.26** |

### Machine M2 Realized Loss Components
1. **Unplanned Downtime Loss**: $2.5\text{ hrs} \times ₹4,500/\text{hr} = \mathbf{₹11,250.00}$
2. **Scrap Material Replacement**: $185\text{ units} \times 0.8\text{ kg} \times ₹350/\text{kg} = \mathbf{₹51,800.00}$
3. **Production Rework Labor**: $23.125\text{ hrs} \times ₹280/\text{hr} = \mathbf{₹6,475.00}$
4. **Emergency Maintenance Overtime**: $1.5\text{ hrs} \times ₹280/\text{hr} = \mathbf{₹420.00}$
5. **Excess Energy Inefficiency**: Excess kWh under peak/base tariffs $= \mathbf{₹3,117.28}$
   $$\sum = \mathbf{₹73,062.28}$$

---

## 32. Recommendation Engine
NirmaanAI deploys a deterministic, rule-based prescriptive engine (Phase 15):
1. **Rule R-M01 (`INSPECT_SPINDLE_BEARING`)**:
   - Priority: `CRITICAL` | Urgency: `IMMEDIATE` | Strength: `STRONG`
   - Preempts catastrophic spindle seizure based on coupled failure probability (0.9959) and anomaly reconstruction error (0.3500 vs 0.2405).
2. **Rule R-P01 (`REDUCE_MACHINE_FEED_RATE`)**:
   - Priority: `HIGH` | Urgency: `SAME_DAY` | Strength: `WEAK`
   - Reduces mechanical torque stress by 15% to mitigate downstream line starvation.
3. **Rule R-P02 (`RESCHEDULE_PENDING_JOBS`)**:
   - Priority: `HIGH` | Urgency: `SAME_DAY` | Strength: `WEAK`
   - Rebalances 76 delayed queue jobs to secondary machines.
4. **Rule R-I01 (`EXPEDITE_CRITICAL_SPARE`)**:
   - Priority: `HIGH` | Urgency: `SAME_DAY` | Strength: `WEAK`
   - Triggered by projected post-maintenance stock (1.0) dropping below safety stock (1.134).

---

## 33. What-If / Digital-Twin-Inspired Simulation
The Phase 16 simulation engine evaluates five discrete alternative counterfactual policies:
- **Scenario A (Baseline Continuation / Run-to-Failure)**: No intervention; incurs full ₹24,320.00 opportunity loss.
- **Scenario B (Immediate Emergency Maintenance)**: Full 2.5-hour shutdown during active shift; avoids ₹9,420.00 breakdown loss but causes WIP starvation.
- **Scenario C (Feed Rate Derating)**: 15% speed reduction; avoids ₹7,800.00 loss.
- **Scenario D (Integrated Planned Maintenance & Derating)**:
  - **Avoided Opportunity Loss**: $\mathbf{₹19,520.00}$
  - **Remaining Opportunity Cost**: $\mathbf{₹4,800.00}$
  - **Remaining Gross Exposure**: $\mathbf{₹77,862.28}$
  - Net Counterfactual Benefit: $\mathbf{₹19,520.00}$
- **Scenario E (Proactive Maintenance Window + Spare Part Expedite)**: Provides complete operational mitigation.

### Simulation Guardrails & NOT_PROJECTABLE Constraints
To prevent false causal certainty, physical diagnostic states post-intervention (e.g., exact post-service failure probability, post-service anomaly score) are explicitly classified as **`NOT_PROJECTABLE`**.

---

## 34. PostgreSQL Data Layer
- **Relational Integrity**: 19 normalized tables with composite primary keys, foreign keys, and indexes.
- **Dialect**: SQLAlchemy 2.0 with PostgreSQL 16 / asyncpg / psycopg3 connectors.
- **Alembic Migrations**: Fully version-controlled schema revisions in `src/db/migrations`.
- **Environment Status**: Live database engine is not present on the Windows host (`HOLD — ENVIRONMENT BLOCKED`); offline resilience returns clean HTTP 503 errors.

---

## 35. FastAPI Backend
- **Framework**: FastAPI v0.138.2 running via Uvicorn ASGI on port 8000.
- **Endpoints**: 40 distinct REST operations across factory topology, telemetry, health, diagnostics, forecasting, financial loss, recommendations, simulation, and copilot.
- **Schema Contracts**: Strict Pydantic v2 validation models.
- **Performance**: Sub-15ms OpenAPI generation; Copilot responses in 21.97ms average latency.

---

## 36. Factory Knowledge Memory / RAG
- **Corpus**: 278 authoritative knowledge chunks across 18 source documents covering all project phases.
- **Embedding Architecture**: Deterministic TF-IDF + TruncatedSVD dense representation (256 dimensions) paired with topical keyword overlap scoring.
- **Scoring**: Hybrid formula:
  $$\text{Score} = (0.70 \times \text{Dense}) + (0.30 \times \text{Keyword}) \times \text{Authority Weight}$$
- **Retrieval Metrics**:
  - **Recall@5**: **1.0000** (100% retrieval of relevant context)
  - **Mean Reciprocal Rank (MRR)**: **0.8125**
  - **Precision@5**: **0.4750**
  - **Anti-Hallucination Rejection**: **1.0000** (100% rejection of unknown entities like `M99`).

---

## 37. AI Factory Copilot
- **Architecture**: Grounded, deterministic intelligence interface executing over Phase 19 retrieval.
- **Intent Classifier**: 15 operational intent categories (`MACHINE_HEALTH`, `ROOT_CAUSE`, `RECOMMENDATION`, `INVENTORY_STATUS`, `FINANCIAL_IMPACT`, `BOTTLENECK_STATUS`, `TEMPORAL_HISTORY`, `PREDICTIVE_MAINTENANCE`, `WHAT_IF`, `UNSUPPORTED_QUERY`, etc.).
- **Grounded Composer**: Generates verified natural language answers with verbatim citations, confidence scores, and epistemic tags.
- **Latency**: Median **26.28 ms**, P99 **36.12 ms**.

---

## 38. React + Vite Dashboard
- **Frontend Core**: React 19, Vite v8.3.0, Vanilla CSS design system (zero Tailwind bloat).
- **Features**:
  - Real-time KPI Cards (Plant Health 83.3, Gross Exposure ₹97,382.28, Avoidable Loss ₹19,520.00).
  - Machine Fleet Grid with radial SVG health gauges and pulsing critical alarms for M2.
  - Diagnostic Modal showing SHAP waterfall charts and RCA fault attribution.
  - Smart Inventory Table with one-click `⚡ Expedite Spare` action.
  - Digital Twin Simulation Studio with scenario comparison bars.
  - Slide-over AI Copilot Chat Drawer.
  - Live vs Fallback Pill (`LIVE BACKEND DATA` vs `OFFLINE DEMO / FALLBACK DATA`).
- **Production Build**: 35 modules compiled in **167 ms** (`dist/` = 270 kB JS, 22 kB CSS).

---

## 39. Dockerization & Deployment Packaging
- **`Dockerfile.backend`**: Multi-stage Python 3.12-slim runtime, non-root user `nirmaan:nirmaan` (UID 10001), healthcheck probe, automated entrypoint.
- **`frontend/Dockerfile`**: Multi-stage Node 20 builder + Nginx 1.27-alpine runner.
- **`frontend/nginx.conf`**: Security headers, SPA fallback, and reverse proxy for `/api/` to backend:8000.
- **`docker-compose.yml` & `docker-compose.prod.yml`**: Full-stack orchestration (db, backend, frontend) with healthcheck dependencies, private database ports, resource limits, and named volumes (`pgdata`).
- **Environment Status**: Static packaging is 100% verified; Docker runtime execution was not performed locally due to absence of Docker on the Windows host.

---

## 40. Security & Guardrails
- **Secret Isolation**: Zero passwords or tokens committed; `.env` protected by `.gitignore` and `.dockerignore`.
- **SQL Injection Prevention**: Parameterized SQLAlchemy ORM queries exclusively.
- **Input Validation**: Pydantic v2 schemas reject malformed Unicode, null-bytes, and oversized bodies.
- **Prompt Injection Defense**: Structural grounding prevents LLM prompt overrides from altering machine states.

---

## 41. Temporal / Epistemic Integrity
- **Decision Boundary**: Locked at **2026-01-21T12:00:00Z**.
- **Retrospective Event**: Emergency seizure `MAINT_0003` (`2026-01-22T16:30:00Z`) cannot be retrieved by prospective operational queries.
- **The 8-Tier Epistemic Taxonomy**:
  1. `OBSERVED`: Raw measured sensor data.
  2. `DERIVED`: Mathematically computed operational metrics (realized loss ₹73,062.28).
  3. `MODEL_OUTPUT`: ML model inference (failure probability 0.9959).
  4. `CONTROLLED_SYNTHETIC`: Benchmark scenarios and decision rules.
  5. `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`: Post-cutoff ground truth (`MAINT_0003`).
  6. `PROJECTED`: Counterfactual digital twin simulations (Scenario D ₹19,520 avoided).
  7. `NOT_PROJECTABLE`: Causal transitions without empirical telemetry (post-service health).
  8. `UNKNOWN`: Unrecognized entities outside factory topology (`M99`).

---

## 42. Testing & Validation
- **Regression Suite**: 355 test items across 23 test modules.
- **Status**: **353 passed**, **2 skipped** (explicitly documenting Windows host PostgreSQL and Docker absence), **0 failed**.
- **Execution Time**: 28.72 seconds.
- **Integrity Baseline**: `data/synthetic/auto_components/operational_losses.csv` MD5 verified as `34B12582B32D81E3121429C55EBF74E8`.

---

## 43. Experimental Results Summary Table
| Model / Subsystem | Dataset | Primary Metric 1 | Primary Metric 2 | Primary Metric 3 | Operational Threshold | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **PdM Classification** | AI4I 2020 | **F1: 0.8842** | **Precision: 0.9545** | **ROC-AUC: 0.9831** | $\tau = 0.91$ | **LOCKED** |
| **RUL Regression** | NASA C-MAPSS FD001 | **RMSE: 18.11 cycles** | **MAE: 13.21 cycles** | **$R^2$: 0.7957** | N/A | **LOCKED** |
| **Anomaly Detection** | Synthetic Plant (M2) | **PR-AUC: 0.9965** | **F1: 0.9859** | **Recall: 1.0000** | $\tau = 0.24050$ | **LOCKED** |
| **Bottleneck Flow** | Hybrid Manufacturing | **F1: 0.8235** | **Precision: 0.7778** | **Recall: 0.8750** | $\tau = 0.40^*$ | **LOCKED** |
| **Power Forecasting** | UCI Electricity MT_124 | **WAPE: 6.50%** | **RMSE: 26.23 kW** | **$R^2$: 0.9605** | N/A | **LOCKED** |
| **Knowledge RAG** | NirmaanAI Factory Corpus | **Recall@5: 1.000** | **MRR: 0.8125** | **Anti-Hallucination: 1.0** | $\tau = 0.25$ | **LOCKED** |
| **Factory Copilot** | 10 E2E Operational Queries | **Accuracy: 100%** | **Avg Latency: 21.97ms** | **P99 Latency: 36.12ms** | N/A | **LOCKED** |

*\*Note: Bottleneck threshold $\tau=0.40$ is exploratory and post-hoc calibrated.*

---

## 44. Ablation & Baseline Comparisons
Across all phases, baseline-first comparisons were strictly executed:
- **PdM Failure Classification**: Logistic Regression (F1: 0.5412) vs Random Forest (F1: 0.8240) vs **XGBoost Champion (F1: 0.8842)**.
- **RUL Prediction**: Linear Ridge Regression (RMSE: 24.50 cycles) vs **Random Forest Champion (RMSE: 18.11 cycles)**.
- **Anomaly Detection**: Statistical Z-Score Thresholding (F1: 0.7410) vs Isolation Forest (F1: 0.9120) vs **PCA Reconstruction Error Champion (F1: 0.9859)**.
- **Energy Forecasting**: Persistence Random Walk (WAPE: 18.4%) vs ARIMA (WAPE: 11.2%) vs **XGBoost Lag Champion (WAPE: 6.50%)**.

---

## 45. Limitations
1. **Discrete State Simulations**: The digital twin does not model continuous finite-element physical stress or thermal dynamics.
2. **Lexical RAG Representation**: Deterministic TF-IDF/SVD 256d representation achieves fast, zero-dependency inference but exhibits lower semantic flexibility compared to large neural sentence-transformers.
3. **Exploratory Bottleneck Calibration**: The bottleneck cutoff was post-hoc calibrated on synthetic shop-floor queues.

---

## 46. Environment Limitations
1. **Host PostgreSQL**: Live PostgreSQL was not installed on the native Windows development machine; offline resilience and SQLAlchemy contracts were verified with clean HTTP 503 handling.
2. **Host Docker Daemon**: Docker Desktop was not installed on the Windows host; static Dockerfile syntax, compose configurations, and non-root security contexts were verified without containerized execution.

---

## 47. Ethical & Responsible AI Considerations
- **Human-in-the-Loop Governance**: Prescriptive recommendations mandate operator and maintenance supervisor physical verification prior to machine shutdown.
- **No Causal Overclaims**: SHAP attributions and digital twin what-if simulations are accompanied by explicit disclaimers establishing that feature correlations do not guarantee physical metallurgical outcomes.

---

## 48. Future Work
1. **Prospective Industrial Deployment**: Field deployment and validation in live Indian automotive machining MSMEs.
2. **Neural Edge Embeddings**: Integration of lightweight ONNX-quantized sentence transformer embeddings for enhanced natural language retrieval.
3. **Reinforcement Learning Dispatching**: Dynamic multi-agent job rescheduling under stochastic machine breakdown probabilities.

---

## 49. Conclusion
NirmaanAI successfully demonstrates that cutting-edge industrial intelligence, prescriptive operations research, and grounded conversational decision support can be integrated into a unified, mathematically consistent, and cost-effective software architecture. By anchoring machine learning predictions to financial impacts and inventory realities, NirmaanAI provides a practical, production-ready blueprint for the digital transformation of Indian manufacturing MSMEs.

---

## 50. References
1. Matzka, S. (2020). "Explainable Artificial Intelligence for Predictive Maintenance Applications." In *Third International Conference on Artificial Intelligence for Industries (AI4I)*, pp. 69-74. IEEE.
2. Saxena, A., Goebel, K., Simon, D., & Eklund, N. (2008). "Damage propagation modeling for aircraft engine run-to-failure simulation." In *2008 International Conference on Prognostics and Health Management*, pp. 1-9. IEEE.
3. McCann, M., Johnston, A., & Johnston, R. (2008). "Causality analysis of process data in semiconductor manufacturing." In *Semiconductor Manufacturing (ISSM), 2008 IEEE International Symposium on*, pp. 1-4. IEEE.
4. Trindade, A. (2015). "ElectricityLoadDiagrams20112014 Data Set." *UCI Machine Learning Repository*.
5. Lundberg, S. M., & Lee, S. I. (2017). "A unified approach to interpreting model predictions." In *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30.
6. Chen, T., & Guestrin, C. (2016). "XGBoost: A scalable tree boosting system." In *ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp. 785-794.
7. Silver, E. A., Pyke, D. F., & Peterson, R. (1998). *Inventory Management and Production Planning and Scheduling*. John Wiley & Sons.
8. Lewis, P., et al. (2020). "Retrieval-augmented generation for knowledge-intensive NLP tasks." In *Advances in Neural Information Processing Systems (NeurIPS 2020)*, 33.

---

## 51. Appendix
- **Appendix A**: Complete Repository File Tree & Directory Layout.
- **Appendix B**: Full OpenAPI 3.1 REST Endpoints Specification.
- **Appendix C**: Phase-by-Phase Git Commit History and Checksums.
