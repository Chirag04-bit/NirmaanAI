# NirmaanAI: Comprehensive Viva Voce & Oral Defense Examination Guide
**System Version:** v0.25.0  
**Repository:** `C:\NIRMAAN AI`  
**Scope:** 65 Comprehensive Technical Questions & Answers Across the Full Architectural Stack

---

## Table of Contents
1. [General System Vision, Novelty & Architecture (Q1–Q7)](#1-general-system-vision-novelty--architecture)
2. [Data Engineering, Schemas & Epistemic Taxonomy (Q8–Q14)](#2-data-engineering-schemas--epistemic-taxonomy)
3. [Predictive Maintenance & Remaining Useful Life (Q15–Q21)](#3-predictive-maintenance--remaining-useful-life)
4. [Anomaly Detection & PCA Reconstruction (Q22–Q26)](#4-anomaly-detection--pca-reconstruction)
5. [Bottleneck Detection & Production Forecasting (Q27–Q32)](#5-bottleneck-detection--production-forecasting)
6. [Explainable AI (SHAP) & Root Cause Analysis (Q33–Q37)](#6-explainable-ai-shap--root-cause-analysis)
7. [Factory Health Score & Diagnostic Banding (Q38–Q41)](#7-factory-health-score--diagnostic-banding)
8. [Financial Impact Analysis & Opportunity Segregation (Q42–Q45)](#8-financial-impact-analysis--opportunity-segregation)
9. [Prescriptive Recommendation Engine (Q46–Q49)](#9-prescriptive-recommendation-engine)
10. [What-If Digital-Twin-Inspired Simulation (Q50–Q53)](#10-what-if-digital-twin-inspired-simulation)
11. [Knowledge Retrieval (RAG) & AI Copilot (Q54–Q58)](#11-knowledge-retrieval-rag--ai-copilot)
12. [Full-Stack Engineering: Database, API & UI (Q59–Q62)](#12-full-stack-engineering-database-api--ui)
13. [Deployment Packaging, Limitations & Future Work (Q63–Q65)](#13-deployment-packaging-limitations--future-work)

---

### 1. General System Vision, Novelty & Architecture

#### Q1: What is NirmaanAI, and what core industrial challenge does it solve?
**Answer:**  
NirmaanAI is an end-to-end, multi-tier AI-powered manufacturing intelligence and prescriptive decision platform. Conventional smart manufacturing platforms suffer from the **"Fragmented Analytics Trap"**: predictive maintenance alerts, anomaly flags, bottleneck warnings, inventory ERP tables, and executive financial ledgers exist in disconnected data silos. Maintenance teams act on machine vibration without knowing if replacement bearings are in stock; plant managers observe throughput drops without tracing them to micro-stoppages; finance measures scrap losses retrospectively without knowing root causes. NirmaanAI bridges this gap by unifying raw industrial telemetry, ML diagnostics, deterministic root-cause analysis, operational loss accounting, inventory-aware prescriptive recommendations, and temporal simulation into a single closed-loop architecture.

#### Q2: What is the primary research gap addressed by NirmaanAI compared to existing literature?
**Answer:**  
Existing literature predominantly treats industrial AI tasks in isolation: PdM models predict failure times without assessing supply chain readiness; anomaly detection models flag outliers without causal attribution or financial impact quantification; LLM copilots hallucinate speculative maintenance remedies without grounding in real-time telemetry or deterministic safety manuals. Furthermore, published benchmarks frequently suffer from retrospective data leakage, evaluating prospective decisions using post-cutoff ground truth. NirmaanAI addresses this by enforcing an **8-tier epistemic taxonomy**, strict temporal isolation, deterministic evidence-grounded recommendation rules, and audit-grade financial loss segregation.

#### Q3: What is the overarching architecture of NirmaanAI?
**Answer:**  
NirmaanAI operates across seven distinct layers:
1. **Telemetry & Data Layer:** Unified 5-station factory topology (`M1` CNC Lathe, `M2` VMC Milling, `M3` Cylindrical Grinder, `M4` Optical Inspection, `M5` Robotic Assembly) streaming 43,200 sensor ticks and 300 production work orders.
2. **Machine Learning Diagnostic Layer:** XGBoost binary classifier for component failure, Random Forest regressor for RUL, PCA for unsupervised reconstruction error anomaly detection, flow-ratio heuristic for bottleneck tracking, and LightGBM for energy forecasting.
3. **Causal & Diagnostic Layer:** TreeSHAP feature attribution, candidate fault-tree Root Cause Analysis (RCA), and multi-dimensional Factory Health Scoring.
4. **Economic & Inventory Layer:** Activity-based loss accounting (realized downtime, scrap, rework, emergency labor, energy) and Wilson safety stock / reorder point inventory intelligence.
5. **Prescriptive & Simulation Layer:** Deterministic recommendation engine with strict antecedent verification, and discrete-event what-if counterfactual simulation.
6. **Knowledge & Copilot Layer:** Hybrid TF-IDF/SVD dense/sparse RAG engine (278 chunks, 18 sources) and 15-intent rule-governed Factory Copilot.
7. **Serving & Presentation Layer:** PostgreSQL 16 relational store (19 tables, Alembic migrations), FastAPI backend (40+ REST endpoints), and React 19 + Vite executive command dashboard.

#### Q4: How does NirmaanAI prevent speculative or non-actionable model outputs?
**Answer:**  
Every diagnostic output is mapped through a strict validation gate. Unsupervised anomalies or raw high failure probabilities cannot directly trigger operational interventions. Instead, outputs must be corroborated by multi-sensor evidence trees, matched against candidate mechanical fault signatures, checked against spare part availability, and validated against temporal cutoff boundaries before forming an actionable recommendation.

#### Q5: What is the difference between data flow and decision flow in NirmaanAI?
**Answer:**  
- **Data Flow (Bottom-Up):** Raw sensors $\to$ Ingestion & Preprocessing $\to$ Unified Feature Store $\to$ ML Inference (PdM, Anomaly, Bottleneck, Forecast) $\to$ Analytical Modules (SHAP, Health Score, Loss Engine).
- **Decision Flow (Top-Down & Lateral Corroboration):** Anomaly/PdM Triggers $\to$ Epistemic Classification $\to$ Fault Tree Evidence Matching (RCA) $\to$ Supply Chain Verification (ERP Inventory) $\to$ Rule-Based Recommendation Engine $\to$ What-If Counterfactual Evaluation $\to$ Operator Verification via AI Copilot / Executive Dashboard.

#### Q6: What original engineering contributions does NirmaanAI deliver?
**Answer:**  
1. A unified schema reconciling continuous 1-second telemetry, discrete production work orders, and maintenance logs into synchronized feature matrices.
2. A formal 8-tier epistemic taxonomy implemented directly in database schemas and API response envelopes.
3. An audit-grade activity-based operational loss engine that mathematically isolates realized historic losses from projected opportunity losses.
4. An inventory-conditioned recommendation engine preventing dangerous "repair immediately" directives when replacement parts are depleted.
5. A deterministic, evidence-grounded Factory Copilot with anti-hallucination guardrails operating with sub-26 ms latency without external LLM API cost or privacy exposure.

#### Q7: Why is NirmaanAI designed with deterministic rules rather than end-to-end deep reinforcement learning or generative agents?
**Answer:**  
Industrial manufacturing environments demand absolute determinism, auditable safety certifications, and explainability. A generative agent or black-box RL policy can propose non-compliant or physically hazardous actions (e.g., overriding feed limits without checking thermal tolerances, or fabricating maintenance steps). NirmaanAI restricts probabilistic models strictly to diagnostic sensing (classification, regression, reconstruction) while executing prescriptive recommendations and copilot responses via deterministic, rule-verified pipelines.

---

### 2. Data Engineering, Schemas & Epistemic Taxonomy

#### Q8: What are the 8 epistemic status tiers in NirmaanAI, and why are they vital?
**Answer:**  
The 8 tiers are:
1. `OBSERVED`: Raw empirical telemetry directly measured by physical sensors (e.g., vibration $= 5.62\text{ mm/s}$).
2. `DERIVED`: Deterministic mathematical calculations from observed data (e.g., cycle time ratio, power factor).
3. `MODEL_OUTPUT`: Statistical or ML inference outputs (e.g., XGBoost failure probability $= 0.996$).
4. `CONTROLLED_SYNTHETIC`: Deterministically injected test scenarios for system benchmarking (e.g., Days 18–21 M2 degradation).
5. `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`: Post-cutoff ground-truth events used strictly for verification and never as model inputs (e.g., `MAINT_0003` at $t = \text{Day 22 16:30 UTC}$).
6. `PROJECTED`: Statistically grounded counterfactual forward estimates under verified interventions.
7. `NOT_PROJECTABLE`: Quantities explicitly blocked from projection due to absent physical transfer functions or missing causal models.
8. `UNKNOWN`: Incomplete telemetry or unmonitored states.  
This prevents cognitive bias, halts data leakage, and ensures regulatory compliance.

#### Q9: What is the authoritative Temporal Cutoff in NirmaanAI, and how is it enforced?
**Answer:**  
The authoritative prospective decision cutoff is **2026-01-21 12:00:00 UTC** ($t_{\text{cutoff}}$). All models, recommendations, financial assessments, and copilot responses evaluated prospective to this point are strictly constrained to telemetry and work orders recorded on or before $t_{\text{cutoff}}$. Future events—specifically `MAINT_0003` occurring at **2026-01-22 16:30:00 UTC**—are quarantined as `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH` and are programmatically invisible to the inference engine.

#### Q10: What public benchmark datasets are incorporated into NirmaanAI?
**Answer:**  
1. **AI4I 2020 Predictive Maintenance Dataset** (UCI/Matthias Fonteyne): 10,000 synthetic machine operation records with 5 component failure modes.
2. **NASA C-MAPSS Turbofan Degradation Dataset (FD001)**: Run-to-failure run cycles for turbofan engines across 21 sensor channels.
3. **UCI Electricity Load Diagrams 2011–2014**: High-resolution electrical consumption series for industrial energy forecasting.
4. **UCI SECOM**: Semiconductor manufacturing fab process features for defect benchmarking.
5. **UCI Appliances Energy**: Telemetry benchmark for multi-variate environmental modeling.

#### Q11: Describe the unified 5-station factory topology modeled in NirmaanAI.
**Answer:**  
The platform models a sequential automotive components manufacturing line:
- **Station M1 (CNC Lathe):** Turning and rough machining operations.
- **Station M2 (VMC Milling):** Precision vertical milling (the designated degradation testbed).
- **Station M3 (Cylindrical Grinder):** Surface finishing and tolerance grinding.
- **Station M4 (Optical Inspection):** Automated dimensional inspection and quality verification.
- **Station M5 (Robotic Assembly):** Sub-assembly mating, fastener torquing, and final packing.

#### Q12: What is the dataset integrity checksum for NirmaanAI, and how was it verified?
**Answer:**  
The authoritative MD5 checksum for the controlled operational loss dataset (`operational_losses.csv`) is:  
`34B12582B32D81E3121429C55EBF74E8`.  
This is validated programmatically in `tests/test_dataset_integrity.py` across every test cycle.

#### Q13: How was data leakage prevented across train, validation, and test splits?
**Answer:**  
1. **Temporal/Group Splitting:** Time-series and run-to-failure records (e.g., C-MAPSS) were split strictly by engine unit ID, ensuring no unit in the test set appeared in training.
2. **Scaler Isolation:** Feature scalers (e.g., `StandardScaler`, `MinMaxScaler`) were fitted exclusively on the training folds and applied out-of-sample to validation and test folds.
3. **Strict Epistemic Isolation:** Maintenance records timestamped after $t_{\text{cutoff}}$ were isolated into a retrospective quarantine table inaccessible to the live feature pipeline.

#### Q14: How does the Unified Schema handle missing or asynchronously arriving sensor data?
**Answer:**  
Sensor telemetry is synchronized into 1-minute aggregations via deterministic forward-filling (up to a 5-minute threshold) and rolling statistics (mean, variance, peak-to-peak). If telemetry data coverage drops below 40% across a sliding window, the Factory Health Score engine assigns a `DATA_INSUFFICIENT` flag and suppresses automated high-confidence predictions.

---

### 3. Predictive Maintenance & Remaining Useful Life

#### Q15: Which algorithm was selected for binary failure prediction on AI4I 2020, and what were the performance metrics?
**Answer:**  
**XGBoost** was the champion model. Evaluated on the held-out test split (1,500 samples, 51 true positives):
- **Precision:** $0.9545$
- **Recall:** $0.8235$
- **F1-Score:** $0.8842$
- **ROC-AUC:** $0.9831$
- **PR-AUC:** $0.8647$
- **Calibrated Threshold ($\tau$):** $0.9100$
- **Confusion Matrix:** $\text{TN}=1447, \text{FP}=2, \text{FN}=9, \text{TP}=42$.

#### Q16: Why was the decision threshold set to 0.91 rather than the standard 0.50?
**Answer:**  
Industrial maintenance incurs significant false-alarm costs (unnecessary machine teardowns, schedule disruption, and technician dispatch). Setting $\tau = 0.91$ heavily penalizes False Positives (reducing FP to just 2) while maintaining strong Recall ($82.35\%$), yielding an outstanding Precision of $95.45\%$ and maximizing operational cost-effectiveness.

#### Q17: Which model was selected for Remaining Useful Life (RUL) estimation on NASA C-MAPSS FD001?
**Answer:**  
**Random Forest Regressor** achieved champion performance on FD001:
- **MAE:** $13.21$ operating cycles
- **RMSE:** $18.11$ operating cycles
- **Coefficient of Determination ($R^2$):** $0.7957$  
This outperformed baseline Gradient Boosting and Ridge models while providing stable piecewise constant predictions across early operating life.

#### Q18: What feature engineering was applied to C-MAPSS sensor channels?
**Answer:**  
Constant/invariant sensors (Channels 1, 5, 10, 16, 18, 19) were removed. The remaining 14 active channels were transformed using rolling window statistics (rolling mean, rolling standard deviation over 5, 10, and 20 cycle horizons), capturing dynamic degradation trends and sensor drift.

#### Q19: Why was an upper bound (piecewise linear target) applied to RUL modeling?
**Answer:**  
In physical turbomachinery, degradation is negligible during early operating cycles. Modeling linear decay from cycle 1 forces the regressor to learn non-existent wear patterns. An upper clip at $RUL_{\text{max}} = 125$ cycles was applied, reflecting realistic initial healthy plateaus and stabilizing gradient descent.

#### Q20: How does NirmaanAI handle extreme class imbalance in industrial failure datasets?
**Answer:**  
The AI4I dataset contains only $3.39\%$ failure instances. NirmaanAI resolved this without synthetic SMOTE artifacts (which can violate physical thermodynamic correlations) by:
1. Utilizing scale-pos-weight tuning in XGBoost to balance negative and positive gradients.
2. Optimizing the decision threshold directly against the Precision-Recall curve (PR-AUC: $0.8647$).
3. Evaluating with cost-sensitive utility matrices rather than raw accuracy.

#### Q21: What are the failure modes detected by NirmaanAI's multi-class framework?
**Answer:**  
On the AI4I foundation, the system recognizes:
1. Tool Wear Failure (TWF)
2. Heat Dissipation Failure (HDF)
3. Power Failure (PWF)
4. Overstrain Failure (OSF)
5. Random Failures (RNF)

---

### 4. Anomaly Detection & PCA Reconstruction

#### Q22: Which unsupervised anomaly detection algorithm was deployed, and why?
**Answer:**  
**Principal Component Analysis (PCA) Reconstruction Error** was chosen as the primary anomaly detector. PCA projects multi-sensor features onto orthogonal eigenvectors capturing dominant operational variance. Unseen mechanical anomalies (such as bearing micro-chatter or spindle unbalance) fall outside the principal subspace, causing a sharp spike in reconstruction error (Squared Prediction Error / $Q$-statistic). PCA was chosen over Deep Autoencoders due to its mathematical determinism, zero GPU dependency, sub-millisecond inference time, and auditable linear projection.

#### Q23: What were the quantitative validation metrics for the PCA anomaly detector?
**Answer:**  
Evaluated on the controlled validation set:
- **ROC-AUC:** $0.9992$
- **PR-AUC:** $0.9965$
- **Precision:** $0.9722$
- **Recall:** $1.0000$
- **F1-Score:** $0.9859$
- **Calibrated Error Threshold ($\tau_{\text{recon}}$):** $0.24050$

#### Q24: What is the early detection lead time achieved by the PCA model on Machine M2?
**Answer:**  
The PCA anomaly detector triggered at **Day 18 05:30:00 UTC**, whereas catastrophic bearing seizure (`MAINT_0003`) occurred at **Day 22 16:30:00 UTC**. This provided an early warning lead time of **106.5 hours (4.44 days)**, affording ample time to inspect, reduce feed rate, or schedule planned maintenance.

#### Q25: Why is PCA reconstruction error preferred over Isolation Forest in NirmaanAI?
**Answer:**  
Isolation Forest relies on randomized tree partitioning, resulting in non-deterministic anomaly scores across runs unless rigidly seeded. PCA yields exact, closed-form algebraic reconstruction metrics, allowing direct decomposition of reconstruction residuals back to specific sensor channels for instant diagnostic explainability.

#### Q26: How does NirmaanAI guard against sensor drift creating false positive anomalies?
**Answer:**  
The platform applies an adaptive baseline comparison window and multi-sensor corroboration. A single sensor exceeding its threshold is flagged as potential instrument drift or calibration error; an operational anomaly requires co-elevation across vibration, acoustic, and thermal channels.

---

### 5. Bottleneck Detection & Production Forecasting

#### Q27: How is a station bottleneck formally defined in NirmaanAI?
**Answer:**  
A station is flagged as a bottleneck if its operating state satisfies the compound condition:
$$\text{cycle\_ratio} \ge 1.20 \quad \lor \quad \text{start\_delay} \ge 10\text{ min} \quad \lor \quad \text{job\_status} = \text{"DELAYED"}$$
where $\text{cycle\_ratio} = \frac{\text{actual\_cycle\_time}}{\text{nominal\_cycle\_time}}$.

#### Q28: What were the validation metrics of the bottleneck detection model, and what is its epistemic status?
**Answer:**  
On the test split:
- **Precision:** $0.7778$
- **Recall:** $0.8750$
- **F1-Score:** $0.8235$
- **ROC-AUC:** $0.9882$
- **PR-AUC:** $0.8040$
- **False Positive Rate:** $0.0164$
- **Cutoff ($\tau$):** $0.4000$  
**Crucial Epistemic Note:** This cutoff was calibrated exploratory/post-hoc on benchmark flow distributions. It is explicitly classified as an exploratory baseline rather than an unbiased prospective validation.

#### Q29: What were the results of the production and energy forecasting models?
**Answer:**  
- **UCI Electricity Benchmark (LightGBM):**
  - **WAPE:** $6.50\%$
  - **sMAPE:** $6.37\%$
  - **RMSE:** $26.23\text{ kW}$
  - **MAE:** $13.80\text{ kW}$
  - **$R^2$:** $0.9605$
- **Controlled Synthetic Plant Energy:**
  - **MAE:** $0.1874$
  - **RMSE:** $0.2335$
  - **WAPE:** $0.31\%$
  - **sMAPE:** $0.31\%$
  - **$R^2$:** $-0.0391$ (due to near-constant baseline variance in controlled conditions).
- **Controlled Production Output:**
  - Correlation: $0.9988$ (strictly labeled as controlled synthetic behavior).

#### Q30: What are the classical inventory control formulas implemented in NirmaanAI?
**Answer:**  
For each critical spare part $i$:
1. **Safety Stock ($SS$):**
   $$SS = Z \times \sigma_d \times \sqrt{L}$$
   where $Z = 1.645$ (95% service level), $\sigma_d$ is daily demand standard deviation, and $L$ is lead time in days.
2. **Reorder Point ($ROP$):**
   $$ROP = (\bar{d} \times L) + SS$$
   where $\bar{d}$ is average daily demand.

#### Q31: What is the exact inventory status of the Machine M2 Spindle Bearing at decision cutoff?
**Answer:**  
- **On-hand Stock:** $2.0\text{ units}$
- **Safety Stock ($SS$):** $1.134\text{ units}$
- **Reorder Point ($ROP$):** $1.367\text{ units}$
- **Supplier Lead Time ($L$):** $7.0\text{ days}$
- **Status at Cutoff:** Healthy ($2.0 > ROP$). The current stock is NOT below $SS$ or $ROP$.

#### Q32: Why does the system trigger an "Expedite Spare Part" recommendation if current stock is 2.0 and ROP is 1.367?
**Answer:**  
This illustrates NirmaanAI's **prescriptive foresight**. The primary maintenance recommendation is to replace the degraded spindle bearing immediately. Performing this replacement consumes 1 unit, reducing projected on-hand inventory to $1.0\text{ unit}$. Because $1.0 < SS$ ($1.134$), the post-service inventory drops into the safety violation zone with a 7-day supplier lead time. The system proactively triggers Rule `R-I01` (`EXPEDITE_CRITICAL_SPARE`) simultaneously with the maintenance work order.

---

### 6. Explainable AI (SHAP) & Root Cause Analysis

#### Q33: How does NirmaanAI utilize TreeSHAP, and what were the top feature contributions on AI4I?
**Answer:**  
TreeSHAP computes exact Shapley values across tree ensembles, measuring the additive marginal contribution of each sensor feature to the log-odds failure probability. For the AI4I XGBoost model, the top features ranked by mean absolute SHAP value are:
1. `tool_wear_min` ($+1.84$ log-odds impact)
2. `rotational_speed_rpm` (inverse relation with torque)
3. `mechanical_power_kw`
4. `temperature_diff_k` (process temp minus air temp)
5. `torque_nm`

#### Q34: Does SHAP constitute causal proof of machine failure?
**Answer:**  
**No.** SHAP measures mathematical feature importance in the model's manifold, not physical causality. High SHAP value indicates statistical association under the training distribution. Corrupted sensors, collinear variables, or external confounding factors can produce high SHAP attributions without direct physical causality. In NirmaanAI, SHAP attributions serve as candidate hypotheses that must be corroborated by physical Fault Tree Root Cause Analysis (RCA).

#### Q35: How does the deterministic Root Cause Analysis (RCA) module work?
**Answer:**  
The RCA module evaluates active sensor telemetry, SHAP attributions, and maintenance history against candidate mechanical fault signatures:
- `BEARING_DEGRADATION`: High vibration, elevated acoustic emission, high tool wear.
- `THERMAL_OVERLOAD`: High process temperature, low rotational speed, high torque.
- `MECHANICAL_LOAD_IMBALANCE`: Spindle unbalance, high torque variance, cyclic vibration.
It computes an evidence score $S \in [0, 1]$ based on the proportion of corroborated symptoms across physical sensors.

#### Q36: What was the authoritative RCA result for Machine M2 at the decision cutoff?
**Answer:**  
- **Primary Root Cause:** `MECHANICAL_LOAD` / Spindle Bearing Wear
- **Confidence Score:** $0.7912$ (Categorized as `HIGH`)
- **Corroborating Evidence:** 4 distinct sources (vibration amplitude at $5.62\text{ mm/s}$, acoustic emission increase, cycle time expansion, and tool wear threshold).
- **Epistemic Classification:** `MODEL_OUTPUT` / `DERIVED`.

#### Q37: What is the retrospective maintenance event MAINT_0003?
**Answer:**  
`MAINT_0003` is a scheduled ground-truth failure record occurring on **2026-01-22 16:30:00 UTC** (unplanned emergency stop on M2, bearing seizure, 150 minutes downtime). Because this occurred 28.5 hours after $t_{\text{cutoff}}$, it serves strictly as **retrospective validation** proving that the prospective warning issued at $t_{\text{cutoff}}$ was accurate.

---

### 7. Factory Health Score & Diagnostic Banding

#### Q38: What are the five diagnostic health score bands in NirmaanAI?
**Answer:**  
1. **$90.0 - 100.0$:** `EXCELLENT` (Optimal operational condition)
2. **$75.0 - 89.9$:** `HEALTHY` (Normal operating state)
3. **$60.0 - 74.9$:** `WATCH` (Sub-nominal performance or minor drift)
4. **$40.0 - 59.9$:** `DEGRADED` (Significant wear, thermal distress, or backlog)
5. **$0.0 - 39.9$:** `CRITICAL` (Imminent failure risk, severe stoppage, or safety hazard)

#### Q39: What mathematical formulation governs the Factory Health Score?
**Answer:**  
The composite health score $H_m \in [0, 100]$ for machine $m$ is a weighted aggregation:
$$H_m = w_{\text{pdm}}(1 - P_{\text{fail}}) \times 100 + w_{\text{anom}}(1 - S_{\text{anom}}) \times 100 + w_{\text{flow}}(1 - B_{\text{ratio}}) \times 100 + w_{\text{qual}} Q_{\text{rate}} \times 100$$
where weights are normalized ($\sum w_i = 1.0$), subject to a hard coverage penalty if valid sensor frames represent $< 40\%$ of the evaluation window.

#### Q40: What was the authoritative Health Score and Status for Machine M2 at cutoff?
**Answer:**  
- **Health Score:** **$26.88 / 100$**
- **Band:** **`CRITICAL`**
- **Underlying Probability of Failure:** $99.6\%$
- **Contributing Factors:** Vibration exceeding safety envelope ($5.62\text{ mm/s}$ vs $1.4\text{ mm/s}$ baseline), cycle ratio degradation ($1.38$), and elevated PCA reconstruction error ($0.7812$).

#### Q41: How does the system handle telemetry dropout during health computation?
**Answer:**  
If sensor data coverage drops below $40\%$, the health engine emits `DATA_INSUFFICIENT` and caps the maximum health score at $50.0$ (`DEGRADED`), preventing the platform from reporting a machine as "HEALTHY" simply because absent telemetry prevented failure detection.

---

### 8. Financial Impact Analysis & Opportunity Segregation

#### Q42: What is the vital distinction between Realized Losses and Projected Opportunity Losses?
**Answer:**  
- **Realized Losses (`DERIVED`):** Sunk, historical operational costs already incurred on the shop floor up to $t_{\text{cutoff}}$ (e.g., recorded scrap units multiplied by unit cost, recorded emergency technician hours multiplied by hourly rate).
- **Projected Opportunity Losses (`PROJECTED`):** Counterfactual estimates of potential financial exposure if degraded machines continue operating without intervention until failure. Conflating these two creates severe accounting fraud and misleading ROI calculations.

#### Q43: What are the authoritative plant-wide and M2 financial figures at cutoff?
**Answer:**  
- **Plant-Wide:**
  - **Realized Historic Loss:** **₹229,105.54**
  - **Projected Opportunity Exposure:** **₹24,320.00**
  - **Gross Exposure:** **₹253,425.54**
- **Machine M2 Breakdown:**
  - **Realized Loss:** **₹73,062.28**
    - Unplanned Downtime: ₹11,250.00
    - Scrap Production: ₹51,800.00
    - Production Rework: ₹6,475.00
    - Emergency Labor: ₹420.00
    - Energy Inefficiency: ₹3,117.28
  - **Projected Opportunity Exposure:** **₹24,320.00**
  - **Gross Financial Exposure:** **₹97,382.28**

#### Q44: What are the economic assumptions utilized in NirmaanAI's cost model?
**Answer:**  
- Unplanned Downtime Cost: ₹4,500.00 / hour (M2 rate)
- Scrap Part Cost: ₹350.00 / component
- Rework Part Cost: ₹175.00 / component
- Emergency Maintenance Labor: ₹280.00 / technician-hour
- Industrial Energy Tariff: ₹8.50 / kWh

#### Q45: What financial savings are estimated under What-If Scenario D?
**Answer:**  
Under Scenario D (Comprehensive Proactive Intervention: bearing replacement + feed rate derating):
- **Avoided Projected Opportunity Loss:** **₹19,520.00**
- **Remaining Unavoidable Opportunity Cost:** **₹4,800.00** (cost of 1-hour planned maintenance window)
- **Net Remaining Gross Exposure:** **₹77,862.28** (₹73,062.28 realized + ₹4,800.00 planned downtime).  
*These savings are strictly classified as `PROJECTED` counterfactual benefits, not observed cash savings.*

---

### 9. Prescriptive Recommendation Engine

#### Q46: How does NirmaanAI formulate prescriptive recommendations?
**Answer:**  
Recommendations are generated via a deterministic, evidence-grounded rule engine. Each rule defines strict antecedents (health band, failure probability, RCA confirmation, inventory stock) before firing an action. Every action carries an ID, priority (`CRITICAL`, `HIGH`, `MEDIUM`), time horizon, evidence strength (`STRONG`, `WEAK`), and epistemic tags.

#### Q47: What are the four active recommendations generated for Machine M2 at cutoff?
**Answer:**  
1. **`REC-M2-01` (Spindle Bearing Inspection & Overhaul):**
   - Priority: `CRITICAL` | Horizon: `IMMEDIATE` | Evidence: `STRONG` (Vibration $5.62\text{ mm/s}$, RCA score $0.791$).
2. **`REC-M2-02` (Derate Spindle Feed Rate by 15%):**
   - Priority: `HIGH` | Horizon: `SAME_DAY` | Evidence: `WEAK` (Interim load mitigation).
3. **`REC-M2-03` (Reschedule Pending Work Orders to M1/M3 Buffer):**
   - Priority: `HIGH` | Horizon: `SAME_DAY` | Evidence: `WEAK` (Mitigate bottleneck risk).
4. **`REC-M2-04` (Expedite Replacement Spindle Bearing):**
   - Priority: `HIGH` | Horizon: `SAME_DAY` | Evidence: `STRONG` (Post-maintenance inventory will drop to $1.0 < SS$).

#### Q48: Why do recommendations refuse to use financial loss values as physical corroboration?
**Answer:**  
Financial losses are derivative economic accounting metrics, not physical phenomena. A machine incurring high financial loss might simply be running high-value parts rather than experiencing severe mechanical wear. Conflating financial loss with physical evidence would cause the system to over-recommend repairs on expensive parts while ignoring critical mechanical wear on cheap parts.

#### Q49: What prevents recommendation loops or conflicting directives?
**Answer:**  
Rule priority hierarchies and exclusivity mutex locks ensure consistency. If an `IMMEDIATE_SHUTDOWN` or `CRITICAL_INSPECTION` rule is active, contradictory rules such as `INCREASE_THROUGHPUT` are suppressed.

---

### 10. What-If Digital-Twin-Inspired Simulation

#### Q50: What is the purpose of NirmaanAI's What-If simulation engine?
**Answer:**  
The simulation engine enables plant managers to model the counterfactual operational and economic consequences of alternative decisions before taking action. It evaluates four standardized scenarios:
- **Scenario A:** No intervention (baseline degradation continues).
- **Scenario B:** Immediate emergency shutdown and bearing replacement.
- **Scenario C:** 15% feed rate derating without immediate stoppage.
- **Scenario D:** Coordinated intervention (planned 1-hour service during shift change + spare part reorder).

#### Q51: What does the designation NOT_PROJECTABLE signify in the simulation?
**Answer:**  
When an intervention's outcome cannot be rigorously derived from empirical physical transfer functions, NirmaanAI marks that KPI as `NOT_PROJECTABLE` rather than inventing speculative numbers. For instance, predicting the exact microsecond acoustic resonance of a degraded spindle under partial lubrication is physically unverified; projecting it would be unscientific. Marking it `NOT_PROJECTABLE` upholds epistemic integrity.

#### Q52: How are throughput and scrap estimated under Scenario C?
**Answer:**  
Derating the feed rate by 15% increases nominal cycle time from $45\text{ s}$ to $52.9\text{ s}$, reducing hourly throughput from $80$ to $68\text{ parts/hr}$. However, thermal cutting stress decreases, lowering projected scrap rate from $8.2\%$ to $3.1\%$, balancing production loss against defect reduction.

#### Q53: Why is NirmaanAI referred to as "Digital-Twin-Inspired" rather than a full Digital Twin?
**Answer:**  
A true 3D/Physics Digital Twin requires real-time finite element analysis (FEA), bidirectional SCADA actuator control, and micro-second physics simulation. NirmaanAI provides statistical, discrete-event, and economic digital-twin capabilities. Calling it "Digital-Twin-Inspired" accurately reflects its analytical scope without misleading industrial stakeholders.

---

### 11. Knowledge Retrieval (RAG) & AI Copilot

#### Q54: What architecture powers NirmaanAI's Factory Knowledge RAG engine?
**Answer:**  
The RAG engine indexes 278 structured chunks across 18 authoritative documents in the validated NirmaanAI knowledge base. It utilizes a deterministic **hybrid retrieval model**:
- **Dense Representation:** 256-dimensional truncated SVD over TF-IDF n-grams (sub-millisecond cosine similarity).
- **Sparse Representation:** BM25/keyword frequency scoring.
- **Hybrid Score:** $0.70 \times \text{Dense} + 0.30 \times \text{Sparse}$, weighted by document authority level.

#### Q55: What were the benchmark validation metrics for the RAG engine?
**Answer:**  
Across the 16-query industrial benchmark:
- **Recall@5:** **$1.0000$** ($100\%$ relevant document retrieval in top-5)
- **Mean Reciprocal Rank (MRR):** **$0.8125$**
- **Precision@5:** **$0.4750$**
- **Anti-Hallucination Rate:** **$1.0000$** ($100\%$ factual grounding)
- **Average Query Latency:** **$21.97\text{ ms}$**

#### Q56: Why does NirmaanAI use TF-IDF/SVD rather than massive proprietary LLMs (e.g., GPT-4)?
**Answer:**  
1. **Determinism:** TF-IDF/SVD vector spaces produce 100% reproducible retrieval without temperature drift.
2. **Anti-Hallucination Guardrails:** Answers are synthesized strictly from retrieved knowledge base chunks and verified against plant entity boundaries.
3. **Air-Gapped Privacy:** Manufacturing telemetry and validated knowledge documents never leave the factory LAN.
4. **Latency & Cost:** $22\text{ ms}$ latency on commodity CPU with zero API subscription overhead.

#### Q57: How does the AI Factory Copilot classify user intents?
**Answer:**  
The Copilot features a deterministic 15-intent slot-filling classifier covering:
- `MACHINE_HEALTH`
- `PREDICTIVE_MAINTENANCE`
- `ANOMALY_STATUS`
- `BOTTLENECK_IDENTIFICATION`
- `ENERGY_FORECAST`
- `INVENTORY_LEVEL`
- `FINANCIAL_LOSS`
- `RECOMMENDATION_QUERY`
- `SIMULATION_RUN`
- `RCA_EXPLANATION`
- `SYSTEM_PROVENANCE`
- `ISO_STANDARDS`
- `SHIFT_SUMMARY`
- `OPERATOR_GUIDANCE`
- `UNKNOWN_FALLBACK`  
On the 14-case regression test suite, the Copilot achieved **100% intent classification accuracy**.

#### Q58: How does the Copilot handle prompt injection or adversarial queries?
**Answer:**  
Input prompts pass through strict regex sanitization, length truncators ($< 500$ chars), and blacklisted keyword filters (`DROP TABLE`, `ignore previous instructions`, `bypass guardrails`). Furthermore, the Copilot cannot execute arbitrary code or write to the database; it is strictly a read-only query synthesizer.

---

### 12. Full-Stack Engineering: Database, API & UI

#### Q59: Describe the PostgreSQL relational schema supporting NirmaanAI.
**Answer:**  
The relational schema comprises 19 normalized tables managed via SQLAlchemy 2.x and Alembic:
- Core Assets: `machines`, `sensor_telemetry`, `production_jobs`, `maintenance_logs`, `inventory_items`.
- ML & Diagnostics: `model_registry`, `predictions`, `anomaly_events`, `bottleneck_records`, `forecasts`.
- Prescriptive & Analytics: `shap_attributions`, `rca_records`, `health_scores`, `financial_losses`, `recommendations`, `simulation_runs`.
- System & Governance: `knowledge_documents`, `copilot_audit_logs`, `epistemic_audit_trail`.  
Every row includes `epistemic_status`, `provenance_hash`, and ISO-8601 timestamps.

#### Q60: How is the FastAPI backend architected?
**Answer:**  
The backend (`backend/main.py`) exposes 40+ REST endpoints organized into modular routers:
- Pydantic v2 schemas ensure strict request/response data validation.
- Dependency injection handles database session pooling.
- A built-in service layer decouples HTTP transport from analytical algorithms.
- Full CORS middleware enables secure local and containerized access.
- In the absence of live PostgreSQL, an in-memory synthetic seed fallback ensures full endpoint functionality for local frontend development.

#### Q61: What technologies power the frontend dashboard?
**Answer:**  
The frontend is built on **React 19** and **Vite**, written in modern modular JavaScript and styled with clean Vanilla CSS (responsive CSS Grid, dark-mode glassmorphism, zero Tailwind bloat):
- **Executive Command Center:** Global OEE, health gauges, plant financial cards.
- **Machine Grid:** Real-time status cards for M1–M5.
- **M2 Deep-Dive Diagnostic:** Sensor telemetry charts, PCA error plots, SHAP waterfall charts.
- **Prescriptive Action Center:** Filterable recommendation cards with priority badges.
- **Simulation Studio:** Interactive What-If slider controls and side-by-side scenario comparisons.
- **Copilot Drawer:** Floating interactive chat interface with suggested prompt chips.

#### Q62: How does the frontend handle backend disconnection?
**Answer:**  
The frontend implements an **Offline Resilience Fallback**: if the FastAPI backend is unreachable, the client transitions gracefully to a bundled mock data provider reflecting Phase 22 seed values, preventing UI crashing and displaying a subtle "Offline / Demonstration Mode" badge.

---

### 13. Deployment Packaging, Limitations & Future Work

#### Q63: What are the primary environment limitations currently documented for NirmaanAI?
**Answer:**  
1. **Docker Engine Host Limitation:** Docker Engine / Docker Desktop was not installed on the native Windows development host. The container configuration (`Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.prod.yml`) was fully verified through static linting and multi-stage syntax audits, but runtime daemon execution remains on `HOLD — ENVIRONMENT BLOCKED`.
2. **Native PostgreSQL Daemon:** PostgreSQL 16 server was not locally installed as a native Windows service. The system was validated against SQLite/In-Memory fallbacks while preserving PostgreSQL Alembic migrations for production containerized deployment.

#### Q64: What are the core industrial limitations of the platform?
**Answer:**  
1. **Synthetic Telemetry Baseline:** While public benchmarks (AI4I, C-MAPSS, UCI Electricity) are real/established, the unified 5-station continuous telemetry is controlled synthetic data. Field deployment across heterogeneous industrial protocols (OPC-UA, MQTT, Modbus) remains required.
2. **Exploratory Bottleneck Cutoff:** The bottleneck heuristic cutoff ($\tau = 0.40$) was tuned post-hoc and requires prospective factory validation.
3. **Discrete Simulation:** What-If simulations model discrete operational states rather than high-fidelity thermo-mechanical continuous physics.

#### Q65: What are the most promising avenues for Future Work?
**Answer:**  
1. **Industrial Hardware-in-the-Loop Testing:** Integrating real OPC-UA/MQTT gateway adapters connected to physical PLCs (Siemens S7, Allen-Bradley).
2. **Quantized Local Small Language Models:** Deploying a quantized 3B/7B parameter local SLM (e.g., Llama-3-8B-Instruct or Phi-3) fine-tuned on ISO maintenance standards to supplement the TF-IDF/SVD RAG engine.
3. **Automated Feedback Learning:** Ingesting operator feedback on recommendation utility to dynamically adjust rule confidence weights.
4. **Multi-Plant Federation:** Extending the architecture to federated multi-factory enterprise deployments with cross-plant benchmark analytics.

---
*End of Comprehensive Viva Voce & Oral Defense Examination Guide.*
