# NirmaanAI Database Architecture (Phase 17)

## 1. Overview & System Boundary

The **NirmaanAI Production Persistence Layer** provides enterprise-grade, relational data persistence for physical plant entities, continuous operational telemetry, analytical workflows, and AI decision outputs from Phases 6 through 16.

```
       +-------------------------------------------------------------+
       |                  NirmaanAI Core Platform                    |
       |  (Phases 6-16: PdM, Anomaly, Flow, Forecast, Health, Loss) |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               SQLAlchemy 2.x ORM / Session Layer            |
       |    - Connection pooling & health checks                     |
       |    - Dialect normalization (postgresql+psycopg)             |
       |    - Research provenance & UTC timestamp mixins             |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |              PostgreSQL 15+ Enterprise Schema               |
       |  +--------------------+  +-------------------------------+  |
       |  | Physical Plant &   |  | Operational Time-Series &     |  |
       |  | Hierarchy (4 tbls) |  | Maintenance (5 tbls)          |  |
       |  +--------------------+  +-------------------------------+  |
       |  +--------------------+  +-------------------------------+  |
       |  | AI & Decision      |  | Finance & Simulation          |  |
       |  | Outputs (6 tbls)   |  | Scenarios (4 tbls)            |  |
       |  +--------------------+  +-------------------------------+  |
       +-------------------------------------------------------------+
```

### Architectural Principles
1. **Persistence, Not Replacement**: The database is a durable storage and query layer. It does not replace or alter the validated analytical engines (Phases 6–16).
2. **Epistemic & Provenance Tracking**: Every persisted AI record answers *where did this number come from?* via standardized metadata (`source`, `model_name`, `model_version`, `as_of_timestamp`, `provenance`, `epistemic_status`).
3. **Temporal Causality**: Preserves the absolute boundary between `DECISION_TIME_INPUT` ($\le$ 2026-01-21T12:00:00Z) and `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH` (Day 22 `MAINT_0003`).
4. **Authoritative Contracts**: Inventory contracts from Phase 10 (`ROP = 1.367`, `SS = 1.134`, `current_stock = 2.0`) are permanently preserved.
5. **Phase 18 Boundary**: No FastAPI endpoints, routers, or REST interfaces are created in Phase 17. The DB layer exposes clean Python ORM abstractions ready for Phase 18 consumption.

---

## 2. Directory Organization

```
src/db/
├── __init__.py           # Unified module interface
├── config.py             # DatabaseConfig, URL normalization, credential masking
├── base.py               # DeclarativeBase, TimestampMixin, ProvenanceMixin
├── session.py            # Engine initialization, pooling, and session management
├── models/
│   ├── __init__.py       # Model registry export
│   ├── factory.py        # Factory, Machine, Sensor, Product
│   ├── operations.py     # ProductionJob, SensorReading, MachineTelemetrySnapshot,
│   │                     # MaintenanceRecord, InventoryItem
│   └── ai_outputs.py     # PredictiveMaintenancePrediction, AnomalyDetectionResult,
│                         # BottleneckPredictionResult, ForecastingResult,
│                         # ShapExplanation, RcaResult, FactoryHealthScore,
│                         # FinancialLossRecord, OperationalRecommendation,
│                         # SimulationScenario
└── seed/
    ├── __init__.py
    └── seeder.py         # Deterministic importer for synthetic datasets & models
```

---

## 3. Database Connection & Pooling Architecture

- **Driver**: `psycopg` (psycopg 3) with binary wheels, configured via `postgresql+psycopg://`.
- **Pool Management**:
  - `DB_POOL_SIZE`: 5 persistent worker connections.
  - `DB_MAX_OVERFLOW`: 10 burst connections.
  - `DB_POOL_TIMEOUT_SECONDS`: 30s connection acquisition timeout.
  - `DB_POOL_RECYCLE_SECONDS`: 1800s (30 min) connection recycling to prevent stale pool drops.
  - `pool_pre_ping=True`: Active connection liveness validation prior to checkout.
- **Credential Protection**: `DatabaseConfig.get_masked_url()` guarantees that passwords never appear in log streams, exceptions, or console output.
