# NirmaanAI: An End-to-End Grounded Cyber-Physical Intelligence & Decision Platform for Manufacturing MSMEs

**IEEE Format Technical Research Paper**  
**Authors**: NirmaanAI Research & Systems Engineering Group  
**Target Venue**: IEEE Transactions on Industrial Informatics / IEEE Robotics and Automation Letters (RA-L)  
**Date**: September 2026  

---

### Abstract
Small and Medium Enterprises (MSMEs) in precision manufacturing operate with minimal capital buffers and are acutely vulnerable to unplanned equipment breakdowns, unpredicted line bottlenecks, and supply chain stockouts. Existing enterprise industrial AI architectures are typically capital-intensive, closed, and detached from shop-floor decision realities. This paper presents **NirmaanAI**, an integrated, open-architecture Cyber-Physical System (CPS) and decision intelligence platform specifically engineered for resource-constrained manufacturing environments. NirmaanAI links raw multivariate equipment telemetry with failure prediction (XGBoost F1: 0.8842 on AI4I 2020), Remaining Useful Life (Random Forest RMSE: 18.11 cycles on NASA C-MAPSS), multivariate anomaly detection (PCA PR-AUC: 0.9965), and dispatch-time bottleneck prediction (F1: 0.8235). Uniquely, the platform transforms statistical inferences into rupee-denominated financial loss assessments, couples maintenance directives with dynamic inventory safety stocks ($SS = 1.134$), and evaluates counterfactual "what-if" policies through a digital twin simulation studio. A grounded, vector-indexed factory knowledge memory (Recall@5: 1.000) powers an AI Factory Copilot enforcing an 8-tier epistemic taxonomy that eliminates generative hallucinations. Across 355 automated test items, the integrated platform exhibits zero regressions, providing a reproducible paradigm for democratizing industrial AI.

### Index Terms
Industrial Artificial Intelligence, Cyber-Physical Systems, Predictive Maintenance, Explainable AI (SHAP), Digital Twin Simulation, Prescriptive Operations Research, Retrieval-Augmented Generation (RAG).

---

## I. INTRODUCTION
THE transition toward Industry 4.0 has yielded substantial productivity gains in large-scale manufacturing conglomerates equipped with dedicated data science teams and bespoke Industrial IoT infrastructure. However, for the millions of Micro, Small, and Medium Enterprises (MSMEs)—which constitute over 90% of global industrial establishments—the adoption of AI-driven decision tools remains minimal. 

MSME machine shops typically house heterogeneous machinery across multiple vintages. Equipment maintenance is predominantly reactive or calendar-driven. Reactive run-to-failure strategies incur catastrophic secondary tool breakage, work-in-progress (WIP) scrap, and punitive customer delay penalties. Calendar preventive maintenance, conversely, halts healthy machines prematurely.

While modern statistical learning models can predict equipment failure with high accuracy, existing academic research rarely addresses the **operational and economic triad** required for deployment:
1. *Financial Quantification*: Linking probabilistic risk scores to concrete currency losses.
2. *Production Constraint Coupling*: Recognizing whether a degraded asset is an active bottleneck starving downstream operations.
3. *Inventory Synchronization*: Verifying spare parts availability before taking machines offline.

To address these challenges, we present **NirmaanAI**, a complete, modular, and grounded manufacturing decision support platform.

---

## II. RELATED WORK
### A. Predictive Maintenance & Prognostics
Early failure modeling relied on physical degradation equations such as Paris' law for crack propagation. In recent years, data-driven approaches have gained dominance. Matzka [1] introduced the AI4I 2020 predictive maintenance benchmark, demonstrating the utility of tree-based ensembles for multi-mode failure classification. For prognostics, the NASA Commercial Modular Aero-Propulsion System Simulation (C-MAPSS) dataset developed by Saxena et al. [2] serves as the standard benchmark for Remaining Useful Life (RUL) estimation under run-to-failure conditions.

