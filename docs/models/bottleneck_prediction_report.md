# NirmaanAI — Bottleneck Prediction & Production Flow Intelligence Report

**Document Version**: 2.0.0 (Methodological Audit & Research-Integrity Corrected)  
**Phase**: Phase 8 — Bottleneck Prediction & Flow Intelligence  
**Subsystem**: Multi-Stage Production Line Flow Congestion & Bottleneck Forecasting  
**Target MSME Verticals**: Precision Auto-Components & Textile Weaving/Spinning  
**Academic Alignment**: Institute of Engineering & Management (IEM), Kolkata | Department of CSE (AI) | Group 59 | Guide: Prof. Kuntal Mondal  

---

## 1. Problem Definition
In manufacturing job shops and discrete production lines, individual machines are sequentially coupled through Work-In-Progress (WIP) buffer stages. A machine slowing down due to mechanical fatigue or improper tooling directly restricts line-level throughput:
- **Local Degradation vs. Flow Bottleneck**: A minor speed drop on an over-capacity non-critical station can be absorbed by buffer stocks. However, when a primary bottleneck machine (such as Machine `M2`, a 22 kW Vertical Machining Center) degrades, unit cycle times balloon by $+29\%\text{ to }+44\%$, causing upstream WIP queues to back up and starving downstream operations (`M3` Surface Grinding, `M4` Inspection).
- **The Phase 8 Objective**: Predict upcoming job delays and line bottlenecks at dispatch time ($t \le t_{\text{scheduled\_start}}$) before delays cascade into severe financial and scheduling losses.

---

## 2. Research Distinction: Equipment Failure vs. Sensor Anomaly vs. Flow Bottleneck

> [!IMPORTANT]
> **Clear Conceptual Separation**:
> - **Phase 6 (Predictive Maintenance)**: Predicts catastrophic machine component failure ($y \in \{0, 1\}$) or Remaining Useful Life ($RUL$).
> - **Phase 7 (Anomaly Detection)**: Identifies microscopic statistical and multivariate telemetry drift (vibration chatter, thermal resistance) without requiring supervised failure labels.
> - **Phase 8 (Bottleneck Prediction)**: Forecasts macroscopic production flow constraints where an operation's throughput falls below line demand, causing dispatch delays and WIP congestion.

---

## 3. Dataset Characteristics & Exact Count Verification
All data was verified directly from local repository files prior to model design:

### Primary Dataset: Synthetic Factory Digital Twin (`DATASET/10_SYNTHETIC_FACTORY/synthetic/`)
- **Total Production Jobs**: Exactly **300 jobs** across 30 days and 2 daily shifts.
- **Timestamp Coverage**: `2026-01-01 06:15:00 UTC` to `2026-01-30 14:15:00 UTC`.
- **Jobs Per Machine**: Exactly 60 jobs each for `M1`, `M2`, `M3`, `M4`, and `M5`.
- **Status Distribution**:
  - `COMPLETED`: 292 jobs (97.33%)
  - `DELAYED`: 8 jobs (2.67%)
- **Distribution by Machine**:
  - `M1`: 60 Completed, 0 Delayed
  - `M2`: 52 Completed, **8 Delayed** (100% of delayed jobs occurred on `M2`)
  - `M3`: 60 Completed, 0 Delayed
  - `M4`: 60 Completed, 0 Delayed
  - `M5`: 60 Completed, 0 Delayed

### Secondary Dataset: Hybrid Manufacturing Categorical (`DATASET/06_MANUFACTURING_PRODUCTION/raw/hybrid_manufacturing_categorical.csv`)
- **Total Jobs**: Exactly 1,000 records across 5 machines (`M01` to `M05`).
- **Status Distribution**: `Completed`: 673 (67.3%), `Delayed`: 198 (19.8%), `Failed`: 129 (12.9%).
- **EDA Cross-Reference**: Jobs with dispatch start delay $\ge 10\text{ min}$ resulted in `Delayed` status.

---

## 4. Bottleneck Target Definition & Anti-Leakage Guardrail
To prevent circular reasoning and label leakage:
- **Target Formulation**:
  $$\text{bottleneck\_event} = 1 \iff \left( \frac{\text{actual\_cycle\_time\_sec}}{\text{design\_cycle\_time\_sec}} \ge 1.20 \right) \lor (\text{start\_delay\_min} \ge 10.0) \lor (\text{status} == \text{'DELAYED'})$$
- **Prediction Point**: Features are evaluated **strictly at scheduled dispatch time** ($t \le t_{\text{scheduled\_start}}$).
- **Prohibited Lookahead Features**: `Actual_End`, total observed duration, future scrap count, and post-completion loss metrics were strictly excluded from feature extraction. The model does not predict whether a job was already delayed; it predicts upcoming bottleneck risk based on pre-job state.

---

