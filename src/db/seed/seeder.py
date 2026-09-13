"""
NirmaanAI Deterministic Database Seeder & Data Importer (Phase 17)
Imports immutable synthetic datasets and model output summaries into PostgreSQL
while strictly preserving research provenance, authoritative inventory values (ROP 1.367),
and temporal counterfactual semantics.
"""

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.factory import Factory, Machine, Product, Sensor
from src.db.models.operations import (
    InventoryItem,
    MachineTelemetrySnapshot,
    MaintenanceRecord,
    ProductionJob,
    SensorReading,
)
from src.db.models.ai_outputs import (
    AnomalyDetectionResult,
    BottleneckPredictionResult,
    FactoryHealthScore,
    FinancialLossRecord,
    ForecastingResult,
    OperationalRecommendation,
    PredictiveMaintenancePrediction,
    RcaResult,
    ShapExplanation,
    SimulationScenario,
)
from src.utils.config_loader import get_project_root

ROOT = get_project_root()
DATASET_SYNTHETIC = ROOT / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic"
MODELS_DIR = ROOT / "models"

DECISION_CUTOFF = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)


class DatabaseSeeder:
    """Orchestrates deterministic import of factory data and AI outputs."""

    def __init__(self, session: Session):
        self.session = session

    def seed_all(self, telemetry_sample_limit: int = 50, jobs_sample_limit: int = 50) -> Dict[str, int]:
        """Seeds all domains in proper dependency order within a transaction."""
        counts = {}
        counts["factories"] = self.seed_factory()
        counts["machines"] = self.seed_machines()
        counts["sensors"] = self.seed_sensors()
        counts["products"] = self.seed_products()
        counts["inventory"] = self.seed_inventory()
        counts["maintenance"] = self.seed_maintenance()
        counts["production_jobs"] = self.seed_production_jobs(limit=jobs_sample_limit)
        counts["telemetry"] = self.seed_telemetry(limit=telemetry_sample_limit)
        counts["ai_pdm"] = self.seed_pdm_predictions()
        counts["ai_anomaly"] = self.seed_anomaly_results()
        counts["ai_bottleneck"] = self.seed_bottleneck_results()
        counts["ai_forecasting"] = self.seed_forecasting_results()
        counts["ai_shap"] = self.seed_shap_explanations()
        counts["ai_rca"] = self.seed_rca_results()
        counts["ai_health"] = self.seed_factory_health()
        counts["ai_loss"] = self.seed_financial_loss()
        counts["ai_recommendations"] = self.seed_recommendations()
        counts["ai_simulation"] = self.seed_simulation_scenarios()
        self.session.flush()
        return counts

    def seed_factory(self) -> int:
        existing = self.session.scalar(select(Factory).where(Factory.factory_id == "FACT_LINE_01"))
        if not existing:
            factory = Factory(
                factory_id="FACT_LINE_01",
                factory_code="FAC_01",
                name="Nirmaan Smart Manufacturing Facility",
                location="Kolkata, West Bengal, India",
                industry="Precision CNC Machining & Textile Equipment",
            )
            self.session.add(factory)
            self.session.flush()
            return 1
        return 0

    def seed_machines(self) -> int:
        machines_csv = DATASET_SYNTHETIC / "machines.csv"
        if not machines_csv.exists():
            return 0

        count = 0
        with open(machines_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m_id = row["machine_id"].strip()
                if not self.session.scalar(select(Machine).where(Machine.machine_id == m_id)):
                    machine = Machine(
                        machine_id=m_id,
                        factory_id="FACT_LINE_01",
                        machine_code=f"MC_{m_id}",
                        machine_name=row["name"].strip(),
                        machine_type=row["machine_type"].strip(),
                        station=row.get("line_id", "LINE_01").strip(),
                        line_id=row.get("line_id", "LINE_01").strip(),
                        design_cycle_time_sec=float(row["design_cycle_time_sec"]),
                        baseline_power_kw=float(row["baseline_power_kw"]),
                        baseline_vibration_mms=float(row["baseline_vibration_mms"]),
                        alert_vibration_mms=float(row["alert_vibration_mms"]),
                        critical_vibration_mms=float(row["critical_vibration_mms"]),
                        rated_capacity_units_per_hour=float(row["rated_capacity_units_per_hour"]),
                        status=row["status"].strip(),
                        installation_year=int(row["installation_year"]) if row.get("installation_year") else 2021,
                    )
                    self.session.add(machine)
                    count += 1
        self.session.flush()
        return count

    def seed_sensors(self) -> int:
        machines = self.session.scalars(select(Machine)).all()
        count = 0
        sensor_types = [
            ("VIBRATION", "mm/s", 1.0),
            ("TEMPERATURE", "degC", 1.0),
            ("POWER", "kW", 1.0),
            ("ROTATIONAL_SPEED", "RPM", 1.0),
            ("TORQUE", "Nm", 1.0),
        ]
        for m in machines:
            for stype, unit, interval in sensor_types:
                s_id = f"SENS_{m.machine_id}_{stype}"
                if not self.session.scalar(select(Sensor).where(Sensor.sensor_id == s_id)):
                    sensor = Sensor(
                        sensor_id=s_id,
                        machine_id=m.machine_id,
                        sensor_code=f"S_{m.machine_id}_{stype[:3]}",
                        sensor_type=stype,
                        unit=unit,
                        sampling_interval=interval,
                    )
                    self.session.add(sensor)
                    count += 1
        self.session.flush()
        return count

    def seed_products(self) -> int:
        products_data = [
            ("PROD_01", "SKU_STEEL_BAR_20MM", "AISI 4140 Alloy Steel Round Bar 20mm", "RAW_MATERIAL", "kg", 95.0),
            ("PROD_02", "SKU_ALUM_BILLET_6061", "Aluminium 6061 Billet 100x100mm", "RAW_MATERIAL", "kg", 240.0),
            ("PROD_03", "SKU_SPINDLE_BEARING_M2", "Precision Angular Contact Spindle Bearing (M2)", "SPARE_PART", "units", 3200.0),
            ("PROD_04", "SKU_ENDMILL_CARBIDE_10MM", "Solid Carbide 4-Flute End Mill 10mm", "SPARE_PART", "units", 1450.0),
            ("PROD_05", "SKU_YARN_COTTON_30S", "Carded Cotton Yarn 30s Count (Textile Loom)", "RAW_MATERIAL", "kg", 280.0),
        ]
        count = 0
        for p_id, sku, name, cat, uom, cost in products_data:
            if not self.session.scalar(select(Product).where(Product.product_id == p_id)):
                product = Product(
                    product_id=p_id,
                    sku_code=sku,
                    name=name,
                    category=cat,
                    unit_of_measure=uom,
                    unit_cost_inr=cost,
                )
                self.session.add(product)
                count += 1
        self.session.flush()
        return count

    def seed_inventory(self) -> int:
        """
        Seeds inventory items.
        CRITICAL: For SKU_SPINDLE_BEARING_M2, authoritative Phase 10 values are preserved:
        current_stock = 2.0, safety_stock = 1.134, reorder_point = 1.367, lead_time_days = 7.0
        """
        inv_csv = DATASET_SYNTHETIC / "inventory_items.csv"
        if not inv_csv.exists():
            return 0

        count = 0
        with open(inv_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row["item_id"].strip()
                if not self.session.scalar(select(InventoryItem).where(InventoryItem.sku_id == sku)):
                    # Check for authoritative Phase 10 M2 Spindle Bearing override
                    if sku == "SKU_SPINDLE_BEARING_M2":
                        curr_stock = 2.0
                        safe_stock = 1.134
                        rop = 1.367
                        lt_days = 7.0
                    else:
                        curr_stock = float(row["current_stock"])
                        safe_stock = float(row["safety_stock"])
                        rop = float(row["reorder_quantity"])  # or default
                        lt_days = 7.0

                    inv = InventoryItem(
                        inventory_id=f"INV_{sku}",
                        factory_id="FACT_LINE_01",
                        sku_id=sku,
                        item_name=row["item_name"].strip(),
                        category=row["category"].strip(),
                        current_stock=curr_stock,
                        safety_stock=safe_stock,
                        reorder_point=rop,
                        lead_time_days=lt_days,
                        unit_cost_inr=float(row["unit_cost_inr"]),
                        reorder_quantity=float(row.get("reorder_quantity", 1.0)),
                        unit_of_measure=row.get("unit_of_measure", "units").strip(),
                    )
                    self.session.add(inv)
                    count += 1
        self.session.flush()
        return count

    def seed_maintenance(self) -> int:
        """
        Seeds maintenance records with strict temporal semantics:
        - Events <= 2026-01-21T12:00:00Z: is_decision_input = True, epistemic_status = OBSERVED
        - MAINT_0003 (Day 22): is_decision_input = False, epistemic_status = RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH
        """
        maint_csv = DATASET_SYNTHETIC / "maintenance_records.csv"
        if not maint_csv.exists():
            return 0

        count = 0
        with open(maint_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec_id = row["record_id"].strip()
                if not self.session.scalar(select(MaintenanceRecord).where(MaintenanceRecord.maintenance_id == rec_id)):
                    ts = datetime.fromisoformat(row["timestamp"].strip())
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)

                    is_pre_cutoff = ts <= DECISION_CUTOFF
                    if rec_id == "MAINT_0003":
                        epistemic = "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"
                        is_decision = False
                    else:
                        epistemic = "OBSERVED" if is_pre_cutoff else "FUTURE_EVENT_NOT_AVAILABLE_AT_DECISION"
                        is_decision = is_pre_cutoff

                    rec = MaintenanceRecord(
                        maintenance_id=rec_id,
                        machine_id=row["machine_id"].strip(),
                        maintenance_type=row["event_type"].strip(),
                        failure_mode=row.get("failure_mode", "NONE").strip(),
                        timestamp=ts,
                        duration_minutes=float(row["downtime_minutes"]),
                        reason=row.get("notes", "").strip()[:255],
                        technician=row.get("technician_id", "TECH_01").strip(),
                        status="COMPLETED",
                        notes=row.get("notes", "").strip(),
                        is_decision_input=is_decision,
                        epistemic_status=epistemic,
                    )
                    self.session.add(rec)
                    count += 1
        self.session.flush()
        return count

    def seed_production_jobs(self, limit: int = 50) -> int:
        jobs_csv = DATASET_SYNTHETIC / "production_jobs.csv"
        if not jobs_csv.exists():
            return 0

        count = 0
        with open(jobs_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                j_id = row["job_id"].strip()
                if not self.session.scalar(select(ProductionJob).where(ProductionJob.job_id == j_id)):
                    s_start = datetime.fromisoformat(row["scheduled_start"].strip())
                    s_end = datetime.fromisoformat(row["scheduled_end"].strip())
                    a_start = datetime.fromisoformat(row["actual_start"].strip()) if row.get("actual_start") else None
                    a_end = datetime.fromisoformat(row["actual_end"].strip()) if row.get("actual_end") else None

                    job = ProductionJob(
                        job_id=j_id,
                        factory_id="FACT_LINE_01",
                        machine_id=row["machine_id"].strip(),
                        product_id="PROD_01",
                        operation_type=row.get("operation_type", "Milling").strip(),
                        scheduled_start=s_start,
                        scheduled_end=s_end,
                        actual_start=a_start,
                        actual_end=a_end,
                        cycle_time=float(row["actual_cycle_time_sec"]) if row.get("actual_cycle_time_sec") else None,
                        quantity=int(row["batch_quantity"]),
                        completed_quantity=int(row.get("completed_quantity", 0)),
                        scrap_quantity=int(row.get("scrap_quantity", 0)),
                        status=row.get("status", "SCHEDULED").strip(),
                    )
                    self.session.add(job)
                    count += 1
        self.session.flush()
        return count

    def seed_telemetry(self, limit: int = 50) -> int:
        telemetry_csv = DATASET_SYNTHETIC / "sensor_readings.csv"
        if not telemetry_csv.exists():
            return 0

        count = 0
        with open(telemetry_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                r_id = int(row["reading_id"])
                m_id = row["machine_id"].strip()
                ts = datetime.fromisoformat(row["timestamp"].strip())
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)

                vib = float(row["vibration_mms"])
                temp = float(row["temperature_c"])
                power = float(row.get("power_consumption_kw", 0.0))

                snapshot = MachineTelemetrySnapshot(
                    snapshot_id=r_id,
                    machine_id=m_id,
                    timestamp=ts,
                    vibration_mms=vib,
                    temperature_c=temp,
                    ambient_temperature_c=float(row["ambient_temperature_c"]) if row.get("ambient_temperature_c") else None,
                    rotational_speed_rpm=float(row["rotational_speed_rpm"]) if row.get("rotational_speed_rpm") else None,
                    torque_nm=float(row["torque_nm"]) if row.get("torque_nm") else None,
                    sound_db=float(row["sound_db"]) if row.get("sound_db") else None,
                    power_consumption_kw=power,
                    oil_level_pct=float(row["oil_level_pct"]) if row.get("oil_level_pct") else None,
                    coolant_level_pct=float(row["coolant_level_pct"]) if row.get("coolant_level_pct") else None,
                    tool_wear_min=float(row["tool_wear_min"]) if row.get("tool_wear_min") else None,
                )
                self.session.add(snapshot)

                # Normalized reading for vibration channel
                reading = SensorReading(
                    reading_id=r_id,
                    sensor_id=f"SENS_{m_id}_VIBRATION",
                    machine_id=m_id,
                    timestamp=ts,
                    value=vib,
                    quality_flag="GOOD",
                    source="PLC_SCADA",
                )
                self.session.add(reading)
                count += 1
        self.session.flush()
        return count

    def seed_pdm_predictions(self) -> int:
        """Seeds Phase 6 Predictive Maintenance failure predictions with 0.91 threshold."""
        predictions_data = [
            ("M1", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.042, 0, 0.91),
            ("M2", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.946, 1, 0.91),  # Exceeds 0.91 threshold!
            ("M3", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.021, 0, 0.91),
            ("M4", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.015, 0, 0.91),
            ("M5", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.018, 0, 0.91),
        ]
        count = 0
        for m_id, ts, prob, pclass, thresh in predictions_data:
            pred = PredictiveMaintenancePrediction(
                machine_id=m_id,
                prediction_timestamp=ts,
                failure_probability=prob,
                prediction_class=pclass,
                threshold=thresh,
                source="PHASE_06_XGBOOST_MODEL",
                dataset_version="AI4I_2020_V1",
                model_name="xgboost_champion",
                model_version="champion_v1",
                pipeline_version="0.6.0",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="DERIVED_FROM_OBSERVED",
                epistemic_status="MODEL_INFERENCE",
            )
            self.session.add(pred)
            count += 1
        self.session.flush()
        return count

    def seed_anomaly_results(self) -> int:
        """Seeds Phase 7 Anomaly detection results with PCA threshold 0.24050."""
        anomaly_data = [
            ("M1", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.085, 0.24050, "NORMAL"),
            ("M2", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.582, 0.24050, "ANOMALOUS"),  # Exceeds threshold!
            ("M3", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.064, 0.24050, "NORMAL"),
            ("M4", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.041, 0.24050, "NORMAL"),
            ("M5", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 0.052, 0.24050, "NORMAL"),
        ]
        count = 0
        for m_id, ts, score, thresh, status in anomaly_data:
            res = AnomalyDetectionResult(
                machine_id=m_id,
                timestamp=ts,
                anomaly_score=score,
                threshold=thresh,
                detector_name="pca_detector",
                anomaly_status=status,
                source="PHASE_07_PCA_ANOMALY_ENGINE",
                dataset_version="SYNTHETIC_FACTORY_V1",
                model_name="pca_reconstruction_detector",
                model_version="v1.0",
                pipeline_version="0.7.0",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="DERIVED_FROM_OBSERVED",
                epistemic_status="STATISTICAL_INFERENCE",
            )
            self.session.add(res)
            count += 1
        self.session.flush()
        return count

    def seed_bottleneck_results(self) -> int:
        """Seeds Phase 8 Bottleneck predictions."""
        bottlenecks = [
            ("M1", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), "NORMAL", 0.12),
            ("M2", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), "BOTTLENECK", 0.88),
            ("M3", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), "NORMAL", 0.09),
            ("M4", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), "NORMAL", 0.05),
            ("M5", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), "NORMAL", 0.07),
        ]
        count = 0
        for m_id, ts, status, prob in bottlenecks:
            bn = BottleneckPredictionResult(
                machine_id=m_id,
                timestamp=ts,
                bottleneck_status=status,
                bottleneck_probability=prob,
                target_metric="cycle_time_ratio",
                source="PHASE_08_BOTTLENECK_PREDICTOR",
                dataset_version="SYNTHETIC_FACTORY_V1",
                model_name="random_forest_bottleneck",
                model_version="v1.0",
                pipeline_version="0.8.0",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="DERIVED_FROM_OBSERVED",
                epistemic_status="MODEL_INFERENCE",
            )
            self.session.add(bn)
            count += 1
        self.session.flush()
        return count

    def seed_forecasting_results(self) -> int:
        """Seeds Phase 9 24-hour ahead forecasts."""
        forecasts = [
            ("production_volume", datetime(2026, 1, 22, 12, 0, 0, tzinfo=timezone.utc), 24, 1420.0, 1380.0),
            ("energy_kwh", datetime(2026, 1, 22, 12, 0, 0, tzinfo=timezone.utc), 24, 3850.5, 3910.2),
        ]
        count = 0
        for target, ts, horizon, pred, act in forecasts:
            fc = ForecastingResult(
                target_series=target,
                forecast_timestamp=ts,
                horizon_hours=horizon,
                predicted_value=pred,
                actual_value=act,
                source="PHASE_09_PROPHET_FORECASTER",
                dataset_version="SYNTHETIC_FACTORY_V1",
                model_name="prophet_production_forecaster",
                model_version="v1.0",
                pipeline_version="0.9.0",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="DERIVED_FROM_OBSERVED",
                epistemic_status="TIME_SERIES_FORECAST",
            )
            self.session.add(fc)
            count += 1
        self.session.flush()
        return count

    def seed_shap_explanations(self) -> int:
        """Seeds Phase 11 SHAP feature attributions for Machine 2."""
        shap_items = [
            ("rotational_speed_rpm", 1493.0, 0.412, 1),
            ("torque_nm", 139.51, 0.354, 2),
            ("vibration_mms", 4.25, 0.288, 3),
            ("temperature_c", 68.4, 0.195, 4),
            ("tool_wear_min", 185.0, 0.142, 5),
        ]
        count = 0
        for feat, val, shap_val, rank in shap_items:
            exp = ShapExplanation(
                prediction_ref_id="PRED_M2_20260121_1200",
                machine_id="M2",
                feature_name=feat,
                feature_value=val,
                shap_value=shap_val,
                ranking=rank,
                context_type="LOCAL",
                model_name="xgboost_champion",
                model_version="champion_v1",
                as_of_timestamp=DECISION_CUTOFF,
            )
            self.session.add(exp)
            count += 1
        self.session.flush()
        return count

    def seed_rca_results(self) -> int:
        """Seeds Phase 12 Root Cause Analysis for Machine 2."""
        rca = RcaResult(
            rca_id="RCA_M2_20260121",
            machine_id="M2",
            event_timestamp=DECISION_CUTOFF,
            primary_cause="Lubrication starvation causing progressive angular contact spindle bearing wear",
            cause_score=0.92,
            severity="CRITICAL",
            evidence_strength="HIGH",
            evidence_details="Vibration RMS increased from 1.4 mm/s baseline to 4.25 mm/s; coolant & oil starvation observed.",
            source="PHASE_12_RCA_ENGINE",
            dataset_version="SYNTHETIC_FACTORY_V1",
            model_name="bayesian_rca_graph",
            model_version="v1.0",
            pipeline_version="0.12.0",
            as_of_timestamp=DECISION_CUTOFF,
            provenance="DERIVED_FROM_OBSERVED",
            epistemic_status="ROOT_CAUSE_DIAGNOSIS",
        )
        self.session.add(rca)
        self.session.flush()
        return 1

    def seed_factory_health(self) -> int:
        """
        Seeds Phase 13 Factory and Machine Health scores.
        Locked bands:
        90-100: EXCELLENT, 75-89: HEALTHY, 60-74: WATCH, 40-59: DEGRADED, 0-39: CRITICAL
        """
        health_scores = [
            ("M1", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 94.20, "EXCELLENT", 95.0, 92.0),
            ("M2", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 26.88, "CRITICAL", 22.0, 31.0),  # Authoritative Jan 21 CRITICAL!
            ("M3", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 88.50, "HEALTHY", 89.0, 87.0),
            ("M4", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 96.10, "EXCELLENT", 97.0, 95.0),
            ("M5", datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc), 91.80, "EXCELLENT", 92.0, 91.0),
        ]
        count = 0
        for m_id, ts, score, state, vib_h, temp_h in health_scores:
            hs = FactoryHealthScore(
                machine_id=m_id,
                factory_id="FACT_LINE_01",
                timestamp=ts,
                health_score=score,
                health_state=state,
                coverage_pct=100.0,
                vibration_health=vib_h,
                temperature_health=temp_h,
                cycle_efficiency_health=90.0,
                maintenance_health=85.0,
                diagnostic_modifier=1.0 if score > 50 else 0.85,
                source="PHASE_13_HEALTH_ENGINE",
                dataset_version="SYNTHETIC_FACTORY_V1",
                model_name="composite_health_scorer",
                model_version="v1.0",
                pipeline_version="0.13.0",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="DERIVED_FROM_OBSERVED",
                epistemic_status="COMPOSITE_INDEX",
            )
            self.session.add(hs)
            count += 1
        self.session.flush()
        return count

    def seed_financial_loss(self) -> int:
        """
        Seeds Phase 14 Financial Loss accounting records.
        Preserves strict separation between:
        - REALIZED_LOSS (M2: ₹73,062.28)
        - PROJECTED_OPPORTUNITY_COST (M2: ₹19,520.00)
        - GROSS_EXPOSURE (M2: ₹92,582.28)
        """
        losses = [
            ("M2", "REALIZED_LOSS", 150.0, 11250.0, 51800.0, 6475.0, 420.0, 3117.28, 0.0, 73062.28, "OBSERVED_HISTORICAL"),
            ("M2", "PROJECTED_OPPORTUNITY_COST", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 19520.0, 19520.0, "PROJECTED_OPPORTUNITY_COST"),
            ("M2", "GROSS_EXPOSURE", 150.0, 11250.0, 51800.0, 6475.0, 420.0, 3117.28, 19520.0, 92582.28, "AGGREGATE_BOUND"),
        ]
        count = 0
        for m_id, ltype, dt_min, dt_loss, scrap_loss, rew_loss, labor_loss, energy_loss, opp_loss, tot, epistemic in losses:
            rec = FinancialLossRecord(
                machine_id=m_id,
                timestamp=DECISION_CUTOFF,
                loss_type=ltype,
                downtime_minutes=dt_min,
                downtime_loss_inr=dt_loss,
                scrap_loss_inr=scrap_loss,
                rework_loss_inr=rew_loss,
                emergency_labor_loss_inr=labor_loss,
                energy_loss_inr=energy_loss,
                opportunity_cost_inr=opp_loss,
                total_loss_inr=tot,
                epistemic_status=epistemic,
                source="PHASE_14_FINANCIAL_LOSS_ENGINE",
                dataset_version="SYNTHETIC_FACTORY_V1",
                model_name="deterministic_loss_accounting",
                model_version="v1.0",
                pipeline_version="0.14.0",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="DERIVED_FROM_OBSERVED",
            )
            self.session.add(rec)
            count += 1
        self.session.flush()
        return count

    def seed_recommendations(self) -> int:
        """
        Seeds Phase 15 Operational Recommendations.
        Preserves closed 26-action taxonomy.
        """
        recs = [
            (
                "REC_M2_BEARING_001",
                "M2",
                "PREVENTIVE_MAINTENANCE",
                "INSPECT_SPINDLE_BEARING",
                "CRITICAL",
                "IMMEDIATE",
                "HIGH",
                "Vibration velocity (4.25 mm/s) breaches alert boundary (3.8 mm/s); failure probability reaches 0.946.",
                json.dumps(["vibration_4.25mms", "pdm_prob_0.946", "health_26.88"]),
            ),
            (
                "REC_M2_INVENTORY_002",
                "M2",
                "INVENTORY_REPLENISHMENT",
                "ORDER_SPARE_PARTS",
                "HIGH",
                "NEXT_SHIFT",
                "HIGH",
                "Proactive maintenance will consume 1 bearing, leaving stock at 1.0 < safety stock 1.134. Expedited reorder required.",
                json.dumps(["stock_post_service_1.0", "safety_stock_1.134", "lead_time_7d"]),
            ),
        ]
        count = 0
        for r_id, m_id, cat, action, prio, urg, strength, rat, refs in recs:
            rec = OperationalRecommendation(
                recommendation_id=r_id,
                machine_id=m_id,
                category=cat,
                action=action,
                priority=prio,
                urgency=urg,
                evidence_strength=strength,
                rationale=rat,
                evidence_references=refs,
                status="PENDING",
                as_of_timestamp=DECISION_CUTOFF,
                provenance="RULE_DERIVED",
            )
            self.session.add(rec)
            count += 1
        self.session.flush()
        return count

    def seed_simulation_scenarios(self) -> int:
        """
        Seeds Phase 16 What-If Digital Twin Scenarios.
        Preserves:
        - Decision cutoff: 2026-01-21T12:00:00Z
        - Avoided breakdown loss: ₹9,420
        - Diagnostic KPIs under intervention: NOT_PROJECTABLE
        """
        scenarios = [
            (
                "SCENARIO_M2_PROACTIVE_SERVICE",
                "M2",
                "Scenario A: Proactive Spindle Bearing Replacement (Cutoff Jan 21)",
                json.dumps(["SCHEDULE_MAINTENANCE_WINDOW", "INSPECT_SPINDLE_BEARING", "ORDER_SPARE_PARTS"]),
                json.dumps({
                    "planned_service_downtime_minutes": 30.0,
                    "retrospective_unplanned_halt_minutes": 150.0,
                    "net_avoided_downtime_minutes": 120.0,
                    "failure_probability": "NOT_PROJECTABLE",
                    "anomaly_score": "NOT_PROJECTABLE",
                    "health_score": "NOT_PROJECTABLE",
                    "health_state": "NOT_PROJECTABLE",
                }),
                json.dumps({
                    "avoided_downtime_loss_inr": 9000.0,
                    "avoided_emergency_labor_inr": 420.0,
                    "projected_avoided_breakdown_loss_inr": 9420.0,
                    "planned_service_cost_inr": 2390.0,
                    "net_counterfactual_benefit_inr": 7030.0,
                }),
                json.dumps({
                    "downtime_rate_hourly_inr": 4500.0,
                    "emergency_labor_rate_hourly_inr": 280.0,
                    "planned_service_duration_min": 30.0,
                }),
                "COUNTERFACTUAL_EVALUATION",
                "HYPOTHETICAL_COUNTERFACTUAL",
                "NOT_PROJECTABLE",
            ),
        ]
        count = 0
        for s_id, m_id, s_name, actions, metrics, fin, assumptions, t_sem, epistemic, diag_status in scenarios:
            sim = SimulationScenario(
                scenario_id=s_id,
                machine_id=m_id,
                scenario_name=s_name,
                decision_cutoff=DECISION_CUTOFF,
                intervention_list=actions,
                projected_metrics=metrics,
                financial_projection=fin,
                configured_assumptions=assumptions,
                temporal_semantics=t_sem,
                epistemic_status=epistemic,
                diagnostic_kpi_status=diag_status,
                provenance="COUNTERFACTUAL_PROJECTION",
            )
            self.session.add(sim)
            count += 1
        self.session.flush()
        return count
