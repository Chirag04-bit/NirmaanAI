# NirmaanAI Relational Schema Reference (Phase 17)

## 1. Schema Overview

The relational schema comprises **19 authoritative tables** organized into three domains:
1. **Core Factory & Physical Plant** (`factories`, `machines`, `sensors`, `products`)
2. **Operations & Telemetry** (`production_jobs`, `sensor_readings`, `machine_telemetry_snapshots`, `maintenance_records`, `inventory_items`)
3. **AI & Decision Intelligence** (`ai_pdm_predictions`, `ai_anomaly_results`, `ai_bottleneck_results`, `ai_forecasting_results`, `ai_shap_explanations`, `ai_rca_results`, `ai_factory_health_scores`, `finance_loss_records`, `ai_recommendations`, `simulation_scenarios`)

---

## 2. Table Specifications

### 2.1 Core Factory Tables

#### `factories`
- `factory_id` (VARCHAR(50), PK)
- `factory_code` (VARCHAR(30), UNIQUE, INDEX)
- `name` (VARCHAR(100))
- `location` (VARCHAR(150))
- `industry` (VARCHAR(100))
- `created_at`, `updated_at` (TIMESTAMPTZ)

#### `machines`
- `machine_id` (VARCHAR(50), PK)
- `factory_id` (VARCHAR(50), FK -> `factories.factory_id` ON DELETE CASCADE, INDEX)
- `machine_code` (VARCHAR(50))
- `machine_name` (VARCHAR(100))
- `machine_type` (VARCHAR(50))
- `station` (VARCHAR(50))
- `line_id` (VARCHAR(50))
- `design_cycle_time_sec` (FLOAT)
- `baseline_power_kw` (FLOAT)
- `baseline_vibration_mms` (FLOAT)
- `alert_vibration_mms` (FLOAT)
- `critical_vibration_mms` (FLOAT)
- `rated_capacity_units_per_hour` (FLOAT)
- `status` (VARCHAR(30))
- `installation_year` (INTEGER, NULLABLE)
- **Constraint**: `chk_machine_vibration_order` (`critical_vibration_mms > alert_vibration_mms`)
- **Index**: `idx_machine_factory_status` (`factory_id`, `status`)

#### `sensors`
- `sensor_id` (VARCHAR(50), PK)
- `machine_id` (VARCHAR(50), FK -> `machines.machine_id` ON DELETE CASCADE, INDEX)
- `sensor_code` (VARCHAR(50))
- `sensor_type` (VARCHAR(50): VIBRATION, TEMPERATURE, POWER, etc.)
- `unit` (VARCHAR(20))
- `sampling_interval` (FLOAT)

#### `products`
- `product_id` (VARCHAR(50), PK)
- `sku_code` (VARCHAR(50), UNIQUE, INDEX)
- `name` (VARCHAR(100))
- `category` (VARCHAR(50))
- `unit_of_measure` (VARCHAR(20))
- `unit_cost_inr` (FLOAT)

---

### 2.2 Operational & Telemetry Tables

#### `sensor_readings` (Narrow Normalized Time-Series)
- `reading_id` (INTEGER, PK, AUTOINCREMENT)
- `sensor_id` (VARCHAR(50), FK -> `sensors.sensor_id` ON DELETE CASCADE, INDEX)
- `machine_id` (VARCHAR(50), FK -> `machines.machine_id` ON DELETE CASCADE, INDEX)
- `timestamp` (TIMESTAMPTZ)
- `value` (FLOAT)
- `quality_flag` (VARCHAR(20), DEFAULT 'GOOD')
- `source` (VARCHAR(50), DEFAULT 'PLC_SCADA')
- **Indexes**:
  - `idx_reading_sensor_time` (`sensor_id`, `timestamp`)
  - `idx_reading_machine_time` (`machine_id`, `timestamp`)

#### `machine_telemetry_snapshots` (Wide Telemetry)
- `snapshot_id` (INTEGER, PK, AUTOINCREMENT)
- `machine_id` (VARCHAR(50), FK -> `machines.machine_id` ON DELETE CASCADE, INDEX)
- `timestamp` (TIMESTAMPTZ)
- `vibration_mms` (FLOAT)
- `temperature_c` (FLOAT)
- `ambient_temperature_c`, `rotational_speed_rpm`, `torque_nm`, `sound_db`, `power_consumption_kw`, `oil_level_pct`, `coolant_level_pct`, `tool_wear_min`
- **Index**: `idx_telemetry_machine_time` (`machine_id`, `timestamp`)

