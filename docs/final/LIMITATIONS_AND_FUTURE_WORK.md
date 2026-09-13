# NirmaanAI: Formal Register of Technical Limitations & Future Work
**System Version:** v0.25.0  
**Repository:** `C:\NIRMAAN AI`  
**Purpose:** Honest, rigorous disclosure of platform limitations, epistemic boundaries, host environment constraints, and planned future research avenues.

---

## 1. Executive Statement of Epistemic & Engineering Integrity

In accordance with rigorous academic and industrial research standards, NirmaanAI strictly rejects the fabrication or exaggeration of experimental results, execution states, or software capabilities. This document formally outlines the active technical and environmental limitations of the platform as of **Phase 25 (v0.25.0)**. 

---

## 2. Formal Limitations Register

### Limitation 1: Native PostgreSQL Host Daemon Unavailable in Windows Development Environment
- **Detailed Description:** The host workstation running Windows 11 did not possess a running native PostgreSQL 16 server daemon.
- **System Impact:** Direct integration tests requiring a live PostgreSQL socket (`localhost:5432`) were placed on `HOLD — ENVIRONMENT BLOCKED`.
- **Mitigation & Verification:** All SQLAlchemy 2.x declarative models and Alembic migration scripts were validated using an in-memory / SQLite fallback compatibility layer. Production database code is statically audited and container-ready.

### Limitation 2: Docker Engine / Docker Desktop Unavailable on Host
- **Detailed Description:** The host workstation did not have Docker Engine or Docker Desktop installed or running in the Windows Subsystem for Linux (WSL).
- **System Impact:** While `Dockerfile.backend`, `frontend/Dockerfile`, and `docker-compose.prod.yml` were authored to strict multi-stage, non-root production specifications, live container instantiation could not be executed on the physical host.
- **Mitigation & Verification:** Container specifications were verified via static linting, multi-stage syntax auditing, and path mapping checks. Live Docker execution is explicitly held as an environment limitation.

### Limitation 3: Controlled Synthetic Factory Telemetry vs. Real Industrial Telemetry
- **Detailed Description:** Continuous 1-minute telemetry across the 5-station manufacturing line (`M1`–`M5`) was generated using a physics-grounded synthetic simulation engine over a 30-day baseline.
- **System Impact:** Controlled synthetic data does not capture the full stochastic complexity of real industrial plant floors, such as electrical noise, sensor communication packet drops, operator manual overrides, or uncalibrated tooling variations.
- **Mitigation & Scientific Honesty:** This dataset is explicitly categorized as `CONTROLLED_SYNTHETIC` and must never be cited as real-world industrial evidence.

### Limitation 4: Unverified Counterfactual Transitions Labeled as NOT_PROJECTABLE
- **Detailed Description:** In the What-If digital-twin-inspired simulation engine, certain secondary and tertiary mechanical behaviors (e.g., exact micro-crack propagation under altered coolant viscosity or microsecond harmonic vibration changes) lack empirical transfer functions.
- **System Impact:** Rather than inventing plausible-looking numbers, NirmaanAI explicitly marks these diagnostic KPIs as `NOT_PROJECTABLE`.
- **Scientific Rationale:** Generating speculative numerical values under the guise of "AI predictions" constitutes scientific malpractice. Marking unverified quantities as `NOT_PROJECTABLE` guarantees decision safety.

### Limitation 5: Bottleneck Detection Threshold Calibrated Post-Hoc / Exploratory
- **Detailed Description:** The decision boundary cutoff ($\tau = 0.40$) for flagging machine bottlenecks on the flow-ratio testbed was calibrated post-hoc on benchmark flow distributions.
- **System Impact:** While the model achieved Precision of $0.7778$, Recall of $0.8750$, and F1 of $0.8235$, these metrics reflect exploratory retrospective calibration rather than an unbiased prospective validation trial.

