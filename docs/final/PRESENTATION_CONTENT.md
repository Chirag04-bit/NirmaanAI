# NirmaanAI Master Presentation Deck: Technical & Academic Slides
**Title**: NirmaanAI — AI-Powered Manufacturing Intelligence & Operational Decision Platform  
**Target Audience**: Academic Defense Committees, Industrial Executives, System Architects  
**Version**: `v0.25.0`  

---

### Slide 1: Title & Executive Summary
- **Slide Title**: NirmaanAI: AI-Powered Manufacturing Intelligence & Operational Decision Platform
- **Bullet Points**:
  - Bridging the gap between raw shop-floor telemetry and executive manufacturing decisions.
  - Tailored specifically for Indian MSMEs in precision machining and textile verticals.
  - End-to-end integration: Sensors $\to$ Predictive ML $\to$ Explainability $\to$ Finance $\to$ Digital Twin $\to$ Prescriptive Actions $\to$ RAG Copilot $\to$ Executive Dashboard.
- **Recommended Visual**: High-level platform hero diagram showing the multi-tier pipeline.
- **Important Metric**: 25 completed phases; 355 test items (353 passed, 2 skipped); 0 failures.
- **Speaker Emphasis**: *"NirmaanAI transforms statistical predictions into rupee-denominated operational actions that plant managers can trust and execute."*

---

### Slide 2: The Industrial Problem
- **Slide Title**: The Realities of Indian MSME Manufacturing
- **Bullet Points**:
  - Over 110 million workers and 27% of India's GDP depend on manufacturing MSMEs.
  - 85% of machine shops operate under reactive run-to-failure or rigid calendar preventive maintenance.
  - Catastrophic failure consequences: ruined tooling, scrapped precision batches, line starvation, customer SLA penalties.
- **Recommended Visual**: Photo comparison: pristine CNC machine vs catastrophic spindle seizure / tool breakage.
- **Important Metric**: Unplanned downtime costs typical MSMEs ₹4,500/hour plus massive scrap losses.
- **Speaker Emphasis**: *"For an MSME, an unpredicted spindle seizure on a bottleneck milling machine doesn't just halt one machine—it stops the entire factory line."*

---

### Slide 3: Motivation
- **Slide Title**: Why Existing Industrial Solutions Fail MSMEs
- **Bullet Points**:
  - Tier-1 conglomerate solutions (Siemens, GE, SAP) cost millions of dollars and require dedicated IT departments.
  - Heterogeneous machine fleets (CNC, VMC, Grinders) of varying ages lack standardized data protocols.
  - Standard ML research reports academic metrics (ROC-AUC, RMSE) that shop-floor supervisors cannot act upon.
- **Recommended Visual**: Cost vs Adoption curve comparing Enterprise IIoT vs NirmaanAI commodity open-architecture.
- **Important Metric**: 90%+ of Indian MSMEs cannot afford proprietary IIoT cloud platforms.
- **Speaker Emphasis**: *"We built NirmaanAI to deliver Tier-1 computational intelligence on low-cost, open-source commodity compute."*

---

### Slide 4: The Existing Operational Gap
- **Slide Title**: The Telemetry-to-Action Disconnect
- **Bullet Points**:
  - Telemetry alerts are isolated from inventory: alerting a failure when the spare part takes 7 days to ship is useless.
  - Predictive maintenance ignores bottleneck dynamics: taking a machine offline when upstream queues are backed up starves production.
  - Financial quantification is completely missing: engineers cannot justify interventions to business owners without currency exposure.
- **Recommended Visual**: Venn diagram showing the three disconnected silos: Maintenance, Production Flow, and Spare Parts Inventory.
- **Important Metric**: 7-day supplier lead time for critical spindle bearings vs immediate breakdown risk.
- **Speaker Emphasis**: *"Maintenance cannot be scheduled in a vacuum. It must be dynamically synchronized with job queues and inventory buffers."*

---

### Slide 5: The Academic Research Gap
- **Slide Title**: Research Limitations in Industrial AI
- **Bullet Points**:
  - **Gap 1**: Data leakage in public benchmarks (e.g. failure modes leaking failure labels).
  - **Gap 2**: Attribution without causality (treating SHAP statistical feature sensitivity as physical proof).
  - **Gap 3**: Unconstrained industrial LLMs hallucinating machine states and leaking future events.
- **Recommended Visual**: Diagram illustrating lookahead temporal leakage in naive RAG systems.
- **Important Metric**: 100% temporal isolation required between decision cutoff (Day 21) and breakdown (Day 22).
- **Speaker Emphasis**: *"Academic research frequently claims 99% accuracy by accidentally peeking at future ground truth. NirmaanAI enforces strict temporal boundaries."*

