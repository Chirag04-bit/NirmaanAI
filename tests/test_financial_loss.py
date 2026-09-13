"""
NirmaanAI Financial & Operational Loss Test Suite
Phase 14: Operational & Financial Loss Analysis (INR)

Comprehensive unit, integration, and integrity test suite verifying:
1. Independent downtime loss calculation
2. Independent scrap material loss calculation
3. Independent rework labor loss calculation
4. Energy consumption and operational cost calculation
5. Energy baseline provenance (M1-M3 config, M4-M5 simulator metadata)
6. Peak tariff pricing schedule (18:00 to 22:00 at ₹12.50/kWh)
7. Base industrial tariff pricing (off-peak at ₹8.50/kWh)
8. Zero-loss nominal operation scenario
9. Strict negative physical input rejection (ValueError)
10. Bottleneck opportunity cost formulation & classification
11. Machine-level attribution across M1 to M5
12. Plant-wide aggregation and mathematical reconciliation
13. Strict temporal causal filtering (zero future leakage)
14. Historical replay reproducibility
15. Monetary rounding consistency (Indian Paise precision)
16. Reference artifact reconciliation with operational_losses.csv
17. Downtime vs bottleneck opportunity cost separation
18. Scrap material vs rework labor cost independence
19. Health score zero financial weight isolation
20. SHAP feature attribution zero financial weight isolation
21. RCA diagnostic candidate zero financial weight isolation
22. Epistemic provenance taxonomy enforcement
23. Machine 2 controlled synthetic degradation chain audit
24. Deterministic repeated execution stability
"""

from datetime import datetime, timezone
import pytest
import numpy as np
import pandas as pd

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


# ============================================================================
# 1. INDEPENDENT CALCULATION FORMULAS & VALIDATION
# ============================================================================

def test_independent_downtime_calculation():
    """Validates downtime_loss = hours * 4500.0 INR/hour."""
    assert calculate_downtime_loss(0.0) == 0.0
    assert calculate_downtime_loss(1.0) == 4500.00
    assert calculate_downtime_loss(2.5) == 11250.00
    assert calculate_downtime_loss(0.75) == 3375.00  # 45 minutes


def test_independent_scrap_calculation():
    """Validates scrap_loss = units * 0.8 kg * 350.0 INR/kg = units * 280.0 INR."""
    mass, loss = calculate_scrap_loss(0)
    assert mass == 0.0
    assert loss == 0.0

    mass, loss = calculate_scrap_loss(1)
    assert mass == 0.8
    assert loss == 280.00

    mass, loss = calculate_scrap_loss(10)
    assert mass == 8.0
    assert loss == 2800.00

    mass, loss = calculate_scrap_loss(76)
    assert mass == 60.8
    assert loss == 21280.00


def test_independent_rework_calculation():
    """Validates rework_loss = hours * 280.0 INR/hour."""
    assert calculate_rework_loss(0.0) == 0.0
    assert calculate_rework_loss(1.0) == 280.00
    assert calculate_rework_loss(1.5) == 420.00
    assert calculate_rework_loss(0.25) == 70.00


def test_energy_cost_calculation():
    """Validates kWh conversion and tariff cost."""
    # 22 kW for 1 hour at base rate 8.50
    kwh, cost = calculate_energy_consumption_and_cost(22.0, 1.0, 8.50)
    assert kwh == 22.0
    assert cost == 187.00

    # 22 kW for 5 minutes (5/60 hours) at peak rate 12.50
    kwh, cost = calculate_energy_consumption_and_cost(22.0, 5.0 / 60.0, 12.50)
    assert round(kwh, 4) == round(22.0 * (5.0 / 60.0), 4)
    assert cost == round_inr((22.0 * (5.0 / 60.0)) * 12.50)


def test_peak_vs_base_tariff():
    """Validates that peak tariff applies strictly to 18:00 to 22:00 hours."""
    peak_hours = [18, 19, 20, 21]
    off_peak_hours = [0, 5, 8, 12, 17, 22, 23]

    for h in peak_hours:
        assert is_peak_tariff_hour(h) is True
        assert get_applicable_tariff(h) == DEFAULT_PEAK_ELECTRICITY_RATE_INR_PER_KWH

    for h in off_peak_hours:
        assert is_peak_tariff_hour(h) is False
        assert get_applicable_tariff(h) == DEFAULT_BASE_ELECTRICITY_RATE_INR_PER_KWH


