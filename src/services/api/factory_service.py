"""
NirmaanAI Factory API Service
Provides query execution and aggregated overview assembly for factory physical topology.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.factory import Factory, Machine
from src.db.models.ai_outputs import FactoryHealthScore, FinancialLossRecord, OperationalRecommendation
from src.schemas.factories import FactoryOverviewResponse, FactoryResponse
from src.schemas.common import ResponseMetadata
from src.db.seed.seeder import DECISION_CUTOFF


class FactoryApiService:
    @staticmethod
    def list_factories(db: Session, page: int = 1, page_size: int = 50) -> Tuple[List[FactoryResponse], int]:
        total = db.scalar(select(func.count()).select_from(Factory)) or 0
        offset = (page - 1) * page_size
        query = select(Factory).order_by(Factory.factory_id).offset(offset).limit(page_size)
        factories = db.scalars(query).all()
        items = [FactoryResponse.model_validate(f) for f in factories]
        return items, total

    @staticmethod
    def get_factory(db: Session, factory_id: str) -> Optional[FactoryResponse]:
        factory = db.scalar(select(Factory).where(Factory.factory_id == factory_id))
        if not factory:
            return None
        return FactoryResponse.model_validate(factory)

    @staticmethod
    def get_factory_overview(db: Session, factory_id: str) -> Optional[FactoryOverviewResponse]:
        factory = db.scalar(select(Factory).where(Factory.factory_id == factory_id))
        if not factory:
            return None

        # Machine counts
        total_machines = db.scalar(
            select(func.count()).select_from(Machine).where(Machine.factory_id == factory_id)
        ) or 0

        active_machines = db.scalar(
            select(func.count()).select_from(Machine).where(
                Machine.factory_id == factory_id,
                Machine.status.in_(["RUNNING", "IDLE"])
            )
        ) or 0

        # Health state & critical machine counts
        latest_health_query = (
            select(FactoryHealthScore)
            .where(FactoryHealthScore.factory_id == factory_id)
            .order_by(FactoryHealthScore.timestamp.desc())
        )
        health_records = db.scalars(latest_health_query).all()

        critical_count = 0
        plant_score = None
        plant_band = "HEALTHY"

        if health_records:
            scores = [h.health_score for h in health_records]
            plant_score = round(sum(scores) / len(scores), 2)
            for h in health_records:
                if h.health_state in ("CRITICAL", "DEGRADED"):
                    critical_count += 1
            if any(h.health_state == "CRITICAL" for h in health_records):
                plant_band = "WATCH"  # Plant capped at WATCH if any machine is CRITICAL
            elif plant_score >= 90:
                plant_band = "EXCELLENT"
            elif plant_score >= 75:
                plant_band = "HEALTHY"
            elif plant_score >= 60:
                plant_band = "WATCH"
            else:
                plant_band = "DEGRADED"

        # Active recommendations count
        rec_count = db.scalar(
            select(func.count()).select_from(OperationalRecommendation).where(
                OperationalRecommendation.status == "PENDING"
            )
        ) or 0

        # Total plant gross financial exposure (INR)
        gross_loss_records = db.scalars(
            select(FinancialLossRecord).where(
                FinancialLossRecord.loss_type == "GROSS_EXPOSURE"
            )
        ).all()
        total_gross_inr = round(sum(r.total_loss_inr for r in gross_loss_records), 2)
        if total_gross_inr == 0.0:
            # Fallback to sum of realized + baseline opp cost if GROSS_EXPOSURE not pre-aggregated
            loss_records = db.scalars(
                select(FinancialLossRecord).where(
                    FinancialLossRecord.loss_type.in_(["REALIZED_LOSS", "PROJECTED_OPPORTUNITY_COST"])
                )
            ).all()
            total_gross_inr = round(sum(r.total_loss_inr for r in loss_records), 2)

        metadata = ResponseMetadata(
            as_of_timestamp=DECISION_CUTOFF,
            source="PHASE_17_POSTGRES_PERSISTENCE",
            dataset_version="SYNTHETIC_FACTORY_V1",
            epistemic_status="COMPOSITE_INDEX",
        )

        return FactoryOverviewResponse(
            factory_id=factory.factory_id,
            factory_name=factory.name,
            total_machines=total_machines,
            active_machines=active_machines,
            critical_machines=critical_count,
            plant_health_score=plant_score,
            plant_health_state=plant_band,
            active_recommendations_count=rec_count,
            total_gross_exposure_inr=total_gross_inr,
            metadata=metadata,
        )
