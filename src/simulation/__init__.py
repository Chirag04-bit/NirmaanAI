"""
NirmaanAI Digital-Twin-Inspired What-If Simulation Subsystem
Phase 16: What-If / Digital-Twin-Inspired Simulation Engine
"""

from src.simulation.simulation_models import (
    KPIDeltaVector,
    OperationalKPIVector,
    ProjectionConfidence,
    ScenarioAssumption,
    ScenarioComparisonReport,
    SensitivityTier,
    SimulationInterventionType,
    WhatIfScenario,
)
from src.simulation.scenario_definitions import (
    CONTRIBUTION_MARGIN_PER_UNIT_INR,
    DOWNTIME_HOURLY_RATE_INR,
    REWORK_HOURLY_RATE_INR,
    compute_kpi_delta,
    get_m1_negative_control_baseline_kpi_vector,
    get_m2_baseline_kpi_vector,
)
from src.simulation.simulation_engine import WhatIfSimulationEngine
from src.simulation.simulation_service import WhatIfSimulationService

__all__ = [
    "SimulationInterventionType",
    "ProjectionConfidence",
    "SensitivityTier",
    "OperationalKPIVector",
    "KPIDeltaVector",
    "ScenarioAssumption",
    "WhatIfScenario",
    "ScenarioComparisonReport",
    "WhatIfSimulationEngine",
    "WhatIfSimulationService",
    "get_m2_baseline_kpi_vector",
    "get_m1_negative_control_baseline_kpi_vector",
    "compute_kpi_delta",
    "DOWNTIME_HOURLY_RATE_INR",
    "REWORK_HOURLY_RATE_INR",
    "CONTRIBUTION_MARGIN_PER_UNIT_INR",
]