def test_energy_baseline_provenance():
    """Validates machine baseline ratings provenance."""
    assert DOCUMENTED_POWER_BASELINES_KW["M1"] == 15.0  # Configured in factory_defaults.yaml
    assert DOCUMENTED_POWER_BASELINES_KW["M2"] == 22.0  # Configured in factory_defaults.yaml
    assert DOCUMENTED_POWER_BASELINES_KW["M3"] == 11.0  # Configured in factory_defaults.yaml
    assert DOCUMENTED_POWER_BASELINES_KW["M4"] == 4.5   # Simulator metadata (machines.csv)
    assert DOCUMENTED_POWER_BASELINES_KW["M5"] == 7.5   # Simulator metadata (machines.csv)


def test_energy_inefficiency_loss():
    """Validates energy excess above baseline power."""
    # Power at or below baseline has zero excess
    exc_kwh, loss = calculate_energy_inefficiency_loss(20.0, 22.0, 1.0, 8.50)
    assert exc_kwh == 0.0
    assert loss == 0.0

    # Power above baseline: 27 kW vs 22 kW baseline (5 kW excess for 1 hour at 12.50 peak)
    exc_kwh, loss = calculate_energy_inefficiency_loss(27.0, 22.0, 1.0, 12.50)
    assert exc_kwh == 5.0
    assert loss == 62.50


def test_bottleneck_opportunity_cost():
    """Validates opportunity cost = lost_units * 320.0 INR/unit."""
    assert calculate_bottleneck_opportunity_cost(0.0) == 0.0
    assert calculate_bottleneck_opportunity_cost(10.0) == 3200.00
    assert calculate_bottleneck_opportunity_cost(76.0) == 24320.00


# ============================================================================
# 2. INPUT VALIDATION & NEGATIVE VALUES REJECTION
# ============================================================================

def test_invalid_negative_inputs():
    """Validates that negative physical quantities and rates are strictly rejected."""
    with pytest.raises(ValueError):
        calculate_downtime_loss(-1.0)

    with pytest.raises(ValueError):
        calculate_downtime_loss(1.0, rate_inr=-4500.0)

    with pytest.raises(ValueError):
        calculate_scrap_loss(-5)

    with pytest.raises(ValueError):
        calculate_rework_loss(-0.5)

    with pytest.raises(ValueError):
        calculate_energy_consumption_and_cost(-10.0, 1.0, 8.50)

    with pytest.raises(ValueError):
        calculate_bottleneck_opportunity_cost(-10.0)

    with pytest.raises(ValueError):
        is_peak_tariff_hour(25)


def test_zero_loss_scenario():
    """Validates zero loss when no disruptions occur."""
    bd = MachineLossBreakdown(
        machine_id="M_NOMINAL",
        observed_unplanned_downtime_hours=0.0,
        observed_unplanned_downtime_loss_inr=0.0,
        scrap_quantity_units=0,
        scrap_mass_kg=0.0,
        scrap_loss_inr=0.0,
        rework_hours=0.0,
        rework_loss_inr=0.0,
        total_energy_kwh=100.0,
        total_energy_cost_inr=850.0,
        energy_inefficiency_kwh=0.0,
        energy_inefficiency_loss_inr=0.0,
        delayed_throughput_units=0.0,
        projected_opportunity_cost_inr=0.0,
        realized_operational_loss_inr=0.0,
        gross_financial_exposure_inr=0.0,
        non_overlapping_financial_exposure_inr=0.0
    )
    assert bd.realized_operational_loss_inr == 0.0
    assert bd.gross_financial_exposure_inr == 0.0
    assert bd.observed_downtime_loss_inr == 0.0


# ============================================================================
# 3. DOUBLE-COUNTING AUDITS & DIAGNOSTIC ISOLATION
# ============================================================================

