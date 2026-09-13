# NirmaanAI Operational Recommendation Engine — Rule Catalog & Logic Specification

**Phase:** Phase 15 — Recommendation Engine  
**Subsystem:** Decision Support Layer (`src/decision/`)

---

## 1. Catalog of Operational Decision Rules

| Rule ID | Rule Name | Category | Antecedents | Consequent Action(s) | Priority | Urgency | Evidence Domains |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`R-M01`** | Spindle Bearing Failure Preemption | `MAINTENANCE` | $P(\text{fail}) \ge 0.91$ $\wedge$ Anomaly $\ge 0.2405$ $\wedge$ RCA = `MECHANICAL_LOAD` | `INSPECT_SPINDLE_BEARING` | `CRITICAL` | `IMMEDIATE` | `PREDICTIVE_FAILURE`, `TELEMETRY_ANOMALY`, `DIAGNOSTIC_RCA` |
| **`R-M02`** | Spindle Degradation Warning | `MAINTENANCE` | $0.75 \le P(\text{fail}) < 0.91$ $\wedge$ Vib dev $> 0.30\text{ mm/s}$ $\wedge$ RCA = `MECHANICAL_LOAD` | `INSPECT_LUBRICATION`, `SCHEDULE_PREVENTIVE_MAINTENANCE` | `HIGH` | `SAME_DAY` | `PREDICTIVE_FAILURE`, `TELEMETRY_ANOMALY`, `DIAGNOSTIC_RCA` |
| **`R-M03`** | Predictive Tooling Replacement | `MAINTENANCE` | `tool_wear_min` $\ge 200$ $\wedge$ Scrap $> 5\%$ $\wedge$ SHAP top feature = `tool_wear_min` | `REPLACE_TOOLING` | `HIGH` | `NEXT_SHIFT` | `TELEMETRY_ANOMALY`, `PRODUCTION_FLOW`, `PREDICTIVE_FAILURE` (SHAP explanation) |
| **`R-P01`** | Bottleneck Load Rebalancing | `PRODUCTION_FLOW` | `is_bottleneck = True` $\wedge$ `cycle_ratio` $\ge 1.20$ $\wedge$ `delayed_units` $> 0$ | `REDUCE_MACHINE_FEED_RATE`, `RESCHEDULE_PENDING_JOBS` | `HIGH` | `SAME_DAY` | `PRODUCTION_FLOW` |
| **`R-I01`** | Proactive Spare Replenishment | `INVENTORY` | Maintenance consumes spare $\wedge$ $S_{\text{obs}} = 2.0$ $\wedge$ $S_{\text{proj}} = 1.0 < S_{\text{safety}} (1.134)$ $\wedge$ Lead time = 7d | `EXPEDITE_CRITICAL_SPARE` | `HIGH` | `SAME_DAY` | `INVENTORY_SPARE` |
| **`R-E01`** | Peak Tariff Load Shifting | `ENERGY` | Peak window (18:00–22:00) $\wedge$ Non-bottleneck machine $\wedge$ Non-urgent job | `SHIFT_HIGH_LOAD_OFF_PEAK` | `LOW` | `ROUTINE` | `PRODUCTION_FLOW` |
| **`R-O01`** | Nominal Monitoring Negative Control | `MONITORING` | Health $\ge 75.0$ $\wedge$ Anomaly $< 0.2405$ $\wedge$ $P(\text{fail}) < 0.75$ $\wedge$ Non-bottleneck | `CONTINUE_NOMINAL_MONITORING` | `MONITOR` | `ROUTINE` | `TELEMETRY_ANOMALY`, `PREDICTIVE_FAILURE` |

---

## 2. Threshold Calibration & Provenance

1. **Phase 6 AI4I Decision Threshold (0.91):**
   - Derived during model training on stratified split (`models/predictive_maintenance/metadata.json`).
   - Represents the optimal F1 operating point for XGBoost failure classification.
2. **Phase 6 Warning Band (0.75):**
   - Configured Phase 15 decision-support threshold (`CONFIGURED_ASSUMPTION`).
   - Captures early mechanical drift before reaching critical failure probability.
3. **Phase 7 PCA Anomaly Threshold (0.2405):**
   - Derived during Phase 7 reconstruction benchmarking (`models/anomaly_detection/metadata.json`).
   - Bounded in $[0, 1]$; zero confusion with raw sensor standard deviation.
4. **Phase 8 Bottleneck Target (Cycle Ratio $\ge 1.20$):**
   - Authoritative bottleneck event definition (`src/features/bottleneck_features.py`).
   - Distinguishes nominal job cycle expansion from true manufacturing bottleneck events.
5. **Phase 13 Locked Health Bands:**
   - `EXCELLENT`: $90.0 \le H \le 100.0$
   - `HEALTHY`: $75.0 \le H < 90.0$
   - `WATCH`: $60.0 \le H < 75.0$
   - `DEGRADED`: $40.0 \le H < 60.0$
   - `CRITICAL`: $0.0 \le H < 40.0$

---

## 3. Inventory State & Projection Rigor

For Rule `R-I01`:
- **Current State Truth:** On-hand inventory is 2.0 units. Safety stock is 1.134 units. Reorder point is 1.367 units. Since $2.0 > 1.134$, **there is no current stockout**.
- **Action Consequence Projection:** If maintenance replaces the bearing, 1.0 unit is consumed:
  $$S_{\text{projected}} = 2.0 - 1.0 = 1.0\text{ unit}$$
  Since $1.0 < 1.134$, the remaining buffer will be below the statistical safety stock requirement.
- **Supplier Lead Time:** The catalog specifies $7.0 \pm 2.0$ days lead time.
- **Narrative Rule:** The recommendation is strictly justified as a **proactive safeguard against subsequent stockouts during the 7-day replenishment window**, never as an immediate stockout.
