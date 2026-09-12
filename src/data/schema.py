"""
NirmaanAI Unified Factory Data Schema — Validation & Domain Entity Models
Provides strictly typed, validated Pydantic v2 models representing the digital factory brain.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ==============================================================================
# Domain Enumerations
# ==============================================================================

class MachineStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class JobStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    FAILED = "FAILED"


class FailureMode(str, Enum):
    NONE = "NONE"
    TWF = "TWF"                    # Tool Wear Failure
    HDF = "HDF"                    # Heat Dissipation Failure
    PWF = "PWF"                    # Power Failure
    OSF = "OSF"                    # Overstrain Failure
    RNF = "RNF"                    # Random Failure
    BEARING_WEAR = "BEARING_WEAR"  # Spindle / Bearing Degradation
    LUBRICATION_FAILURE = "LUBRICATION_FAILURE"
    ELECTRICAL_FAULT = "ELECTRICAL_FAULT"
    OTHER = "OTHER"


class HealthState(str, Enum):
    EXCELLENT = "EXCELLENT"        # 90.0 - 100.0
    GOOD = "GOOD"                  # 75.0 - 89.9
    WARNING = "WARNING"            # 50.0 - 74.9
    CRITICAL = "CRITICAL"          # 0.0 - 49.9


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ==============================================================================
# 1. Machine Entity
# ==============================================================================

class Machine(BaseModel):
    machine_id: str = Field(..., description="Unique machine identifier, e.g., MC_001, M2")
    name: str = Field(..., description="Human-readable machine name")
    machine_type: str = Field(..., description="Machine category: VMC Milling, CNC Lathe, Loom, Grinder")
    line_id: str = Field(default="LINE_01", description="Production line identifier")
    design_cycle_time_sec: float = Field(..., gt=0.0, description="Nominal cycle time per unit in seconds")
    baseline_power_kw: float = Field(..., ge=0.0, description="Nominal power consumption in kW")
    baseline_vibration_mms: float = Field(default=1.2, ge=0.0, description="Normal baseline vibration in mm/s")
    alert_vibration_mms: float = Field(default=3.8, gt=0.0, description="Warning vibration threshold in mm/s")
    critical_vibration_mms: float = Field(default=5.5, gt=0.0, description="Critical shutdown vibration threshold in mm/s")
    rated_capacity_units_per_hour: float = Field(default=60.0, gt=0.0, description="Nominal maximum units per hour")
    status: MachineStatus = Field(default=MachineStatus.OPERATIONAL, description="Current operational state")
    installation_year: Optional[int] = Field(default=None, description="Year machine was commissioned")

    @model_validator(mode="after")
    def validate_vibration_thresholds(self):
        if self.critical_vibration_mms <= self.alert_vibration_mms:
            raise ValueError(
                f"critical_vibration_mms ({self.critical_vibration_mms}) must be greater than alert_vibration_mms ({self.alert_vibration_mms})"
            )
        return self


# ==============================================================================
# 2. Sensor Telemetry Entity
# ==============================================================================

class SensorReading(BaseModel):
    reading_id: Optional[int] = Field(default=None, description="Sequential or auto-incremented reading ID")
    machine_id: str = Field(..., description="Target machine identifier foreign key")
    timestamp: datetime = Field(..., description="Timestamp of the sensor observation (UTC)")
    vibration_mms: float = Field(..., ge=0.0, description="Measured RMS vibration velocity in mm/s")
    temperature_c: float = Field(..., description="Process or casing temperature in Celsius")
    ambient_temperature_c: Optional[float] = Field(default=None, description="Ambient air temperature in Celsius")
    rotational_speed_rpm: Optional[float] = Field(default=None, ge=0.0, description="Spindle rotational speed in RPM")
    torque_nm: Optional[float] = Field(default=None, ge=0.0, description="Spindle torque in Nm")
    sound_db: Optional[float] = Field(default=None, ge=0.0, description="Acoustic emission in dB")
    power_consumption_kw: Optional[float] = Field(default=None, ge=0.0, description="Active power consumption in kW")
    oil_level_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Lubricant oil level percentage")
    coolant_level_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Coolant fluid level percentage")
    tool_wear_min: Optional[float] = Field(default=None, ge=0.0, description="Cumulative tool wear in minutes")

    @property
    def temperature_difference_k(self) -> Optional[float]:
        """Computes delta T between process and ambient if available."""
        if self.ambient_temperature_c is not None:
            return self.temperature_c - self.ambient_temperature_c
        return None

    @property
    def mechanical_power_kw(self) -> Optional[float]:
        """Computes mechanical output power (2*pi*RPM*Torque / 60,000) if RPM and Torque are present."""
        if self.rotational_speed_rpm is not None and self.torque_nm is not None:
            import math
            return (2 * math.pi * self.rotational_speed_rpm * self.torque_nm) / 60000.0
        return None


# ==============================================================================
# 3. Production Job Entity
# ==============================================================================

class ProductionJob(BaseModel):
    job_id: str = Field(..., description="Unique job/batch identifier, e.g., J_1001")
    machine_id: str = Field(..., description="Assigned machine identifier")
    operation_type: str = Field(..., description="Operation type: Milling, Turning, Weaving, Grinding")
    scheduled_start: datetime = Field(..., description="Planned start timestamp")
    scheduled_end: datetime = Field(..., description="Planned completion timestamp")
    actual_start: Optional[datetime] = Field(default=None, description="Recorded start timestamp")
    actual_end: Optional[datetime] = Field(default=None, description="Recorded completion timestamp")
    batch_quantity: int = Field(..., gt=0, description="Total units scheduled for production")
    completed_quantity: int = Field(default=0, ge=0, description="Good units completed")
    scrap_quantity: int = Field(default=0, ge=0, description="Defective/scrapped units produced")
    actual_cycle_time_sec: Optional[float] = Field(default=None, ge=0.0, description="Observed average cycle time per unit")
    status: JobStatus = Field(default=JobStatus.SCHEDULED, description="Job execution status")

    @model_validator(mode="after")
    def validate_job_timings(self):
        if self.scheduled_end < self.scheduled_start:
            raise ValueError(
                f"scheduled_end ({self.scheduled_end}) cannot be earlier than scheduled_start ({self.scheduled_start})"
            )
        if self.actual_start and self.actual_end and self.actual_end < self.actual_start:
            raise ValueError(
                f"actual_end ({self.actual_end}) cannot be earlier than actual_start ({self.actual_start})"
            )
        if self.completed_quantity + self.scrap_quantity > self.batch_quantity:
            raise ValueError(
                f"Completed ({self.completed_quantity}) + Scrap ({self.scrap_quantity}) exceeds scheduled Batch Quantity ({self.batch_quantity})"
            )
        return self

    @property
    def start_delay_minutes(self) -> Optional[float]:
        """Calculates dispatch start delay in minutes."""
        if self.actual_start:
            delta = self.actual_start - self.scheduled_start
            return delta.total_seconds() / 60.0
        return None


# ==============================================================================
# 4. Maintenance Record Entity
# ==============================================================================

class MaintenanceRecord(BaseModel):
    record_id: str = Field(..., description="Unique maintenance record ID, e.g., MAINT_001")
    machine_id: str = Field(..., description="Serviced machine identifier")
    timestamp: datetime = Field(..., description="Timestamp maintenance event occurred")
    event_type: str = Field(..., description="PREVENTIVE, UNPLANNED_STOP, BREAKDOWN, TOOL_CHANGE")
    failure_mode: FailureMode = Field(default=FailureMode.NONE, description="Root cause failure category")
    downtime_minutes: float = Field(default=0.0, ge=0.0, description="Duration machine was halted in minutes")
    technician_id: str = Field(default="TECH_01", description="Technician responsible")
    corrective_action: str = Field(default="", description="Actions taken (lubrication, replacement, tuning)")
    notes: Optional[str] = Field(default=None, description="Free text technician log")


# ==============================================================================
# 5. Inventory Item Entity
# ==============================================================================

class InventoryItem(BaseModel):
    item_id: str = Field(..., description="Part or raw material SKU, e.g., SKU_STEEL_ROD_10MM")
    item_name: str = Field(..., description="Descriptive component name")
    category: str = Field(..., description="RAW_MATERIAL, WORK_IN_PROGRESS, FINISHED_GOOD, SPARE_PART")
    current_stock: float = Field(..., ge=0.0, description="Available stock on hand")
    safety_stock: float = Field(..., ge=0.0, description="Minimum buffer stock before stockout risk")
    unit_cost_inr: float = Field(..., ge=0.0, description="Unit cost in Indian Rupees")
    reorder_quantity: float = Field(default=100.0, gt=0.0, description="Standard purchase batch quantity")
    unit_of_measure: str = Field(default="kg", description="kg, units, meters, liters")

    @property
    def is_stockout_risk(self) -> bool:
        """Flags when current inventory dips below designated safety stock threshold."""
        return self.current_stock < self.safety_stock


# ==============================================================================
# 6. MSME Financial Parameters Entity
# ==============================================================================

from datetime import datetime, timezone

class FinancialParameters(BaseModel):
    config_id: str = Field(default="MSME_DEFAULT_RATES", description="Rate profile identifier")
    downtime_hourly_cost_inr: float = Field(default=4500.0, ge=0.0, description="Hourly downtime overhead loss in INR")
    base_electricity_rate_inr_per_kwh: float = Field(default=8.50, ge=0.0, description="Standard industrial electricity tariff")
    peak_electricity_rate_inr_per_kwh: float = Field(default=12.50, ge=0.0, description="Peak hours electricity tariff (18:00-22:00)")
    scrap_cost_rate_inr_per_kg: float = Field(default=350.0, ge=0.0, description="Material cost rate per kg scrapped")
    rework_hourly_labor_inr: float = Field(default=280.0, ge=0.0, description="Technician hourly rework labor rate")
    effective_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date rates became active")


# ==============================================================================
# 7. Factory Health Snapshot Entity
# ==============================================================================

class FactoryHealthSnapshot(BaseModel):
    snapshot_id: Optional[int] = Field(default=None, description="Snapshot identifier")
    machine_id: str = Field(..., description="Target machine identifier")
    timestamp: datetime = Field(..., description="Assessment timestamp")
    composite_health_score: float = Field(..., ge=0.0, le=100.0, description="Unified Health Score (0-100 scale)")
    vibration_health: float = Field(default=100.0, ge=0.0, le=100.0, description="Vibration health index")
    temperature_health: float = Field(default=100.0, ge=0.0, le=100.0, description="Thermal health index")
    cycle_efficiency_health: float = Field(default=100.0, ge=0.0, le=100.0, description="Cycle time efficiency index")
    maintenance_health: float = Field(default=100.0, ge=0.0, le=100.0, description="Maintenance wear index")
    health_state: HealthState = Field(default=HealthState.EXCELLENT, description="Discrete classification")
    contributing_anomaly: Optional[str] = Field(default=None, description="Primary degrading factor candidate")


# ==============================================================================
# 8. Operational & Financial Loss Record Entity
# ==============================================================================

class OperationalLossRecord(BaseModel):
    loss_id: Optional[int] = Field(default=None, description="Loss event identifier")
    machine_id: str = Field(..., description="Associated machine identifier")
    timestamp: datetime = Field(..., description="Timestamp loss calculated")
    downtime_minutes: float = Field(default=0.0, ge=0.0, description="Total downtime duration in minutes")
    downtime_loss_inr: float = Field(default=0.0, ge=0.0, description="Quantified downtime loss in INR")
    energy_wastage_kwh: float = Field(default=0.0, ge=0.0, description="Excess energy consumed in kWh")
    energy_loss_inr: float = Field(default=0.0, ge=0.0, description="Excess power cost in INR")
    scrap_quantity: int = Field(default=0, ge=0, description="Defective items scrapped")
    scrap_loss_inr: float = Field(default=0.0, ge=0.0, description="Scrap material loss in INR")
    rework_hours: float = Field(default=0.0, ge=0.0, description="Secondary correction technician hours")
    rework_loss_inr: float = Field(default=0.0, ge=0.0, description="Rework labor cost in INR")
    total_financial_loss_inr: float = Field(..., ge=0.0, description="Total composite rupee loss")

    @model_validator(mode="after")
    def validate_total_loss(self):
        computed_total = self.downtime_loss_inr + self.energy_loss_inr + self.scrap_loss_inr + self.rework_loss_inr
        if not (self.total_financial_loss_inr >= 0.0):
            raise ValueError("total_financial_loss_inr must be non-negative")
        return self