## 5. Temporal Splitting Strategy & Zero-Positive Training Constraint
Chronological splitting was enforced across the 30-day timeline to preserve historical causality:

| Split Window | Calendar Period (UTC) | Job IDs | Total Jobs ($N$) | Bottleneck Positives |
| :--- | :--- | :---: | :---: | :---: |
| **Train (Reference Normal)** | 2026-01-01 06:15 to 2026-01-15 14:15 (Days 1–15) | `JOB_0001` – `JOB_0150` | 150 | **0 (0.0%)** |
| **Validation (Tuning)** | 2026-01-16 06:15 to 2026-01-17 14:15 (Days 16–17) | `JOB_0151` – `JOB_0170` | 20 | **0 (0.0%)** |
| **Test (Evaluation)** | 2026-01-18 06:15 to 2026-01-30 14:15 (Days 18–30) | `JOB_0171` – `JOB_0300` | 130 | **8 (6.15%)** |

> [!WARNING]
> **Critical Statistical & Cold-Start Constraint**:
> In strict chronological splitting, the training window (Days 1–15, $N = 150$) and validation window (Days 16–17, $N = 20$) represent nominal operations with exactly **0 positive bottleneck cases** ($y_{\text{train}} = 0$). Under this strict constraint, conventional supervised threshold optimization is impossible. No positive labels were artificially injected, no data was leaked across time, and test data was strictly quarantined from threshold tuning.

---

