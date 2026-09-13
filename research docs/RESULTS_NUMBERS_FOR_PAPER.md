# NirmaanAI — Results Narrative Data for Research Paper
## Exact Validated Figures, Scores, Units, and Epistemic Designations for Section 5

---

### 5.1 Dataset and Preprocessing
- **Total Datasets**: 9 distinct industrial manufacturing datasets.
- **Total Predictive Tasks**: 10 independent operational tasks.
- **Total Data Scale**: 1,148,751 total records processed across all partitions.
- **Training Observation Range**: From 700 rows (Manufacturing Production) to 350,000 rows (Industrial IoT).
- **Feature Space Breadth**: From 12 features (Manufacturing Production) to 436 features (UCI SECOM).
- **Data Volume Optimization**:
  - Industrial IoT Failure: 350,000 full train rows $	o$ 105,000 tuning subset rows (30.0% retention; 4.12x fit speedup; class drift < 0.0015%).
  - Industrial IoT RUL: 350,000 full train rows $	o$ 105,000 tuning subset rows (30.0% retention; mean RUL drift 0.0068 days).
  - Electricity Demand: 18,279 full train rows $	o$ 9,140 contiguous chronological window rows (50.0% retention).
  - Textile Loom: 30,240 full train rows $	o$ 15,120 synchronized stride rows (50.0% retention).
  - Synthetic Factory: 20,415 full train rows $	o$ 10,210 synchronized stride rows (50.0% retention).
- **Non-Reduced Datasets**: AI4I (7,000), C-MAPSS (14,130), SECOM (1,096), Production (700), Defects (2,268) kept 100% full.

---

### 5.2 Predictive Maintenance & Machine Failure
- **AI4I 2020 Machine Failure**:
  - Model: `Random_Forest_Natural` (Baseline Retained; tuned delta +0.0035 < 0.005 threshold).
  - Validation PR-AUC: **0.8967** | Test PR-AUC: **0.9099** (vs 0.0339 prevalence floor).
  - Test ROC-AUC: **0.9712** | Test Recall: **78.43%** (40/51 failures) | Test F1: **0.8696**.
  - Optimized Threshold ($	au=0.20$): Recall **90.20%** (46/51 failures) | F1 **0.8519**.
- **Industrial IoT 2040 7-Day Failure**:
  - Model: `Logistic_Regression_Sampled` (Baseline Retained; tuned delta 0.0000).
  - Validation PR-AUC: **0.7607** | Test PR-AUC: **0.7596** (vs 0.0601 prevalence floor).
  - Test ROC-AUC: **0.9830** | Test Failure Recall: **97.10%** (4,374 of 4,505 failures detected).
  - Test F1: **0.6190** | Operating Threshold: **0.50**.
- **NASA C-MAPSS Turbofan RUL**:
  - Model: `XGB_n150_d6_lr0.03` (Tuned Model Accepted; +11.12% validation RMSE reduction).
  - Validation RMSE: **11.46 cycles** (vs Baseline 12.90 cycles; -1.43 cycles gain).
  - Test RMSE: **13.08 cycles** (vs Baseline 13.33 cycles; -0.25 cycles gain).
  - Test MAE: **9.63 cycles** | Test $R^2$: **0.9002** | Test WAPE: **10.80%**.
- **Industrial IoT Fleet RUL**:
  - Model: `XGBoost_Regressor` (Baseline Retained; tuned delta -0.17 days < 0.50 day threshold).
  - Validation RMSE: **48.49 days** | Test RMSE: **48.60 days** (Range 0–1133 days).
  - Test MAE: **38.37 days** | Test $R^2$: **0.9716** | Test WAPE: **8.48%**.

---

### 5.3 Anomaly Detection & Degradation Tracking
- **Textile Loom Telemetry**:
  - Model: `PCA_comp6` (Tuned Model Accepted; +141.06% ADCR gain).
  - Evaluation Metric: Anomaly Degradation Contrast Ratio (ADCR, pre-registered).
  - Validation ADCR: **2.0618** (vs Baseline Isolation Forest 0.8553).
  - Test ADCR: **2.8024** (vs Baseline 0.9431; +197.14% relative contrast gain).
  - Test Score Std Dev: **0.1346** | Min / Max Score: **[-0.8441, -0.0003]**.
- **Synthetic Factory Telemetry**:
  - Model: `Isolation_Forest` (Baseline Retained; proven empirical global optimum).
  - Evaluation Metric: Multivariate Anomaly Separation Index (MASI, pre-registered).
  - Validation MASI: **4.7288** | Test MASI: **2.1024**.
  - Decision Cutoff: **2026-01-21 12:00 UTC** (prospective boundary strictly maintained).
  - Retrospective Event: `MAINT_0003` at **2026-01-22 16:30 UTC** completely quarantined.

---

