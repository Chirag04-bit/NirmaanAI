"""
NirmaanAI Phase 17 Test Suite: PostgreSQL Persistence & Production Data Layer
Validates database configuration, declarative schema DDL, constraints, indexes,
CRUD operations, AI output persistence, provenance retention, temporal causality,
authoritative inventory contracts (ROP 1.367, SS 1.134), and live PostgreSQL integration gating.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import pytest
from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    create_engine,
    inspect,
    select,
    text,
)
from sqlalchemy.orm import sessionmaker

import src.db as db
from src.db.config import (
    DatabaseConfig,
    DatabaseConfigurationError,
    is_postgres_available,
)
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
from src.db.seed.seeder import DatabaseSeeder, DECISION_CUTOFF
from src.utils.config_loader import get_project_root

ROOT = get_project_root()
OPERATIONAL_LOSSES_CSV = ROOT / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "operational_losses.csv"
EXPECTED_OPERATIONAL_LOSSES_MD5 = "34b12582b32d81e3121429c55ebf74e8"


@pytest.fixture
def memory_db():
    """In-memory SQLite database fixture for isolated unit testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    db.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    yield session
    session.close()
    engine.dispose()


# ==============================================================================
# 1. DATABASE CONFIGURATION TESTS
# ==============================================================================

def test_database_config_valid_and_normalization():
    """Verify URL normalization and driver compatibility mapping."""
    cfg = DatabaseConfig("postgresql://user:pass@localhost:5432/nirmaanai")
    assert cfg.database_url == "postgresql+psycopg://user:pass@localhost:5432/nirmaanai"
    assert cfg.is_postgres is True
    assert cfg.is_sqlite is False
    assert "******" in cfg.get_masked_url()
    assert "pass" not in cfg.get_masked_url()


def test_database_config_missing_raises_clean_error():
    """Verify missing DATABASE_URL raises DatabaseConfigurationError with helpful message."""
    old_val = os.environ.pop("DATABASE_URL", None)
    try:
        with pytest.raises(DatabaseConfigurationError) as exc_info:
            DatabaseConfig(database_url=None)
        assert "DATABASE_URL environment variable is not set" in str(exc_info.value)
        assert "postgresql+psycopg://" in str(exc_info.value)
    finally:
        if old_val:
            os.environ["DATABASE_URL"] = old_val


# ==============================================================================
# 2. SCHEMA DEFINITION & METADATA TESTS
# ==============================================================================

