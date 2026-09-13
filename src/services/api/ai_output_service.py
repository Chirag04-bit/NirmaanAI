"""
NirmaanAI Subsystems AI Output API Service
Exposes Phase 6, 7, 8, 9, 11, 12, 13 persisted intelligence.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.ai_outputs import (
    AnomalyDetectionResult,
    BottleneckPredictionResult,
    FactoryHealthScore,
    ForecastingResult,
    PredictiveMaintenancePrediction,
    RcaResult,
    ShapExplanation,
)
from src.schemas.ai_outputs import (
    AnomalyDetectionResponse,
    BottleneckResponse,
    FactoryHealthScoreResponse,
    ForecastingResponse,
    PredictiveMaintenanceResponse,
    RcaResultResponse,
    ShapExplanationResponse,
)


class AiOutputApiService:
    # 1. Predictive Maintenance (Phase 6)
    @staticmethod
    def get_pdm_predictions(
        db: Session,
        machine_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[PredictiveMaintenanceResponse], int]:
        stmt = select(PredictiveMaintenancePrediction)
        if machine_id:
            stmt = stmt.where(PredictiveMaintenancePrediction.machine_id == machine_id)
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(PredictiveMaintenancePrediction.prediction_timestamp.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [PredictiveMaintenanceResponse.model_validate(r) for r in records], total

    # 2. Anomaly Detection (Phase 7)
    @staticmethod
    def get_anomaly_results(
        db: Session,
        machine_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AnomalyDetectionResponse], int]:
        stmt = select(AnomalyDetectionResult)
        if machine_id:
            stmt = stmt.where(AnomalyDetectionResult.machine_id == machine_id)
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(AnomalyDetectionResult.timestamp.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [AnomalyDetectionResponse.model_validate(r) for r in records], total

    # 3. Bottleneck Prediction (Phase 8)
    @staticmethod
    def get_bottleneck_results(
        db: Session,
        machine_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[BottleneckResponse], int]:
        stmt = select(BottleneckPredictionResult)
        if machine_id:
            stmt = stmt.where(BottleneckPredictionResult.machine_id == machine_id)
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(BottleneckPredictionResult.timestamp.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [BottleneckResponse.model_validate(r) for r in records], total

    # 4. Forecasting (Phase 9)
    @staticmethod
    def get_forecasts(
        db: Session,
        target_series: Optional[str] = None,
        horizon_hours: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ForecastingResponse], int]:
        stmt = select(ForecastingResult)
        if target_series:
            stmt = stmt.where(ForecastingResult.target_series == target_series)
        if horizon_hours:
            stmt = stmt.where(ForecastingResult.horizon_hours == horizon_hours)
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(ForecastingResult.forecast_timestamp.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [ForecastingResponse.model_validate(r) for r in records], total

    # 5. SHAP Feature Attribution (Phase 11)
    @staticmethod
    def get_shap_explanations(db: Session, machine_id: str) -> List[ShapExplanationResponse]:
        stmt = (
            select(ShapExplanation)
            .where(ShapExplanation.machine_id == machine_id)
            .order_by(ShapExplanation.ranking.asc())
        )
        records = db.scalars(stmt).all()
        return [ShapExplanationResponse.model_validate(r) for r in records]

    # 6. Root Cause Analysis (Phase 12)
    @staticmethod
    def get_rca_results(db: Session, machine_id: str) -> List[RcaResultResponse]:
        stmt = (
            select(RcaResult)
            .where(RcaResult.machine_id == machine_id)
            .order_by(RcaResult.event_timestamp.desc())
        )
        records = db.scalars(stmt).all()
        return [RcaResultResponse.model_validate(r) for r in records]

    # 7. Factory Health Scores (Phase 13)
    @staticmethod
    def get_health_scores(
        db: Session,
        machine_id: Optional[str] = None,
        factory_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[FactoryHealthScoreResponse], int]:
        stmt = select(FactoryHealthScore)
        if machine_id:
            stmt = stmt.where(FactoryHealthScore.machine_id == machine_id)
        if factory_id:
            stmt = stmt.where(FactoryHealthScore.factory_id == factory_id)
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(FactoryHealthScore.timestamp.desc()).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [FactoryHealthScoreResponse.model_validate(r) for r in records], total
