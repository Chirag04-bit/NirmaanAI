"""
NirmaanAI Financial API Service
Preserves strict separation between realized losses, baseline opportunity costs,
gross exposure bounds, and counterfactual avoided opportunity costs.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.ai_outputs import FinancialLossRecord
from src.schemas.finance import FinancialLossResponse, MachineFinancialSummaryResponse
from src.db.seed.seeder import DECISION_CUTOFF


class FinanceApiService:
    @staticmethod
    def list_losses(
        db: Session,
        machine_id: Optional[str] = None,
        loss_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[FinancialLossResponse], int]:
        stmt = select(FinancialLossRecord)
        if machine_id:
            stmt = stmt.where(FinancialLossRecord.machine_id == machine_id)
        if loss_type:
            stmt = stmt.where(FinancialLossRecord.loss_type == loss_type)

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(FinancialLossRecord.timestamp.desc(), FinancialLossRecord.loss_id).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [FinancialLossResponse.model_validate(r) for r in records], total

    @staticmethod
    def get_machine_finance_summary(db: Session, machine_id: str) -> MachineFinancialSummaryResponse:
        records = db.scalars(
            select(FinancialLossRecord).where(FinancialLossRecord.machine_id == machine_id)
        ).all()

        realized_rec = next((r for r in records if r.loss_type == "REALIZED_LOSS"), None)
        opp_rec = next((r for r in records if r.loss_type == "PROJECTED_OPPORTUNITY_COST"), None)
        gross_rec = next((r for r in records if r.loss_type == "GROSS_EXPOSURE"), None)
        avoided_rec = next((r for r in records if r.loss_type == "AVOIDED_OPPORTUNITY_COST"), None)

        realized_tot = realized_rec.total_loss_inr if realized_rec else 0.0
        opp_tot = opp_rec.total_loss_inr if opp_rec else 0.0
        gross_tot = gross_rec.total_loss_inr if gross_rec else round(realized_tot + opp_tot, 2)
        avoided_tot = avoided_rec.total_loss_inr if avoided_rec else None

        remaining_gross = round(gross_tot - avoided_tot, 2) if avoided_tot is not None else None

        return MachineFinancialSummaryResponse(
            machine_id=machine_id,
            as_of_timestamp=DECISION_CUTOFF,
            realized_historical_loss_inr=realized_tot,
            realized_downtime_loss_inr=realized_rec.downtime_loss_inr if realized_rec else 0.0,
            realized_scrap_loss_inr=realized_rec.scrap_loss_inr if realized_rec else 0.0,
            realized_rework_loss_inr=realized_rec.rework_loss_inr if realized_rec else 0.0,
            realized_emergency_labor_inr=realized_rec.emergency_labor_loss_inr if realized_rec else 0.0,
            realized_energy_inefficiency_inr=realized_rec.energy_loss_inr if realized_rec else 0.0,
            baseline_projected_opportunity_cost_inr=opp_tot,
            baseline_gross_financial_exposure_inr=gross_tot,
            counterfactual_avoided_opportunity_cost_inr=avoided_tot,
            counterfactual_remaining_gross_exposure_inr=remaining_gross,
            epistemic_status="FINANCIAL_SUMMARY_SEGREGATED",
        )