---

### Slide 6: The NirmaanAI Solution
- **Slide Title**: The Unified Decision-Support Pipeline
- **Bullet Points**:
  - Integrated 7-tier decision architecture: Data $\to$ ML $\to$ XAI $\to$ Finance $\to$ Simulation $\to$ Prescriptions $\to$ Copilot.
  - Triad Coupling: Synchronizes Machine Health $\leftrightarrow$ Flow Bottlenecks $\leftrightarrow$ Spare Inventory.
  - Production-ready: Full-stack implementation from PostgreSQL to React 19 dashboard.
- **Recommended Visual**: End-to-end block diagram highlighting the data flow and decision flow.
- **Important Metric**: 40 FastAPI operational endpoints; sub-30ms response times.
- **Speaker Emphasis**: *"We didn't just build a model; we built the complete computational nervous system for the factory floor."*

---

### Slide 7: Overall System Architecture
- **Slide Title**: Layered Software Architecture
- **Bullet Points**:
  - **Layer 1**: Relational Data & Normalization (19 PostgreSQL tables via SQLAlchemy 2.0).
  - **Layer 2**: ML & Analytics (XGBoost, Random Forest, PCA Anomaly, Flow Heuristics).
  - **Layer 3**: Explainability & Loss Accounting (TreeExplainer SHAP, RCA, INR loss calculator).
  - **Layer 4**: Decision Intelligence (Operations Research Safety Stock, What-If Simulation).
  - **Layer 5**: Knowledge Memory, Copilot & Presentation (TF-IDF/SVD RAG, FastAPI, React 19, Nginx).
- **Recommended Visual**: 5-layer vertical architectural stack diagram.
- **Important Metric**: 100% open-source software stack (Python 3.12+, React 19, PostgreSQL, Nginx).
- **Speaker Emphasis**: *"Every layer communicates via strict Pydantic contracts, ensuring absolute decoupling and maintainability."*

---

### Slide 8: Dataset Ecosystem & Provenance
- **Slide Title**: Rigorous Industrial Dataset Benchmarking
- **Bullet Points**:
  - **AI4I 2020**: 10,000 rows of milling tool telemetry with masked failure modes to prevent leakage.
  - **NASA C-MAPSS (FD001)**: 100 engine trajectories, 20,631 run-to-failure cycles split by unit ID.
  - **UCI Electricity Load**: 140,257 readings across 370 client demand profiles.
  - **30-Day Automotive Digital Twin**: 43,200 minutely readings across 5 machines (M1–M5) with calibrated M2 degradation.
- **Recommended Visual**: Table listing verified rows, features, provenance hash, and industrial domain.
- **Important Metric**: Dataset MD5 `34B12582B32D81E3121429C55EBF74E8` verified unchanged.
- **Speaker Emphasis**: *"We test on real-world NASA and UCI benchmarks, complemented by a calibrated digital twin shop floor."*

---

### Slide 9: Data Engineering & Preprocessing Pipeline
- **Slide Title**: Zero-Lookahead Data Pipelines
- **Bullet Points**:
  - Strict temporal ordering: $t_{\text{train}} < t_{\text{val}} < t_{\text{test}}$ prevents temporal lookahead.
  - Grouped trajectory splitting ensures engines/machines never cross train and test sets.
  - Leakage masking: UDI indices and categorical failure indicators strictly removed prior to training.
- **Recommended Visual**: Split timeline diagram showing chronological train/val/test partitions.
- **Important Metric**: Zero data leakage across 100% of data loading pipelines.
- **Speaker Emphasis**: *"If a data pipeline leaks even one millisecond of future telemetry, the model's high accuracy is an illusion."*

---

### Slide 10: Predictive Maintenance (Phase 6)
- **Slide Title**: Failure Classification & RUL Regression
- **Bullet Points**:
  - **XGBoost Failure Classifier (AI4I)**: Precision **0.9545**, Recall **0.8235**, F1 **0.8842**, ROC-AUC **0.9831**.
  - Operational threshold locked at $\tau = 0.91$, resulting in only 2 false alarms across 1,500 test samples.
  - **Random Forest RUL (NASA C-MAPSS)**: MAE **13.21 cycles**, RMSE **18.11 cycles**, $R^2$ **0.7957**.
- **Recommended Visual**: Confusion Matrix (1447 TN, 2 FP, 9 FN, 42 TP) and RUL degradation curves.
- **Important Metric**: $\tau = 0.91$ threshold delivers 95.45% precision, eliminating operator alarm fatigue.
- **Speaker Emphasis**: *"In manufacturing, false alarms are deadly—operators learn to ignore them. We prioritize high precision at $\tau=0.91$."*

