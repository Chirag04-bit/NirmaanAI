# NirmaanAI Database Testing Guide (Phase 17)

## 1. Testing Philosophy & Test Separation

The Phase 17 test harness (`tests/test_database.py`) strictly separates **Unit Tests** from **Live PostgreSQL Integration Tests**:

1. **Unit Tests (Offline & Memory-Isolated)**:
   - Run in-memory via SQLite (`sqlite:///:memory:`) and SQLAlchemy schema DDL compilers.
   - Do NOT require a running PostgreSQL daemon.
   - Verify table structure, foreign keys, cascade rules, multi-column indexes, check constraints, seeder execution, AI output fidelity, provenance, and temporal integrity.
2. **Live Integration Tests**:
   - Gated with `@pytest.mark.skipif(not is_postgres_available(), ...)`.
   - If PostgreSQL is reachable at `DATABASE_URL`, exercises live transactions and queries against the PostgreSQL engine.
   - If PostgreSQL is unavailable, cleanly skips with an explicit reason rather than failing or silently masking errors.

---

## 2. Test Suites & Coverage Matrix

| Test Suite | Function | Target Area |
| :--- | :--- | :--- |
| **Config** | `test_database_config_valid_and_normalization` | Driver mapping (`postgresql+psycopg`), credentials masking |
| **Config** | `test_database_config_missing_raises_clean_error` | Missing `DATABASE_URL` error handling |
| **Schema** | `test_schema_tables_and_metadata_completeness` | All 19 required tables in `Base.metadata` |
| **Schema** | `test_schema_table_primary_and_foreign_keys` | Foreign keys, cascade rules |
| **Schema** | `test_schema_indexes_telemetry_and_maintenance` | Multi-column indexes on telemetry & maintenance |
| **Schema** | `test_schema_required_columns_audit` | Column presence across domain entities |
| **CRUD** | `test_crud_factory_and_machines` | Factory/Machine relationship lifecycle |
| **CRUD** | `test_crud_sensor_and_readings` | Sensor readings time-series |
| **CRUD** | `test_crud_production_jobs` | Production job tracking |
| **CRUD** | `test_crud_inventory_contract` | Authoritative inventory contract (`ROP = 1.367`, `SS = 1.134`, `Stock = 2.0`) |
| **AI Persistence** | `test_ai_outputs_persistence_roundtrip` | Phases 6, 7, 13, 14, 15, 16 round-trip persistence |
| **AI Persistence** | `test_ai_individual_subsystems_persistence` | Phases 8 (Bottleneck), 9 (Forecast), 11 (SHAP), 12 (RCA) |
| **Temporal** | `test_temporal_integrity_decision_time_vs_day22_ground_truth` | Cutoff 2026-01-21T12:00:00Z vs Day 22 `MAINT_0003` ground truth |
| **Seeder** | `test_deterministic_database_seeder` | Deterministic import pipeline |
| **Integrity** | `test_upstream_operational_losses_md5_immutable` | MD5 validation of `operational_losses.csv` |
| **Migrations** | `test_alembic_migration_reproducibility` | Alembic revision and head script validation |
| **Integration** | `test_postgresql_live_integration` | Live PostgreSQL connectivity (cleanly skipped if offline) |

---

## 3. Running the Tests

### 3.1 Running Phase 17 Targeted Tests
```powershell
C:\Python314\python.exe -m pytest tests/test_database.py -v
```

### 3.2 Running Full System Regression
```powershell
C:\Python314\python.exe -m pytest tests/ -q
```
