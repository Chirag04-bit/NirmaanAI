# NirmaanAI — Phase 20 Implementation Report
## AI Factory Copilot Subsystem (`v0.20.0`)

**Date:** 2026-09-13  
**Status:** COMPLETED & VERIFIED  
**Version:** v0.20.0  
**Authors:** NirmaanAI Systems Engineering  

---

### 1. Executive Summary
Phase 20 delivers the **AI Factory Copilot (`v0.20.0`)**, a grounded, deterministic, decision-support interface built on top of the Phase 19 Factory Knowledge Memory and Grounded RAG engine. 

The Copilot enables plant operators, maintenance engineers, and factory managers to submit natural-language operational inquiries and receive evidence-backed, provenance-cited responses. The system operates strictly within approved manufacturing evidence, enforcing plant topology verification, temporal cutoff isolation, epistemic classification, source authority ranking, and counterfactual safety guardrails.

The Copilot is engineered strictly as a **controlled decision-support system**—it is not an autonomous agent, does not execute unverified plant actions, and completely prevents hallucinations by returning `NO_SUFFICIENT_EVIDENCE` whenever requested data is missing, out-of-scope, or unprojectable.

---

### 2. Architecture & Processing Pipeline

```
                                  [ User Query ]
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       1. Entity Extraction            │
                     │  (Machines M1–M5, FAC_01, Metrics)    │
                     └───────────────────┬───────────────────┘
                                         │
                    Invalid Entities?    ├─────────► [ Refusal: NO_SUFFICIENT_EVIDENCE ]
                                         │ (Valid)
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       2. Intent Classification        │
                     │    (15 Deterministic Intent Enums)    │
                     └───────────────────┬───────────────────┘
                                         │
                    Out of Scope?        ├─────────► [ Refusal: NO_SUFFICIENT_EVIDENCE ]
                                         │ (In Scope)
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       3. Causal Guardrail Check       │
                     │ (NOT_PROJECTABLE counterfactual check) │
                     └───────────────────┬───────────────────┘
                                         │
                    Unprojectable Metric?├─────────► [ Refusal: NO_SUFFICIENT_EVIDENCE ]
                                         │ (Projectable)
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       4. Temporal Policy Engine       │
                     │  (Cutoff: 2026-01-21T12:00:00Z;       │
                     │   Prospective vs Retrospective Gate)  │
                     └───────────────────┬───────────────────┘
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       5. Phase 19 Knowledge Store     │
                     │  (Hybrid Dense/Lexical Retrieval,     │
                     │   Authority Weights, Cosine Sim)      │
                     └───────────────────┬───────────────────┘
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       6. Source Authority Filter      │
                     │ (Authoritative Phase 14 over drafts;  │
                     │  Purge superseded INR 92,582.28)      │
                     └───────────────────┬───────────────────┘
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       7. Grounded Answer Composer     │
                     │  (Synthesizes domain answer text with │
                     │   epistemic status & provenance tags) │
                     └───────────────────┬───────────────────┘
                                         │
                                         ▼
                               [ CopilotResponse ]
```

---

### 3. File Manifest

#### Created Phase 20 Files:
```
src/copilot/
├── __init__.py                                 # Package export root
├── schemas.py                                  # Pydantic v2 schemas: CopilotIntent, CopilotResponse, CopilotContext
├── intent.py                                   # Deterministic 15-intent rule classifier
├── entities.py                                 # Entity extraction: machines (M1–M5), FAC_01, metrics, phases
├── temporal.py                                 # Temporal boundary interpretation & retrospective gating
├── policies.py                                 # Epistemic policies, authority ranking, and NOT_PROJECTABLE guardrails
├── composer.py                                 # Grounded operational answer composer with evidence citations
├── copilot_service.py                          # FactoryCopilotService core interface (.ask(query, context))
├── router.py                                   # FastAPI APIRouter exposing POST /api/v1/copilot/ask
└── evaluation/
    ├── __init__.py
    └── benchmark.py                            # 14-case benchmark evaluator (Q1–Q8, NQ1–NQ5, TQ1)

models/copilot/
└── copilot_evaluation.json                     # Serialized benchmark evaluation report (100% accuracy)

docs/copilot/
├── architecture.md                             # Copilot system architecture documentation
└── PHASE20_IMPLEMENTATION_REPORT.md            # Comprehensive Phase 20 report

tests/
└── test_copilot.py                             # 19 comprehensive unit, integration, and API tests
```

#### Modified Files:
```
src/api/router.py                               # Mounted copilot_router under /api/v1/copilot
```

---