---

### Slide 11: Multi-Sensor Anomaly Detection (Phase 7)
- **Slide Title**: Unsupervised Multivariate Telemetry Screening
- **Bullet Points**:
  - Learns the nominal machine manifold using PCA reconstruction error on clean Days 1–15.
  - 14 principal components explain 92.30% cumulative variance.
  - Precision: **0.9722**, Recall: **1.0000**, F1: **0.9859**, PR-AUC: **0.9965**.
  - Triggered early warning **106.5 hours (4.44 days)** before catastrophic spindle seizure.
- **Recommended Visual**: PCA reconstruction error time-series plot crossing threshold $\tau=0.24050$.
- **Important Metric**: 4.44 days of early warning lead time before physical machine seizure.
- **Speaker Emphasis**: *"Unsupervised PCA detected M2's vibration anomaly over 4 days before the bearing seized."*

---

### Slide 12: Production Line Bottleneck Detection (Phase 8)
- **Slide Title**: Flow Intelligence & Scheduling Constraints
- **Bullet Points**:
  - Evaluated strictly at job dispatch time ($t \le t_{\text{dispatch}}$) without post-job data.
  - Target: cycle ratio $\ge 1.20$, start delay $\ge 10\text{ min}$, or delayed status.
  - F1-Score: **0.8235**, Precision: **0.7778**, Recall: **0.8750**, ROC-AUC: **0.9882**.
  - Correctly identified Machine M2 cycle expansion (1.38x) and 76 delayed queue units.
- **Recommended Visual**: Factory machine queue buffer chart showing WIP backlog accumulating behind M2.
- **Important Metric**: Machine M2 cycle ratio expanded to 1.38x nominal, creating 76 delayed units.
- **Speaker Emphasis**: *"M2 wasn't just vibrating; its expanded cycle time was actively bottlenecking the entire assembly line."*

---

### Slide 13: Energy Forecasting & Smart Inventory (Phases 9 & 10)
- **Slide Title**: Grid Power Costing & Dynamic Safety Stock
- **Bullet Points**:
  - **Forecasting**: XGBoost on UCI Electricity achieves WAPE **6.50%** and $R^2$ **0.9605**; tracks peak tariffs (₹12.50 vs ₹8.50/kWh).
  - **Dynamic Inventory Core**: $SS = Z \sqrt{\bar{L}\sigma_d^2 + \bar{d}^2\sigma_L^2} = 1.134\text{ units}$, $ROP = 1.367\text{ units}$.
  - On-hand stock is 2.0 (nominal), but maintenance consumes 1.0 $\implies$ projected stock drops to 1.0 ($<SS$).
- **Recommended Visual**: Inventory buffer chart showing stock dropping below safety stock threshold post-service.
- **Important Metric**: Supplier lead time of 7.0 days demands proactive spare expediting before maintenance starts.
- **Speaker Emphasis**: *"Our inventory engine warned that replacing the bearing would breach safety stock, proactively ordering spares."*

---

### Slide 14: Explainable AI & Root Cause Analysis (Phases 11 & 12)
- **Slide Title**: SHAP Feature Attribution & Fault Trees
- **Bullet Points**:
  - TreeExplainer SHAP computed in additive log-odds margin space with zero attribution error.
  - Primary degradation drivers on M2: Torque excursion (+0.412), Tool wear (+0.285), Temperature (+0.198).
  - Root Cause Analysis fused signals into candidate diagnostic: **`MECHANICAL_LOAD`** (Score: 0.791, HIGH confidence).
- **Recommended Visual**: SHAP horizontal waterfall attribution plot paired with candidate fault tree.
- **Important Metric**: Explains why M2 is failing without metallurgical disassembly.
- **Speaker Emphasis**: *"We don't give the operator a black-box probability; SHAP tells them torque surge and bearing wear are the culprits."*

---

### Slide 15: Composite Factory Health Score (Phase 13)
- **Slide Title**: Multi-Tier Factory Health Scoring
- **Bullet Points**:
  - Authoritative 0–100 score synthesizing failure risk, anomaly magnitude, and line flow.
  - Locked bands: Excellent (90–100), Healthy (75–89), Watch (60–74), Degraded (40–59), Critical (0–39).
  - Machine M2 isolated in **`CRITICAL`** state at **26.88 / 100** (Failure risk: 99.6%).
  - Fleet overall health remains **83.3 / 100** (`HEALTHY`), localizing the problem asset.
