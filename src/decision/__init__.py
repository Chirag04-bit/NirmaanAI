"""
NirmaanAI Decision & Loss Analysis Subsystem
Phase 14: Operational & Financial Loss Analysis (INR)
"""

from src.decision.loss_models import (
    EpistemicClassification,
    FactoryLossSummary,
    LossCategory,
    LossItem,
    MachineLossBreakdown,
)
from src.decision.loss_engine import (
    DEFAULT_BASE_ELECTRICITY_RATE_INR_PER_KWH,
    DEFAULT_CONTRIBUTION_MARGIN_PER_UNIT_INR,
    DEFAULT_DOWNTIME_RATE_INR_PER_HOUR,
    DEFAULT_PEAK_ELECTRICITY_RATE_INR_PER_KWH,
    DEFAULT_REWORK_RATE_INR_PER_HOUR,
    DEFAULT_SCRAP_RATE_INR_PER_KG,
    DEFAULT_UNIT_MASS_KG,
    DOCUMENTED_POWER_BASELINES_KW,
    calculate_bottleneck_opportunity_cost,
    calculate_downtime_loss,
    calculate_emergency_maintenance_labor_loss,
    calculate_energy_consumption_and_cost,
    calculate_energy_inefficiency_loss,
    calculate_rework_loss,
    calculate_scrap_loss,
    get_applicable_tariff,
    is_peak_tariff_hour,
    round_inr,
    validate_non_negative,
    verify_no_pseudo_financial_coupling,
)
from src.decision.loss_service import FinancialLossService

__all__ = [
    "EpistemicClassification",
    "LossCategory",
    "LossItem",
    "MachineLossBreakdown",
    "FactoryLossSummary",
    "FinancialLossService",
    "calculate_downtime_loss",
    "calculate_emergency_maintenance_labor_loss",
    "calculate_energy_consumption_and_cost",
    "calculate_energy_inefficiency_loss",
    "calculate_scrap_loss",
    "calculate_rework_loss",
    "calculate_bottleneck_opportunity_cost",
    "get_applicable_tariff",
    "is_peak_tariff_hour",
    "round_inr",
    "validate_non_negative",
    "verify_no_pseudo_financial_coupling",
    "DEFAULT_DOWNTIME_RATE_INR_PER_HOUR",
    "DEFAULT_BASE_ELECTRICITY_RATE_INR_PER_KWH",
    "DEFAULT_PEAK_ELECTRICITY_RATE_INR_PER_KWH",
    "DEFAULT_SCRAP_RATE_INR_PER_KG",
    "DEFAULT_REWORK_RATE_INR_PER_HOUR",
    "DEFAULT_CONTRIBUTION_MARGIN_PER_UNIT_INR",
    "DEFAULT_UNIT_MASS_KG",
    "DOCUMENTED_POWER_BASELINES_KW",
]