#### `maintenance_records`
- `maintenance_id` (VARCHAR(50), PK)
- `machine_id` (VARCHAR(50), FK -> `machines.machine_id` ON DELETE CASCADE, INDEX)
- `maintenance_type` (VARCHAR(50))
- `failure_mode` (VARCHAR(50))
- `timestamp` (TIMESTAMPTZ)
- `duration_minutes` (FLOAT)
- `reason` (VARCHAR(255))
- `technician` (VARCHAR(100))
- `status` (VARCHAR(30))
- `notes` (TEXT)
- `is_decision_input` (BOOLEAN): `True` for events $\le$ 2026-01-21T12:00:00Z; `False` for future events.
- `epistemic_status` (VARCHAR(60)): Explicitly `RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH` for Day 22 `MAINT_0003`.
- **Indexes**:
  - `idx_maint_machine_time` (`machine_id`, `timestamp`)
  - `idx_maint_decision_input` (`machine_id`, `is_decision_input`)

#### `inventory_items`
- `inventory_id` (VARCHAR(50), PK)
- `factory_id` (VARCHAR(50), FK -> `factories.factory_id` ON DELETE CASCADE, INDEX)
- `sku_id` (VARCHAR(50), UNIQUE, INDEX)
- `item_name` (VARCHAR(100))
- `category` (VARCHAR(50))
- `current_stock` (FLOAT)
- `safety_stock` (FLOAT)
- `reorder_point` (FLOAT)
- `lead_time_days` (FLOAT)
- `unit_cost_inr` (FLOAT)
- `reorder_quantity` (FLOAT)
- `unit_of_measure` (VARCHAR(20))
- **Authoritative Phase 10 Contract**:
  - `SKU_SPINDLE_BEARING_M2`: `current_stock = 2.0`, `safety_stock = 1.134`, `reorder_point = 1.367`, `lead_time_days = 7.0`
- **Constraints**: Non-negative stock and cost bounds (`current_stock >= 0`, etc.)

---

### 2.3 AI & Decision Persistence Tables

| Table Name | Phase | Key Stored Fields | Locked Upstream Contract |
| :--- | :--- | :--- | :--- |
| `ai_pdm_predictions` | Phase 6 | `failure_probability`, `prediction_class`, `threshold`, `model_name` | Operational threshold = 0.91 (XGBoost) |
| `ai_anomaly_results` | Phase 7 | `anomaly_score`, `threshold`, `anomaly_status`, `detector_name` | PCA threshold = 0.24050 |
| `ai_bottleneck_results` | Phase 8 | `bottleneck_status`, `bottleneck_probability`, `target_metric` | Target = cycle time ratio |
| `ai_forecasting_results` | Phase 9 | `target_series`, `horizon_hours`, `predicted_value`, `actual_value` | 24-hour ahead production & energy |
| `ai_shap_explanations` | Phase 11 | `feature_name`, `feature_value`, `shap_value`, `ranking`, `context_type` | Normalized feature attribution values |
| `ai_rca_results` | Phase 12 | `primary_cause`, `cause_score`, `severity`, `evidence_strength` | Structured Bayesian root cause findings |
| `ai_factory_health_scores` | Phase 13 | `health_score`, `health_state`, `vibration_health`, `temperature_health` | Locked bands: EXCELLENT (90-100), HEALTHY (75-89), WATCH (60-74), DEGRADED (40-59), CRITICAL (0-39) |
| `finance_loss_records` | Phase 14 | `loss_type`, `downtime_loss_inr`, `scrap_loss_inr`, `opportunity_cost_inr`, `total_loss_inr` | Strict separation: REALIZED_LOSS (₹73,062.28) vs PROJECTED_OPPORTUNITY_COST (₹19,520) |
| `ai_recommendations` | Phase 15 | `category`, `action`, `priority`, `urgency`, `evidence_strength`, `rationale` | Preserves closed 26-action taxonomy |
| `simulation_scenarios` | Phase 16 | `scenario_id`, `decision_cutoff`, `intervention_list`, `projected_metrics`, `financial_projection` | Cutoff: 2026-01-21T12:00:00Z; Avoided breakdown loss: ₹9,420; Diagnostic KPIs = NOT_PROJECTABLE |