def test_health_score_isolation():
    """Validates that composite health score does not alter financial loss calculations."""
    assert verify_no_pseudo_financial_coupling(health_score=0.0) == 0.0
    assert verify_no_pseudo_financial_coupling(health_score=50.0) == 0.0
    assert verify_no_pseudo_financial_coupling(health_score=100.0) == 0.0


def test_shap_isolation():
    """Validates that SHAP feature attribution margins incur zero financial loss."""
    assert verify_no_pseudo_financial_coupling(shap_values={"tool_wear": 4.5, "vibration": 3.2}) == 0.0


def test_rca_isolation():
    """Validates that RCA candidate causes do not generate independent loss line items."""
    assert verify_no_pseudo_financial_coupling(rca_candidates=["BEARING_WEAR", "HEAT_DISSIPATION_FAILURE"]) == 0.0


def test_monetary_rounding_consistency():
    """Validates consistent 2-decimal rounding to Indian Paise across diverse arithmetic values."""
    assert round_inr(12.345) == 12.35
    assert round_inr(12.344) == 12.34
    assert round_inr(100.0) == 100.0
    assert round_inr(0.001) == 0.0
    assert round_inr(0.009) == 0.01


def test_downtime_vs_opportunity_cost_separation():
    """Validates separation of downtime fixed overhead vs delayed throughput margin."""
    # Machine halted for 2.5 hours (downtime loss = 11,250)
    dt_loss = calculate_downtime_loss(2.5, 4500.0)
    assert dt_loss == 11250.0

    # Running machine delayed 76 unproduced units (opportunity cost = 24,320)
    opp_cost = calculate_bottleneck_opportunity_cost(76.0, 320.0)
    assert opp_cost == 24320.0

    # Ensure they are reported separately and not collapsed
    assert dt_loss != opp_cost


def test_scrap_vs_rework_separation():
    """Validates that scrap material cost and rework technician labor are tracked independently."""
    mass, scrap_loss = calculate_scrap_loss(10, unit_mass_kg=0.8, scrap_rate_inr_per_kg=350.0)
    rework_loss = calculate_rework_loss(1.25, rework_rate_inr=280.0)

    # Scrap is raw material replacement (8.0 kg * 350 = 2800)
    assert mass == 8.0
    assert scrap_loss == 2800.00
    # Rework is technician labor hours (1.25 hr * 280 = 350)
    assert rework_loss == 350.00
    assert scrap_loss != rework_loss


# ============================================================================
# 4. SERVICE INTEGRATION, MACHINE ATTRIBUTION, AND AGGREGATION
# ============================================================================

@pytest.fixture
def loss_service():
    """Initializes FinancialLossService for integration tests."""
    return FinancialLossService()


def test_machine_attribution(loss_service):
    """Validates that every machine (M1 to M5) receives independent, tracked loss breakdowns."""
    machines = loss_service.get_machine_list()
    assert set(machines) == {"M1", "M2", "M3", "M4", "M5"}

    for m_id in machines:
        bd = loss_service.calculate_machine_loss(m_id)
        assert isinstance(bd, MachineLossBreakdown)
        assert bd.machine_id == m_id
        assert bd.total_energy_cost_inr > 0.0
        assert bd.scrap_loss_inr >= 0.0
        assert bd.realized_operational_loss_inr >= 0.0
        assert bd.gross_financial_exposure_inr >= bd.realized_operational_loss_inr


def test_factory_aggregation(loss_service):
    """Validates that factory summary equals the exact mathematical sum of machine breakdowns."""
    summary = loss_service.calculate_factory_loss_summary()
    assert isinstance(summary, FactoryLossSummary)

    sum_realized = sum(b.realized_operational_loss_inr for b in summary.machine_breakdowns.values())
    sum_energy = sum(b.total_energy_cost_inr for b in summary.machine_breakdowns.values())
    sum_opp = sum(b.projected_opportunity_cost_inr for b in summary.machine_breakdowns.values())
    sum_gross = sum(b.gross_financial_exposure_inr for b in summary.machine_breakdowns.values())

    assert round_inr(summary.total_realized_loss_inr) == round_inr(sum_realized)
    assert round_inr(summary.total_energy_cost_inr) == round_inr(sum_energy)
    assert round_inr(summary.total_projected_opportunity_cost_inr) == round_inr(sum_opp)
    assert round_inr(summary.gross_financial_exposure_inr) == round_inr(sum_gross)


