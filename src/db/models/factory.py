"""
NirmaanAI Core Factory & Physical Plant Models
Defines relational tables for Factory, Machine, Sensor, and Product entities
with constraints, indexes, and cascades.
"""

from typing import List, Optional
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin


class Factory(Base, TimestampMixin):
    __tablename__ = "factories"

    factory_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    factory_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    machines: Mapped[List["Machine"]] = relationship(
        "Machine", back_populates="factory", cascade="all, delete-orphan"
    )
    production_jobs: Mapped[List["ProductionJob"]] = relationship(
        "ProductionJob", back_populates="factory", cascade="all, delete-orphan"
    )
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem", back_populates="factory", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Factory {self.factory_code}: {self.name}>"


class Machine(Base, TimestampMixin):
    __tablename__ = "machines"

    machine_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    factory_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("factories.factory_id", ondelete="CASCADE"), nullable=False, index=True
    )
    machine_code: Mapped[str] = mapped_column(String(50), nullable=False)
    machine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    machine_type: Mapped[str] = mapped_column(String(50), nullable=False)
    station: Mapped[str] = mapped_column(String(50), nullable=False, default="LINE_01")
    line_id: Mapped[str] = mapped_column(String(50), nullable=False, default="LINE_01")
    design_cycle_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_vibration_mms: Mapped[float] = mapped_column(Float, nullable=False, default=1.2)
    alert_vibration_mms: Mapped[float] = mapped_column(Float, nullable=False, default=3.8)
    critical_vibration_mms: Mapped[float] = mapped_column(Float, nullable=False, default=5.5)
    rated_capacity_units_per_hour: Mapped[float] = mapped_column(Float, nullable=False, default=60.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPERATIONAL")
    installation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "critical_vibration_mms > alert_vibration_mms",
            name="chk_machine_vibration_order",
        ),
        Index("idx_machine_factory_status", "factory_id", "status"),
    )

    # Relationships
    factory: Mapped["Factory"] = relationship("Factory", back_populates="machines")
    sensors: Mapped[List["Sensor"]] = relationship(
        "Sensor", back_populates="machine", cascade="all, delete-orphan"
    )
    production_jobs: Mapped[List["ProductionJob"]] = relationship(
        "ProductionJob", back_populates="machine", cascade="all, delete-orphan"
    )
    maintenance_records: Mapped[List["MaintenanceRecord"]] = relationship(
        "MaintenanceRecord", back_populates="machine", cascade="all, delete-orphan"
    )
    sensor_readings: Mapped[List["SensorReading"]] = relationship(
        "SensorReading", back_populates="machine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Machine {self.machine_id} ({self.machine_name})>"


class Sensor(Base, TimestampMixin):
    __tablename__ = "sensors"

    sensor_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    machine_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True
    )
    sensor_code: Mapped[str] = mapped_column(String(50), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    sampling_interval: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Relationships
    machine: Mapped["Machine"] = relationship("Machine", back_populates="sensors")
    readings: Mapped[List["SensorReading"]] = relationship(
        "SensorReading", back_populates="sensor", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sensor {self.sensor_id} ({self.sensor_type}) on {self.machine_id}>"


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    sku_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="units")
    unit_cost_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Relationships
    production_jobs: Mapped[List["ProductionJob"]] = relationship("ProductionJob", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product {self.sku_code}: {self.name}>"