- **Recommended Visual**: SVG radial health gauge dial showing M2 at 26.88 in bold crimson.
- **Important Metric**: M2 Health Score: 26.88 / 100; Fleet Health Score: 83.3 / 100.
- **Speaker Emphasis**: *"A plant manager can instantly see that while the factory is at 83.3, Machine M2 is in critical crisis at 26.88."*

---

### Slide 16: Operational & Financial Loss Accounting (Phase 14)
- **Slide Title**: Realized Financial Losses vs Gross Exposure
- **Bullet Points**:
  - **M2 Realized Operational Loss**: $\mathbf{₹73,062.28}$ (Downtime ₹11,250, Scrap ₹51,800, Rework ₹6,475, Overtime ₹420, Tariff ₹3,117.28).
  - **M2 Projected Opportunity Cost**: $\mathbf{₹24,320.00}$ (76 delayed units $\times$ ₹320 contribution margin).
  - **M2 Gross Exposure**: $\mathbf{₹97,382.28}$ (Realized Loss + Opportunity Cost).
  - Plant-wide gross exposure: $\mathbf{₹253,425.54}$.
- **Recommended Visual**: Financial exposure waterfall chart breaking down scrap, downtime, rework, and opportunity loss.
- **Important Metric**: M2 Realized Loss: ₹73,062.28; Gross Exposure: ₹97,382.28.
- **Speaker Emphasis**: *"Scrap was the largest loss component at ₹51,800—far exceeding the direct labor cost of the repair."*

---

### Slide 17: Prescriptive Recommendation Engine (Phase 15)
- **Slide Title**: Deterministic Evidence-Grounded Directives
- **Bullet Points**:
  - **Rule R-M01 (`INSPECT_SPINDLE_BEARING`)**: Priority CRITICAL, Urgency IMMEDIATE (Preempts catastrophic seizure).
  - **Rule R-P01 (`REDUCE_MACHINE_FEED_RATE`)**: Priority HIGH, Urgency SAME_DAY (Relieves torque and starvation).
  - **Rule R-P02 (`RESCHEDULE_PENDING_JOBS`)**: Priority HIGH, Urgency SAME_DAY (Reroutes 76 delayed queue jobs).
  - **Rule R-I01 (`EXPEDITE_CRITICAL_SPARE`)**: Priority HIGH, Urgency SAME_DAY (Restores safety stock buffer).
- **Recommended Visual**: Prescriptive directive cards displaying urgency badges and corroborating evidence tags.
- **Important Metric**: 4 synchronized interventions addressing maintenance, queue flow, and spare parts.
- **Speaker Emphasis**: *"Our rules prescribe the exact actions needed: inspect the bearing, slow the feed rate, reschedule jobs, expedite spares."*

---

### Slide 18: Digital Twin Counterfactual Simulation (Phase 16)
- **Slide Title**: What-If Scenario Studio & Guardrails
- **Bullet Points**:
  - Evaluates Scenarios A through E prior to physical intervention.
  - **Scenario D (Integrated Planned Maintenance + Speed Derating)**:
    - Avoided Opportunity Loss: $\mathbf{₹19,520.00}$
    - Remaining Gross Exposure: $\mathbf{₹77,862.28}$
    - Net Counterfactual ROI: $\mathbf{₹19,520.00}$
  - **Epistemic Guardrail**: Unsupported physical recovery states are strictly marked **`NOT_PROJECTABLE`**.
- **Recommended Visual**: Comparative bar chart of Scenarios A, B, C, D, E with avoidable loss highlighted in green.
- **Important Metric**: ₹19,520.00 in opportunity loss avoided by choosing Scenario D over baseline run-to-failure.
- **Speaker Emphasis**: *"Scenario D saves ₹19,520 in lost production margin without claiming impossible causal certainty."*

---

### Slide 19: Factory Knowledge Memory & Copilot (Phases 19 & 20)
- **Slide Title**: Grounded RAG & AI Factory Copilot
- **Bullet Points**:
  - 278 authoritative knowledge chunks indexed via hybrid TF-IDF/SVD (256d) + topical keyword overlap.
  - Recall@5: **1.000**, MRR: **0.8125**, Anti-Hallucination Rejection: **1.000**.
  - Natural language Copilot answers operational queries in **21.97 ms average latency**.
  - Strictly enforces 8-tier epistemic taxonomy and rejects unknown entities (`M99`).
- **Recommended Visual**: Screenshot of the interactive Copilot chat drawer displaying citations and epistemic badges.
- **Important Metric**: 100% precision across 10 representative queries; median latency 26.28 ms.
- **Speaker Emphasis**: *"Our Copilot enforces strict deterministic anti-hallucination guardrails. If an entity is outside the plant topology, it rejects the query in 0.09 ms."*