### Limitation 6: Synthetic Production and Energy Correlation Not Real-World Validation
- **Detailed Description:** The high correlation ($0.9988$) between scheduled and actual production in the controlled factory testbed is a consequence of deterministic scheduling rules within the synthetic generator.
- **System Impact:** This high metric must be interpreted strictly as verification of algorithmic pipeline consistency and not as empirical proof that real-world factories operate with $99.88\%$ adherence.

### Limitation 7: SHAP Attributions Represent Model Manifold, Not Physical Causality
- **Detailed Description:** TreeSHAP calculates the additive marginal contribution of input features to model output log-odds.
- **System Impact:** A high SHAP attribution indicates statistical correlation within the training distribution; it does not constitute physical causal proof. If a sensor drifts or correlates with an unmeasured lurking variable, SHAP will attribute importance to the proxy rather than the physical root cause.
- **Mitigation:** In NirmaanAI, SHAP rankings are never treated as final diagnoses; they serve merely as candidate hypotheses that must be corroborated by deterministic Root Cause Analysis (RCA) fault trees.

### Limitation 8: RAG Retrieval Precision@5 Reflects Document Density
- **Detailed Description:** In the hybrid TF-IDF/SVD RAG retrieval benchmark, the engine achieved $100\%$ Recall@5 (all true source documents were retrieved in the top 5), but Precision@5 was $0.4750$.
- **System Impact:** This indicates that while the system never misses the correct engineering reference, approximately half of the retrieved top-5 chunks contain contextual or peripheral information rather than direct verbatim answers.
- **Mitigation:** The Copilot's answer synthesizer uses authority weighting and strict keyword matching to filter irrelevant content before generating responses.

### Limitation 9: Lack of Prospective Field Validation
- **Detailed Description:** All validations conducted within NirmaanAI were performed on historical public benchmark splits (AI4I 2020, NASA C-MAPSS, UCI Electricity) or controlled synthetic environments.
- **System Impact:** True prospective validation requires deploying the platform across active industrial PLCs over months of live manufacturing cycles.

---

## 3. Future Work & Research Roadmap

### 3.1 Hardware-in-the-Loop & Industrial IoT Protocol Adapters
- **Objective:** Develop native communication adapters for industrial protocols:
  - **OPC-UA (IEC 62541):** Bidirectional subscription to Siemens S7-1500 and Beckhoff TwinCAT PLCs.
  - **MQTT with Sparkplug B:** Lightweight, edge-optimized pub/sub telemetry for distributed brownfield sensors.
  - **Modbus TCP:** Direct interrogation of legacy motor drives, power meters, and temperature controllers.

### 3.2 Quantized Edge Small Language Models (SLMs)
- **Objective:** Augment the deterministic TF-IDF/SVD RAG engine with an on-premises, 4-bit quantized local SLM (e.g., Llama-3-8B-Instruct or Phi-3-Mini) running on an edge GPU or Intel NPU.
- **Benefits:** Rich natural language synthesis for complex operator queries while maintaining zero external cloud API exposure and guaranteed air-gapped data privacy.

### 3.3 Bidirectional Closed-Loop SCADA Control
- **Objective:** Progress from advisory recommendations (open-loop decision support) to supervisory automated setpoint adjustments (closed-loop control) for verified non-safety-critical parameters:
  - Automated feed rate derating during thermal warnings.
  - Dynamic buffer routing adjustments during upstream bottlenecks.
  - Automated spare part reorder requests via SAP/Oracle ERP webhooks.

### 3.4 Dynamic Rule Weight Adaptation via Operator Feedback
- **Objective:** Implement a Reinforcement Learning from Human Feedback (RLHF) or Bayesian updating mechanism for recommendation rules:
  - When plant maintenance supervisors accept, modify, or reject recommendations, the system updates the rule's historical confidence score and priority weighting.

### 3.5 Multi-Site Enterprise Federation
- **Objective:** Implement federated learning across multiple geographically distributed manufacturing plants:
  - Train component failure models collaboratively without sharing proprietary factory telemetry across corporate boundaries.

---
*End of Formal Register of Technical Limitations & Future Work.*
