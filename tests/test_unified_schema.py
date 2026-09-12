"""
Phase 4 Unified Factory Data Schema Test Suite
Validates Pydantic entity models, boundary constraints, relational SQLite schema DDL,
and real dataset mapping into unified schema representations.
"""

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import pandas as pd
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.data.schema import (
    FailureMode,
    FinancialParameters,
    FactoryHealthSnapshot,
    HealthState,
    InventoryItem,
    JobStatus,
    Machine,
    MachineStatus,
    MaintenanceRecord,
    OperationalLossRecord,
    ProductionJob,
    SensorReading,
)
from src.data.sql_schema import (
    Base,
    MachineModel,
    SensorReadingModel,
    create_all_tables,
)
from src.utils.config_loader import get_project_root

PROJECT_ROOT = get_project_root()
DATASET_ROOT = PROJECT_ROOT / "DATASET"


# ==============================================================================
# 1. Pydantic Validation & Constraints Tests
# ==============================================================================

def test_machine_validation_success():
    """Verify clean instantiation of Machine model."""
    m = Machine(
        machine_id="M2",
        name="Vertical Milling Center M2",
        machine_type="VMC Milling",
        design_cycle_time_sec=45.0,
        baseline_power_kw=22.0,
        baseline_vibration_mms=1.4,
        alert_vibration_mms=3.8,
        critical_vibration_mms=5.5
    )
    assert m.machine_id == "M2"
    assert m.status == MachineStatus.OPERATIONAL
    assert m.design_cycle_time_sec == 45.0


def test_machine_validation_vibration_order_failure():
    """Verify that critical_vibration_mms <= alert_vibration_mms raises ValidationError."""
    with pytest.raises(ValidationError):
        Machine(
            machine_id="M2_BAD",
            name="Bad Machine",
            machine_type="VMC Milling",
            design_cycle_time_sec=45.0,
            baseline_power_kw=22.0,
            alert_vibration_mms=5.0,
            critical_vibration_mms=4.0  # Invalid: critical <= alert
        )


def test_production_job_timing_validation():
    """Verify timing constraints on ProductionJob."""
    now = datetime.now(timezone.utc)
    # Valid job
    job = ProductionJob(
        job_id="J_101",
        machine_id="M2",
        operation_type="Milling",
        scheduled_start=now,
        scheduled_end=now + timedelta(hours=2),
        batch_quantity=100,
        completed_quantity=95,
        scrap_quantity=5
    )
    assert job.batch_quantity == 100

    # Invalid: scheduled_end before scheduled_start
    with pytest.raises(ValidationError):
        ProductionJob(
            job_id="J_102",
            machine_id="M2",
            operation_type="Milling",
            scheduled_start=now,
            scheduled_end=now - timedelta(hours=1),
            batch_quantity=100
        )

    # Invalid: completed + scrap exceeds batch_quantity
    with pytest.raises(ValidationError):
        ProductionJob(
            job_id="J_103",
            machine_id="M2",
            operation_type="Milling",
            scheduled_start=now,
            scheduled_end=now + timedelta(hours=2),
            batch_quantity=100,
            completed_quantity=95,
            scrap_quantity=10  # 105 > 100
        )


def test_inventory_item_stockout_risk():
    """Verify stockout risk property on InventoryItem."""
    item_safe = InventoryItem(
        item_id="SKU_BEARING_01",
        item_name="Deep Groove Ball Bearing",
        category="SPARE_PART",
        current_stock=25.0,
        safety_stock=10.0,
        unit_cost_inr=850.0
    )
    assert not item_safe.is_stockout_risk

    item_risk = InventoryItem(
        item_id="SKU_BEARING_02",
        item_name="Spindle Bearing",
        category="SPARE_PART",
        current_stock=4.0,
        safety_stock=10.0,
        unit_cost_inr=2400.0
    )
    assert item_risk.is_stockout_risk


