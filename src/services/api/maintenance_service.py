"""
NirmaanAI Maintenance Records API Service
Enforces temporal boundary between prospective decision evidence (<= cutoff)
and retrospective synthetic ground truth (MAINT_0003).
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.operations import MaintenanceRecord
from src.schemas.maintenance import MaintenanceRecordResponse
from src.db.seed.seeder import DECISION_CUTOFF


class MaintenanceApiService:
    @staticmethod
    def list_maintenance(
        db: Session,
        machine_id: Optional[str] = None,
        include_retrospective: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[MaintenanceRecordResponse], int]:
        stmt = select(MaintenanceRecord)
        if machine_id:
            stmt = stmt.where(MaintenanceRecord.machine_id == machine_id)

        # By default, exclude retrospective post-cutoff records to prevent decision leakage
        if not include_retrospective:
            stmt = stmt.where(MaintenanceRecord.is_decision_input.is_(True))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(MaintenanceRecord.timestamp.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        items = [MaintenanceRecordResponse.model_validate(r) for r in records]
        return items, total

    @staticmethod
    def get_maintenance_record(db: Session, maintenance_id: str) -> Optional[MaintenanceRecordResponse]:
        rec = db.scalar(select(MaintenanceRecord).where(MaintenanceRecord.maintenance_id == maintenance_id))
        if not rec:
            return None
        return MaintenanceRecordResponse.model_validate(rec)
