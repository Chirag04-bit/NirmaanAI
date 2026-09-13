# Machine 2 What-If Simulation Walkthrough & Policy Analysis

**Phase:** Phase 16 — What-If / Digital-Twin-Inspired Simulation Engine  
**Target Asset:** Multi-Axis Vertical Milling Center M2  
**Decision Evaluation Point:** `2026-01-21T12:00:00Z` (Day 21)

---

## 1. Baseline Decision-Point Context

At Day 21 ($t = \text{2026-01-21T12:00:00Z}$), Machine M2 is in severe mechanical distress:
- **Failure Probability:** $0.9959$ (exceeds locked $0.91$ threshold).
- **PCA Anomaly Score:** $0.35$ (exceeds calibrated $0.2405$ cutoff).
- **Health Score:** $26.88$ (locked `CRITICAL` band, $< 40.0$).
- **Cycle Ratio:** $1.38$ ($> 1.20$ bottleneck target).
- **Delayed Units:** $76$ units (unearned contribution margin $= 76 \times ₹320 = ₹24,320.00$).
- **Bearing Inventory:** Observed current stock is $2.0\text{ units}$, Safety Stock is $1.134\text{ units}$, and Reorder Point ($ROP$) is $1.367\text{ units}$. Because $2.0 > 1.134$ and $2.0 > 1.367$, current stock is **NOT** below safety stock and **NOT** below reorder point (**no current-stockout claim permitted**).
- **Gross Financial Exposure:** $₹97,382.28$ ($₹73,062.28\text{ realized loss} + ₹24,320.00\text{ opportunity cost}$).

---

## 2. Walkthrough of What-If Scenarios

### Scenario A: Baseline Continuation (No Intervention)
- **Operational Reality:** If no action is taken, M2 runs unmitigated until catastrophic bearing seizure occurs at Day 22T16:30 (`MAINT_0003`).
- **Projected Result:**
  - $150\text{ min}$ unplanned emergency downtime ($₹11,250.00\text{ loss}$).
  - $1.5\text{ h}$ emergency technician overhaul overtime ($₹420.00\text{ cost}$).
  - $76\text{ delayed units}$ ($₹24,320.00\text{ opportunity cost}$).
  - **Projected Avoided Loss:** **₹0.00**.

### Scenario B: Preemptive Spindle Inspection
- **Intervention:** `INSPECT_SPINDLE_BEARING`.
- **Mechanism:** A controlled $30\text{ min}$ planned maintenance halt replaces the $150\text{ min}$ emergency halt.
- **Financial Delta:**
  - Avoided downtime loss: $(150 - 30)/60 \times ₹4,500 = ₹9,000.00$.
  - Avoided emergency labor: $1.5\text{ h} \times ₹280 = ₹420.00$.
  - **Total Avoided Loss:** **₹9,420.00** (`PROJECTED` breakdown loss avoidance).
- **Inventory Consequence:** $1\text{ bearing}$ is consumed. Projected stock drops to $1.0\text{ unit}$, which breaches the safety stock threshold ($1.0 < 1.134$).
- **Health & Failure Probability:** `NOT_PROJECTABLE` (no empirical causal treatment effect is available in the existing controlled synthetic dataset for preventive bearing replacement).

### Scenario C: Preemptive Inspection + Expedited Replenishment
- **Interventions:** `INSPECT_SPINDLE_BEARING` + `EXPEDITE_CRITICAL_SPARE`.
- **Mechanism:** Same mechanical repair as Scenario B, but simultaneously triggers an expedited purchase order for $12\text{ units}$ (Phase 10 EOQ) with a $7\text{ day}$ supplier lead time.
- **Outcome:** Eliminates emergency breakdown losses ($₹9,420.00$) while actively mitigating the post-action safety stock breach ($1.0 < 1.134$).
- **Health & Failure Probability:** `NOT_PROJECTABLE`.

### Scenario D: Production Flow Mitigation
- **Interventions:** `REDUCE_MACHINE_FEED_RATE` + `RESCHEDULE_PENDING_JOBS`.
- **Mechanism:** Throttles feed rate and offloads pending batches to parallel CNC lines.
- **Assumed Flow Delta:**
  - Delayed units reduced from $76 \to 15$ units. (Clearly classified as a `CONFIGURED_ASSUMPTION`; NOT empirically validated).
  - Avoided opportunity cost: $(76 - 15) \times ₹320 = ₹19,520.00$ (strictly `PROJECTED_OPPORTUNITY_COST`; **never called realized savings**).
- **Mechanical State:** Spindle bearing remains unserviced; Health and Failure Risk are `NOT_PROJECTABLE`. Zero bearings consumed.

### Scenario E: Full Mitigation Portfolio
- **Interventions:** `INSPECT_SPINDLE_BEARING` + `REDUCE_MACHINE_FEED_RATE` + `RESCHEDULE_PENDING_JOBS` + `EXPEDITE_CRITICAL_SPARE`.
- **Mechanism:** Synthesizes mechanical preemption, production flow rebalancing, and proactive inventory procurement.
- **Total Financial Delta:**
  - Avoided breakdown loss: $₹9,420.00$ (`PROJECTED`).
  - Avoided opportunity cost: $₹19,520.00$ (`PROJECTED_OPPORTUNITY_COST`).
  - **Total Projected Avoided Financial Exposure:** **₹28,940.00**.
  - Resulting Gross Financial Exposure: $₹97,382.28 - ₹28,940.00 = \mathbf{₹68,442.28}$.
  - Mechanical Health & Failure Risk: `NOT_PROJECTABLE` (unsupported causal intervention effects are strictly withheld).
- **Policy Classification:** Designated as providing the **broadest modeled mitigation coverage under configured assumptions**. (Zero claims of unproven mathematical global optimality).

---

## 3. Decision Support & Human Governance

All What-If scenario projections are decision-support outputs. A human plant manager or maintenance engineer must review the trade-offs (e.g. planned downtime scheduling, batch rerouting feasibility, and procurement lead times) before authorizing physical changes on the shop floor.
