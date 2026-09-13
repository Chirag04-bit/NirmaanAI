"""
NirmaanAI Recommendations API Service
Exposes Phase 15 prescriptive recommendations.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.ai_outputs import OperationalRecommendation
from src.schemas.recommendations import RecommendationResponse


class RecommendationApiService:
    @staticmethod
    def list_recommendations(
        db: Session,
        machine_id: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        urgency: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[RecommendationResponse], int]:
        stmt = select(OperationalRecommendation)
        if machine_id:
            stmt = stmt.where(OperationalRecommendation.machine_id == machine_id)
        if category:
            stmt = stmt.where(OperationalRecommendation.category == category)
        if priority:
            stmt = stmt.where(OperationalRecommendation.priority == priority)
        if urgency:
            stmt = stmt.where(OperationalRecommendation.urgency == urgency)
        if status:
            stmt = stmt.where(OperationalRecommendation.status == status)

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(OperationalRecommendation.created_at.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [RecommendationResponse.model_validate(r) for r in records], total

    @staticmethod
    def get_recommendation(db: Session, recommendation_id: str) -> Optional[RecommendationResponse]:
        rec = db.scalar(
            select(OperationalRecommendation).where(OperationalRecommendation.recommendation_id == recommendation_id)
        )
        if not rec:
            return None
        return RecommendationResponse.model_validate(rec)
