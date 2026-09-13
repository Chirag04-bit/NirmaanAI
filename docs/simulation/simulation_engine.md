# NirmaanAI Digital-Twin-Inspired What-If Simulation Engine — Architecture & Subsystem Specification

**Phase:** Phase 16 — What-If / Digital-Twin-Inspired Simulation Engine  
**Subsystem:** Decision Support Simulation Layer (`src/simulation/`)  
**Governance:** Decision Support Only (Human Supervisor Authorization Mandatory)

---

## 1. Subsystem Philosophy & Precise Classification

### Precise Classification:
**DIGITAL-TWIN-INSPIRED WHAT-IF SIMULATION**

### What it IS:
- A transparent, deterministic, decision-support simulation layer that evaluates:
  *"What would likely happen to operational KPIs if a proposed intervention were applied?"*
- A counterfactual evaluation engine that compares hypothetical operational interventions against the established controlled synthetic factory state.
- An auditable scenario delta calculator ($Delta = \text{Projected State} - \text{Baseline State}$).

### What it is NOT:
- **NOT** a physical digital twin.
- **NOT** a physics-validated simulator (no CFD, FEM, or continuum mechanics).
- **NOT** an autonomous machine controller.
- **NOT** a causal discovery system claiming real-world deployment validation.
- **NOT** an optimization engine claiming global mathematical optimality.

---

## 2. Architecture & Component Structure

```
src/simulation/
├── __init__.py                     # Exposes simulation models and services
├── simulation_models.py            # Pydantic v2 schemas, KPI vectors, uncertainty enums
├── scenario_definitions.py         # Authoritative baseline states and delta calculators
├── simulation_engine.py            # Deterministic scenario generators (Scenarios A through E)
└── simulation_service.py           # Facade orchestrating simulations, negative controls, and sensitivity
```

### 2.1 Core Schemas (`simulation_models.py`)
- `SimulationInterventionType`: Closed catalog of **strictly 15 approved actions** from Phase 15 recommendation taxonomy.
- `OperationalKPIVector`: Multidimensional state vector tracking failure probability, anomaly score, health score, cycle ratio, delayed units, downtime (unplanned vs planned), scrap, rework, inventory on-hand/projected, and Phase 14 financial exposures.
- `KPIDeltaVector`: Difference vector computing $\Delta = \text{Projected} - \text{Baseline}$.
- `ScenarioAssumption`: Explicitly declared assumption with parameter name, configured value, unit, and rationale.
- `WhatIfScenario`: Immutable scenario record with baseline, assumptions, projected state, delta, confidence, and limitations.
- `ScenarioComparisonReport`: Multi-scenario comparative evaluation with policy-based ranking narrative.

---

## 3. Epistemic Provenance Integrity

Every metric and scenario output strictly enforces epistemic demarcation:
- `OBSERVED`: Measured sensor telemetry, actual scrap parts, physical on-hand stock ($2.0\text{ units}$), safety stock threshold ($1.134\text{ units}$), authoritative reorder point ($1.367\text{ units}$).
- `DERIVED_FROM_OBSERVED`: Baseline predictive failure probability ($0.9959$), anomaly score ($0.35$), health score ($26.88$), baseline realized loss ($₹73,062.28$).
- `CONFIGURED_ASSUMPTION`: Planned service downtime duration ($30\text{ min}$), remaining delayed units ($15.0\text{ units}$), contribution margin ($₹320/\text{unit}$), downtime rate ($₹4,500/\text{h}$), sensitivity bounds (LOW, BASE, HIGH).
- `PROJECTED`: Projected post-action inventory stock ($1.0\text{ unit}$), projected avoided downtime ($120\text{ min}$), projected avoided breakdown loss ($₹9,420.00$).
- `PROJECTED_OPPORTUNITY_COST`: Avoided margin loss from clearing bottleneck throughput delay ($(76 - 15) \times ₹320 = ₹19,520.00$).
- `CONTROLLED_SYNTHETIC`: Scenario validation wrapper for simulated degradation chains (Scenario A unmitigated Day 22 halt).
- `NOT_PROJECTABLE`: Explicitly assigned when an empirical causal treatment effect is absent from the repository (preventive intervention mechanical health score, failure probability, and anomaly score).

---

## 4. Financial Simulation Standards (Phase 14 Compliance)

1. **Zero Pseudo-Financial Formulas:**
   $$₹ \ne f(\text{Health}),\quad ₹ \ne f(\text{SHAP}),\quad ₹ \ne f(\text{RCA})$$
   Monetary calculations strictly follow Phase 14 physical accounting identities.
2. **Realized vs Projected Separation:**
   - `realized_operational_loss_inr`: Historical disruption loss already incurred ($₹73,062.28$).
   - `projected_opportunity_cost_inr`: Unearned margin from remaining delayed units ($15 \times ₹320 = ₹4,800.00$).
   - `projected_avoided_loss_inr`: Avoided losses resulting from the hypothetical intervention (avoided breakdown loss ₹9,420 + avoided opportunity cost ₹19,520 = ₹28,940).
   - Projected avoided losses are **never** described as "realized savings".

---

## 5. Categorical Uncertainty & Robustness

Statistical confidence intervals are **not** fabricated where uncalibrated. The engine enforces categorical uncertainty:
- `HIGH_EVIDENCE`: Grounded in observed historical transitions (e.g. baseline continuation in Scenario A, nominal invariance in Negative Control M1).
- `ASSUMPTION_DEPENDENT`: Directly dependent on configured MSME parameters and hypothetical scenario assumptions (Scenarios B, C, D, E).
- `NOT_PROJECTABLE`: Output when empirical or analytical evidence is insufficient (numbers are **never** fabricated). Reason: *"No intervention-specific empirical treatment effect is available in the existing controlled synthetic dataset."*
