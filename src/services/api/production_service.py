"""
NirmaanAI Production Jobs API Service
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.operations import ProductionJob
from src.schemas.production import ProductionJobResponse


class ProductionApiService:
    @staticmethod
    def list_jobs(
        db: Session,
        machine_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ProductionJobResponse], int]:
        stmt = select(ProductionJob)
        if machine_id:
            stmt = stmt.where(ProductionJob.machine_id == machine_id)
        if status:
            stmt = stmt.where(ProductionJob.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(ProductionJob.scheduled_start.desc()).offset(offset).limit(page_size)
        jobs = db.scalars(stmt).all()
        items = [ProductionJobResponse.model_validate(j) for j in jobs]
        return items, total

    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[ProductionJobResponse]:
        job = db.scalar(select(ProductionJob).where(ProductionJob.job_id == job_id))
        if not job:
            return None
        return ProductionJobResponse.model_validate(job)
