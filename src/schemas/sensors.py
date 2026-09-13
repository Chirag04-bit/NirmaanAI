"""
NirmaanAI Sensor & Telemetry Schemas (Pydantic v2)
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SensorResponse(BaseModel):
    """Physical sensor metadata."""
    model_config = ConfigDict(from_attributes=True)

    sensor_id: str
    machine_id: str
    sensor_code: str
    sensor_type: str
    unit: str
    sampling_interval: float
    is_active: bool
    created_at: Optional[datetime] = None


class SensorReadingResponse(BaseModel):
    """Time-series sensor reading record."""
    model_config = ConfigDict(from_attributes=True)

    reading_id: int
    sensor_id: Optional[str] = None
    machine_id: str
    timestamp: datetime
    value: float
    quality_flag: str = "GOOD"
    source: Optional[str] = None


class TelemetrySnapshotResponse(BaseModel):
    """Multi-channel machine telemetry snapshot."""
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: int
    machine_id: str
    timestamp: datetime
    vibration_mms: float
    temperature_c: float
    ambient_temperature_c: Optional[float] = None
    rotational_speed_rpm: Optional[float] = None
    torque_nm: Optional[float] = None
    sound_db: Optional[float] = None
    power_consumption_kw: Optional[float] = None
    oil_level_pct: Optional[float] = None
    coolant_level_pct: Optional[float] = None
    tool_wear_min: Optional[float] = None


class TelemetryQueryParams(BaseModel):
    """Bounded query parameters for telemetry retrieval."""
    start: Optional[datetime] = Field(default=None, description="Start timestamp (inclusive, UTC).")
    end: Optional[datetime] = Field(default=None, description="End timestamp (inclusive, UTC).")
    limit: int = Field(default=100, ge=1, le=1000, description="Max records to return (1-1000).")

    @model_validator(mode="after")
    def validate_time_range(self) -> "TelemetryQueryParams":
        if self.start and self.end and self.start > self.end:
            raise ValueError("Query parameter 'start' must be less than or equal to 'end'.")
        return self