---

### Slide 20: Executive Dashboard & Deployment Packaging (Phases 21 & 24)
- **Slide Title**: Production React Dashboard & Docker Architecture
- **Bullet Points**:
  - **React 19 + Vite Dashboard**: Real-time KPI cards, interactive machine modal, SHAP waterfalls, Copilot drawer.
  - Live Status Pill: Automatically displays `LIVE BACKEND DATA` or `OFFLINE DEMO / FALLBACK DATA`.
  - **Docker Topology**: PostgreSQL 16 (`db`), Python 3.12-slim (`backend`), and Nginx Alpine (`frontend`).
  - Non-root user `nirmaan:nirmaan`, internal private database port, automated entrypoint migrations.
- **Recommended Visual**: Screenshot of the dark-mode executive dashboard paired with Docker Compose topology.
- **Important Metric**: Frontend production bundle compiles in 167 ms; 0 missing imports.
- **Speaker Emphasis**: *"The dashboard provides plant managers with a sleek, single-pane-of-glass command center ready for containerized deployment."*

---

### Slide 21: Experimental Results Summary
- **Slide Title**: Consolidated Subsystem Performance
- **Bullet Points**:
  - Failure Classification: F1 **0.8842** (Precision 95.5%, ROC-AUC 0.9831).
  - RUL Prognostics: RMSE **18.11 cycles**, $R^2$ **0.7957**.
  - Anomaly Detection: PR-AUC **0.9965**, F1 **0.9859**, 4.44 days lead time.
  - Bottleneck Prediction: F1 **0.8235**, PR-AUC **0.8040**.
  - Concurrency: Sustained **296.5 req/s** under 50 concurrent worker threads.
- **Recommended Visual**: Performance scoreboard table highlighting top metrics across all ML and systems tasks.
- **Important Metric**: 353 automated unit, integration, and stress tests passed; zero regressions.
- **Speaker Emphasis**: *"Every single metric reported here is backed by automated reproducible test scripts in the repository."*

---

### Slide 22: Limitations Register
- **Slide Title**: Honest Scientific & Environment Limitations
- **Bullet Points**:
  - **Environment**: Native Windows host lacked live PostgreSQL and Docker Engine runtimes (packaging statically verified).
  - **Simulation**: Discrete operational states modeled; continuous finite-element thermal curves not simulated.
  - **Epistemic**: Diagnostic recovery post-service is strictly `NOT_PROJECTABLE` without empirical telemetry.
  - **Bottleneck**: Heuristic cutoff ($\tau=0.40$) was post-hoc calibrated on synthetic queues.
- **Recommended Visual**: Transparent checklist of verified vs bounded capabilities.
- **Important Metric**: Zero fabricated metrics; 100% honest documentation of environment constraints.
- **Speaker Emphasis**: *"True engineering integrity requires stating what the system cannot do just as clearly as what it can do."*

---

### Slide 23: Future Research Directions
- **Slide Title**: Roadmap for Field Deployment
- **Bullet Points**:
  - Prospective field validation on CNC shop floors in automotive manufacturing clusters (Pune, Chennai, Rajkot).
  - Edge containerization on NVIDIA Jetson embedded hardware for real-time high-frequency vibration FFT processing.
  - Multi-echelon supply chain coordination across regional Tier-2 supplier networks.
- **Recommended Visual**: Roadmap diagram showing progression from lab validation to multi-factory industrial deployment.
- **Important Metric**: Target sub-10ms edge inference on quantized ONNX runtimes.
- **Speaker Emphasis**: *"The next horizon is taking NirmaanAI from the digital twin lab to live factory floors across industrial India."*

---

### Slide 24: Conclusion
- **Slide Title**: Summary of Contributions
- **Bullet Points**:
  - Delivered an end-to-end, grounded Cyber-Physical Intelligence Platform across 25 phases.
  - Solved the triad coupling between machine degradation, line bottlenecks, and inventory replenishment.
  - Quantified physical anomalies into actionable Indian Rupee operational exposures.
  - Provided an anti-hallucinatory AI Copilot adhering to formal epistemic guardrails.
  - Validated with 353 passing tests, full reproducibility artifacts, and zero technical debt.
- **Recommended Visual**: Final NirmaanAI logo and GitHub repository link.
- **Important Metric**: `v0.25.0` Complete, Verified, and Permanently Locked.
- **Speaker Emphasis**: *"NirmaanAI demonstrates that state-of-the-art AI can be practical, explainable, and accessible for manufacturing MSMEs."*
