# NIRMAANAI — PHASE 17 HANDOFF REPORT
**PostgreSQL Persistence Layer & Production Data Modeling**

============================================================
### 1. WHAT WAS IMPLEMENTED
============================================================
- **SQLAlchemy 2.0 ORM Architecture**: Declarative base with `TimestampMixin` and `ProvenanceMixin` under `src/db/`.
- **19 Database Tables**:
  - Plant physical hierarchy: `factories`, `machines`
  - Sensor & telemetry time-series: `sensors`, `sensor_readings`, `machine_telemetry_snapshots`
  - Operations & maintenance: `products`, `production_jobs`, `maintenance_records`, `inventory_items`
  - AI intelligence subsystems: `ai_pdm_predictions`, `ai_anomaly_results`, `ai_bottleneck_results`, `ai_forecasting_results`, `ai_shap_explanations`, `ai_rca_results`, `ai_factory_health_scores`
  - Financial accounting: `finance_loss_records`
  - Operational decision support: `ai_recommendations`, `simulation_scenarios`
- **Alembic Database Migrations**: Revision `49835d070f24_initial_schema.py` defining initial schema creation, indexes, foreign keys, and downgrades.
- **Deterministic Transactional Seeder**: `src/db/seeders/deterministic_seeder.py` populating baseline data reproducibly without external dataset mutation.
- **Database Connection & Session Management**: `src/db/config.py` and `src/db/session.py` with URL normalization, connection pooling, and credential masking.

============================================================
### 2. WHAT WAS VERIFIED
============================================================
- **ORM Models & Metadata**: All 19 tables verified in `Base.metadata.tables` with proper foreign keys, cascade rules, and compound indexes.
- **Provenance Integrity**: AI output tables strictly persist `source`, `dataset_version`, `model_name`, `model_version`, `pipeline_version`, `as_of_timestamp`, `provenance`, and `epistemic_status`.
- **Temporal Boundary**: `DECISION_CUTOFF = 2026-01-21T12:00:00Z`. Synthetic post-cutoff failure `MAINT_0003` (`2026-01-22T16:30:00Z`) is tagged with `is_decision_input=False` and `epistemic_status="RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"`, preventing prospective decision-state contamination.
- **Financial Segregation**: Machine M2 financial fields strictly separate:
  - Realized historical loss: ₹73,062.28
  - Baseline projected opportunity cost: ₹24,320.00
  - Gross baseline financial exposure: ₹97,382.28
  - Counterfactual avoided opportunity cost: ₹19,520.00
  - Counterfactual remaining opportunity cost: ₹4,800.00
  - Counterfactual remaining gross exposure: ₹77,862.28
  - Obsolete estimate ₹92,582.28 is completely rejected.
- **Simulation Persistence**: Diagnostic KPIs under hypothetical intervention remain `"NOT_PROJECTABLE"`.
- **Inventory Contract**: Machine M2 spindle bearing (`SKU_SPINDLE_BEARING_M2`) stock = 2.0 > ROP (1.367) > SS (1.134); no current-stockout claim.

============================================================
### 3. WHAT WAS NOT VERIFIED
============================================================
- **Live Remote/Local PostgreSQL Execution**: Live execution of migrations, table creation, and transactions against a running PostgreSQL server daemon was **NOT VERIFIED**.

============================================================
### 4. WHY POSTGRESQL REMAINS UNVERIFIED
============================================================
- PostgreSQL server software is not installed on this Windows host.
- No PostgreSQL Windows service is registered (`Get-Service *postgres*, *pgsql*` returns empty).
- `psql.exe` and `postgres.exe` are not present in PATH or standard system directories.
- TCP port 5432 on localhost has no listener.
- Docker daemon is not installed on the host.
- WSL has no Linux distribution configured.

============================================================
### 5. EXACT TEST COUNTS
============================================================
- **Targeted Database Tests (`tests/test_database.py`)**:
  - **20 PASSED**
  - **1 SKIPPED** (`test_postgresql_live_integration`)
  - **0 FAILED**
- **Full Project Regression (`pytest tests/ -q`)**:
  - **293 PASSED**
  - **1 SKIPPED**
  - **0 FAILED**

============================================================
### 6. ENVIRONMENT LIMITATION
============================================================
- The local execution environment provides Python 3.14.6 with `psycopg 3.3.5` and `SQLAlchemy 2.0.44`, but lacks a running PostgreSQL server daemon or container runtime.
- Verification relied on SQLite in-memory engines (`sqlite://`) with `StaticPool` for unit testing and dialect-level SQL validation for PostgreSQL.

============================================================
### 7. INSTRUCTIONS FOR FUTURE LIVE POSTGRESQL VERIFICATION
============================================================
When a PostgreSQL instance becomes available (via Docker or local install):
1. Start PostgreSQL on port 5432:
   ```bash
   docker run -d --name nirmaanai-postgres -e POSTGRES_DB=nirmaanai -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16-alpine
   ```
2. Configure `.env` in the project root:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/nirmaanai
   ```
3. Run Alembic migrations:
   ```bash
   alembic upgrade head
   ```
4. Run the deterministic seeder:
   ```bash
   python -m src.db.seeders.deterministic_seeder
   ```
5. Run the live PostgreSQL test suite:
   ```bash
   pytest tests/test_database.py -v
   ```

============================================================
### 8. CONFIRMATION OF UPSTREAM INTEGRITY
============================================================
- Phases 0–16 remain strictly untouched and immutable.
- External source dataset `C:\Users\user\OneDrive\Desktop\NIRMAAN\DATASET` is untouched.
- `operational_losses.csv` MD5 checksum remains `34B12582B32D81E3121429C55EBF74E8`.

============================================================
### 9. PHASE 19 STATUS
============================================================
- **PHASE 19 HAS NOT BEEN STARTED.**

============================================================
### 10. CURRENT PHASE 17 VERDICT
============================================================
- **IMPLEMENTATION**: **VERIFIED**
- **LIVE POSTGRESQL**: **NOT VERIFIED**
- **VERDICT**: **HOLD — ENVIRONMENT BLOCKED**
