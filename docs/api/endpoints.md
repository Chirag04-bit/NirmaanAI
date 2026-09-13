# NirmaanAI Phase 18 — API Endpoints Reference Specification

**Base URL**: `/api/v1`  
**API Version**: `0.18.0`  
**OpenAPI Interactive UI**: `/docs` (Swagger), `/redoc` (ReDoc)  
**Total Registered Endpoints**: 38

---

## 1. System & Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | API Root information and documentation links |
| `GET` | `/health` | System liveness and DB connectivity check |
| `GET` | `/api/v1/health` | Subsystem status verification |

---

## 2. Factory Hierarchy & Physical Assets

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/factories` | List all factories with machine counts |
| `GET` | `/api/v1/factories/{factory_id}` | Get factory details by ID |
| `GET` | `/api/v1/factories/{factory_id}/overview` | Aggregated factory operational overview |
| `GET` | `/api/v1/machines` | List machines (filterable by factory_id, status) |
| `GET` | `/api/v1/machines/{machine_id}` | Get detailed machine specifications |
| `GET` | `/api/v1/machines/{machine_id}/overview` | Machine high-level status (health, anomaly, recs) |

---

## 3. Telemetry & Sensor Readings

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/sensors` | List sensor definitions (filterable by machine_id) |
| `GET` | `/api/v1/machines/{machine_id}/telemetry` | Time-windowed telemetry query (bounded, default 24h) |
| `GET` | `/api/v1/machines/{machine_id}/telemetry/latest` | Latest telemetry snapshot across all sensors |

---

## 4. Production & Manufacturing Jobs

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/production/jobs` | Paginated production jobs (filterable by status) |
| `GET` | `/api/v1/machines/{machine_id}/production-jobs` | Production jobs scheduled or run on a specific machine |

---

## 5. Maintenance & Temporal Ground Truth

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/maintenance/records` | Maintenance log records (default excludes post-cutoff ground truth) |
| `GET` | `/api/v1/maintenance/records/{record_id}` | Single maintenance event record |
| `GET` | `/api/v1/machines/{machine_id}/maintenance` | Maintenance history for a specific machine |

> **Temporal Isolation Parameter**:
> `include_retrospective=true` must be explicitly passed to inspect post-cutoff ground truth (`MAINT_0003`).

---

## 6. Inventory & Spare Parts (Phase 10 Contracts)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/inventory` | Paginated spare parts and consumables catalog |
| `GET` | `/api/v1/inventory/{sku}` | Authoritative SKU details (stock, safety stock, ROP) |
| `GET` | `/api/v1/machines/{machine_id}/inventory` | Critical spares coupled to machine (e.g. M2 Spindle Bearing) |

---

## 7. AI & Predictive Intelligence Subsystems

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/ai/predictive-maintenance` | List predictive maintenance predictions (RUL, failure prob) |
| `GET` | `/api/v1/machines/{machine_id}/pdm` | Predictive maintenance predictions for a specific machine |
| `GET` | `/api/v1/ai/anomalies` | Multi-detector anomaly events (Vibration, Isolation Forest, etc.) |
| `GET` | `/api/v1/machines/{machine_id}/anomalies` | Detected anomalies on a specific machine |
| `GET` | `/api/v1/ai/bottlenecks` | Bottleneck risk predictions across workstations |
| `GET` | `/api/v1/ai/forecasting` | Temporal demand and sensor forecasting results |
| `GET` | `/api/v1/ai/shap` | SHAP feature attribution rankings |
| `GET` | `/api/v1/ai/shap/{machine_id}` | Feature attributions explaining machine failure risk |
| `GET` | `/api/v1/ai/rca` | Root Cause Analysis diagnostic evaluations |
| `GET` | `/api/v1/ai/rca/{machine_id}` | Root Cause Analysis diagnoses for a specific machine |
| `GET` | `/api/v1/ai/health-scores` | Composite health scores and health bands across assets |
| `GET` | `/api/v1/machines/{machine_id}/health` | Authoritative health score and health band for a machine |

---

## 8. Financial Loss Accounting (Strict Segregation)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/finance/losses` | Granular financial loss records across categories |
| `GET` | `/api/v1/finance/summary` | Fleet-wide segregated financial loss breakdown |
| `GET` | `/api/v1/machines/{machine_id}/finance` | Machine-specific segregated financial summary |

---

## 9. Operational Recommendations & Simulation

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/recommendations` | List operational recommendations (closed 26-action taxonomy) |
| `GET` | `/api/v1/recommendations/{rec_id}` | Recommendation details with evidence and financial justification |
| `GET` | `/api/v1/machines/{machine_id}/recommendations` | Machine-specific operational recommendations sorted by priority |
| `GET` | `/api/v1/simulations` | List What-If digital twin scenarios |
| `GET` | `/api/v1/simulations/{scenario_id}` | Scenario details (avoided cost, unprojectable diagnostic KPIs) |
