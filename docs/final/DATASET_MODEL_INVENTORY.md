# NirmaanAI: Master Dataset, Model & Artifact Inventory
**System Version:** v0.25.0  
**Repository:** `C:\NIRMAAN AI`  
**Scope:** Complete Comprehensive Audit Tables for Datasets, Models, Artifacts, Epistemic Categories, and Phase Milestones

---

## 1. Master Dataset Inventory

| Dataset Name | Source / Origin | Type | Sample / Time Horizon | Key Monitored Variables | Preprocessing & Transformations | Primary Role in NirmaanAI | Real vs. Synthetic | Split / Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AI4I 2020 Predictive Maintenance** | UCI ML Repository / Matthias Fonteyne | Tabular Sensor | 10,000 operational records | Air temp [K], Process temp [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Failure modes (TWF, HDF, PWF, OSF, RNF) | Standard scaling, power feature derivation ($P = \tau \cdot \omega$), temp diff derivation ($\Delta T = T_{\text{proc}} - T_{\text{air}}$), target encoding | PdM failure classification & failure mode identification | Real-derived synthetic benchmark | Train (70%), Val (15%), Test (15%) |
| **NASA C-MAPSS Turbofan Degradation (FD001)** | NASA Prognostics Center of Excellence | Multivariate Run-to-Failure Time Series | 100 train units, 100 test units (run-to-failure cycles) | 21 sensor channels (temperatures, pressures, fan speeds, bleed ratios) across sea-level conditions | Invariant sensor drop (ch 1, 5, 10, 16, 18, 19), rolling mean & std windows (5, 10, 20 cycles), piecewise linear RUL clip ($RUL_{\text{max}} = 125$) | Remaining Useful Life (RUL) regression benchmarking | Physics-based simulation benchmark | Train units / Test units split by engine ID |
| **UCI Electricity Load Diagrams (2011–2014)** | UCI Machine Learning Repository | High-Resolution Time Series | 370 clients, 15-minute intervals over 4 years | Electrical power consumption [kW], timestamp, customer ID | Hourly aggregation, cyclic calendar features (hour-of-day, day-of-week), lag features (1h, 24h, 168h), rolling stats | Industrial plant electrical power forecasting | Real industrial metering | Train (80%), Val (10%), Test (10%) chronologically |
| **UCI SECOM** | UCI Machine Learning Repository | High-Dimensional Tabular | 1,567 fab process records, 591 sensors | In-line semiconductor manufacturing sensor signals | High missingness feature filter ($> 50\%$ drop), median imputation, variance thresholding | Anomaly detection & quality defect benchmarking | Real fab telemetry | Benchmark exploration |
| **UCI Appliances Energy** | UCI Machine Learning Repository | Multivariate Environmental Time Series | 19,735 records (10-minute intervals over 4.5 months) | Appliances energy [Wh], light [Wh], T1–T9, RH1–RH9, weather variables | Scaling, cyclical temporal encoding, lag creation | Auxiliary energy & multi-variate environmental modeling | Real sensor telemetry | Benchmark comparison |
| **Controlled 5-Station Factory Dataset** | NirmaanAI Synthetic Generator | Synchronized Sensor & Production Telemetry | 30 days, 43,200 sensor rows (1-min ticks), 300 production jobs | Vibration [mm/s], acoustic [dB], motor current [A], power [kW], tool wear [min], cycle time [s], scrap, rework | 1-minute temporal aggregation, sliding window statistics, unit conversion, event alignment | End-to-end integration, temporal cutoff enforcement, validation | Controlled Synthetic | Benchmark demonstration & integration |
| **Operational Losses Ledger (`operational_losses.csv`)** | Phase 14 / Financial Accounting Engine | Structured Ledger | 30 days shop floor financial records | Downtime hours, scrap count, rework units, technician hours, energy waste, unit financial losses | Currency conversion (INR), rate multiplication, realized vs. projected segregation | Financial impact quantification & ROI baseline | Controlled Synthetic | Baseline financial ledger (MD5: `34B12582B32D81E3121429C55EBF74E8`) |
| **Factory Maintenance Knowledge Corpus** | Phase 19 / Curated Industrial Manuals | Semi-Structured Technical Text | 18 documents, 278 chunks | Equipment manuals, ISO 10816 standards, maintenance SOPs, failure catalogs | Markdown parsing, semantic chunking (200–500 tokens), metadata extraction, authority scoring | RAG knowledge retrieval & Copilot ground truth | Curated Domain Knowledge | Retrieval corpus (100% indexed) |

---

## 2. Master Machine Learning Model Inventory

| Subsystem / Model Name | Primary Algorithm | Optimization Target | Champion Hyperparameters | Decision Threshold ($\tau$) | Primary Evaluation Metric | Holdout Performance Metric | Epistemic Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Predictive Maintenance Classifier** | XGBoost (`XGBClassifier`) | Binary Machine Failure (`Machine failure` $\in \{0, 1\}$) | `n_estimators=150`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.8`, `scale_pos_weight=10.0` | $\tau = 0.9100$ | Precision, Recall, F1, PR-AUC | **Precision: 0.9545**<br>**Recall: 0.8235**<br>**F1: 0.8842**<br>**ROC-AUC: 0.9831**<br>**PR-AUC: 0.8647** | `MODEL_OUTPUT` |
| **RUL Prognostic Regressor** | Random Forest (`RandomForestRegressor`) | Remaining Useful Life in operating cycles | `n_estimators=200`, `max_depth=15`, `min_samples_split=5`, `random_state=42` | N/A (Regression) | MAE, RMSE, $R^2$ | **MAE: 13.21 cycles**<br>**RMSE: 18.11 cycles**<br>**$R^2$: 0.7957** | `MODEL_OUTPUT` |
| **Unsupervised Anomaly Detector** | Principal Component Analysis (PCA) | Squared Prediction Error (SPE / $Q$-statistic) | `n_components=5`, `whiten=False`, fitted on healthy operational baseline | $\tau_{\text{recon}} = 0.24050$ | Reconstruction ROC-AUC, PR-AUC, Early Warning Lead Time | **ROC-AUC: 0.9992**<br>**PR-AUC: 0.9965**<br>**Precision: 0.9722**<br>**Recall: 1.0000**<br>**F1: 0.9859**<br>**Lead Time: 106.5 hrs** | `MODEL_OUTPUT` |
| **Station Bottleneck Detector** | Flow-Ratio Decision Boundary | Flow restriction condition: $\text{cycle\_ratio} \ge 1.20 \lor \text{delay} \ge 10 \lor \text{DELAYED}$ | Dynamic moving average window over consecutive jobs | $\tau = 0.4000$ (Exploratory / Post-hoc) | Precision, Recall, F1, FPR | **Precision: 0.7778**<br>**Recall: 0.8750**<br>**F1: 0.8235**<br>**ROC-AUC: 0.9882**<br>**PR-AUC: 0.8040**<br>**FPR: 0.0164** | `MODEL_OUTPUT` |
| **Energy Consumption Forecaster** | LightGBM (`LGBMRegressor`) | 24-hour horizon hourly electricity demand [kW] | `n_estimators=300`, `num_leaves=31`, `learning_rate=0.03`, `colsample_bytree=0.8` | N/A (Regression) | WAPE, sMAPE, RMSE, $R^2$ | **WAPE: 6.50%**<br>**sMAPE: 6.37%**<br>**RMSE: 26.23 kW**<br>**MAE: 13.80 kW**<br>**$R^2$: 0.9605** | `MODEL_OUTPUT` |
| **Explainable AI (XAI)** | TreeSHAP (`shap.TreeExplainer`) | Additive feature attribution in log-odds space | Exact tree traversal, background training summary | N/A | Feature Attribution Ranking | **Top: `tool_wear_min` (+1.84)**<br>**2: `rotational_speed`**<br>**3: `power_kw`**<br>**4: `temp_diff`** | `MODEL_OUTPUT` |
| **Root Cause Analysis (RCA)** | Fault Tree Signature Corroboration | Candidate mechanical fault attribution ($S \in [0, 1]$) | Weighted corroboration over vibration, acoustic, thermal, and wear | $S \ge 0.70$ (`HIGH` confidence) | Signature Corroboration Count | **M2 Result: MECHANICAL_LOAD (Score: 0.7912, 4 sources)** | `DERIVED` / `MODEL_OUTPUT` |

---

## 3. Master Decision & Analytics Rules Inventory

| Rule / Module | Input Condition | Mathematical Formulation | Output Action / Classification | Confidence / Epistemic Status |
| :--- | :--- | :--- | :--- | :--- |
| **Health Band: CRITICAL** | Composite Health Score $H_m \in [0.0, 39.9]$ | Weighted sum of PdM, Anomaly, Flow, Quality $< 40.0$ | Flag machine for immediate intervention | High / `MODEL_OUTPUT` |
| **Health Band: DEGRADED** | Composite Health Score $H_m \in [40.0, 59.9]$ | Weighted sum of diagnostic factors in $[40.0, 59.9]$ | Schedule inspection during shift change | High / `MODEL_OUTPUT` |
| **Health Band: WATCH** | Composite Health Score $H_m \in [60.0, 74.9]$ | Weighted sum of diagnostic factors in $[60.0, 74.9]$ | Monitor sensor drift and lubrication | Moderate / `MODEL_OUTPUT` |
| **Health Band: HEALTHY** | Composite Health Score $H_m \in [75.0, 89.9]$ | Normal operating envelope | Maintain standard production schedule | High / `MODEL_OUTPUT` |
| **Health Band: EXCELLENT** | Composite Health Score $H_m \in [90.0, 100.0]$ | Optimal operating condition | Full speed continuous operation | High / `MODEL_OUTPUT` |
| **Coverage Penalty** | Sensor valid frame ratio $< 40\%$ | $\text{coverage} < 0.40$ | Cap score at 50.0, emit `DATA_INSUFFICIENT` | Deterministic / `DERIVED` |
| **Safety Stock ($SS$)** | Lead time $L$, demand variance $\sigma_d$ | $SS = Z \times \sigma_d \times \sqrt{L}$ ($Z=1.645$) | Spindle Bearing $SS = 1.134\text{ units}$ | Deterministic / `DERIVED` |
| **Reorder Point ($ROP$)** | Daily demand $\bar{d}$, Lead time $L$, Safety Stock $SS$ | $ROP = (\bar{d} \times L) + SS$ | Spindle Bearing $ROP = 1.367\text{ units}$ | Deterministic / `DERIVED` |
| **Proactive Expedite Rule (`R-I01`)** | Post-maintenance inventory $< SS$ | $(\text{Stock}_{\text{on-hand}} - 1) < SS$ | Trigger `EXPEDITE_CRITICAL_SPARE` | High / `PROJECTED` |
| **Financial Loss Realization** | Historical events up to $t_{\text{cutoff}}$ | $\sum (\text{Downtime}\times C_{dt} + \text{Scrap}\times C_{sc} + \dots)$ | Plant Realized Loss: **₹229,105.54**<br>M2 Realized Loss: **₹73,062.28** | Audit-Grade / `DERIVED` |
| **Opportunity Exposure** | Projected run-to-failure exposure | Predicted hours to failure $\times C_{dt}$ | Plant Opportunity: **₹24,320.00**<br>M2 Opportunity: **₹24,320.00** | Model-Grounded / `PROJECTED` |
| **Scenario D Avoided Loss** | Proactive bearing service + feed derating | $\text{Exposure} - \text{Planned\_Service\_Cost}$ | Avoided Opportunity: **₹19,520.00**<br>Net Remaining Exposure: **₹77,862.28** | Counterfactual / `PROJECTED` |

---

## 4. Master RAG & Copilot Inventory

| Component | Parameter / Specification | Validated Metric / Value | Epistemic Role |
| :--- | :--- | :--- | :--- |
| **Corpus Volume** | 18 engineering manuals & standards | 278 indexed text chunks | Grounded Industrial Knowledge Base |
| **Vector Space** | Truncated SVD over TF-IDF n-grams | 64-dimensional dense representation | Deterministic, zero-hallucination semantic search |
| **Hybrid Retrieval Weight** | $0.70 \times \text{Dense} + 0.30 \times \text{Sparse}$ | Formulaic balance between semantic concepts and OEM part numbers | Multi-modal ranking |
| **Retrieval Recall@5** | 16-query domain benchmark | **1.0000 (100% recall)** | Retrieval Completeness |
| **Mean Reciprocal Rank (MRR)** | 16-query domain benchmark | **0.8125** | Top-rank Precision |
| **Retrieval Precision@5** | 16-query domain benchmark | **0.4750** | Non-relevant chunk filtering |
| **Anti-Hallucination Rate** | 16-query domain benchmark | **1.0000 (100% grounded)** | Hallucination Prevention |
| **Mean Query Latency** | Local commodity CPU execution | **21.97 ms (sub-26 ms)** | Real-time Operator Responsiveness |
| **Supported Copilot Intents** | 15 specialized manufacturing intents | 100% test accuracy on 14 benchmark regression tests | Structured natural language parsing |

---

## 5. Epistemic Taxonomy Classification Registry

| Epistemic Tier | Formal Definition | Primary NirmaanAI Examples | System Handling Policy |
| :--- | :--- | :--- | :--- |
| `OBSERVED` | Directly captured physical sensor or device measurements | Vibration amplitude ($5.62\text{ mm/s}$), air temperature ($300.1\text{ K}$) | Unfiltered ground truth; stored in time-series tables |
| `DERIVED` | Deterministic mathematical calculations from observed data | Cycle time ratio ($1.38$), realized scrap cost (₹51,800.00), safety stock ($1.134$) | Fully auditable formulas; zero stochastic variance |
| `MODEL_OUTPUT` | Inferences generated by statistical, ML, or regression models | XGBoost failure probability ($0.996$), C-MAPSS RUL ($13.21$), PCA anomaly score ($0.781$) | Must display confidence interval and decision threshold |
| `CONTROLLED_SYNTHETIC` | Deterministically generated test scenarios for system benchmarking | Days 18–21 M2 progressive degradation simulation | Labeled as synthetic; must never be claimed as real field telemetry |
| `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH` | Ground-truth event occurring after the decision cutoff | `MAINT_0003` at Day 22 16:30:00 UTC (150 min downtime) | Quarantined; strictly prohibited from entering prospective feature pipelines |
| `PROJECTED` | Statistically grounded counterfactual forward estimates | Scenario D avoided loss (₹19,520.00), post-service inventory ($1.0\text{ unit}$) | Displayed with scenario assumptions; separated from realized accounting |
| `NOT_PROJECTABLE` | Quantities where physical transfer functions are unverified | Specific microsecond resonance under partial lubrication in simulation | Explicitly labeled `NOT_PROJECTABLE`; numerical fabrication blocked |
| `UNKNOWN` | Unmonitored states or missing sensor coverage | Telemetry windows with $< 40\%$ data coverage | Triggers `DATA_INSUFFICIENT` alert; caps health score at $50.0$ |

---

## 6. Project Phase Milestone Registry

| Phase | Title | Core Deliverables | Verification Status | Environment Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Project Setup & Governance | Repository layout, environment configs, git branching | **LOCKED & VERIFIED** | None |
| **Phase 1** | Unified Factory Schema | Pydantic data contracts, relational schema definition | **LOCKED & VERIFIED** | None |
| **Phase 2** | Synthetic Factory Generator | 5-station continuous telemetry generator | **LOCKED & VERIFIED** | None |
| **Phase 3** | Exploratory Data Analysis | Statistical distributions, sensor correlations, missingness | **LOCKED & VERIFIED** | None |
| **Phase 4** | Feature Engineering Pipeline | Rolling statistics, lag features, thermodynamic transforms | **LOCKED & VERIFIED** | None |
| **Phase 5** | PdM Model Development | AI4I XGBoost classifier, precision-recall thresholding | **LOCKED & VERIFIED** | None |
| **Phase 6** | RUL Prognostics | NASA C-MAPSS Random Forest regressor | **LOCKED & VERIFIED** | None |
| **Phase 7** | Anomaly Detection | PCA reconstruction error model, lead time evaluation | **LOCKED & VERIFIED** | None |
| **Phase 8** | Bottleneck Prediction | Flow-ratio tracking, job delay heuristic classification | **LOCKED & VERIFIED** | None |
| **Phase 9** | Production & Energy Forecasting | UCI Electricity LightGBM, plant energy forecasting | **LOCKED & VERIFIED** | None |
| **Phase 10** | Inventory Intelligence | Wilson safety stock, reorder point, spare lead times | **LOCKED & VERIFIED** | None |
| **Phase 11** | Explainable AI (SHAP) | TreeSHAP attributions, feature importance waterfall | **LOCKED & VERIFIED** | None |
| **Phase 12** | Root Cause Analysis (RCA) | Deterministic candidate fault-tree corroboration | **LOCKED & VERIFIED** | None |
| **Phase 13** | Factory Health Score | 5-band composite health scoring with coverage penalty | **LOCKED & VERIFIED** | None |
| **Phase 14** | Financial Loss Accounting | Realized loss vs. projected opportunity loss segregation | **LOCKED & VERIFIED** | None (MD5 Checksum Locked) |
| **Phase 15** | Recommendation Engine | Deterministic prescriptive action rules | **LOCKED & VERIFIED** | None |
| **Phase 16** | What-If Simulation Engine | Discrete-event counterfactual simulation (Scenarios A–D) | **LOCKED & VERIFIED** | None |
| **Phase 17** | PostgreSQL Data Layer | 19 SQLAlchemy models, Alembic migrations, seeder | **LOCKED** | Native PostgreSQL daemon unavailable on host (`HOLD`) |
| **Phase 18** | FastAPI Backend Implementation | 40+ REST API endpoints, Pydantic schemas, service layer | **LOCKED** | Live PostgreSQL integration blocked (`HOLD`) |
| **Phase 19** | Knowledge Retrieval & Copilot | 278-chunk hybrid RAG, 15-intent deterministic Copilot | **LOCKED & VERIFIED** | None |
| **Phase 20** | React + Vite Dashboard | Modern command center, M2 deep dive, Copilot drawer | **LOCKED & VERIFIED** | None |
| **Phase 21** | Frontend-Backend Integration | Axios client, live telemetry sync, offline mock fallback | **LOCKED & VERIFIED** | None |
| **Phase 22** | Full E2E System Integration | Unified 7-layer verification pipeline | **LOCKED** | Host database limitation remains (`HOLD`) |
| **Phase 23** | System Hardening & Stress Testing | Concurrency, adversarial injection, drift resilience (347 tests) | **LOCKED & VERIFIED** | None |
| **Phase 24** | Docker Packaging & Deployment | Multi-stage Dockerfiles, compose specs, Nginx reverse proxy | **LOCKED & COMPLETE** | Docker Engine unavailable on host (`HOLD`) |
| **Phase 25** | Final Documentation & Packaging | Academic report, IEEE paper, Viva guide, inventory, checklist | **COMPLETED & LOCKED** | None |

---
*End of Master Dataset, Model & Artifact Inventory.*
