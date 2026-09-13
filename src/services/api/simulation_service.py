"""
NirmaanAI Simulation API Service
Exposes Phase 16 What-If Counterfactual Scenarios.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.ai_outputs import SimulationScenario
from src.schemas.simulations import SimulationScenarioResponse


class SimulationApiService:
    @staticmethod
    def list_scenarios(
        db: Session,
        machine_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[SimulationScenarioResponse], int]:
        stmt = select(SimulationScenario)
        if machine_id:
            stmt = stmt.where(SimulationScenario.machine_id == machine_id)

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(SimulationScenario.decision_cutoff.desc(), SimulationScenario.scenario_id).offset(offset).limit(page_size)
        records = db.scalars(stmt).all()
        return [SimulationScenarioResponse.model_validate(r) for r in records], total

    @staticmethod
    def get_scenario(db: Session, scenario_id: str) -> Optional[SimulationScenarioResponse]:
        rec = db.scalar(
            select(SimulationScenario).where(SimulationScenario.scenario_id == scenario_id)
        )
        if not rec:
            return None
        return SimulationScenarioResponse.model_validate(rec)
