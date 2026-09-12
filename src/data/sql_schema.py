"""
NirmaanAI Relational SQL Schema & SQLAlchemy ORM Models
Defines declarative database tables, indexes, constraints, and DDL generation.
"""

from datetime import datetime, timezone
from typing import Any
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

Base: Any = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)


class MachineModel(Base):
    __tablename__ = "machines"

    machine_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    machine_type = Column(String(50), nullable=False)
    line_id = Column(String(50), nullable=False, default="LINE_01")
    design_cycle_time_sec = Column(Float, nullable=False)
    baseline_power_kw = Column(Float, nullable=False)
    baseline_vibration_mms = Column(Float, nullable=False, default=1.2)
    alert_vibration_mms = Column(Float, nullable=False, default=3.8)
    critical_vibration_mms = Column(Float, nullable=False, default=5.5)
    rated_capacity_units_per_hour = Column(Float, nullable=False, default=60.0)
    status = Column(String(30), nullable=False, default="OPERATIONAL")
    installation_year = Column(Integer, nullable=True)

    # Relationships
    sensor_readings = relationship("SensorReadingModel", back_populates="machine", cascade="all, delete-orphan")
    production_jobs = relationship("ProductionJobModel", back_populates="machine", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecordModel", back_populates="machine", cascade="all, delete-orphan")
    health_snapshots = relationship("FactoryHealthSnapshotModel", back_populates="machine", cascade="all, delete-orphan")
    operational_losses = relationship("OperationalLossModel", back_populates="machine", cascade="all, delete-orphan")


class SensorReadingModel(Base):
    __tablename__ = "sensor_readings"

    reading_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=utcnow)
    vibration_mms = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    ambient_temperature_c = Column(Float, nullable=True)
    rotational_speed_rpm = Column(Float, nullable=True)
    torque_nm = Column(Float, nullable=True)
    sound_db = Column(Float, nullable=True)
    power_consumption_kw = Column(Float, nullable=True)
    oil_level_pct = Column(Float, nullable=True)
    coolant_level_pct = Column(Float, nullable=True)
    tool_wear_min = Column(Float, nullable=True)

    machine = relationship("MachineModel", back_populates="sensor_readings")

    __table_args__ = (
        Index("idx_sensor_machine_time", "machine_id", "timestamp"),
    )


class ProductionJobModel(Base):
    __tablename__ = "production_jobs"

    job_id = Column(String(50), primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    operation_type = Column(String(50), nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    batch_quantity = Column(Integer, nullable=False)
    completed_quantity = Column(Integer, nullable=False, default=0)
    scrap_quantity = Column(Integer, nullable=False, default=0)
    actual_cycle_time_sec = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="SCHEDULED")

    machine = relationship("MachineModel", back_populates="production_jobs")

    __table_args__ = (
        Index("idx_job_machine_start", "machine_id", "scheduled_start"),
    )


class MaintenanceRecordModel(Base):
    __tablename__ = "maintenance_records"

    record_id = Column(String(50), primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=utcnow)
    event_type = Column(String(50), nullable=False)
    failure_mode = Column(String(50), nullable=False, default="NONE")
    downtime_minutes = Column(Float, nullable=False, default=0.0)
    technician_id = Column(String(50), nullable=False, default="TECH_01")
    corrective_action = Column(String(200), nullable=False, default="")
    notes = Column(Text, nullable=True)

    machine = relationship("MachineModel", back_populates="maintenance_records")

    __table_args__ = (
        Index("idx_maint_machine_time", "machine_id", "timestamp"),
    )


class InventoryItemModel(Base):
    __tablename__ = "inventory_items"

    item_id = Column(String(50), primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    current_stock = Column(Float, nullable=False)
    safety_stock = Column(Float, nullable=False)
    unit_cost_inr = Column(Float, nullable=False)
    reorder_quantity = Column(Float, nullable=False, default=100.0)
    unit_of_measure = Column(String(20), nullable=False, default="kg")


class FinancialParametersModel(Base):
    __tablename__ = "financial_parameters"

    config_id = Column(String(50), primary_key=True, index=True)
    downtime_hourly_cost_inr = Column(Float, nullable=False, default=4500.0)
    base_electricity_rate_inr_per_kwh = Column(Float, nullable=False, default=8.50)
    peak_electricity_rate_inr_per_kwh = Column(Float, nullable=False, default=12.50)
    scrap_cost_rate_inr_per_kg = Column(Float, nullable=False, default=350.0)
    rework_hourly_labor_inr = Column(Float, nullable=False, default=280.0)
    effective_date = Column(DateTime, nullable=False, default=utcnow)


class FactoryHealthSnapshotModel(Base):
    __tablename__ = "factory_health_snapshots"

    snapshot_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=utcnow)
    composite_health_score = Column(Float, nullable=False)
    vibration_health = Column(Float, nullable=False, default=100.0)
    temperature_health = Column(Float, nullable=False, default=100.0)
    cycle_efficiency_health = Column(Float, nullable=False, default=100.0)
    maintenance_health = Column(Float, nullable=False, default=100.0)
    health_state = Column(String(30), nullable=False, default="EXCELLENT")
    contributing_anomaly = Column(String(100), nullable=True)

    machine = relationship("MachineModel", back_populates="health_snapshots")

    __table_args__ = (
        Index("idx_health_machine_time", "machine_id", "timestamp"),
    )


class OperationalLossModel(Base):
    __tablename__ = "operational_loss_records"

    loss_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=utcnow)
    downtime_minutes = Column(Float, nullable=False, default=0.0)
    downtime_loss_inr = Column(Float, nullable=False, default=0.0)
    energy_wastage_kwh = Column(Float, nullable=False, default=0.0)
    energy_loss_inr = Column(Float, nullable=False, default=0.0)
    scrap_quantity = Column(Integer, nullable=False, default=0)
    scrap_loss_inr = Column(Float, nullable=False, default=0.0)
    rework_hours = Column(Float, nullable=False, default=0.0)
    rework_loss_inr = Column(Float, nullable=False, default=0.0)
    total_financial_loss_inr = Column(Float, nullable=False)

    machine = relationship("MachineModel", back_populates="operational_losses")

    __table_args__ = (
        Index("idx_loss_machine_time", "machine_id", "timestamp"),
    )


def create_all_tables(engine):
    """Creates all relational tables defined in this schema."""
    Base.metadata.create_all(engine)