## 6. Zero-Lookahead Feature Engineering
A set of 15 causal predictors was extracted in [bottleneck_features.py](file:///c:/NIRMAAN%20AI/src/features/bottleneck_features.py):
1. **Capacity & Workload Features**: `batch_quantity`, `planned_duration_min`, `batch_load_ratio`, `hour_of_day`, `is_afternoon_shift`.
2. **Machine Historical Flow Dynamics**:
   - `prior_cycle_ratio_mean`: Causal moving average of cycle ratios for the last 3 completed jobs on that machine.
   - `prior_start_delay_mean`: Causal moving average of start dispatch delays for prior completed jobs.
3. **Telemetry-Flow Physical Coupling (1-Hour Pre-Dispatch Window)**:
   - `pre_job_vibration_1h`: Mean RMS vibration in the $(t_{\text{sch}} - 1\text{h}, t_{\text{sch}}]$ window.
   - `pre_job_temperature_1h`: Mean casing temperature in the pre-job window.
   - `pre_job_vibration_dev_1h`: Elevation relative to machine baseline ($\text{vib} - 1.4\text{ mm/s}$).
4. **Machine Identifiers**: One-hot indicators `is_machine_M1` through `is_machine_M5`.

---

## 7. Model Benchmarking & Performance Comparison
Four model families were evaluated on the independent chronological test split ($N = 130$ jobs, Positives = 8):

| Model | Model Nature | Decision Threshold | Test Precision | Test Recall | Test F1 | Test ROC-AUC | Test PR-AUC | Test FPR |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Heuristic Baseline** | **Domain/Physics Prior** | **0.40 (Configured)** | **0.7778** | **0.8750** | **0.8235** | **0.9882** | **0.8040** | **0.0164** |
| **Logistic Regression** | Supervised Discriminative | 0.50 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0615 | 0.0000 |
| **Random Forest** | Supervised Discriminative | 0.50 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0615 | 0.0000 |
| **XGBoost Classifier** | Supervised Discriminative | 0.50 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0615 | 0.0000 |

### Domain-Informed Heuristic Baseline Confusion Matrix ($N = 130$):
- **True Negatives ($TN$)**: 120
- **False Positives ($FP$)**: 2 (Jobs `JOB_0212` and `JOB_0217` on Day 22 immediately following maintenance while historical moving average was normalizing)
- **False Negatives ($FN$)**: 1 (`JOB_0172`, the very first job on Day 18 where bearing degradation had just initiated)
- **True Positives ($TP$)**: 7

### Scientific Interpretation of Supervised Classifiers:
Supervised discriminative classifiers (Logistic Regression, Random Forest, XGBoost) could not learn a positive bottleneck class under the strictly chronological training regime because the available training period contained no positive bottleneck events. This is not simply poor algorithmic performance; rather, it demonstrates that **the available historical window contains insufficient positive bottleneck examples for conventional supervised classification**. This finding provides strong academic motivation for domain-informed priors during cold-start operations and future supervised learning after sufficient labeled bottleneck history accumulates.

### Threshold Methodology Guardrail:
The heuristic baseline evaluates pre-job physical deviation and lagged cycle drag using **configured domain/scenario thresholds**:
- Pre-job vibration deviation threshold: $0.30\text{ mm/s}$
- Lagged cycle ratio threshold: $1.10$ ($+10\%$ cycle slowdown)
- Continuous risk cutoff: $0.40$

These thresholds are configured domain priors established independently of the test labels. Threshold calibration could not be statistically learned because validation contained zero positive events; test evaluation was reserved strictly for final reporting.

---

## 8. Secondary Benchmark Findings: Hybrid Manufacturing Categorical
- On `06_MANUFACTURING_PRODUCTION` ($N = 1,000$), Random Forest evaluated on tabular manufacturing features (`Processing_Time`, `Material_Used`, `Energy_Consumption`, `Machine_Availability`) yielded:
  - **ROC-AUC**: **0.4903**
  - **PR-AUC**: **0.3531** (Baseline = 0.3270)
- **Scientific Finding**: The available analysis indicates that dispatch delay is a stronger observable signal of delay status in this dataset than the examined electrical and material variables.

---

## 9. M2 Controlled Scenario Flow Analysis
Within the controlled synthetic scenario, the propagation of physical wear into flow bottleneck was evaluated:
1. **Day 18 06:00 (Onset of Bearing Wear)**: Pre-job vibration increased to $1.47\text{ mm/s}$ ($\Delta = +0.07$). Job `JOB_0172` experienced cycle slowdown ($45\text{s} \to 58.6\text{s}$).
2. **Days 18–21 (Sustained Bottleneck)**: Pre-job vibration rose to $3.16\text{ mm/s}$ and temperature to $50.7\text{ °C}$. All 7 subsequent M2 jobs experienced severe cycle expansion ($58\text{--}65\text{s}$), queue accumulation, and dispatch delays of $12\text{--}28\text{ minutes}$.
3. **Day 22 16:30 (Emergency Stop & Spindle Replacement)**: After maintenance, nominal cycle times recovered to $44.8\text{s}$, clearing the downstream bottleneck.
- *Notice*: This sequence represents **controlled synthetic scenario validation** within the configured simulation environment and does NOT establish real-world causality.

---

## 10. Flow Intelligence Service Implementation
The real-time service [bottleneck_service.py](file:///c:/NIRMAAN%20AI/src/services/bottleneck_service.py) exposes:
- **Flow States**:
  - `NOMINAL_FLOW`: All machines operating within 10% of design cycle time.
  - `MODERATE_CONGESTION`: Buffer queue lag or cycle expansion between $+10\%$ and $+20\%$.
  - `CRITICAL_BOTTLENECK`: Severe pre-dispatch telemetry elevation and cycle expansion $>+20\%$, triggering active downstream constraint warnings.
- **Sequential Coupling**: Flags downstream starvation on `M3` (Grinding) when `M2` enters critical bottleneck.

---

## 11. Test Suite Verification
- **Bottleneck Tests**:
  ```
  tests/test_bottleneck_prediction.py::test_dataset_exact_counts PASSED    [ 14%]
  tests/test_bottleneck_prediction.py::test_zero_lookahead_feature_causality PASSED [ 28%]
  tests/test_bottleneck_prediction.py::test_temporal_split_isolation PASSED [ 42%]
  tests/test_bottleneck_prediction.py::test_heuristic_bottleneck_classifier_fit_predict PASSED [ 57%]
  tests/test_bottleneck_prediction.py::test_bottleneck_service_inference PASSED [ 71%]
  tests/test_bottleneck_prediction.py::test_heuristic_thresholds_configured_independent_of_test_data PASSED [ 85%]
  tests/test_bottleneck_prediction.py::test_zero_positive_training_constraint PASSED [100%]
  7 passed in 3.86s
  ```
- **Full Project Suite**: **61 passed tests**, 1 warning in 10.66s.

---

## 12. Artifacts Created
- `src/features/bottleneck_features.py`: Feature engineering and chronological splitting.
- `src/models/bottleneck_predictor.py`: Domain-informed heuristic baseline and discriminative bottleneck classifiers.
- `src/models/train_bottleneck.py`: Training, benchmarking, and metadata logging pipeline.
- `src/services/bottleneck_service.py`: Real-time flow assessment and active constraint identification engine.
- `models/bottleneck_prediction/bottleneck_predictor.joblib`: Serialized deployed baseline model.
- `models/bottleneck_prediction/metadata.json`: Complete benchmark metrics, split metadata, and zero-positive training explanations.
- `tests/test_bottleneck_prediction.py`: Comprehensive test suite.
- `docs/models/bottleneck_prediction_report.md`: Full scientific documentation.

---

## 13. Limitations & Research Safeguards
1. **Chronological Cold-Start Limitation**: Because the training baseline represents strictly nominal operations, supervised discriminative classifiers require historical bottleneck variety to train effective boundaries.
2. **Sequential Line Routing**: WIP queue propagation assumes linear sequential routing (`M1` to `M5`). Non-linear split/merge topologies will require graph network flow modeling.
3. **Controlled Synthetic Environment**: Primary results reflect the generative simulation equations and do NOT constitute physical empirical validation, do NOT prove real-world factory performance, and do NOT establish real-world causality.
