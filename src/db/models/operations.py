"""
NirmaanAI Operational Relational Models
Defines tables for ProductionJob, SensorReading, MachineTelemetrySnapshot,
MaintenanceRecord, and InventoryItem.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, utcnow


class ProductionJob(Base, TimestampMixin):
    __tablename__ = "production_jobs"

    job_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    factory_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("factories.factory_id", ondelete="CASCADE"), nullable=False, index=True
    )
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("products.product_id", ondelete="SET NULL"), nullable=True, index=True
    )
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cycle_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scrap_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="SCHEDULED")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="chk_job_quantity_non_negative"),
        CheckConstraint("completed_quantity >= 0", name="chk_job_completed_non_negative"),
        CheckConstraint("scrap_quantity >= 0", name="chk_job_scrap_non_negative"),
        Index("idx_job_machine_start", "machine_id", "scheduled_start"),
        Index("idx_job_factory_status", "factory_id", "status"),
    )

    # Relationships
    factory: Mapped["Factory"] = relationship("Factory", back_populates="production_jobs")
    machine: Mapped["Machine"] = relationship("Machine", back_populates="production_jobs")
    product: Mapped[Optional["Product"]] = relationship("Product", back_populates="production_jobs")

    def __repr__(self) -> str:
        return f"<ProductionJob {self.job_id} on {self.machine_id} ({self.status})>"


class SensorReading(Base):
    """
    High-efficiency normalized sensor reading time-series.
    Indexes explicitly cover (sensor_id, timestamp) and (machine_id, timestamp).
    """
    __tablename__ = "sensor_readings"

    reading_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("sensors.sensor_id", ondelete="CASCADE"), nullable=True, index=True
    )
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    quality_flag: Mapped[str] = mapped_column(String(20), nullable=False, default="GOOD")
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="PLC_SCADA")

    __table_args__ = (
        Index("idx_reading_sensor_time", "sensor_id", "timestamp"),
        Index("idx_reading_machine_time", "machine_id", "timestamp"),
    )

    # Relationships
    sensor: Mapped[Optional["Sensor"]] = relationship("Sensor", back_populates="readings")
    machine: Mapped["Machine"] = relationship("Machine", back_populates="sensor_readings")

    def __repr__(self) -> str:
        return f"<SensorReading {self.reading_id}: {self.sensor_id} @ {self.timestamp} = {self.value}>"


class MachineTelemetrySnapshot(Base):
    """
    Wide machine telemetry snapshot mapping the multi-sensor readings dataset.
    Optimized for analytical queries across synchronous channels.
    """
    __tablename__ = "machine_telemetry_snapshots"

    snapshot_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    vibration_mms: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    ambient_temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rotational_speed_rpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    torque_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sound_db: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    power_consumption_kw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    oil_level_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coolant_level_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tool_wear_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("idx_telemetry_machine_time", "machine_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MachineTelemetrySnapshot {self.machine_id} @ {self.timestamp}>"


class MaintenanceRecord(Base, TimestampMixin):
    """
    Maintains machine maintenance history with strict temporal semantics:
    - is_decision_input distinguishes pre-cutoff evidence vs post-cutoff events.
    - MAINT_0003 is explicitly flagged as RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.
    """
    __tablename__ = "maintenance_records"

    maintenance_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    maintenance_type: Mapped[str] = mapped_column(String(50), nullable=False)
    failure_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="NONE")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reason: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    technician: Mapped[str] = mapped_column(String(100), nullable=False, default="TECH_01")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Explicit Temporal & Epistemic Boundary Flag
    is_decision_input: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    epistemic_status: Mapped[str] = mapped_column(
        String(60), nullable=False, default="OBSERVED"
    )

    __table_args__ = (
        Index("idx_maint_machine_time", "machine_id", "timestamp"),
        Index("idx_maint_decision_input", "machine_id", "is_decision_input"),
    )

    machine: Mapped["Machine"] = relationship("Machine", back_populates="maintenance_records")

    def __repr__(self) -> str:
        return f"<MaintenanceRecord {self.maintenance_id}: {self.machine_id} ({self.maintenance_type})>"


class InventoryItem(Base, TimestampMixin):
    """
    Persists inventory intelligence.
    Preserves authoritative Phase 10 M2 values:
    current_stock = 2.0, SS = 1.134, ROP = 1.367, lead_time_days = 7.0
    """
    __tablename__ = "inventory_items"

    inventory_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    factory_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("factories.factory_id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    current_stock: Mapped[float] = mapped_column(Float, nullable=False)
    safety_stock: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False)
    lead_time_days: Mapped[float] = mapped_column(Float, nullable=False, default=7.0)
    unit_cost_inr: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="units")

    __table_args__ = (
        CheckConstraint("current_stock >= 0.0", name="chk_inv_current_stock_non_negative"),
        CheckConstraint("safety_stock >= 0.0", name="chk_inv_safety_stock_non_negative"),
        CheckConstraint("reorder_point >= 0.0", name="chk_inv_reorder_point_non_negative"),
        CheckConstraint("unit_cost_inr >= 0.0", name="chk_inv_unit_cost_non_negative"),
        Index("idx_inv_sku", "sku_id"),
    )

    factory: Mapped["Factory"] = relationship("Factory", back_populates="inventory_items")

    def __repr__(self) -> str:
        return f"<InventoryItem {self.sku_id}: Stock={self.current_stock}, ROP={self.reorder_point}>"
