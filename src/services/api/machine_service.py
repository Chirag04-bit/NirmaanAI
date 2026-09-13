"""
NirmaanAI Machine API Service
Assembles multi-signal machine overview separating OBSERVED, MODEL_INFERENCE, COMPOSITE_INDEX, and COUNTERFACTUAL.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.factory import Machine
from src.db.models.operations import InventoryItem
from src.db.models.ai_outputs import (
    AnomalyDetectionResult,
    BottleneckPredictionResult,
    FactoryHealthScore,
    FinancialLossRecord,
    OperationalRecommendation,
    PredictiveMaintenancePrediction,
)
from src.schemas.machines import MachineOverviewResponse, MachineResponse
from src.schemas.common import ResponseMetadata
from src.db.seed.seeder import DECISION_CUTOFF


class MachineApiService:
    @staticmethod
    def list_machines(
        db: Session,
        factory_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[MachineResponse], int]:
        stmt = select(Machine)
        if factory_id:
            stmt = stmt.where(Machine.factory_id == factory_id)
        if status:
            stmt = stmt.where(Machine.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Machine.machine_id).offset(offset).limit(page_size)
        machines = db.scalars(stmt).all()
        items = [MachineResponse.model_validate(m) for m in machines]
        return items, total

    @staticmethod
    def get_machine(db: Session, machine_id: str) -> Optional[MachineResponse]:
        machine = db.scalar(select(Machine).where(Machine.machine_id == machine_id))
        if not machine:
            return None
        return MachineResponse.model_validate(machine)

    @staticmethod
    def get_machine_overview(db: Session, machine_id: str) -> Optional[MachineOverviewResponse]:
        machine = db.scalar(select(Machine).where(Machine.machine_id == machine_id))
        if not machine:
            return None

        # 1. Predictive Maintenance (Phase 6)
        pdm = db.scalar(
            select(PredictiveMaintenancePrediction)
            .where(PredictiveMaintenancePrediction.machine_id == machine_id)
            .order_by(PredictiveMaintenancePrediction.prediction_timestamp.desc())
        )
        fp = pdm.failure_probability if pdm else None
        pdm_thresh = pdm.threshold if pdm else 0.91
        pdm_alert = (fp >= pdm_thresh) if fp is not None else False

        # 2. Anomaly Detection (Phase 7)
        anom = db.scalar(
            select(AnomalyDetectionResult)
            .where(AnomalyDetectionResult.machine_id == machine_id)
            .order_by(AnomalyDetectionResult.timestamp.desc())
        )
        anom_score = anom.anomaly_score if anom else None
        anom_thresh = anom.threshold if anom else 0.24050
        anom_status = anom.anomaly_status if anom else "NORMAL"

        # 3. Bottleneck (Phase 8)
        bn = db.scalar(
            select(BottleneckPredictionResult)
            .where(BottleneckPredictionResult.machine_id == machine_id)
            .order_by(BottleneckPredictionResult.timestamp.desc())
        )
        bn_status = bn.bottleneck_status if bn else "NOMINAL_FLOW"

        # 4. Composite Health (Phase 13)
        health = db.scalar(
            select(FactoryHealthScore)
            .where(FactoryHealthScore.machine_id == machine_id)
            .order_by(FactoryHealthScore.timestamp.desc())
        )
        h_score = health.health_score if health else None
        h_state = health.health_state if health else "HEALTHY"

        # 5. Inventory & Spares Context (Phase 10)
        # Match SKU for this machine (e.g. SKU_SPINDLE_BEARING_M2)
        inv = db.scalar(
            select(InventoryItem)
            .where(InventoryItem.sku_id.like(f"%_{machine_id}%"))
        )
        spare_sku = inv.sku_id if inv else None
        c_stock = inv.current_stock if inv else None
        s_stock = inv.safety_stock if inv else None
        r_point = inv.reorder_point if inv else None
        inv_status = "OPTIMAL_BUFFER"
        if inv:
            if inv.current_stock < inv.safety_stock:
                inv_status = "CRITICAL_DEFICIT"
            elif inv.current_stock < inv.reorder_point:
                inv_status = "REORDER_NOW"

        # 6. Financial Loss & Exposure (Phase 14)
        loss_records = db.scalars(
            select(FinancialLossRecord).where(FinancialLossRecord.machine_id == machine_id)
        ).all()
        realized_loss = 0.0
        gross_exposure = 0.0
        opp_loss = 0.0
        for r in loss_records:
            if r.loss_type == "REALIZED_LOSS":
                realized_loss = r.total_loss_inr
            elif r.loss_type == "PROJECTED_OPPORTUNITY_COST":
                opp_loss = r.total_loss_inr
            elif r.loss_type == "GROSS_EXPOSURE":
                gross_exposure = r.total_loss_inr
        if gross_exposure == 0.0:
            gross_exposure = round(realized_loss + opp_loss, 2)

        # 7. Recommendations (Phase 15)
        from sqlalchemy import case
        priority_order = case(
            (OperationalRecommendation.priority == "CRITICAL", 1),
            (OperationalRecommendation.priority == "HIGH", 2),
            (OperationalRecommendation.priority == "MEDIUM", 3),
            else_=4,
        )
        recs = db.scalars(
            select(OperationalRecommendation)
            .where(
                OperationalRecommendation.machine_id == machine_id,
                OperationalRecommendation.status == "PENDING"
            )
            .order_by(priority_order, OperationalRecommendation.created_at.desc())
        ).all()
        rec_count = len(recs)
        top_action = recs[0].action if recs else None

        metadata = ResponseMetadata(
            as_of_timestamp=DECISION_CUTOFF,
            source="PHASE_17_POSTGRES_PERSISTENCE",
            dataset_version="SYNTHETIC_FACTORY_V1",
            epistemic_status="MULTI_SIGNAL_SYNTHESIS",
        )

        return MachineOverviewResponse(
            machine_id=machine.machine_id,
            machine_name=machine.machine_name,
            machine_type=machine.machine_type,
            status=machine.status,
            station=machine.station,
            design_cycle_time_sec=machine.design_cycle_time_sec,
            baseline_vibration_mms=machine.baseline_vibration_mms,
            alert_vibration_mms=machine.alert_vibration_mms,
            critical_vibration_mms=machine.critical_vibration_mms,
            failure_probability=fp,
            pdm_threshold=pdm_thresh,
            pdm_alert=pdm_alert,
            anomaly_score=anom_score,
            anomaly_threshold=anom_thresh,
            anomaly_status=anom_status,
            bottleneck_status=bn_status,
            health_score=h_score,
            health_state=h_state,
            spare_sku=spare_sku,
            current_stock=c_stock,
            safety_stock=s_stock,
            reorder_point=r_point,
            inventory_status=inv_status,
            realized_historical_loss_inr=realized_loss,
            gross_financial_exposure_inr=gross_exposure,
            active_recommendations_count=rec_count,
            top_recommendation_action=top_action,
            metadata=metadata,
        )