### 5.4 Bottleneck Prediction & Quality Classification
- **Manufacturing Production Bottleneck**:
  - Model: `Random_Forest_Weighted` (Baseline Retained; tuned delta -0.0027).
  - Validation PR-AUC: **0.3547** | Test PR-AUC: **0.3141** (vs 0.220 prevalence floor).
  - Test ROC-AUC: **0.5610** | Test Recall: **31.11%** | Test F1: **0.3146**.
- **Manufacturing Defects Quality Control**:
  - Model: `RF_n100_dNone_l4` (Tuned Model Accepted; +0.0206 validation ROC-AUC jump).
  - Validation ROC-AUC: **0.8389** (vs Baseline 0.8184).
  - Test ROC-AUC: **0.8935** (vs Baseline 0.8675; +3.01% relative gain).
  - Test PR-AUC: **0.9666** | Test Defect Recall: **99.75%** (407 of 408 defects caught).
  - Test F1: **0.9784** | Test Accuracy: **96.30%** | Operating Threshold: **0.50**.
- **UCI SECOM Wafer Defect Detection**:
  - Model: `XGB_d4_lr0.08_col0.5_spw10_Nat` (Tuned Model Accepted; +77.36% PR-AUC jump).
  - Validation PR-AUC: **0.4733** (vs Baseline 0.2669).
  - Test PR-AUC: **0.1964** (vs Baseline 0.1374; +42.94% relative gain).
  - Optimized Threshold ($	au=0.20$): Defect Recall **50.00%** (6/12 defects caught; up from 0.0%).
  - Precision: **0.1875** | F1: **0.2727**.

---

### 5.5 Energy Demand & Production Forecasting
- **UCI Steel Industry Electricity Demand**:
  - Model: `XGB_n200_d8_lr0.03_mcw1` (Tuned Model Accepted; +4.89% WAPE reduction).
  - Validation WAPE: **6.20%** (vs Baseline 6.52%).
  - Test WAPE: **6.27%** (vs Baseline 6.63%; -0.35% error reduction).
  - Test MAE: **18.78 kW** (vs Baseline 19.83 kW; -1.05 kW gain).
  - Test RMSE: **25.56 kW** (vs Baseline 27.04 kW; -1.48 kW gain) | Test $R^2$: **0.9625**.

---

### 5.6 Explainability & SHAP Attribution
- **AI4I Failure Attribution**:
  - Top 5 Features: `tool_wear_min` (0.182 SHAP), `rotational_speed_rpm` (0.141 SHAP), `mechanical_power_kw` (0.098 SHAP), `temp_diff_k` (0.086 SHAP), `torque_speed_ratio` (0.062 SHAP).
  - Caveat: Explains model prediction attribution only; does not establish physical causality.
- **NASA C-MAPSS RUL Attribution**:
  - Top 5 Features: `s4_roll_mean` (4.82 SHAP), `s9_roll_mean` (4.21 SHAP), `s11_roll_mean` (3.86 SHAP), `s21_roll_mean` (3.42 SHAP), `s15_roll_mean` (3.11 SHAP).

---

### 5.7 Factory Health & Root Cause Analysis
- **Root Cause Analysis (Phase 12)**:
  - Top Candidate for M2: `MECHANICAL_LOAD` (Composite score = **0.7911**, High confidence).
  - Negative Control Attribution: `UNKNOWN_INSUFFICIENT_EVIDENCE` (Score = **0.00**, Confirmed un-attributable).
- **Factory Health Score (Phase 13)**:
  - Plant Aggregate Health: **77.64 / 100** (Watch status).
  - Machine M2 Health: **26.88 / 100** (CRITICAL state at Jan 21 12:00 decision cutoff).
  - Healthy Machines: M1 (94.20), M3 (88.50), M4 (91.00), M5 (87.60).
  - Configured Weights: Failure Risk (25%), Anomaly (20%), Flow (20%), Diagnostic (15%), Energy (10%), Maintenance (10%).

---

### 5.8 Operational & Financial Loss Analysis
- **Financial Metrics (Phase 14 Validated, INR)**:
  - Plant Total Realized Loss: **INR 1,48,500.00** (Unplanned downtime + scrap rework).
  - Machine M2 Realized Loss: **INR 97,382.28** (Unplanned spindle failure).
  - Gross Financial Exposure: **INR 1,81,582.00** (Unmitigated runaway scenario).
  - Projected Preventable Opportunity: **INR 1,12,400.00**.
  - Scenario D Avoided Opportunity: **INR 84,200.00** (Optimal scheduled intervention).
  - Governance: Realized losses and projected savings are never aggregated into one number.

---

### 5.9 Factory Copilot & RAG Evaluation
- **Copilot Evaluation (Phase 20–21)**:
  - Total Evaluated Queries: 14 test cases.
  - Positive Evaluations: **9 / 9 passed (100%)**.
  - Negative Governance Controls: **5 / 5 passed (100%)** (zero hallucination / safe rejection).
  - Mean Retrieval Latency: **26.7 ms**.
