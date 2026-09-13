# NirmaanAI What-If Simulation — Approved Scenario & Intervention Catalog

**Phase:** Phase 16 — What-If / Digital-Twin-Inspired Simulation Engine  
**Subsystem:** Decision Support Simulation Layer (`src/simulation/`)

---

## 1. Approved Intervention Catalog (Strictly 15 Actions)

| Category | Approved Intervention | Description | Modeled Operational Effect |
| :--- | :--- | :--- | :--- |
| **`MAINTENANCE`** | `INSPECT_SPINDLE_BEARING` | Controlled preemptive stoppage to inspect/replace spindle bearing | Preempts catastrophic halt (replaces 150m unplanned with 30m planned) |
| **`MAINTENANCE`** | `INSPECT_LUBRICATION` | Check and replenish oil film on spindle and guideways | Slows mechanical wear and stabilizes operating temperature |
| **`MAINTENANCE`** | `REPLACE_WORN_COMPONENT` | Overhaul degraded subassembly | Restores mechanical clearance and vibration baseline |
| **`MAINTENANCE`** | `REPLACE_TOOLING` | Exchange worn insert/toolhead before failure | Restores part dimensional accuracy and cuts scrap rate |
| **`MAINTENANCE`** | `SCHEDULE_PREVENTIVE_MAINTENANCE` | Plan service window in upcoming shift | Transitions corrective stoppage into planned downtime |
| **`PRODUCTION`** | `REDUCE_MACHINE_FEED_RATE` | Throttle cutting feed rate on distressed asset | Lowers cutting torque and thermal buildup |
| **`PRODUCTION`** | `RESCHEDULE_PENDING_JOBS` | Offload queued batches to parallel machines | Clears bottleneck queue and avoids delivery delays |
| **`PRODUCTION`** | `REBALANCE_LINE_WORKLOAD` | Adjust routing across workcenter | Minimizes starvation of downstream processes |
| **`PRODUCTION`** | `BUFFER_DOWNSTREAM_INVENTORY` | Stage safety stock between workstations | Decouples bottleneck delays from downstream lines |
| **`PRODUCTION`** | `PAUSE_NEW_JOB_RELEASE` | Halt dispatching new jobs to bottleneck queue | Prevents WIP explosion at constrained asset |
| **`INVENTORY`** | `EXPEDITE_CRITICAL_SPARE` | Accelerate supplier PO for critical spare | Replenishes depleted safety buffer under lead time constraint |
| **`INVENTORY`** | `TRIGGER_STANDARD_REORDER` | Issue standard purchase order at ROP | Maintains nominal stock replenishment cadence |
| **`INVENTORY`** | `INCREASE_SAFETY_STOCK_BUFFER` | Raise statistical safety stock threshold | Mitigates demand volatility or extended lead times |
| **`ENERGY`** | `SHIFT_HIGH_LOAD_OFF_PEAK` | Defer non-critical batch machining to off-peak | Captures peak-to-base tariff differential (₹4.00/kWh) |
| **`ENERGY`** | `INVESTIGATE_POWER_EXCURSION` | Inspect drive electronics for current surge | Detects electrical phase imbalance or motor overload |

---

## 2. Machine 2 What-If Scenarios Catalog

| Scenario ID | Name | Interventions | Core Assumptions | Avoided Loss (INR) | Post-Action Stock |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **`SCEN_M2_A_BASELINE`** | Scenario A: Baseline Continuation | None | Unmitigated progression to Day 22 halt (MAINT_0003) | ₹0.00 | 2.0 (no consumption) |
| **`SCEN_M2_B_INSPECT`** | Scenario B: Spindle Inspection | `INSPECT_SPINDLE_BEARING` | 30m planned service replaces 150m unplanned halt; consumes 1 spare | ₹9,420.00 | 1.0 (safety breached) |
| **`SCEN_M2_C_INSPECT_EXPEDITE`** | Scenario C: Inspection + Expedite | `INSPECT_SPINDLE_BEARING`, `EXPEDITE_CRITICAL_SPARE` | Preempts halt + places PO for 12 units under 7-day lead time | ₹9,420.00 | 1.0 (reorder active) |
| **`SCEN_M2_D_FLOW_MITIGATION`** | Scenario D: Flow Rebalancing | `REDUCE_MACHINE_FEED_RATE`, `RESCHEDULE_PENDING_JOBS` | Offloads batches; reduces delayed units from 76 to 15 | ₹19,520.00 | 2.0 (no consumption) |
| **`SCEN_M2_E_FULL_PORTFOLIO`** | Scenario E: Full Portfolio | `INSPECT_SPINDLE_BEARING`, `REDUCE_MACHINE_FEED_RATE`, `RESCHEDULE_PENDING_JOBS`, `EXPEDITE_CRITICAL_SPARE` | Preempts halt + clears queue + reorders spare | ₹28,940.00 | 1.0 (reorder active) |

---

## 3. Negative Control Scenario Catalog

- **`SCEN_M1_NEGATIVE_CONTROL`**:
  - **Asset:** Machine M1 at Day 17 (`2026-01-17T12:00:00Z`).
  - **Interventions:** None (Nominal operation).
  - **Projected Effect:** Delta = 0.0 across all KPIs; avoided loss = ₹0.00.
  - **Purpose:** Verifies simulator invariance when no physical degradation is present.