def test_temporal_causality_leakage(loss_service):
    """Validates strict temporal causality: evaluating at t excludes events at t + dt."""
    # Emergency halt on M2 occurred at 2026-01-22 16:30:00 UTC
    t_before = datetime(2026, 1, 22, 12, 0, 0, tzinfo=timezone.utc)
    t_after = datetime(2026, 1, 22, 18, 0, 0, tzinfo=timezone.utc)

    bd_before = loss_service.calculate_machine_loss("M2", as_of_time=t_before)
    bd_after = loss_service.calculate_machine_loss("M2", as_of_time=t_after)

    # Before emergency halt: 0 unplanned downtime hours
    assert bd_before.observed_unplanned_downtime_hours == 0.0
    assert bd_before.observed_unplanned_downtime_loss_inr == 0.0

    # After emergency halt: 2.5 hours unplanned downtime recorded
    assert bd_after.observed_unplanned_downtime_hours == 2.5
    assert bd_after.observed_unplanned_downtime_loss_inr == 11250.00
    assert bd_after.realized_operational_loss_inr > bd_before.realized_operational_loss_inr


def test_historical_replay_reproducibility(loss_service):
    """Validates that repeated evaluation at a historical timestamp yields identical outputs."""
    t_eval = datetime(2026, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    res1 = loss_service.calculate_factory_loss_summary(as_of_time=t_eval)
    res2 = loss_service.calculate_factory_loss_summary(as_of_time=t_eval)

    assert res1.total_realized_loss_inr == res2.total_realized_loss_inr
    assert res1.total_energy_cost_inr == res2.total_energy_cost_inr
    assert res1.gross_financial_exposure_inr == res2.gross_financial_exposure_inr


def test_reference_artifact_reconciliation(loss_service):
    """Validates 100% reconciliation against operational_losses.csv reference."""
    rec = loss_service.reconcile_with_reference_losses()
    assert rec["status"] == "RECONCILED"
    assert rec["all_downtime_match"] is True
    assert rec["all_scrap_match"] is True
    assert rec["all_rework_match"] is True


def test_machine_2_controlled_scenario(loss_service):
    """Validates data-driven evaluation of the Machine 2 degradation scenario."""
    scen = loss_service.evaluate_machine_2_controlled_scenario()
    assert scen["machine_id"] == "M2"
    assert scen["emergency_maintenance_record"] == "MAINT_0003"

    # Emergency halt verification
    halt = scen["emergency_halt_maint_0003"]
    assert halt["downtime_minutes"] == 150.0
    assert halt["downtime_loss_inr"] == 11250.00
    assert halt["technician_rework_hours"] == 1.5
    assert halt["technician_rework_loss_inr"] == 420.00
    assert halt["single_event_halt_loss_inr"] == 11670.00

    # Degradation period deltas
    deg = scen["degradation_period_days_18_to_21_delta"]
    assert deg["scrap_loss_inr"] > 0.0
    assert deg["rework_loss_inr"] > 0.0
    assert deg["energy_inefficiency_loss_inr"] > 0.0
    assert deg["projected_opportunity_cost_inr"] > 0.0


def test_epistemic_labels_integrity(loss_service):
    """Validates that summary contains all required epistemic categories."""
    summary = loss_service.calculate_factory_loss_summary()
    ep = summary.by_epistemic_type

    assert EpistemicClassification.OBSERVED.value in ep
    assert EpistemicClassification.DERIVED_FROM_OBSERVED.value in ep
    assert EpistemicClassification.CONFIGURED_ASSUMPTION.value in ep
    assert EpistemicClassification.PROJECTED_OPPORTUNITY_COST.value in ep
    assert ep[EpistemicClassification.PROJECTED_OPPORTUNITY_COST.value] == 24320.00


def test_deterministic_repeated_execution(loss_service):
    """Validates exact numerical determinism over repeated executions."""
    runs = [loss_service.calculate_factory_loss_summary().total_realized_loss_inr for _ in range(5)]
    assert len(set(runs)) == 1
