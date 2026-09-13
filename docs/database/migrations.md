# NirmaanAI Alembic Database Migrations Guide (Phase 17)

## 1. Overview & Setup

NirmaanAI uses **Alembic** alongside **SQLAlchemy 2.x** for version-controlled, reproducible schema migrations. Schema creation and evolution is strictly managed through Python migration scripts rather than manual SQL execution.

### Migration Files & Hierarchy
```
alembic.ini                         # Root Alembic configuration
alembic/
├── env.py                          # Migration harness binding Base.metadata and dynamic URLs
├── README                          # Standard Alembic documentation
├── script.py.mako                  # Template for new revision files
└── versions/
    └── 49835d070f24_initial_schema.py # Phase 17 authoritative initial migration (19 tables)
```

---

## 2. Dynamic Database URL Resolution

In `alembic/env.py`, the database connection string is resolved dynamically:
1. Environment variable `DATABASE_URL` (e.g. `postgresql+psycopg://user:pass@localhost:5432/nirmaanai`)
2. Normalization: Automatically rewrites `postgres://` or `postgresql://` to `postgresql+psycopg://` for modern driver compatibility.
3. Fallback: Safe fallback to SQLite file for offline DDL verification without requiring live server access.

---

## 3. Migration Commands

### 3.1 Applying Migrations Online
To upgrade an active database instance to the latest migration head:
```powershell
python -m alembic upgrade head
```

### 3.2 Generating Offline SQL Scripts
To inspect raw DDL without connecting to a live database:
```powershell
python -m alembic upgrade head --sql
```

### 3.3 Creating Future Revisions
```powershell
python -m alembic revision --autogenerate -m "description_of_change"
```

### 3.4 Downgrading / Rollback
```powershell
python -m alembic downgrade -1
```

---

## 4. Verification & Testing

The Phase 17 test suite verifies migration integrity via:
- [`test_alembic_migration_reproducibility`](file:///c:/NIRMAAN%20AI/tests/test_database.py#L580-L588): Validates that migration scripts and heads exist and are free from parse errors.