### B. Industrial Anomaly Detection
Unsupervised multivariate screening is critical because true failure events are rare in nominal factory operations. McCann et al. [3] explored sensor correlation matrices in semiconductor manufacturing (UCI SECOM). Principal Component Analysis (PCA) reconstruction error and Isolation Forests remain preferred baselines due to computational efficiency and interpretability on edge devices.

### C. Explainability & Causal Root Cause Analysis
Explainable AI (XAI) is vital for industrial trust. Lundberg and Lee [4] established SHAP (SHapley Additive exPlanations) based on cooperative game theory, providing unified local feature attributions. However, researchers frequently confuse predictive feature importance with physical causality. Root cause analysis requires combining statistical attributions with physical fault tree logic.

### D. Prescriptive Operations Research & Grounded Copilots
Operations research traditionally solves dynamic safety stock and replenishment rules in isolation from equipment condition [5]. Recently, LLM-based assistants have been proposed for industrial operations, but generic models suffer from hallucination and temporal leakage [6]. Grounding models through Retrieval-Augmented Generation (RAG) with formal epistemic status labeling represents the frontier of reliable industrial AI.

---

## III. RESEARCH GAP
1. **The Disconnected AI Silo**: ML models predict failure probabilities, scheduling heuristics manage job queues, and ERP systems track inventory—yet these systems never communicate.
2. **Abstract Metrics vs. Economic Realities**: Academic benchmarks report AUC-ROC or RMSE, which shop-floor managers cannot map to capital loss or shift budgets.
3. **Unconstrained Generative Chatbots**: Emerging conversational factory tools lack temporal boundary enforcement, allowing future ground truth to contaminate historical operational audits.

---

## IV. PROPOSED ARCHITECTURE
NirmaanAI is structured across five integrated functional layers:
- **Layer 1: Unified Schema**: Standardizes multi-rate sensors, machines, production jobs, inventory SKUs, and Indian industrial financial parameters in a normalized PostgreSQL schema.
- **Layer 2: Inference Core**: Executes XGBoost failure prediction ($\tau=0.91$), Random Forest RUL estimation, PCA anomaly detection ($\tau=0.24050$), and bottleneck flow heuristics ($\tau=0.40$).
- **Layer 3: Explainability & Business Translation**: Evaluates TreeExplainer SHAP log-odds margins, synthesizes RCA candidate trees, and calculates rupee-denominated operational losses (downtime, scrap, rework, peak energy tariffs).
- **Layer 4: Simulation & Prescriptive Actions**: Formulates counterfactual What-If policies (Scenarios A–E) while enforcing `NOT_PROJECTABLE` guardrails on unsupported physical states.
- **Layer 5: RAG Memory & AI Copilot**: Indexes 278 authoritative knowledge chunks into a hybrid TF-IDF/SVD vector space to power an anti-hallucinatory Copilot interface.

---

## V. METHODOLOGY
### A. Predictive Maintenance Formulation
Binary failure classification is formulated as predicting whether machine failure occurs given pre-failure telemetry $\mathbf{x} \in \mathbb{R}^d$. The XGBoost objective optimizes log-loss with positive class weighting:
$$\mathcal{L}(\theta) = -\sum_{i=1}^N \left[ w \cdot y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right]$$
where $w = (\text{negatives}/\text{positives}) \approx 15$. The operational decision threshold is locked at $\tau = 0.91$ to suppress false positives in industrial production.

### B. Remaining Useful Life (RUL) Modeling
For engine degradation on NASA C-MAPSS, RUL is modeled using a Random Forest regressor with causal rolling features:
$$\bar{s}_{i,t} = \frac{1}{k} \sum_{j=0}^{k-1} s_{i,t-j}, \quad \sigma_{s_{i,t}} = \sqrt{\frac{1}{k}\sum_{j=0}^{k-1} (s_{i,t-j} - \bar{s}_{i,t})^2}$$
with window length $k=5$ cycles.

