"""
NirmaanAI Telemetry API Service
Provides bounded queries for multi-channel snapshots and normalized readings.
Enforces limits and time-range validity.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.operations import MachineTelemetrySnapshot, SensorReading
from src.schemas.sensors import SensorReadingResponse, TelemetrySnapshotResponse


class TelemetryApiService:
    @staticmethod
    def get_machine_telemetry(
        db: Session,
        machine_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[TelemetrySnapshotResponse]:
        limit = min(max(1, limit), 1000)
        stmt = (
            select(MachineTelemetrySnapshot)
            .where(MachineTelemetrySnapshot.machine_id == machine_id)
        )
        if start:
            stmt = stmt.where(MachineTelemetrySnapshot.timestamp >= start)
        if end:
            stmt = stmt.where(MachineTelemetrySnapshot.timestamp <= end)

        stmt = stmt.order_by(MachineTelemetrySnapshot.timestamp.desc()).limit(limit)
        records = db.scalars(stmt).all()
        return [TelemetrySnapshotResponse.model_validate(r) for r in records]

    @staticmethod
    def get_sensor_readings(
        db: Session,
        sensor_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SensorReadingResponse]:
        limit = min(max(1, limit), 1000)
        stmt = (
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor_id)
        )
        if start:
            stmt = stmt.where(SensorReading.timestamp >= start)
        if end:
            stmt = stmt.where(SensorReading.timestamp <= end)

        stmt = stmt.order_by(SensorReading.timestamp.desc()).limit(limit)
        records = db.scalars(stmt).all()
        return [SensorReadingResponse.model_validate(r) for r in records]
