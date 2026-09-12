# NirmaanAI — Phase 12: Root Cause Analysis (RCA) Report

## 1. Executive Summary & Objective
Phase 12 implements an evidence-based Root Cause Analysis (RCA) framework for NirmaanAI.
The primary objective of the RCA layer is to systematically transform model predictions, local SHAP feature attributions, multi-sensor anomaly scores, and operational flow metrics into ranked, interpretable operational candidate causes.

```
Model Prediction ($P$)
        ↓
Model Attribution (SHAP) + Anomaly Detection (PCA/Z-score) + Operational Metrics (Cycle/Flow/Spares)
        ↓
Machine-Specific Baseline Normalization & Temporal Precedence ($t_0 \to t_1 \to t_2 \to t_3$)
        ↓
Evidence Fusion & Contradictory Penalty Subtraction
        ↓
Root-Cause Candidate Ranking & Confidence Classification (HIGH / MEDIUM / LOW / INSUFFICIENT_EVIDENCE)
        ↓
Evidence-Backed Human-Readable RCA Explanation with Strict Scientific Disclaimers
```

---

## 2. Fundamental Distinctions: Prediction vs. SHAP vs. Anomaly vs. RCA

To prevent conceptual conflation and misleading industrial claims, the NirmaanAI architecture maintains strict mathematical boundaries between its analytical layers:

| Layer | Question Answered | Underlying Methodology | Causality Status |
| :--- | :--- | :--- | :--- |
| **Prediction (Phase 6)** | *"What is the probability of an equipment failure within the prediction horizon?"* | Supervised Classification (XGBoost) evaluated against approved threshold $\tau = 0.91$. | **Statistical Correlation**: Quantifies failure risk conditioned on feature values. |
| **Model Attribution / SHAP (Phase 11)** | *"Which features contributed to the model's prediction, and by how much?"* | Cooperative Game Theory (Shapley values / TreeExplainer in additive log-odds margin space). | **Model-Internal Attribution**: Explains the model's internal score function, NOT physical causality. |
| **Anomaly Detection (Phase 7)** | *"Does current multi-sensor telemetry deviate from the expected operating regime?"* | Unsupervised Reconstruction (PCA / baseline Mahalanobis distance) against threshold $\tau = 0.2405$. | **Statistical Novelty**: Flags unusual multi-sensor covariance. $\text{Anomaly} \neq \text{Failure}$. |
| **Root Cause Analysis (Phase 12)** | *"What operational factors are most strongly associated with the observed event based on all available evidence?"* | Deterministic Multi-Source Evidence Fusion, Machine Baseline Normalization, and Temporal Precedence ($t_0 \dots t_3$). | **Operational Consistency**: Identifies corroborating physical factors. Does **NOT** constitute causal proof without interventional data. |

> [!IMPORTANT]
> **Strict Scientific Principle**:
> A high SHAP attribution value alone is **insufficient** to declare a physical root cause. A machine can exhibit high tool wear feature attribution in a model query, but if physical vibration, spindle temperature, cycle times, and anomaly scores remain nominal, no physical failure mechanism is active.

---

## 3. Controlled Cause Taxonomy (13 Categories)

To prevent hallucinated, ungrounded, or arbitrary root causes, candidate causes are strictly restricted to 13 domain-grounded categories backed by available sensors, logs, and engineering features:

1. **`THERMAL_STRESS`**: Elevated process/spindle temperature, thermal gradient expansion (`temp_diff_c`, `temperature_c`).
2. **`MECHANICAL_LOAD`**: High spindle torque, mechanical power surge (`power_mw`, `torque_nm`), overstrain ratio.
3. **`TOOL_WEAR`**: Accumulated cutting time exceeding threshold (`tool_wear_min`).
4. **`SPEED_DEVIATION`**: Spindle rotational velocity excursions outside nominal machining envelope (`rotational_speed_rpm`).
5. **`VIBRATION_DEVIATION`**: Spindle/axis mechanical vibration exceeding machine baseline limits (`vibration_mms`, `sound_db`).
6. **`PROCESS_INSTABILITY`**: Multi-sensor covariance disturbance, high anomaly score with fluctuating readings.
7. **`CYCLE_TIME_DEGRADATION`**: Substantial unit cycle time expansion beyond machine design specification (`cycle_time_sec`, `cycle_ratio`).
8. **`FLOW_CONGESTION`**: Line flow starvation, downstream queue accumulation, job start delay.
9. **`ENERGY_DEVIATION`**: Electrical power draw or load significantly divergent from baseline or forecasted regime (`power_consumption_kw`).
10. **`MATERIAL_OR_SPARE_CONSTRAINT`**: Critical replacement spare stockout, zero days of supply, or extended replenishment lead time.
11. **`MAINTENANCE_STATE`**: Overdue routine maintenance, post-maintenance run-in, or severe degradation history.
12. **`SENSOR_OR_DATA_QUALITY_ANOMALY`**: Telemetry dropout, frozen sensor signal, or unphysical spike lacking cross-sensor corroboration.
13. **`UNKNOWN_INSUFFICIENT_EVIDENCE`**: Default fallback when evidence is below significance threshold ($< 0.15$) or contradictory signals dominate.