### 4. Intent Taxonomy & Classification
The intent classification engine (`src/copilot/intent.py`) uses a prioritized, deterministic pattern engine covering 15 operational categories without neural model overhead:
1. `FACT_LOOKUP`: Technical plant specifications, machine types, sensor lists.
2. `MACHINE_HEALTH`: Real-time health states and composite scores.
3. `MACHINE_DEGRADATION`: Spindle wear, vibration creep, mechanical distress.
4. `PREDICTIVE_MAINTENANCE`: Predictive failure probability, RUL estimation.
5. `ANOMALY_STATUS`: PCA reconstruction error, normalized anomaly scores.
6. `BOTTLENECK_STATUS`: Active constraints, cycle ratio, delayed units.
7. `PRODUCTION_FORECAST`: Production scheduling and demand targets.
8. `INVENTORY_STATUS`: Critical spares, safety stock buffers, reorder points.
9. `ROOT_CAUSE`: Fault tree diagnosis, primary candidate causes (e.g. `MECHANICAL_LOAD`).
10. `RECOMMENDATION`: Prescriptive decision rules (e.g. `INSPECT_SPINDLE_BEARING`).
11. `FINANCIAL_IMPACT`: Quantified realized loss, projected opportunity, gross exposure.
12. `WHAT_IF`: Monte Carlo simulation scenarios and avoidable loss projections.
13. `TEMPORAL_HISTORY`: Historical telemetry, maintenance logs, retrospective events.
14. `SYSTEM_CAPABILITY`: Copilot capabilities, scope boundaries, and help.
15. `UNSUPPORTED_QUERY`: Out-of-scope subjects (weather, politics, 2027 expansion budget).

---

### 5. Entity Extraction & Topology Validation
The entity extraction engine (`src/copilot/entities.py`) verifies all plant assets against cataloged topology:
- **Valid Assets**: `M1`, `M2`, `M3`, `M4`, `M5`.
- **Valid Facilities**: `FAC_01`.
- **Validation Rule**: Any inquiry referencing an uncataloged machine (e.g. `M99`, `M0`, `M6`) or factory (e.g. `FAC_99`, `FAC_02`) is flagged at extraction time and rejected immediately with `NO_SUFFICIENT_EVIDENCE`.

---

### 6. Temporal Governance & Boundary Isolation
- **Authoritative Cutoff**: `2026-01-21T12:00:00Z` (Locked Decision Boundary).
- **Default Prospective Mode**: `include_retrospective = False`.
- **Synthetic Ground Truth Event (`MAINT_0003`)**:
  - Timestamp: `2026-01-22T16:30:00Z` (150-minute emergency spindle seizure).
  - Prospective Isolation: Default decision queries exclude `MAINT_0003` to prevent future knowledge leakage into past decisions.
  - Boundary Inquiries (e.g. TQ1): Specifically confirms that `MAINT_0003` was post-cutoff and strictly excluded from prospective decision evidence.
  - Retrospective Access: If explicitly requested (`include_retrospective=True`), the event is surfaced and prominently labeled `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`.

---

### 7. Epistemic Classification & Counterfactual Guardrails
- **Epistemic Classification**:
  - `OBSERVED`: Raw telemetry and empirical maintenance logs.
  - `DERIVED`: Algorithmic calculations (realized financial loss, cycle ratio).
  - `MODEL_OUTPUT`: ML model inference outputs (failure probability, health scores).
  - `CONTROLLED_SYNTHETIC`: Phase 15 prescriptive rules and benchmark scenario definitions.
  - `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`: Post-cutoff evaluation records (`MAINT_0003`).
  - `PROJECTED`: Simulated what-if counterfactuals.
  - `NOT_PROJECTABLE`: Causal values unsupported by validated empirical evidence.
- **Counterfactual Guardrail**:
  - Queries requesting unprojectable metrics (e.g., exact post-intervention failure probability or post-service health index recovery) return `NO_SUFFICIENT_EVIDENCE` with the explicit limitation:
    `"Exact post-intervention mechanical metrics are NOT_PROJECTABLE from the validated evidence base without empirical post-treatment telemetry."`

---

### 8. Source Authority & Financial Governance
- **Authoritative Values Grounded**:
  - Realized Operational Loss: **₹73,062.28** (scrap, rework, downtime).
  - Baseline Projected Opportunity Cost: **₹24,320.00**.
  - Authoritative Gross Financial Exposure: **₹97,382.28**.
  - Phase 16 Scenario D Avoided Opportunity Cost: **₹19,520.00**.
- **Superseded Figure Protection**:
  - Historical draft audit loss of ₹92,582.28 is marked `is_superseded=True` and filtered out by default.

---

### 9. Benchmark Evaluation Results
Evaluated against the 14 comprehensive test queries in `src/copilot/evaluation/benchmark.py`:

| Metric | Target | Achieved | Status |
|---|---|---|---|
| Positive Queries (Q1–Q8, TQ1) | 9 | 9 | **100% Passed** |
| Negative Queries (NQ1–NQ5) | 5 | 5 | **100% Rejected** |
| Overall Benchmark Accuracy | 100% | **100% (14/14)** | **PERFECT** |
| Mean Query Latency | $< 50$ ms | **25.2 ms** | **PASSED** |

