# NirmaanAI Database Seeding & Data Ingestion Strategy (Phase 17)

## 1. Principles of Data Ingestion

The NirmaanAI database seeder (`DatabaseSeeder` in `src/db/seed/seeder.py`) is designed around strict research principles:
1. **Source Data Immutability**: Source datasets under `DATASET/` are treated as strictly **READ-ONLY**. The seeder never modifies, rewrites, or regenerates baseline CSV or Parquet files.
2. **Authoritative Inventory Integrity**: Preserves the locked Phase 10 inventory values for `SKU_SPINDLE_BEARING_M2`:
   - `current_stock = 2.0`
   - `safety_stock = 1.134`
   - `reorder_point = 1.367`
   - `lead_time_days = 7.0`
3. **Temporal Counterfactual Semantics**:
   - `DECISION_CUTOFF`: `2026-01-21T12:00:00Z`
   - Events on or prior to cutoff are marked `is_decision_input = True`, `epistemic_status = "OBSERVED"`.
   - The Day-22 catastrophic failure event `MAINT_0003` (`2026-01-22T16:30:00Z`) is explicitly seeded with `is_decision_input = False` and `epistemic_status = "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"`.
4. **Determinism**: Seeding produces identical record states across environments.

---

## 2. Ingestion Pipeline Sequence

The seeder operates within a single transactional boundary in strict foreign key order:

```
[1. Factory & Machines]
      |---> FACT_LINE_01 + M1, M2, M3, M4, M5 (from machines.csv)
[2. Physical Sensors]
      |---> 25 multi-channel sensors (Vibration, Temp, Power, Speed, Torque)
[3. Products & Catalog]
      |---> 5 standard manufactured SKUs
[4. Inventory Intelligence]
      |---> 5 inventory items, enforcing ROP 1.367 for M2 Spindle Bearing
[5. Maintenance History]
      |---> 4 maintenance records, isolating MAINT_0003 to retrospective ground truth
[6. Production Jobs]
      |---> Sample production batch jobs from production_jobs.csv
[7. Sensor Telemetry]
      |---> Normalized time-series + multi-channel snapshots
[8. AI & Decision Outputs (Phases 6-16)]
      |---> PdM (0.91 threshold), Anomaly (0.24050 PCA threshold)
      |---> Bottleneck, Forecasting, SHAP, RCA
      |---> Factory Health Score (CRITICAL 26.88 for M2 on Jan 21)
      |---> Financial Loss (Realized ₹73,062.28 vs Opportunity Cost ₹19,520)
      |---> Recommendations (Closed 26-action taxonomy)
      |---> Simulation Scenarios (Avoided ₹9,420; NOT_PROJECTABLE diagnostic KPIs)
```

---

## 3. Usage

### Programmatic Seeding
```python
import src.db as db
from src.db.seed.seeder import DatabaseSeeder

engine = db.get_engine()
with db.get_db_session(engine) as session:
    seeder = DatabaseSeeder(session)
    counts = seeder.seed_all()
    print("Seeded successfully:", counts)
```