def test_sensor_reading_properties():
    """Verify computed properties on SensorReading."""
    reading = SensorReading(
        machine_id="M2",
        timestamp=datetime.now(timezone.utc),
        vibration_mms=2.1,
        temperature_c=55.0,
        ambient_temperature_c=25.0,
        rotational_speed_rpm=1500.0,
        torque_nm=40.0
    )
    assert reading.temperature_difference_k == 30.0
    assert reading.mechanical_power_kw is not None
    # Power = 2*pi*1500*40 / 60000 = 6.283 kW
    assert pytest.approx(reading.mechanical_power_kw, rel=1e-2) == 6.28


# ==============================================================================
# 2. In-Memory SQLite Relational DDL Tests
# ==============================================================================

def test_sqlite_table_creation_and_insertion():
    """Verify DDL creation and foreign key relationships in SQLite in-memory."""
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    create_all_tables(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert Machine
    machine = MachineModel(
        machine_id="M2",
        name="Vertical Milling Center M2",
        machine_type="VMC Milling",
        design_cycle_time_sec=45.0,
        baseline_power_kw=22.0,
        baseline_vibration_mms=1.4,
        alert_vibration_mms=3.8,
        critical_vibration_mms=5.5
    )
    session.add(machine)
    session.commit()

    # Insert Sensor Reading referencing M2
    now = datetime.now(timezone.utc)
    reading = SensorReadingModel(
        machine_id="M2",
        timestamp=now,
        vibration_mms=1.8,
        temperature_c=48.0,
        rotational_speed_rpm=1400.0,
        torque_nm=38.0
    )
    session.add(reading)
    session.commit()

    # Query back
    retrieved = session.query(MachineModel).filter_by(machine_id="M2").first()
    assert retrieved is not None
    assert len(retrieved.sensor_readings) == 1
    assert retrieved.sensor_readings[0].vibration_mms == 1.8

    session.close()


# ==============================================================================
# 3. Empirical Dataset Mapping Tests
# ==============================================================================

def test_map_ai4i_row_to_unified_schema():
    """Verify that a row from AI4I 2020 cleanly maps into SensorReading and MaintenanceRecord."""
    ai4i_path = DATASET_ROOT / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    assert ai4i_path.is_file()
    df = pd.read_csv(ai4i_path, nrows=1)
    row = df.iloc[0]

    # Map to SensorReading
    # Convert Kelvin to Celsius: K - 273.15
    reading = SensorReading(
        machine_id="M1",
        timestamp=datetime.now(timezone.utc),
        vibration_mms=1.2,  # Nominal default
        temperature_c=round(float(row["Process temperature [K]"] - 273.15), 2),
        ambient_temperature_c=round(float(row["Air temperature [K]"] - 273.15), 2),
        rotational_speed_rpm=float(row["Rotational speed [rpm]"]),
        torque_nm=float(row["Torque [Nm]"]),
        tool_wear_min=float(row["Tool wear [min]"])
    )
    assert reading.rotational_speed_rpm == 1551.0
    assert reading.torque_nm == 42.8
    assert reading.tool_wear_min == 0.0


def test_map_iot_row_to_unified_schema():
    """Verify that a row from Industrial IoT cleanly maps into Machine and SensorReading."""
    iot_path = DATASET_ROOT / "05_INDUSTRIAL_IOT" / "raw" / "factory_sensor_simulator_2040.csv"
    assert iot_path.is_file()
    df = pd.read_csv(iot_path, nrows=1)
    row = df.iloc[0]

    reading = SensorReading(
        machine_id=str(row["Machine_ID"]),
        timestamp=datetime.now(timezone.utc),
        vibration_mms=float(row["Vibration_mms"]),
        temperature_c=float(row["Temperature_C"]),
        sound_db=float(row["Sound_dB"]),
        power_consumption_kw=float(row["Power_Consumption_kW"]),
        oil_level_pct=float(row["Oil_Level_pct"]),
        coolant_level_pct=float(row["Coolant_Level_pct"])
    )
    assert reading.machine_id == "MC_000000"
    assert reading.vibration_mms == 12.78
    assert reading.temperature_c == 73.43
