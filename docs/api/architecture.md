# NirmaanAI Phase 18 — API Architecture & Design Specification

## 1. System Overview

NirmaanAI Phase 18 establishes the production-grade FastAPI backend service layer (`v0.18.0`). It serves as the typed, high-performance bridge between the underlying PostgreSQL / SQLAlchemy 2.0 persistence layer (Phase 17) and upstream analytical consumers (including the upcoming Phase 21 React/Vite web application).

```
PostgreSQL / SQLite
       ↓
SQLAlchemy 2.x Declarative Models (`src/db/models/`)
       ↓
API Service Layer (`src/services/api/`)
       ↓
FastAPI Dependency Injection (`src/api/dependencies.py`)
       ↓
Domain Routers (`src/api/routes/*.py` mounted under `/api/v1`)
       ↓
Pydantic v2 Serialization (`src/schemas/`)
       ↓
Frontend / External Consumers (Phase 21 React + Vite Dashboard)
```

## 2. Architectural Layers

### 2.1 Pydantic v2 Schema Layer (`src/schemas/`)
- Strict validation and serialization with `from_attributes=True`.
- Standardized pagination wrappers: `PaginationParams`, `PaginatedResponse[T]`.
- Standardized JSON envelope: `Envelope[T]`.
- Structured error envelopes: `ErrorResponse`, `ErrorDetail`.
- Type annotations across all 16 business domains:
  - `factories.py`, `machines.py`, `sensors.py`
  - `production.py`, `maintenance.py`, `inventory.py`
  - `ai_outputs.py` (PdM, Anomaly, Bottleneck, Forecast, SHAP, RCA, Health)
  - `finance.py`, `recommendations.py`, `simulations.py`

### 2.2 API Service Layer (`src/services/api/`)
Encapsulates all database query logic, filtering, aggregations, and business reconciliations:
- **`FactoryApiService`**: Factory listing, machine aggregation, and multi-machine high-level overviews.
- **`MachineApiService`**: Single-machine drilldown, reconciles health state, active anomaly count, and prioritized recommendations.
- **`TelemetryApiService`**: Query telemetry snapshots, bounded time-range queries, and per-sensor downsampling/aggregates.
- **`ProductionApiService`**: Production job logs, batch tracking, and machine job allocations.
- **`MaintenanceApiService`**: Enforces temporal segregation (`DECISION_CUTOFF` vs ground truth).
- **`InventoryApiService`**: SKU retrieval and machine-spare associations (enforcing Phase 10 inventory contracts).
- **`AiOutputApiService`**: Unified query interface for PdM RUL, multi-detector anomalies, bottleneck risks, forecasts, SHAP attributions, and RCA causes.
- **`FinanceApiService`**: Strict segregation between realized historical losses (₹73,062.28) and counterfactual opportunity costs (₹24,320.00 baseline vs ₹19,520.00 avoided).
- **`RecommendationApiService`**: Closed 26-action operational recommendation queries with priority-weighted ordering.
- **`SimulationApiService`**: What-If scenario querying ensuring diagnostic KPIs remain `"NOT_PROJECTABLE"`.

### 2.3 Dependency Injection Layer (`src/api/dependencies.py`)
- `get_db`: Yields request-scoped SQLAlchemy `Session`, properly committed or rolled back and closed upon request completion. Supports testing override via `app.dependency_overrides[get_db]`.
- `get_pagination`: Query-parameter extractor enforcing `page >= 1` and `1 <= page_size <= 100` (default 50).
- `get_telemetry_params`: Validates ISO-8601 start/end timestamps and ensures bounded windows (default 24h, max 168h).

### 2.4 FastAPI Application Factory (`app/main.py`)
- Factory pattern: `create_app()` initializes CORS middleware, routes, exception handlers, and lifespan handlers.
- **Structured Error Handling**:
  - `404 Not Found`: Returns standard `{ "detail": "...", "code": "NOT_FOUND" }`.
  - `422 Unprocessable Entity`: Formats validation errors into field-level detail lists `{ "detail": "Validation error", "code": "VALIDATION_ERROR", "errors": [...] }`.
  - `503 Service Unavailable`: Triggered when database connection or dependency health checks fail.
  - `500 Internal Server Error`: Masked internal exceptions to prevent credential or stack trace leakage in production responses.
- **Liveness & Readiness**:
  - `/health`: System-level health endpoint verifying database connectivity (`SELECT 1`).
  - `/api/v1/health`: API subsystem status report.

## 3. Strict Semantic Guardrails

1. **Temporal Horizon Guardrail**:
   - `DECISION_CUTOFF = 2026-01-21T12:00:00Z`.
   - The synthetic failure record `MAINT_0003` at `2026-01-22T16:30:00Z` is flagged with `is_decision_input=False` and `epistemic_status="RETROSPECTIVE_GROUND_TRUTH"`.
   - Default maintenance queries filter by `is_decision_input=True`. Retrospective records are only accessible when `include_retrospective=True` is explicitly passed.

2. **Financial Loss vs. Opportunity Cost Segregation**:
   - Realized Historical Loss: ₹73,062.28 (direct downtime, scrap, rework, emergency labor, energy).
   - Baseline Opportunity Cost: ₹24,320.00 (projected lost throughput under baseline degradation).
   - Gross Exposure: ₹97,382.28.
   - Counterfactual Avoided Opportunity Cost: ₹19,520.00 under proactive bearing intervention.
   - Counterfactual Remaining Gross Exposure: ₹77,862.28.
   - All financial responses explicitly report `epistemic_status="FINANCIAL_SUMMARY_SEGREGATED"`.

3. **Simulation Diagnostic Guardrail**:
   - What-if digital twin simulations strictly maintain `"NOT_PROJECTABLE"` for causal health score and RUL projections under hypothetical intervention, preserving Phase 16 epistemic integrity.

4. **Inventory Contract Guardrail**:
   - Machine M2 spindle bearing (`SKU_SPINDLE_BEARING_M2`) authoritative values:
     - `observed_current_stock = 2.0`
     - `safety_stock = 1.134`
     - `reorder_point = 1.367`
     - `lead_time_mean_days = 7.0`
   - Current stock (2.0) > ROP (1.367) > SS (1.134); no current-stockout claim permitted.