#### Query Breakdown:
1. **Q1 (Health of M2)**: SUCCESS | Health Score 26.88/100, CRITICAL, P(fail) 0.9959 (`MODEL_OUTPUT`).
2. **Q2 (M2 Degradation Cause)**: SUCCESS | `MECHANICAL_LOAD` spindle bearing wear and torque surge (`DERIVED`).
3. **Q3 (M2 Recommendation)**: SUCCESS | `INSPECT_SPINDLE_BEARING` (Critical/Immediate) + `EXPEDITE_CRITICAL_SPARE` (`CONTROLLED_SYNTHETIC`).
4. **Q4 (M2 Bearing Inventory)**: SUCCESS | Current 2.0, Safety stock 1.134, Projected 1.0 (safety breached), Lead time 7d (`DERIVED`).
5. **Q5 (M2 Realized Loss)**: SUCCESS | Authoritative Realized Loss ₹73,062.28 (`DERIVED`).
6. **Q6 (M2 Gross Exposure)**: SUCCESS | Authoritative Gross Exposure ₹97,382.28 (Realized ₹73,062.28 + Opportunity ₹24,320.00) (`DERIVED`).
7. **Q7 (M2 Bottleneck Risk)**: SUCCESS | Cycle ratio 1.38, 76 delayed units (`DERIVED`).
8. **Q8 (M2 Retrospective Event)**: SUCCESS | 150m unplanned halt, labeled `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`.
9. **TQ1 (Temporal Boundary)**: SUCCESS | Confirms MAINT_0003 was post-cutoff and NOT prospective decision evidence.
10. **NQ1 (M99 Health)**: `NO_SUFFICIENT_EVIDENCE` (Entity guardrail rejected invalid machine M99).
11. **NQ2 (Coolant Explosion)**: `NO_SUFFICIENT_EVIDENCE` (Topical anchor guardrail rejected unsupported event).
12. **NQ3 (2027 Expansion Budget)**: `NO_SUFFICIENT_EVIDENCE` (Out-of-scope domain rejected).
13. **NQ4 (Exact Post-Service Failure Probability)**: `NO_SUFFICIENT_EVIDENCE` (Counterfactual causal guardrail rejected NOT_PROJECTABLE metric).
14. **NQ5 (Unrelated General Knowledge)**: `NO_SUFFICIENT_EVIDENCE` (Out-of-scope domain rejected).

---

### 10. Automated Testing & Verification

- **Phase 20 Pytest Suite (`tests/test_copilot.py`)**:
  - **19 passed in 3.95s**.
  - Covers intent classification, entity extraction, invalid entity rejection, Phase 19 retrieval, provenance retention, temporal cutoff, retrospective isolation, TQ1 boundary check, epistemic preservation, superseded financial protection, realized loss accuracy, recommendation grounding, RCA grounding, inventory grounding, bottleneck grounding, unprojectable causal guardrail, negative query rejection, deterministic reproducibility, benchmark evaluation, and FastAPI HTTP endpoints.

- **Full Project Regression (`tests/`)**:
  - **328 passed, 1 skipped, 0 failed in 21.60s**.
  - Zero regressions across Phases 0–19.
  - The 1 skipped test is the Phase 17 live PostgreSQL environment test (`test_postgresql_connection`), which remains properly skipped in the absence of a local PostgreSQL server.

---

### 11. Baseline Data Integrity
- `data/synthetic/auto_components/operational_losses.csv`:
  - **MD5 Checksum**: `34B12582B32D81E3121429C55EBF74E8` (100% unaltered; matches Phase 14–19 locked baseline).
- No external datasets or existing models were modified.

---

### 12. Dependencies & Environment Compliance
- **Python Version**: Python 3.14.6
- **Installed Packages Used**: `scikit-learn 1.9.0`, `numpy 2.4.6`, `scipy 1.18.0`, `pydantic 2.13.4`, `fastapi 0.115.6`, `pytest 9.1.1`.
- **Zero External Packages Installed**: No `torch`, `transformers`, `sentence-transformers`, `LangChain`, or external agent frameworks were added.

---

### 13. Authoritative Project State

- **Phases 0–16**: COMPLETE / LOCKED
- **Phase 17**: HOLD — ENVIRONMENT BLOCKED (Implementation verified; live PostgreSQL unavailable)
- **Phase 18**: HOLD — ENVIRONMENT BLOCKED (FastAPI implementation verified; live PostgreSQL unavailable)
- **Phase 19**: COMPLETE & LOCKED (Knowledge Memory / RAG layer)
- **Phase 20**: **COMPLETE & LOCKED** (AI Factory Copilot)
- **Phase 21 (React + Vite UI Dashboard)**: **NOT STARTED** (Awaiting explicit user instruction).
