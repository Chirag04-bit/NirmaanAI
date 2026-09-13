# Machine 2 Controlled Scenario Recommendation Walkthrough

**Phase:** Phase 15 — Recommendation Engine  
**Scenario:** Machine 2 Spindle Bearing Controlled Degradation Chain  
**Decision Evaluation Timestamp:** `2026-01-21T12:00:00Z` (Day 21)

---

## 1. Scenario Timeline & Physical Progression

1. **Days 1–17 (Nominal Operation):** Machine M2 operates with nominal spindle vibration ($1.4\text{ mm/s}$), baseline temperature ($45^\circ\text{C}$), Health Score $97.47$ (`EXCELLENT`), failure probability $0.02$.
2. **Days 18–20 (Incipient Spindle Degradation):** Spindle bearing raceway begins spalling. Vibration drifts upwards ($1.4 \to 3.2\text{ mm/s}$), temperature rises ($45 \to 54^\circ\text{C}$), failure probability climbs ($0.12 \to 0.65$), Health Score degrades to $40.17$ (`DEGRADED`).
3. **Day 21 (Critical Escalation — Decision Evaluation Point):** Spindle bearing enters severe mechanical distress. Vibration reaches $4.2\text{ mm/s}$ (alert threshold $3.8\text{ mm/s}$), PCA reconstruction error reaches $0.35$ (calibrated threshold $0.2405$), failure probability reaches $0.9959$ (locked operational threshold $0.91$). Health Score drops to $26.88$ (`CRITICAL`). Cycle time expands to $62\text{s}$ ($1.38\times$ nominal $45\text{s}$), making M2 the plant bottleneck with 76 delayed parts.
4. **Day 22 (Unplanned Halt & Overhaul):** Without preemption, M2 halts at 16:30 for 150 minutes of unplanned downtime (`MAINT_0003`) and 1.5 hours of emergency technician labor (₹420).

---

## 2. Recommendation Portfolio Generated at Day 21

At $t = \text{2026-01-21T12:00:00Z}$, evaluating strictly historical operational evidence without lookahead leakage produces the following 4 prioritized actions:

### Action 1: Spindle Bearing Inspection & Controlled Preemption
- **ID:** `REC_M2_MAINT_001`
- **Category:** `MAINTENANCE`
- **Action:** `INSPECT_SPINDLE_BEARING`
- **Priority:** `CRITICAL`
- **Urgency:** `IMMEDIATE`
- **Evidence Strength:** `STRONG` (corroborated across Predictive Failure, Anomaly Detection, and Diagnostic RCA)
- **Supporting Evidence:**
  - $P(\text{fail}) = 0.9959 \ge 0.91$ (`DERIVED_FROM_OBSERVED`)
  - PCA Reconstruction Error $= 0.3500 \ge 0.2405$ (`DERIVED_FROM_OBSERVED`)
  - RCA Candidate $= \text{MECHANICAL\_LOAD}$ (`DERIVED_FROM_OBSERVED`)
- **Impact:** Prevents catastrophic spindle seizure during active production.

### Action 2: Bottleneck Feed-Rate Reduction
- **ID:** `REC_M2_FLOW_FEED_001`
- **Category:** `PRODUCTION_FLOW`
- **Action:** `REDUCE_MACHINE_FEED_RATE`
- **Priority:** `HIGH`
- **Urgency:** `SAME_DAY`
- **Evidence Strength:** `WEAK` (Production Flow domain)
- **Supporting Evidence:**
  - `is_bottleneck = True` (`DERIVED_FROM_OBSERVED`)
  - `cycle_ratio = 1.38 >= 1.20` (`DERIVED_FROM_OBSERVED`)
  - `delayed_throughput_units = 76.0` (`OBSERVED`)
- **Impact:** Relieves mechanical torque stress and stabilizes temperature while maintaining partial production.

### Action 3: Downstream Job Rescheduling
- **ID:** `REC_M2_FLOW_RESCHED_001`
- **Category:** `PRODUCTION_FLOW`
- **Action:** `RESCHEDULE_PENDING_JOBS`
- **Priority:** `HIGH`
- **Urgency:** `SAME_DAY`
- **Evidence Strength:** `WEAK` (Production Flow domain)
- **Impact:** Rebalances WIP queues to downstream workcenters and clears order backlog.

### Action 4: Proactive Spare Expediting (Projected State Justification)
- **ID:** `REC_M2_INV_EXPEDITE_001`
- **Category:** `INVENTORY`
- **Action:** `EXPEDITE_CRITICAL_SPARE` (`SKU_SPINDLE_BEARING_M2`)
- **Priority:** `HIGH`
- **Urgency:** `SAME_DAY`
- **Inventory Accounting:**
  - Observed Current Stock: **2.0 units** (Current Stockout: **False**)
  - Safety Stock: **1.134 units**
  - Reorder Point: **1.367 units**
  - Hypothetical Maintenance Consumption: **1.0 unit**
  - Projected Post-Action Stock: **1.0 unit** (Projected Safety Breach: **True**)
  - Supplier Replenishment Lead Time: **7.0 days**
- **Justification:** Current stock is 2.0 (above safety stock 1.134). Recommendation to expedite is proactive because consuming 1 spare during the upcoming maintenance projects inventory to 1.0, below the required safety buffer with a 7-day supplier replenishment window.

---

## 3. Retrospective Causal Discipline Audit

- **Decision Timestamp:** $t = \text{2026-01-21T12:00:00Z}$
- **Future Exclusion:**
  - Day 22 emergency halt downtime (150 min = ₹11,250) is strictly **excluded**.
  - Day 22 emergency overhaul labor (1.5 h = ₹420) is strictly **excluded**.
  - Day 22 maintenance log (`MAINT_0003`) is strictly **excluded**.
  - Day 23 post-maintenance health recovery ($96.91$) is strictly **excluded**.
- **Audit Verdict:** 100% causal compliance. Zero future lookahead contamination.