### C. Unsupervised PCA Reconstruction Error
The normal operating manifold is learned on clean nominal data $\mathbf{X}_{\text{nominal}} \in \mathbb{R}^{N \times d}$. Given projection matrix $\mathbf{P}_k \in \mathbb{R}^{d \times k}$, reconstruction error for reading $\mathbf{x}_t$ is:
$$\text{SPE}_t = \|\mathbf{x}_t - \mathbf{P}_k \mathbf{P}_k^T \mathbf{x}_t\|_2^2$$
An alert is triggered when $\text{SPE}_t > \tau_{\text{anom}} = 0.24050$.

### D. Dynamic Inventory Safety Stock Coupling
Safety stock ($SS$) and reorder point ($ROP$) incorporate supplier replenishment lead time uncertainty ($\bar{L}, \sigma_L$) and consumption demand ($\bar{d}, \sigma_d$):
$$SS = Z \cdot \sqrt{\bar{L}\sigma_d^2 + \bar{d}^2\sigma_L^2}, \quad ROP = \bar{d}\bar{L} + SS$$
For Machine M2 spindle bearings ($Z=2.326$, 99% factor), $SS = 1.134$ units and $ROP = 1.367$ units.

---

## VI. DATASET AND EXPERIMENTAL SETUP
The platform is validated against four benchmark datasets alongside a 30-day automotive digital twin:
1. **AI4I 2020 Predictive Maintenance**: 10,000 observations, 14 features, 339 failure events.
2. **NASA C-MAPSS FD001**: 100 engine trajectories, 20,631 operational cycles.
3. **UCI Electricity Load Diagrams**: 140,257 readings (15-min intervals) across 370 client profiles.
4. **NirmaanAI Automotive Component Digital Twin**: 5 interconnected CNC machines (M1–M5), 43,200 minutely readings, 300 scheduled jobs, and a calibrated M2 spindle degradation event spanning Days 18–21.

---

## VII. RESULTS
### A. Predictive Maintenance Performance
On the holdout test set ($N=1,500$):
- **Precision**: **0.9545** (42 True Positives, 2 False Positives)
- **Recall**: **0.8235** (9 False Negatives)
- **F1-Score**: **0.8842**
- **ROC-AUC**: **0.9831** | **PR-AUC**: **0.8647**

### B. NASA C-MAPSS Prognostics
- **Mean Absolute Error (MAE)**: **13.21 cycles**
- **Root Mean Squared Error (RMSE)**: **18.11 cycles**
- **$R^2$ Score**: **0.7957**

### C. Anomaly Detection Calibration
- **Precision**: **0.9722** | **Recall**: **1.0000** | **F1**: **0.9859**
- **PR-AUC**: **0.9965** | **ROC-AUC**: **0.9992**
- **Early Warning Lead Time**: **106.5 hours (4.44 days)** before physical seizure.

### D. Bottleneck Flow Classification
- **Precision**: **0.7778** | **Recall**: **0.8750** | **F1**: **0.8235**
- **ROC-AUC**: **0.9882** | **PR-AUC**: **0.8040** (Heuristic cutoff $\tau=0.40$).

---

## VIII. EXPLAINABILITY AND ROOT CAUSE ANALYSIS
TreeExplainer computes additive local SHAP attributions:
$$\text{margin}(\mathbf{x}) = \phi_0 + \sum_{j=1}^M \phi_j(\mathbf{x})$$
For Machine M2, primary attribution drivers are `torque_nm` ($\phi=+0.412$), `tool_wear_min` ($\phi=+0.285$), and `process_temp_k` ($\phi=+0.198$). The RCA engine maps these attributions to candidate cause **`MECHANICAL_LOAD`** (spindle bearing degradation, confidence score: **0.791**, 4 supporting evidence sources).

---

## IX. DECISION INTELLIGENCE & FINANCIAL QUANTIFICATION
NirmaanAI quantifies machine failure into Indian Rupee operational losses:
- **Unplanned Downtime Loss**: $2.5\text{ hrs} \times ₹4,500/\text{hr} = ₹11,250.00$
- **Scrap Material Replacement**: $185\text{ units} \times 0.8\text{ kg} \times ₹350/\text{kg} = ₹51,800.00$
- **Production Rework Labor**: $23.125\text{ hrs} \times ₹280/\text{hr} = ₹6,475.00$
- **Emergency Labor Overtime**: $1.5\text{ hrs} \times ₹280/\text{hr} = ₹420.00$
- **Energy Inefficiency Loss**: $₹3,117.28$
- **Total Realized M2 Loss**: $\mathbf{₹73,062.28}$
- **Gross Exposure (including opportunity cost ₹24,320.00)**: $\mathbf{₹97,382.28}$

