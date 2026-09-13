# NirmaanAI Phase 20: AI Factory Copilot Architecture

## 1. System Overview
The **AI Factory Copilot** (`v0.20.0`) is a grounded, deterministic, decision-support interface for plant operators, reliability engineers, and factory managers. Operating strictly on top of the **Phase 19 Factory Knowledge Memory / RAG layer**, the Copilot translates natural-language manufacturing queries into evidence-backed, provenance-cited responses.

The Copilot is engineered as a controlled decision-support system, deliberately designed without ungrounded conversational generative models, autonomous tool execution loops, or probabilistic hallucinations.

---

## 2. High-Level Architecture

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

## 3. Core Subsystems

### 3.1 Intent Classification Engine (`src/copilot/intent.py`)
Deterministic pattern-and-rule classifier mapping natural language questions into 15 operational intents:
1. `FACT_LOOKUP`: Technical plant parameters, machine types, sensor specs.
2. `MACHINE_HEALTH`: Real-time machine health state and composite score.
3. `MACHINE_DEGRADATION`: Wear patterns, spindle degradation, vibration creep.
4. `PREDICTIVE_MAINTENANCE`: Predictive failure probability, RUL estimates.
5. `ANOMALY_STATUS`: PCA reconstruction error, normalized anomaly scores.
6. `BOTTLENECK_STATUS`: Active flow constraints, cycle ratio, delayed units.
7. `PRODUCTION_FORECAST`: Production scheduling and demand targets.
8. `INVENTORY_STATUS`: Critical spare parts, safety stock buffers, reorder points.
9. `ROOT_CAUSE`: Root Cause Analysis (Phase 12 fault tree, candidate causes).
10. `RECOMMENDATION`: Prescriptive decision rules (Phase 15 approved actions).
11. `FINANCIAL_IMPACT`: Quantified realized loss, projected opportunity, gross exposure.
12. `WHAT_IF`: Monte Carlo simulation scenarios and counterfactual loss avoidance.
13. `TEMPORAL_HISTORY`: Historical telemetry, maintenance logs, retrospective audits.
14. `SYSTEM_CAPABILITY`: Copilot capabilities, operational scope, and usage help.
15. `UNSUPPORTED_QUERY`: Out-of-scope subjects (weather, gossip, external finances).

### 3.2 Entity Extraction & Plant Topology (`src/copilot/entities.py`)
- **Valid Plant Topology**:
  - Valid Machines: `M1`, `M2`, `M3`, `M4`, `M5`.
  - Valid Factories: `FAC_01`.
- **Rejection Policy**:
  - Any query referencing unknown machine assets (e.g. `M99`, `M0`, `M6`) or unknown factory identifiers (e.g. `FAC_99`, `FAC_02`) is rejected at extraction time with `NO_SUFFICIENT_EVIDENCE`.

### 3.3 Temporal Governance & Boundary Isolation (`src/copilot/temporal.py`)
- **Locked Decision Boundary**: `DECISION_CUTOFF = 2026-01-21T12:00:00Z`.
- **Default Mode**: `include_retrospective = False`.
- **Retrospective Event Isolation**:
  - Synthetic event `MAINT_0003` occurs at `2026-01-22T16:30:00Z` (`RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`).
  - Prospective decision queries exclude `MAINT_0003` to prevent forward data leakage.
  - Queries interrogating the boundary status of `MAINT_0003` explicitly state that it was NOT part of prospective decision evidence.

### 3.4 Epistemic Policy & Causal Guardrails (`src/copilot/policies.py`)
- **Epistemic Classification**:
  - `OBSERVED`: Raw empirical records.
  - `DERIVED`: Computed analytical metrics.
  - `MODEL_OUTPUT`: ML model inference outputs.
  - `CONTROLLED_SYNTHETIC`: Phase 15 prescriptive rule outputs and benchmark scenarios.
  - `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH`: Post-cutoff evaluation records.
  - `PROJECTED`: Simulated what-if counterfactuals.
  - `NOT_PROJECTABLE`: Causal values that cannot be computed from validated evidence.
- **Counterfactual Guardrail**:
  - Questions asking for exact post-intervention failure probability or post-service health index recovery are rejected as `NOT_PROJECTABLE`.
- **Source Authority Enforcement**:
  - Phase 14 authoritative figures (Realized: ₹73,062.28, Opportunity: ₹24,320.00, Gross Exposure: ₹97,382.28) outrank superseded draft figures (₹92,582.28).

### 3.5 Grounded Answer Composer (`src/copilot/composer.py`)
- Synthesizes retrieved evidence into concise operational language.
- Generates typed Pydantic v2 `CopilotResponse` payloads containing:
  - `answer`: Grounded operational text.
  - `evidence`: List of retrieved `EvidenceItem` citations.
  - `epistemic_status`: Authoritative epistemic classification.
  - `provenance`: Full traceability back to source files and sections.
  - `confidence`: Confidence score (`HIGH`, `MEDIUM`, `NO_EVIDENCE`).
  - `limitations`: Explicit assumptions and counterfactual boundaries.

---

## 4. API & Integration Layer
- **Service Layer**: `FactoryCopilotService` (`src/copilot/copilot_service.py`).
  - Direct programmatic method: `service.ask(query, context)`
- **FastAPI Subsystem**: `src/copilot/router.py` mounted at `/api/v1/copilot`.
  - `POST /api/v1/copilot/ask`: Ingests `CopilotAskRequest` and returns `CopilotResponse`.
  - `GET /api/v1/copilot/health`: Health status, indexed chunk count, and cutoff metadata.
- **Frontend Compatibility**: Ready for zero-friction consumption by the Phase 21 React/Vite dashboard.