---

## 4. Evidence Fusion & Mathematical Formulation

### A. Machine-Specific Baseline Normalization
Industrial machines operate under distinct physical envelopes (as established in Phase 7). Direct cross-machine comparisons distort physical signals. Telemetry is normalized relative to each machine $m$'s baseline parameters:
$$\Delta_{\text{telem}}(x, m) = \text{clamp}\left(\frac{x - \mu_m}{\theta_{\text{crit}, m} - \mu_m}, 0.0, 1.0\right)$$
where $\mu_m$ is the machine-specific nominal baseline and $\theta_{\text{crit}, m}$ is the critical shutdown threshold.

| Machine | Baseline Vibration ($\mu_m$) | Alert Threshold ($\theta_{\text{alert}, m}$) | Critical Threshold ($\theta_{\text{crit}, m}$) | Baseline Power ($\text{kW}$) | Design Cycle ($\text{s}$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M1** (Turning Center) | $1.20\text{ mm/s}$ | $3.80\text{ mm/s}$ | $5.50\text{ mm/s}$ | $18.0$ | $30.0$ |
| **M2** (VMC Milling) | $1.40\text{ mm/s}$ | $3.80\text{ mm/s}$ | $5.50\text{ mm/s}$ | $22.0$ | $45.0$ |
| **M3** (Surface Grinder) | $1.10\text{ mm/s}$ | $3.50\text{ mm/s}$ | $5.00\text{ mm/s}$ | $15.0$ | $60.0$ |
| **M4** (Inspection Optical) | $0.80\text{ mm/s}$ | $3.00\text{ mm/s}$ | $4.50\text{ mm/s}$ | $8.0$ | $15.0$ |
| **M5** (Ultrasonic Cleaner) | $1.00\text{ mm/s}$ | $3.20\text{ mm/s}$ | $4.80\text{ mm/s}$ | $12.0$ | $25.0$ |

### B. Signal Evidence Components
For candidate cause $c \in \text{Taxonomy}$:
1. **$S_{\text{SHAP}}(c) \in [0, 1]$**: Normalized model attribution for associated features from Phase 11 TreeExplainer in margin space ($\text{clamp}(\bar{\phi}_c / 3.0, 0, 1)$).
2. **$S_{\text{anomaly}}(c) \in [0, 1]$**: Normalized anomaly contribution from Phase 7 ($\text{clamp}(\text{score} / 2\tau_{\text{anom}}, 0, 1)$).
3. **$S_{\text{telemetry}}(c) \in [0, 1]$**: Normalized deviation from machine-specific baseline.
4. **$S_{\text{operational}}(c) \in [0, 1]$**: Cycle time expansion ratio ($>1.10$) or bottleneck flow congestion index.
5. **$P_{\text{contradiction}}(c) \in [0, 1]$**: Penalty applied when critical corroborating physical signals are nominal (penalty weight $w_{\text{pen}} = 0.35$).
6. **$T_{\text{precedence}}(c) \in [0, 1]$**: Temporal multiplier confirming signal onset preceded the consequence ($t_0 \le t_1 \le t_2 \le t_3$).

### C. Composite Analytical Score Formulation
$$\text{Score}(c) = \text{clamp}\left( T_{\text{precedence}} \cdot \left[ w_{\text{SHAP}} S_{\text{SHAP}} + w_{\text{anom}} S_{\text{anomaly}} + w_{\text{telem}} S_{\text{telemetry}} + w_{\text{ops}} S_{\text{operational}} \right] - w_{\text{pen}} P_{\text{contradiction}}(c), 0.0, 1.0 \right)$$
- **Configured Analytical Weights**:
  - $w_{\text{SHAP}} = 0.25$
  - $w_{\text{anom}} = 0.25$
  - $w_{\text{telem}} = 0.30$
  - $w_{\text{ops}} = 0.20$
  - $w_{\text{pen}} = 0.35$
- **Mathematical Bound**: Every score is strictly bounded in $[0.0, 1.0]$.
- **Labeling Rule**: Documented strictly as a **CONFIGURED ANALYTICAL SCORE**, never a "probability of causation".

---

## 5. Temporal Precedence & Leakage Prevention

Temporal ordering is essential to prevent confusing operational consequences with root causes:
- **$t_0$ (Precursor)**: Earliest significant telemetry excursion (e.g. vibration elevation $> 1.3 \times \mu_m$).
- **$t_1$ (Escalation)**: Degradation escalation (e.g. thermal buildup $\ge 45^\circ\text{C}$ or vibration exceeding alert threshold $3.8\text{ mm/s}$).
- **$t_2$ (Operational Consequence)**: Operational degradation (cycle time expansion $> 1.15 \times \text{nominal}$ or queue growth).
- **$t_3$ (Event Point)**: Failure prediction threshold breach ($P \ge 0.91$) or emergency shutdown.

> [!NOTE]
> **Strict Causal Filtering**:
> Any telemetry observation with timestamp $t > t_{\text{event}}$ is strictly filtered out prior to RCA processing, preventing lookahead leakage.

---

## 6. Confidence Classification Framework

Evidence confidence is classified categorically, reflecting empirical cross-signal agreement rather than physical probabilities:

| Category | Criteria | Operational Meaning |
| :--- | :--- | :--- |
| **`HIGH`** | $\text{Score} \ge 0.60$, $\ge 2$ independent sources agree, verified temporal precedence ($t_0 \le t_1 \le t_2 \le t_3$), $0$ contradictions. | Multiple independent physical telemetry and model attributions corroborate candidate cause. |
| **`MEDIUM`** | $\text{Score} \ge 0.35$, at least 1 corroborating physical signal, no dominant contradiction. | Evidence supports candidate, but temporal progression or secondary signals are incomplete. |
| **`LOW`** | $\text{Score} \ge 0.15$, or isolated signal without multi-sensor corroboration, or contradiction present. | Isolated model attribution or uncorroborated sensor drift. Insufficient to declare physical cause. |
| **`INSUFFICIENT_EVIDENCE`** | $\text{Score} < 0.15$ across all candidates, or contradictory signals completely neutralize hypothesis. | Signals are within normal noise envelope or inconclusive. Defaults to `UNKNOWN_INSUFFICIENT_EVIDENCE`. |

---

## 7. Controlled Demonstration: Machine 2 Synthetic Degradation

The Machine 2 degradation episode (Days 18–21) is executed using actual synthetic factory records:
- **Label**: `[CONTROLLED SYNTHETIC SCENARIO]`
- **Chronological Reconstruction**:
  - $t_0$ (2026-01-18 11:40 UTC): Initial vibration deviation detected ($1.99\text{ mm/s}$ vs baseline $1.40\text{ mm/s}$).
  - $t_1$ (2026-01-18 12:00 UTC): Physical degradation escalation (process temp rises to $50.3^\circ\text{C}$, anomaly score reaches $0.120$).
  - $t_2$ (2026-01-20 02:40 UTC): Operational consequence observed (unit cycle time expands to $55.0\text{s}$ vs nominal $45.0\text{s}$, ratio $1.22$).
  - $t_3$ (2026-01-21 10:30 UTC): Vibration reaches critical $5.60\text{ mm/s}$ ($\ge 5.50\text{ mm/s}$), failure predicted ($P = 0.965 \ge 0.910$), emergency shutdown triggered.
- **RCA Findings**:
  - Primary Candidate: **`MECHANICAL_LOAD`** (Mechanical Overload / Torque Surge)
  - Analytical Score: **$0.791$**
  - Confidence: **`HIGH`** (4 independent corroborating sources: SHAP attribution, machine telemetry, Phase 7 anomaly score, Phase 8 cycle degradation).
  - Secondary Candidates: `VIBRATION_DEVIATION` ($0.550$), `THERMAL_STRESS` ($0.344$), `PROCESS_INSTABILITY` ($0.250$).
  - Interpretation: *"The available synthetic evidence is temporally and operationally consistent with the configured M2 degradation scenario."*

---

## 8. False Cause & Negative Control Evaluation

To prove that SHAP model attribution alone does NOT constitute root cause analysis, a controlled negative test was executed:
- **Scenario**: AI4I query with high tool wear attribution (SHAP $+3.80$ in margin space), triggering model prediction alert ($P = 0.925 \ge 0.910$).
- **Telemetry Reality**: Machine 2 operating at nominal baseline (vibration $1.35\text{ mm/s}$, process temp $34.0^\circ\text{C}$, cycle time $44.8\text{s}$, anomaly score $0.082 < 0.2405$, tool wear $15.0\text{ min}$).
- **RCA Evaluation**:
  - Contradiction Engine detects that tool wear is minimal ($15.0\text{ min}$ vs limit $200\text{ min}$) and vibration is normal.
  - Contradiction penalty ($w_{\text{pen}} = 0.35$) applied.
  - Composite score collapses to $< 0.15$.
  - Result: Classified as **`INSUFFICIENT_EVIDENCE`** / `UNKNOWN_INSUFFICIENT_EVIDENCE` (Confidence: `INSUFFICIENT_EVIDENCE`).
- **Conclusion**: Confirms that SHAP attribution without physical telemetry cross-corroboration is safely rejected.

---

## 9. Verification & Test Suite Results

The RCA test suite (`tests/test_root_cause_analysis.py`) covers 18 rigorous test scenarios:

```
tests/test_root_cause_analysis.py::test_rca_event_schema_validation PASSED [  5%]
tests/test_root_cause_analysis.py::test_cause_taxonomy_completeness PASSED [ 11%]
tests/test_root_cause_analysis.py::test_deterministic_evidence_scoring PASSED [ 16%]
tests/test_root_cause_analysis.py::test_shap_evidence_integration PASSED [ 22%]
tests/test_root_cause_analysis.py::test_anomaly_evidence_integration PASSED [ 27%]
tests/test_root_cause_analysis.py::test_temporal_precedence_ordering PASSED [ 33%]
tests/test_root_cause_analysis.py::test_machine_specific_normalization PASSED [ 38%]
tests/test_root_cause_analysis.py::test_contradictory_evidence_handling PASSED [ 44%]
tests/test_root_cause_analysis.py::test_confidence_classification_logic PASSED [ 50%]
tests/test_root_cause_analysis.py::test_anomaly_not_equal_failure PASSED [ 55%]
tests/test_root_cause_analysis.py::test_synthetic_m2_scenario_reconstruction PASSED [ 61%]
tests/test_root_cause_analysis.py::test_temporal_leakage_prevention PASSED [ 66%]
tests/test_root_cause_analysis.py::test_no_causal_probability_claims PASSED [ 72%]
tests/test_root_cause_analysis.py::test_insufficient_evidence_handling PASSED [ 77%]
tests/test_root_cause_analysis.py::test_deterministic_repeated_execution PASSED [ 83%]
tests/test_root_cause_analysis.py::test_service_layer_end_to_end PASSED  [ 88%]
tests/test_root_cause_analysis.py::test_invalid_missing_evidence_graceful_fallback PASSED [ 94%]
tests/test_root_cause_analysis.py::test_negative_control_shap_alone_not_rca PASSED [100%]

============================= 18 passed in 0.94s ==============================
```

Full regression suite across all project components (Phases 0–12):
```
119 passed, 4 warnings in 12.62s (100% PASSING, ZERO REGRESSIONS)
```

---

## 10. Scientific Integrity & Prohibited Language Compliance

All RCA reports, schemas, code, and documentation strictly comply with NirmaanAI scientific language rules:

| Prohibited Language | Preferred Scientific Language |
| :--- | :--- |
| *"SHAP proves the root cause"* | *"Model attribution provides predictive contribution evidence"* |
| *"Vibration caused the failure"* | *"Vibration elevation is temporally and operationally consistent with the failure event"* |
| *"RCA proves causality"* | *"RCA establishes multi-source operational correlation and temporal precedence"* |
| *"87% probability of causation"* | *"Composite analytical evidence score of 0.87 (configured analytical weights)"* |
| *"Synthetic RCA validates factory physics"* | *"Controlled synthetic demonstration reconstructing configured simulator dynamics"* |

---

## 11. Artifacts Generated in Phase 12

1. **`src/rca/cause_taxonomy.py`**: Controlled taxonomy of 13 operational causes and feature mappings.
2. **`src/rca/rca_models.py`**: Validated Pydantic v2 schemas for events, evidence, temporal steps, and responses.
3. **`src/rca/temporal_analysis.py`**: Precedence verification engine ($t_0 \to t_1 \to t_2 \to t_3$) with strict lookahead exclusion.
4. **`src/rca/evidence_engine.py`**: Deterministic scoring engine with machine baseline normalization and contradiction penalties.
5. **`src/rca/rca_engine.py`**: Core fusion engine orchestrating ranking and confidence classification.
6. **`src/rca/rca_service.py`**: Production service facade exposing `analyze_event`, `run_m2_controlled_scenario`, and `format_human_readable_report`.
7. **`src/rca/__init__.py`**: Module namespace exports.
8. **`src/models/evaluate_rca.py`**: Evaluation pipeline serializing scenario results.
9. **`models/rca/rca_summary.json`**: Verified output metrics and metadata.
10. **`tests/test_root_cause_analysis.py`**: 18 comprehensive test scenarios.
11. **`docs/rca/root_cause_analysis_report.md`**: Complete technical and research report.