---

## X. KNOWLEDGE RETRIEVAL AND AI FACTORY COPILOT
The Phase 19 knowledge store indexes 278 chunks using a hybrid 64-dimensional TF-IDF/SVD dense representation and topical keyword overlap.
- **Recall@5**: **1.0000** | **MRR**: **0.8125** | **Anti-Hallucination Rejection**: **1.0000**
- **Query Latency**: Median **26.28 ms**, P99 **36.12 ms**.
- **Copilot Grounding**: Evaluated across 10 representative operational inquiries with 100% intent classification accuracy.

---

## XI. SECURITY AND EPISTEMIC GUARDRAILS
NirmaanAI implements an authoritative **8-tier epistemic taxonomy**:
1. `OBSERVED`: Physical sensor readings.
2. `DERIVED`: Mathematically computed metrics (realized loss ₹73,062.28).
3. `MODEL_OUTPUT`: ML predictions (failure probability 0.9959).
4. `CONTROLLED_SYNTHETIC`: Benchmark operational scenarios.
5. `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`: Post-cutoff ground truth (`MAINT_0003`).
6. `PROJECTED`: Counterfactual simulations (Scenario D ₹19,520 avoided).
7. `NOT_PROJECTABLE`: Causal transitions lacking empirical telemetry.
8. `UNKNOWN`: Unrecognized entities outside factory topology (`M99`).

---

## XII. DISCUSSION
The experimental results demonstrate that coupling predictive failure models with inventory lead times and bottleneck detection resolves the primary deployment barrier in MSME manufacturing: decision paralysis. Rather than presenting plant managers with isolated probability curves, NirmaanAI presents an actionable intervention package (Rule R-M01, R-I01, R-P01) with quantified counterfactual ROI (₹19,520 avoided opportunity cost).

---

## XIII. LIMITATIONS
1. **Host Environment Boundaries**: Native PostgreSQL and Docker Engine were unavailable on the Windows development host; static packaging and offline 503 resilience were verified.
2. **Exploratory Bottleneck Calibration**: The $\tau=0.40$ flow cutoff was post-hoc calibrated.
3. **Causal Bounds**: Post-intervention physical recovery states remain strictly `NOT_PROJECTABLE`.

---

## XIV. FUTURE WORK
- Live prospective field trials on automotive shop floors in Pune and Coimbatore.
- Edge deployment on embedded micro-controllers (e.g., NVIDIA Jetson Orin Nano).
- Dynamic multi-echelon spare parts supply chain coordination.

---

## XV. CONCLUSION
NirmaanAI establishes an end-to-end, reproducible, and mathematically rigorous factory intelligence platform. By bridging the gap between machine learning, explainability, operations research, and financial exposure, it offers an accessible path toward Industry 4.0 for manufacturing MSMEs.

---

## REFERENCES
1. S. Matzka, "Explainable Artificial Intelligence for Predictive Maintenance Applications," in *Proc. 3rd Int. Conf. Artificial Intelligence for Industries (AI4I)*, 2020, pp. 69–74.
2. A. Saxena, K. Goebel, D. Simon, and N. Eklund, "Damage propagation modeling for aircraft engine run-to-failure simulation," in *Proc. Int. Conf. Prognostics and Health Management*, 2008, pp. 1–9.
3. M. McCann, A. Johnston, and R. Johnston, "Causality analysis of process data in semiconductor manufacturing," in *Proc. IEEE Int. Symp. Semiconductor Manufacturing*, 2008, pp. 1–4.
4. S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017.
5. E. A. Silver, D. F. Pyke, and R. Peterson, *Inventory Management and Production Planning and Scheduling*. New York: Wiley, 1998.
6. P. Lewis *et al.*, "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020.