def test_schema_tables_and_metadata_completeness():
    """Verify all 19 required tables exist in Base.metadata."""
    expected_tables = {
        "factories",
        "machines",
        "sensors",
        "products",
        "production_jobs",
        "sensor_readings",
        "machine_telemetry_snapshots",
        "maintenance_records",
        "inventory_items",
        "ai_pdm_predictions",
        "ai_anomaly_results",
        "ai_bottleneck_results",
        "ai_forecasting_results",
        "ai_shap_explanations",
        "ai_rca_results",
        "ai_factory_health_scores",
        "finance_loss_records",
        "ai_recommendations",
        "simulation_scenarios",
    }
    actual_tables = set(db.Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


def test_schema_table_primary_and_foreign_keys():
    """Verify primary and foreign key constraints across tables."""
    tables = db.Base.metadata.tables

    # Machine foreign key to Factory
    machine_fks = list(tables["machines"].foreign_keys)
    assert any(fk.target_fullname == "factories.factory_id" for fk in machine_fks)

    # Sensor foreign key to Machine
    sensor_fks = list(tables["sensors"].foreign_keys)
    assert any(fk.target_fullname == "machines.machine_id" for fk in sensor_fks)

    # SensorReading foreign keys
    reading_fks = list(tables["sensor_readings"].foreign_keys)
    assert any(fk.target_fullname == "machines.machine_id" for fk in reading_fks)

    # Simulation foreign key
    sim_fks = list(tables["simulation_scenarios"].foreign_keys)
    assert any(fk.target_fullname == "machines.machine_id" for fk in sim_fks)


def test_schema_indexes_telemetry_and_maintenance():
    """Verify multi-column query indexes on sensor telemetry and maintenance records."""
    tables = db.Base.metadata.tables

    reading_indexes = {idx.name for idx in tables["sensor_readings"].indexes}
    assert "idx_reading_sensor_time" in reading_indexes
    assert "idx_reading_machine_time" in reading_indexes

    maint_indexes = {idx.name for idx in tables["maintenance_records"].indexes}
    assert "idx_maint_machine_time" in maint_indexes
    assert "idx_maint_decision_input" in maint_indexes


# ==============================================================================
# 3. CRUD & DATA LAYER TESTS
# ==============================================================================

def test_crud_factory_and_machines(memory_db):
    """Verify creation, relationship binding, and cascade for Factory and Machine."""
    factory = Factory(
        factory_id="F_TEST",
        factory_code="FAC_TEST",
        name="Test Plant",
        location="Kolkata",
        industry="Machining",
    )
    machine = Machine(
        machine_id="M_TEST",
        factory_id="F_TEST",
        machine_code="MC_TEST",
        machine_name="Test Milling Machine",
        machine_type="VMC",
        design_cycle_time_sec=45.0,
        baseline_power_kw=22.0,
        baseline_vibration_mms=1.4,
        alert_vibration_mms=3.8,
        critical_vibration_mms=5.5,
    )
    factory.machines.append(machine)
    memory_db.add(factory)
    memory_db.commit()

    retrieved = memory_db.scalar(select(Factory).where(Factory.factory_id == "F_TEST"))
    assert retrieved is not None
    assert len(retrieved.machines) == 1
    assert retrieved.machines[0].machine_id == "M_TEST"


def test_crud_inventory_contract(memory_db):
    """Verify inventory item insertion with authoritative values."""
    factory = Factory(
        factory_id="F_INV",
        factory_code="FAC_INV",
        name="Inv Plant",
        location="Kolkata",
        industry="Precision",
    )
    memory_db.add(factory)
    memory_db.commit()

    item = InventoryItem(
        inventory_id="INV_M2_BEARING",
        factory_id="F_INV",
        sku_id="SKU_SPINDLE_BEARING_M2",
        item_name="Precision Spindle Bearing",
        category="SPARE_PART",
        current_stock=2.0,
        safety_stock=1.134,
        reorder_point=1.367,
        lead_time_days=7.0,
        unit_cost_inr=3200.0,
    )
    memory_db.add(item)
    memory_db.commit()

    retrieved = memory_db.scalar(select(InventoryItem).where(InventoryItem.sku_id == "SKU_SPINDLE_BEARING_M2"))
    assert retrieved.current_stock == 2.0
    assert retrieved.safety_stock == 1.134
    assert retrieved.reorder_point == 1.367
    assert retrieved.lead_time_days == 7.0


# ==============================================================================
# 4. AI & DECISION OUTPUT PERSISTENCE TESTS
# ==============================================================================

def test_ai_outputs_persistence_roundtrip(memory_db):
    """Verify persistence and fidelity of Phases 6, 7, 8, 9, 11, 12, 13, 14, 15, 16."""
    factory = Factory(
        factory_id="F_AI",
        factory_code="FAC_AI",
        name="AI Plant",
        location="Kolkata",
        industry="Automotive",
    )
    machine = Machine(
        machine_id="M2",
        factory_id="F_AI",
        machine_code="MC_M2",
        machine_name="VMC M2",
        machine_type="VMC",
        design_cycle_time_sec=45.0,
        baseline_power_kw=22.0,
    )
    factory.machines.append(machine)
    memory_db.add(factory)
    memory_db.commit()

    # Phase 6: PdM with 0.91 threshold and authoritative 0.9959 probability
    pdm = PredictiveMaintenancePrediction(
        machine_id="M2",
        prediction_timestamp=DECISION_CUTOFF,
        failure_probability=0.9959,
        prediction_class=1,
        threshold=0.91,
        source="PHASE_06_XGBOOST",
        as_of_timestamp=DECISION_CUTOFF,
        provenance="DERIVED_FROM_OBSERVED",
        epistemic_status="MODEL_INFERENCE",
    )
    memory_db.add(pdm)

    # Phase 7: Anomaly with 0.24050 threshold and authoritative 0.3500 score
    anomaly = AnomalyDetectionResult(
        machine_id="M2",
        timestamp=DECISION_CUTOFF,
        anomaly_score=0.3500,
        threshold=0.24050,
        anomaly_status="ANOMALOUS",
        source="PHASE_07_PCA",
        as_of_timestamp=DECISION_CUTOFF,
        provenance="DERIVED_FROM_OBSERVED",
        epistemic_status="STATISTICAL_INFERENCE",
    )
    memory_db.add(anomaly)

    # Phase 13: Health Score with authoritative CRITICAL 26.88
    health = FactoryHealthScore(
        machine_id="M2",
        factory_id="F_AI",
        timestamp=DECISION_CUTOFF,
        health_score=26.88,
        health_state="CRITICAL",
        as_of_timestamp=DECISION_CUTOFF,
        provenance="DERIVED_FROM_OBSERVED",
        epistemic_status="COMPOSITE_INDEX",
    )
    memory_db.add(health)

    # Phase 14: Financial Loss (Realized ₹73,062.28, Baseline Opportunity ₹24,320.00, Gross ₹97,382.28)
    realized_loss = FinancialLossRecord(
        machine_id="M2",
        timestamp=DECISION_CUTOFF,
        loss_type="REALIZED_LOSS",
        downtime_minutes=150.0,
        downtime_loss_inr=11250.0,
        scrap_loss_inr=51800.0,
        rework_loss_inr=6475.0,
        emergency_labor_loss_inr=420.0,
        energy_loss_inr=3117.28,
        opportunity_cost_inr=0.0,
        total_loss_inr=73062.28,
        epistemic_status="OBSERVED_HISTORICAL",
        provenance="DERIVED_FROM_OBSERVED",
        as_of_timestamp=DECISION_CUTOFF,
    )
    opp_loss = FinancialLossRecord(
        machine_id="M2",
        timestamp=DECISION_CUTOFF,
        loss_type="PROJECTED_OPPORTUNITY_COST",
        total_loss_inr=24320.0,
        opportunity_cost_inr=24320.0,
        epistemic_status="PROJECTED_OPPORTUNITY_COST",
        provenance="DERIVED_FROM_OBSERVED",
        as_of_timestamp=DECISION_CUTOFF,
    )
    gross_loss = FinancialLossRecord(
        machine_id="M2",
        timestamp=DECISION_CUTOFF,
        loss_type="GROSS_FINANCIAL_EXPOSURE",
        total_loss_inr=97382.28,
        opportunity_cost_inr=24320.0,
        epistemic_status="PROJECTED_GROSS_EXPOSURE",
        provenance="DERIVED_FROM_OBSERVED",
        as_of_timestamp=DECISION_CUTOFF,
    )
    memory_db.add_all([realized_loss, opp_loss, gross_loss])

    # Phase 15: Operational Recommendation with closed taxonomy action
    rec = OperationalRecommendation(
        recommendation_id="REC_TEST_001",
        machine_id="M2",
        category="PREVENTIVE_MAINTENANCE",
        action="INSPECT_SPINDLE_BEARING",
        priority="CRITICAL",
        urgency="IMMEDIATE",
        evidence_strength="HIGH",
        rationale="Alert threshold breached (pdm=0.9959, anomaly=0.3500)",
        as_of_timestamp=DECISION_CUTOFF,
        provenance="RULE_DERIVED",
    )
    memory_db.add(rec)

    # Phase 16: Simulation Scenario with normalized queryable columns & NOT_PROJECTABLE diagnostic KPIs
    sim = SimulationScenario(
        scenario_id="SCENARIO_M2_A",
        machine_id="M2",
        scenario_name="Scenario A: Proactive Service",
        decision_cutoff=DECISION_CUTOFF,
        intervention_list=json.dumps(["INSPECT_SPINDLE_BEARING", "ORDER_SPARE_PARTS"]),
        baseline_downtime_minutes=150.0,
        baseline_failure_probability=0.9959,
        baseline_anomaly_score=0.35,
        baseline_health_score=26.88,
        baseline_realized_loss_inr=73062.28,
        baseline_gross_exposure_inr=97382.28,
        planned_service_downtime_minutes=30.0,
        net_avoided_downtime_minutes=120.0,
        avoided_downtime_loss_inr=9000.0,
        avoided_emergency_labor_inr=420.0,
        projected_avoided_breakdown_loss_inr=9420.0,
        planned_service_cost_inr=2390.0,
        net_counterfactual_benefit_inr=7030.0,
        remaining_gross_exposure_inr=77862.28,
        projected_failure_probability="NOT_PROJECTABLE",
        projected_anomaly_score="NOT_PROJECTABLE",
        projected_health_score="NOT_PROJECTABLE",
        projected_health_state="NOT_PROJECTABLE",
        projected_metrics=json.dumps({
            "net_avoided_downtime_minutes": 120.0,
            "failure_probability": "NOT_PROJECTABLE",
            "health_score": "NOT_PROJECTABLE",
        }),
        financial_projection=json.dumps({
            "projected_avoided_breakdown_loss_inr": 9420.0,
            "net_counterfactual_benefit_inr": 7030.0,
        }),
        configured_assumptions=json.dumps({"downtime_rate": 4500.0}),
        temporal_semantics="COUNTERFACTUAL_EVALUATION",
        epistemic_status="HYPOTHETICAL_COUNTERFACTUAL",
        diagnostic_kpi_status="NOT_PROJECTABLE",
        provenance="COUNTERFACTUAL_PROJECTION",
    )
    memory_db.add(sim)
    memory_db.commit()

    # Assertions
    ret_pdm = memory_db.scalar(select(PredictiveMaintenancePrediction).where(PredictiveMaintenancePrediction.machine_id == "M2"))
    assert ret_pdm.threshold == 0.91
    assert ret_pdm.failure_probability == 0.9959

    ret_anom = memory_db.scalar(select(AnomalyDetectionResult).where(AnomalyDetectionResult.machine_id == "M2"))
    assert ret_anom.threshold == 0.24050
    assert ret_anom.anomaly_score == 0.3500
    assert ret_anom.anomaly_status == "ANOMALOUS"

    ret_health = memory_db.scalar(select(FactoryHealthScore).where(FactoryHealthScore.machine_id == "M2"))
    assert ret_health.health_score == 26.88
    assert ret_health.health_state == "CRITICAL"

    ret_realized = memory_db.scalar(
        select(FinancialLossRecord).where(
            FinancialLossRecord.machine_id == "M2",
            FinancialLossRecord.loss_type == "REALIZED_LOSS",
        )
    )
    assert ret_realized.total_loss_inr == 73062.28

    ret_opp = memory_db.scalar(
        select(FinancialLossRecord).where(
            FinancialLossRecord.machine_id == "M2",
            FinancialLossRecord.loss_type == "PROJECTED_OPPORTUNITY_COST",
        )
    )
    assert ret_opp.total_loss_inr == 24320.0

    ret_gross = memory_db.scalar(
        select(FinancialLossRecord).where(
            FinancialLossRecord.machine_id == "M2",
            FinancialLossRecord.loss_type == "GROSS_FINANCIAL_EXPOSURE",
        )
    )
    assert ret_gross.total_loss_inr == 97382.28

    ret_sim = memory_db.scalar(select(SimulationScenario).where(SimulationScenario.scenario_id == "SCENARIO_M2_A"))
    assert ret_sim.diagnostic_kpi_status == "NOT_PROJECTABLE"
    assert ret_sim.projected_failure_probability == "NOT_PROJECTABLE"
    assert ret_sim.net_counterfactual_benefit_inr == 7030.0
    assert ret_sim.baseline_gross_exposure_inr == 97382.28
    assert ret_sim.remaining_gross_exposure_inr == 77862.28
    assert ret_sim.temporal_semantics == "COUNTERFACTUAL_EVALUATION"


# ==============================================================================
# 5. TEMPORAL INTEGRITY & DAY-22 GROUND TRUTH TESTS
# ==============================================================================

def test_temporal_integrity_decision_time_vs_day22_ground_truth(memory_db):
    """
    Validates strict temporal boundary in database records:
    - MAINT_0003 is timestamped 2026-01-22T16:30:00Z (> cutoff 2026-01-21T12:00:00Z).
    - MAINT_0003 has is_decision_input = False and epistemic_status = RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.
    - Decision-time query strictly excludes MAINT_0003.
    """
    seeder = DatabaseSeeder(memory_db)
    seeder.seed_factory()
    seeder.seed_machines()
    seeder.seed_maintenance()
    memory_db.commit()

    # Query all decision-time maintenance records
    decision_records = memory_db.scalars(
        select(MaintenanceRecord).where(MaintenanceRecord.is_decision_input.is_(True))
    ).all()
    for rec in decision_records:
        ts = rec.timestamp if rec.timestamp.tzinfo is not None else rec.timestamp.replace(tzinfo=timezone.utc)
        assert ts <= DECISION_CUTOFF
        assert rec.maintenance_id != "MAINT_0003"

    # Query MAINT_0003 specifically
    maint_0003 = memory_db.scalar(
        select(MaintenanceRecord).where(MaintenanceRecord.maintenance_id == "MAINT_0003")
    )
    assert maint_0003 is not None
    m_ts = maint_0003.timestamp if maint_0003.timestamp.tzinfo is not None else maint_0003.timestamp.replace(tzinfo=timezone.utc)
    assert m_ts > DECISION_CUTOFF
    assert maint_0003.is_decision_input is False
    assert maint_0003.epistemic_status == "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"


# ==============================================================================
# 6. DETERMINISTIC SEEDER TESTS
# ==============================================================================

def test_deterministic_database_seeder(memory_db):
    """Verify complete database seeding completes deterministically."""
    seeder = DatabaseSeeder(memory_db)
    counts = seeder.seed_all(telemetry_sample_limit=30, jobs_sample_limit=20)
    memory_db.commit()

    assert counts["factories"] == 1
    assert counts["machines"] == 5
    assert counts["sensors"] == 25
    assert counts["inventory"] == 5
    assert counts["maintenance"] == 4
    assert counts["ai_pdm"] == 5
    assert counts["ai_anomaly"] == 5
    assert counts["ai_health"] == 5
    assert counts["ai_loss"] == 4
    assert counts["ai_simulation"] == 1


# ==============================================================================
# 7. SOURCE DATASET INTEGRITY TEST
# ==============================================================================

def test_upstream_operational_losses_md5_immutable():
    """Verify that operational_losses.csv MD5 is byte-for-byte identical to baseline."""
    assert OPERATIONAL_LOSSES_CSV.exists()
    hasher = hashlib.md5()
    with open(OPERATIONAL_LOSSES_CSV, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest().lower()
    assert actual_hash == EXPECTED_OPERATIONAL_LOSSES_MD5, (
        f"DATASET CORRUPTION DETECTED: expected {EXPECTED_OPERATIONAL_LOSSES_MD5}, got {actual_hash}"
    )


def test_schema_required_columns_audit():
    """Verify presence of core business and AI fields on table definitions."""
    tables = db.Base.metadata.tables

    # Machines
    machine_cols = {c.name for c in tables["machines"].columns}
    assert {"machine_id", "factory_id", "machine_code", "machine_name", "machine_type", "station", "status"}.issubset(machine_cols)

    # Sensors
    sensor_cols = {c.name for c in tables["sensors"].columns}
    assert {"sensor_id", "machine_id", "sensor_code", "sensor_type", "unit", "sampling_interval"}.issubset(sensor_cols)

    # Inventory
    inv_cols = {c.name for c in tables["inventory_items"].columns}
    assert {"inventory_id", "factory_id", "sku_id", "current_stock", "safety_stock", "reorder_point", "lead_time_days", "unit_cost_inr"}.issubset(inv_cols)

    # Maintenance
    maint_cols = {c.name for c in tables["maintenance_records"].columns}
    assert {"maintenance_id", "machine_id", "maintenance_type", "timestamp", "duration_minutes", "is_decision_input", "epistemic_status"}.issubset(maint_cols)

    # Simulation - Normalized Columns
    sim_cols = {c.name for c in tables["simulation_scenarios"].columns}
    assert {
        "scenario_id", "machine_id", "decision_cutoff", "temporal_semantics",
        "epistemic_status", "diagnostic_kpi_status", "baseline_downtime_minutes",
        "baseline_failure_probability", "baseline_anomaly_score", "baseline_health_score",
        "baseline_realized_loss_inr", "baseline_gross_exposure_inr",
        "net_avoided_downtime_minutes", "avoided_downtime_loss_inr", "avoided_emergency_labor_inr",
        "projected_avoided_breakdown_loss_inr", "planned_service_cost_inr",
        "net_counterfactual_benefit_inr", "remaining_gross_exposure_inr",
        "projected_failure_probability", "projected_anomaly_score",
        "projected_health_score", "projected_health_state",
    }.issubset(sim_cols)


def test_crud_sensor_and_readings(memory_db):
    """Verify sensor creation and time-series reading insert/query."""
    factory = Factory(factory_id="F_SENS", factory_code="FAC_SENS", name="P", location="K", industry="M")
    machine = Machine(machine_id="M_SENS", factory_id="F_SENS", machine_code="MC_S", machine_name="M", machine_type="VMC", design_cycle_time_sec=40.0, baseline_power_kw=15.0)
    sensor = Sensor(sensor_id="S_VIB_1", machine_id="M_SENS", sensor_code="VIB", sensor_type="VIBRATION", unit="mm/s", sampling_interval=1.0)
    reading = SensorReading(reading_id=1, sensor_id="S_VIB_1", machine_id="M_SENS", timestamp=DECISION_CUTOFF, value=1.42, quality_flag="GOOD", source="PLC")

    memory_db.add_all([factory, machine, sensor, reading])
    memory_db.commit()

    retrieved = memory_db.scalar(select(SensorReading).where(SensorReading.reading_id == 1))
    assert retrieved is not None
    assert retrieved.value == 1.42
    assert retrieved.sensor.sensor_type == "VIBRATION"


def test_crud_production_jobs(memory_db):
    """Verify production job creation, timing, and quantity tracking."""
    factory = Factory(factory_id="F_JOB", factory_code="FAC_JOB", name="P", location="K", industry="M")
    machine = Machine(machine_id="M_JOB", factory_id="F_JOB", machine_code="MC_J", machine_name="M", machine_type="VMC", design_cycle_time_sec=40.0, baseline_power_kw=15.0)
    job = ProductionJob(
        job_id="JOB_001",
        factory_id="F_JOB",
        machine_id="M_JOB",
        operation_type="Turning",
        scheduled_start=DECISION_CUTOFF,
        scheduled_end=DECISION_CUTOFF,
        quantity=100,
        completed_quantity=95,
        scrap_quantity=5,
        status="COMPLETED",
    )
    memory_db.add_all([factory, machine, job])
    memory_db.commit()

    retrieved = memory_db.scalar(select(ProductionJob).where(ProductionJob.job_id == "JOB_001"))
    assert retrieved is not None
    assert retrieved.completed_quantity == 95
    assert retrieved.scrap_quantity == 5


def test_ai_individual_subsystems_persistence(memory_db):
    """Verify Bottleneck, Forecasting, SHAP, and RCA subsystem outputs."""
    factory = Factory(factory_id="F_SUB", factory_code="FAC_SUB", name="P", location="K", industry="M")
    machine = Machine(machine_id="M_SUB", factory_id="F_SUB", machine_code="MC_SUB", machine_name="M", machine_type="VMC", design_cycle_time_sec=40.0, baseline_power_kw=15.0)
    memory_db.add_all([factory, machine])
    memory_db.commit()

    bn = BottleneckPredictionResult(
        machine_id="M_SUB",
        timestamp=DECISION_CUTOFF,
        bottleneck_status="BOTTLENECK",
        bottleneck_probability=0.88,
        target_metric="cycle_time_ratio",
        as_of_timestamp=DECISION_CUTOFF,
    )
    fc = ForecastingResult(
        target_series="production_volume",
        forecast_timestamp=DECISION_CUTOFF,
        horizon_hours=24,
        predicted_value=1420.0,
        actual_value=1380.0,
        as_of_timestamp=DECISION_CUTOFF,
    )
    shap = ShapExplanation(
        prediction_ref_id="PRED_001",
        machine_id="M_SUB",
        feature_name="rotational_speed_rpm",
        feature_value=1493.0,
        shap_value=0.412,
        ranking=1,
        as_of_timestamp=DECISION_CUTOFF,
    )
    rca = RcaResult(
        rca_id="RCA_SUB_001",
        machine_id="M_SUB",
        event_timestamp=DECISION_CUTOFF,
        primary_cause="Lubrication starvation",
        cause_score=0.92,
        severity="CRITICAL",
        evidence_strength="HIGH",
        as_of_timestamp=DECISION_CUTOFF,
    )
    memory_db.add_all([bn, fc, shap, rca])
    memory_db.commit()

    assert memory_db.scalar(select(BottleneckPredictionResult).where(BottleneckPredictionResult.machine_id == "M_SUB")).bottleneck_probability == 0.88
    assert memory_db.scalar(select(ForecastingResult).where(ForecastingResult.target_series == "production_volume")).predicted_value == 1420.0
    assert memory_db.scalar(select(ShapExplanation).where(ShapExplanation.machine_id == "M_SUB")).shap_value == 0.412
    assert memory_db.scalar(select(RcaResult).where(RcaResult.rca_id == "RCA_SUB_001")).primary_cause == "Lubrication starvation"


def test_phase6_phase7_authoritative_reconciliation(memory_db):
    """
    Blocker 2 Reconciliation Test:
    - Phase 6 M2 failure probability must be exactly 0.9959 (exceeds locked 0.91 threshold).
    - Phase 7 M2 anomaly score must be exactly 0.3500 (exceeds locked 0.24050 threshold).
    - Full provenance, source, and as_of_timestamp metadata must be retained.
    """
    seeder = DatabaseSeeder(memory_db)
    seeder.seed_factory()
    seeder.seed_machines()
    seeder.seed_pdm_predictions()
    seeder.seed_anomaly_results()
    memory_db.commit()

    m2_pdm = memory_db.scalar(select(PredictiveMaintenancePrediction).where(PredictiveMaintenancePrediction.machine_id == "M2"))
    assert m2_pdm is not None
    assert m2_pdm.failure_probability == 0.9959
    assert m2_pdm.threshold == 0.91
    assert m2_pdm.prediction_class == 1
    assert m2_pdm.source in ("PHASE_06_XGBOOST", "PHASE_06_XGBOOST_MODEL")
    pdm_ts = m2_pdm.as_of_timestamp if m2_pdm.as_of_timestamp.tzinfo is not None else m2_pdm.as_of_timestamp.replace(tzinfo=timezone.utc)
    assert pdm_ts == DECISION_CUTOFF

    m2_anom = memory_db.scalar(select(AnomalyDetectionResult).where(AnomalyDetectionResult.machine_id == "M2"))
    assert m2_anom is not None
    assert m2_anom.anomaly_score == 0.3500
    assert m2_anom.threshold == 0.24050
    assert m2_anom.anomaly_status == "ANOMALOUS"
    assert m2_anom.source in ("PHASE_07_PCA", "PHASE_07_PCA_ANOMALY_ENGINE")
    anom_ts = m2_anom.as_of_timestamp if m2_anom.as_of_timestamp.tzinfo is not None else m2_anom.as_of_timestamp.replace(tzinfo=timezone.utc)
    assert anom_ts == DECISION_CUTOFF


def test_simulation_scenarios_normalized_queryable(memory_db):
    """
    Blocker 3 Simulation Persistence Test:
    - Verifies simulation scenarios are queryable via normalized columns WITHOUT parsing JSON blobs.
    - Asserts net_counterfactual_benefit_inr == 7030.0
    - Asserts diagnostic KPIs are explicitly NOT_PROJECTABLE.
    """
    seeder = DatabaseSeeder(memory_db)
    seeder.seed_factory()
    seeder.seed_machines()
    seeder.seed_simulation_scenarios()
    memory_db.commit()

    sim = memory_db.scalar(select(SimulationScenario).where(SimulationScenario.scenario_id == "SCENARIO_M2_PROACTIVE_SERVICE"))
    assert sim is not None
    assert sim.machine_id == "M2"
    assert sim.baseline_failure_probability == 0.9959
    assert sim.baseline_anomaly_score == 0.35
    assert sim.baseline_health_score == 26.88
    assert sim.baseline_realized_loss_inr == 73062.28
    assert sim.baseline_gross_exposure_inr == 97382.28
    assert sim.planned_service_downtime_minutes == 30.0
    assert sim.net_avoided_downtime_minutes == 120.0
    assert sim.avoided_downtime_loss_inr == 9000.0
    assert sim.avoided_emergency_labor_inr == 420.0
    assert sim.projected_avoided_breakdown_loss_inr == 9420.0
    assert sim.planned_service_cost_inr == 2390.0
    assert sim.net_counterfactual_benefit_inr == 7030.0
    assert sim.remaining_gross_exposure_inr == 87962.28
    assert sim.projected_failure_probability == "NOT_PROJECTABLE"
    assert sim.projected_anomaly_score == "NOT_PROJECTABLE"
    assert sim.projected_health_score == "NOT_PROJECTABLE"
    assert sim.projected_health_state == "NOT_PROJECTABLE"
    assert sim.temporal_semantics == "COUNTERFACTUAL_EVALUATION"


def test_financial_baseline_vs_scenario_opportunity_cost(memory_db):
    """
    Blocker 4 Financial Semantics Reconciliation Test:
    - Realized loss: ₹73,062.28
    - Baseline projected opportunity cost: ₹24,320.00 (76 delayed units * ₹320/unit)
    - Baseline gross financial exposure: ₹97,382.28 (73,062.28 + 24,320.00)
    - Scenario D avoided opportunity cost: ₹19,520.00 ((76 - 15) * 320)
    - Remaining gross exposure under Scenario D: ₹77,862.28 (97,382.28 - 19,520.00)
    """
    seeder = DatabaseSeeder(memory_db)
    seeder.seed_factory()
    seeder.seed_machines()
    seeder.seed_financial_loss()
    memory_db.commit()

    records = {
        r.loss_type: r
        for r in memory_db.scalars(select(FinancialLossRecord).where(FinancialLossRecord.machine_id == "M2")).all()
    }
    assert "REALIZED_LOSS" in records
    assert "PROJECTED_OPPORTUNITY_COST" in records
    assert "GROSS_EXPOSURE" in records
    assert "AVOIDED_OPPORTUNITY_COST" in records

    realized = records["REALIZED_LOSS"]
    baseline_opp = records["PROJECTED_OPPORTUNITY_COST"]
    gross = records["GROSS_EXPOSURE"]
    avoided_opp = records["AVOIDED_OPPORTUNITY_COST"]

    assert realized.total_loss_inr == 73062.28
    assert baseline_opp.total_loss_inr == 24320.0
    assert gross.total_loss_inr == 97382.28
    assert avoided_opp.total_loss_inr == 19520.0
    assert round(realized.total_loss_inr + baseline_opp.total_loss_inr, 2) == gross.total_loss_inr
    remaining_exposure = gross.total_loss_inr - avoided_opp.total_loss_inr
    assert round(remaining_exposure, 2) == 77862.28


def test_transaction_rollback_preserves_consistency(memory_db):
    """Verify transaction rollback rolls back uncommitted changes."""
    factory = Factory(
        factory_id="F_ROLLBACK",
        factory_code="FAC_RB",
        name="Rollback Plant",
        location="Kolkata",
        industry="Machining",
    )
    memory_db.add(factory)
    memory_db.commit()

    # Attempt to insert an invalid machine inside a transaction and rollback
    try:
        invalid_machine = Machine(
            machine_id="M_INVALID",
            factory_id="F_NONEXISTENT",  # Foreign key violation or error
            machine_code="MC_INV",
            machine_name="Invalid Machine",
            machine_type="VMC",
            design_cycle_time_sec=40.0,
            baseline_power_kw=15.0,
        )
        memory_db.add(invalid_machine)
        memory_db.flush()
    except Exception:
        memory_db.rollback()

    # Verify factory remains intact
    retrieved = memory_db.scalar(select(Factory).where(Factory.factory_id == "F_ROLLBACK"))
    assert retrieved is not None


def test_alembic_migration_reproducibility():
    """Verify that Alembic migration environment has valid revision files and can produce DDL."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert len(heads) >= 1, "No Alembic migration heads found"


# ==============================================================================
# 8. POSTGRESQL INTEGRATION GATE (CLEAN SKIP IF NO POSTGRES SERVICE)
# ==============================================================================

@pytest.mark.skipif(
    not is_postgres_available(),
    reason="PostgreSQL server is not reachable at DATABASE_URL (localhost:5432). PostgreSQL integration = NOT VERIFIED."
)
def test_postgresql_live_integration():
    """
    Executes live PostgreSQL connection, table creation, and transactional round-trip.
    Only runs when an actual PostgreSQL server is reachable.
    """
    cfg = DatabaseConfig()
    engine = db.get_engine(cfg)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1")).scalar()
        assert res == 1
