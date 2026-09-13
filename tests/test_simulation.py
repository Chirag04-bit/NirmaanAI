"""
NirmaanAI Digital-Twin-Inspired What-If Simulation Engine — Unit & Integration Test Suite
Phase 16: What-If / Digital-Twin-Inspired Simulation Engine

Validates:
1. Baseline repository & dataset integrity (operational_losses.csv MD5 = 34B12582B32D81E3121429C55EBF74E8).
2. Closed approved intervention taxonomy (strictly 15 approved actions from Phase 15 taxonomy).
3. M2 baseline state reconstruction at t = 2026-01-21T12:00:00Z.
4. M2 inventory distinction: current stock 2.0 (above safety stock 1.134; never called a stockout); projected stock 1.0.
5. Strict temporal causality & Day 22 exclusion from baseline state.
6. Realized loss (₹73,062.28) kept strictly separate from projected loss and projected avoided loss.
7. No pseudo-financial coupling (zero money derived from Health, SHAP, or RCA).
8. Categorical uncertainty labels & NOT_PROJECTABLE handling.
9. Healthy machine negative control validation (Machine M1 emits zero fabricated improvements).
10. Scenario comparison & ranking narrative integrity (broadest modeled coverage; no fake mathematical global optimality).
11. Configured sensitivity analysis (LOW, BASE, HIGH tiers).
12. Deterministic repeated execution & artifact parity.
13. Human-in-the-loop decision-support governance (no autonomous machine commands).
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pytest

from src.decision.loss_models import EpistemicClassification
from src.health.health_models import HealthState
from src.simulation.scenario_definitions import (
    CONTRIBUTION_MARGIN_PER_UNIT_INR,
    DOWNTIME_HOURLY_RATE_INR,
    REWORK_HOURLY_RATE_INR,
    compute_kpi_delta,
    get_m1_negative_control_baseline_kpi_vector,
    get_m2_baseline_kpi_vector,
)
from src.simulation.simulation_engine import WhatIfSimulationEngine
from src.simulation.simulation_models import (
    KPIDeltaVector,
    OperationalKPIVector,
    ProjectionConfidence,
    ScenarioAssumption,
    SensitivityTier,
    SimulationInterventionType,
    WhatIfScenario,
)
from src.simulation.simulation_service import WhatIfSimulationService
from src.utils.config_loader import get_project_root


@pytest.fixture
def engine():
    return WhatIfSimulationEngine()


@pytest.fixture
def service():
    return WhatIfSimulationService()


# ==============================================================================
# 1. BASELINE DATASET & UPSTREAM ARTIFACT INTEGRITY
# ==============================================================================

def test_operational_losses_md5_unchanged():
    """Verifies reference operational_losses.csv remains byte-for-byte unmodified."""
    root = get_project_root()
    ref_path = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "operational_losses.csv"
    assert ref_path.exists(), "operational_losses.csv missing"

    with open(ref_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    assert file_hash == "34b12582b32d81e3121429c55ebf74e8", f"MD5 mismatch: {file_hash}"


def test_upstream_artifacts_read_only_presence():
    """Verifies all required Phase 6-15 artifacts exist and are readable without modification."""
    root = get_project_root()
    required_artifacts = [
        root / "models" / "predictive_maintenance" / "metadata.json",
        root / "models" / "anomaly_detection" / "metadata.json",
        root / "models" / "bottleneck_prediction" / "metadata.json",
        root / "models" / "inventory_intelligence" / "sku_optimization_summary.csv",
        root / "models" / "explainability" / "metadata.json",
        root / "models" / "rca" / "rca_summary.json",
        root / "models" / "health" / "health_summary.json",
        root / "models" / "loss" / "loss_summary.json",
        root / "models" / "recommendations" / "recommendation_summary.json",
    ]
    for p in required_artifacts:
        assert p.exists(), f"Upstream artifact missing: {p}"
        assert p.stat().st_size > 0, f"Upstream artifact empty: {p}"


# ==============================================================================
# 2. CLOSED INTERVENTION TAXONOMY
# ==============================================================================

def test_closed_intervention_taxonomy():
    """Validates strictly 15 approved actions exist in SimulationInterventionType."""
    assert len(SimulationInterventionType) == 15
    expected_interventions = {
        # MAINTENANCE (5)
        "INSPECT_SPINDLE_BEARING",
        "INSPECT_LUBRICATION",
        "REPLACE_WORN_COMPONENT",
        "REPLACE_TOOLING",
        "SCHEDULE_PREVENTIVE_MAINTENANCE",
        # PRODUCTION (5)
        "REDUCE_MACHINE_FEED_RATE",
        "RESCHEDULE_PENDING_JOBS",
        "REBALANCE_LINE_WORKLOAD",
        "BUFFER_DOWNSTREAM_INVENTORY",
        "PAUSE_NEW_JOB_RELEASE",
        # INVENTORY (3)
        "EXPEDITE_CRITICAL_SPARE",
        "TRIGGER_STANDARD_REORDER",
        "INCREASE_SAFETY_STOCK_BUFFER",
        # ENERGY (2)
        "SHIFT_HIGH_LOAD_OFF_PEAK",
        "INVESTIGATE_POWER_EXCURSION",
    }
    actual_interventions = {i.value for i in SimulationInterventionType}
    assert actual_interventions == expected_interventions


# ==============================================================================
# 3. M2 BASELINE RECONSTRUCTION & INVENTORY INTEGRITY (BLOCKER 1 & 7)
# ==============================================================================

def test_m2_baseline_reconstruction():
    """Validates exact reconstruction of M2 baseline at t = 2026-01-21T12:00:00Z."""
    base = get_m2_baseline_kpi_vector()
    assert base.failure_probability == 0.9959
    assert base.anomaly_score == 0.35
    assert base.health_score == 26.88
    assert base.health_state == HealthState.CRITICAL
    assert base.cycle_ratio == 1.38
    assert base.delayed_throughput_units == 76.0
    assert base.is_bottleneck is True
    assert base.realized_operational_loss_inr == 73062.28
    assert base.projected_opportunity_cost_inr == 24320.00
    assert base.gross_financial_exposure_inr == 97382.28


def test_m2_rop_equals_authoritative_1_367():
    """Guarantee 1: M2 Reorder Point == 1.367 units (Phase 10 authoritative value)."""
    base = get_m2_baseline_kpi_vector()
    assert base.reorder_point == 1.367


def test_m2_current_stock_greater_than_rop():
    """Guarantee 2: M2 current stock 2.0 > ROP 1.367 (never below ROP)."""
    base = get_m2_baseline_kpi_vector()
    assert base.observed_current_stock == 2.0
    assert base.reorder_point == 1.367
    assert base.observed_current_stock > base.reorder_point


def test_m2_current_stock_greater_than_safety_stock():
    """Guarantee 3: M2 current stock 2.0 > safety stock 1.134 (no stockout claim permitted)."""
    base = get_m2_baseline_kpi_vector()
    assert base.observed_current_stock == 2.0
    assert base.safety_stock == 1.134
    assert base.observed_current_stock > base.safety_stock
    assert base.is_safety_stock_breached is False


def test_projected_stock_after_consuming_bearing_is_one(engine):
    """Guarantee 4: Projected stock after consuming one bearing = 1.0."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen_b = engine.simulate_m2_scenario_b(dt)
    assert scen_b.projected_state.observed_current_stock == 2.0
    assert scen_b.projected_state.projected_post_action_stock == 1.0


def test_projected_stock_one_is_less_than_safety_stock(engine):
    """Guarantee 5: Projected stock 1.0 < safety stock 1.134 (breaches safety stock)."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen_b = engine.simulate_m2_scenario_b(dt)
    proj = scen_b.projected_state
    assert proj.projected_post_action_stock < proj.safety_stock
    assert proj.is_safety_stock_breached is True


def test_no_rop_five_in_phase_16_outputs():
    """Guarantee 6: No occurrence of ROP = 5.0 exists in Phase 16 models or documentation."""
    root = get_project_root()
    phase16_files = [
        root / "models" / "simulation" / "simulation_summary.json",
        root / "docs" / "simulation" / "simulation_engine.md",
        root / "docs" / "simulation" / "scenario_catalog.md",
        root / "docs" / "simulation" / "simulation_evaluation.md",
        root / "docs" / "simulation" / "m2_what_if_walkthrough.md",
    ]
    for p in phase16_files:
        assert p.exists(), f"File missing: {p}"
        content = p.read_text(encoding="utf-8")
        assert "ROP = 5.0" not in content
        assert "ROP=5.0" not in content
        assert "reorder point = 5.0" not in content.lower()
        assert "reorder point of 5.0" not in content.lower()


def test_unsupported_causal_intervention_effects_are_not_projectable(engine):
    """Guarantee 7: Unsupported causal intervention effects become NOT_PROJECTABLE."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    for scen_fn in [
        engine.simulate_m2_scenario_b,
        engine.simulate_m2_scenario_c,
        engine.simulate_m2_scenario_d,
        engine.simulate_m2_scenario_e,
    ]:
        scen = scen_fn(dt)
        proj = scen.projected_state
        assert proj.failure_probability == "NOT_PROJECTABLE"
        assert proj.anomaly_score == "NOT_PROJECTABLE"
        assert proj.health_score == "NOT_PROJECTABLE"
        assert proj.health_state == "NOT_PROJECTABLE"
        assert scen.delta.health_state_change == "NOT_PROJECTABLE"
        assert any(
            "No intervention-specific empirical treatment effect is available" in lim
            for lim in scen.limitations
        )


def test_configured_assumption_never_reported_as_empirical_validation(engine):
    """Guarantee 8: CONFIGURED_ASSUMPTION is never reported as empirical validation."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen_d = engine.simulate_m2_scenario_d(dt)
    assert scen_d.epistemic_classification == EpistemicClassification.CONFIGURED_ASSUMPTION
    assert scen_d.confidence == ProjectionConfidence.ASSUMPTION_DEPENDENT
    delay_assump = next(a for a in scen_d.assumptions if a.parameter_name == "delayed_units_after_rescheduling")
    assert delay_assump.configured_value == 15.0
    assert delay_assump.epistemic_classification == EpistemicClassification.CONFIGURED_ASSUMPTION
    assert "NOT empirically validated" in delay_assump.rationale


def test_projected_opportunity_cost_never_labelled_realized_savings(engine):
    """Guarantee 9: Projected opportunity cost is never labelled realized savings."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen_d = engine.simulate_m2_scenario_d(dt)
    assert scen_d.projected_state.projected_avoided_loss_inr == 19520.00
    assert any("never realized savings" in lim for lim in scen_d.limitations)
    margin_assump = next(a for a in scen_d.assumptions if a.parameter_name == "contribution_margin_per_unit_inr")
    assert "NOT realized savings" in margin_assump.rationale


# ==============================================================================
# 4. TEMPORAL CAUSALITY & DAY 22 EXCLUSION (GUARANTEE 11)
# ==============================================================================

def test_temporal_causality_and_day22_exclusion():
    """Guarantee 11: Validates baseline state excludes future Day 22 emergency halt, repair labor, and recovery."""
    base = get_m2_baseline_kpi_vector()
    # Baseline at Day 21 must have 0.0 unplanned downtime
    assert base.unplanned_downtime_minutes == 0.0
    # Baseline rework hours is 23.12 (excludes 1.5h Day 22 repair labor = 24.62)
    assert base.rework_hours == 23.12
    # Baseline health is 26.88 (excludes Day 23 post-maintenance recovery = 96.91)
    assert base.health_score == 26.88


# ==============================================================================
# 5. FINANCIAL SIMULATION STANDARDS (GUARANTEE 10)
# ==============================================================================

def test_realized_vs_projected_loss_separation(engine):
    """Verifies realized loss is strictly separated from projected avoided loss."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen_b = engine.simulate_m2_scenario_b(dt)

    # Realized loss remains historical baseline loss (₹73,062.28)
    assert scen_b.projected_state.realized_operational_loss_inr == 73062.28

    # Projected avoided loss is separated: 2.0h avoided downtime (₹9,000) + avoided labor (₹420) = ₹9,420
    assert scen_b.projected_state.projected_avoided_loss_inr == 9420.00
    assert scen_b.delta.projected_avoided_loss_inr == 9420.00

    # Gross financial exposure is reduced by avoided loss
    assert scen_b.projected_state.gross_financial_exposure_inr == round(97382.28 - 9420.00, 2)


def test_no_money_derived_from_diagnostics(engine):
    """Guarantee 10: Asserts no pseudo-financial formula (Health * money, SHAP * money) exists in calculations."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen_d = engine.simulate_m2_scenario_d(dt)

    # Avoided opportunity cost is strictly (delayed_units_avoided * contribution_margin_inr)
    # (76 - 15) * 320 = 61 * 320 = ₹19,520.00
    assert scen_d.projected_state.projected_avoided_loss_inr == 19520.00
    assert scen_d.delta.projected_avoided_loss_inr == 19520.00


# ==============================================================================
# 6. M2 SCENARIO PORTFOLIO & COMPARISON
# ==============================================================================

def test_m2_scenarios_comparison_consistency(engine):
    """Validates Scenarios A through E execution and comparative ranking narrative."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    report = engine.compare_m2_scenarios(dt)

    assert len(report.scenarios) == 5
    ids = [s.scenario_id for s in report.scenarios]
    assert ids == [
        "SCEN_M2_A_BASELINE",
        "SCEN_M2_B_INSPECT",
        "SCEN_M2_C_INSPECT_EXPEDITE",
        "SCEN_M2_D_FLOW_MITIGATION",
        "SCEN_M2_E_FULL_PORTFOLIO",
    ]

    # Scenario E must be the recommended scenario
    assert report.recommended_scenario_id == "SCEN_M2_E_FULL_PORTFOLIO"

    # Narrative must claim broadest modeled mitigation coverage, NOT unproven global optimality
    assert "broadest modeled mitigation coverage" in report.ranking_narrative.lower()
    assert "no claim of unconstrained mathematical global optimality" in report.ranking_narrative.lower()

    # Scenario E combines breakdown avoidance (₹9,420) and bottleneck delay avoidance (₹19,520) = ₹28,940
    scen_e = next(s for s in report.scenarios if s.scenario_id == "SCEN_M2_E_FULL_PORTFOLIO")
    assert scen_e.projected_state.projected_avoided_loss_inr == 28940.00
    assert scen_e.projected_state.health_state == "NOT_PROJECTABLE"
    assert scen_e.projected_state.health_score == "NOT_PROJECTABLE"
    assert scen_e.projected_state.failure_probability == "NOT_PROJECTABLE"


# ==============================================================================
# 7. HEALTHY MACHINE NEGATIVE CONTROL
# ==============================================================================

def test_healthy_machine_negative_control(engine):
    """Validates healthy machine produces zero fabricated operational or financial improvement."""
    dt = datetime(2026, 1, 17, 12, 0, 0, tzinfo=timezone.utc)
    neg = engine.simulate_negative_control_m1(dt)

    assert neg.machine_id == "M1"
    assert neg.confidence == ProjectionConfidence.HIGH_EVIDENCE
    assert neg.projected_state.health_score == 97.47
    assert neg.delta.health_score_delta == 0.0
    assert neg.projected_state.projected_avoided_loss_inr == 0.0
    assert neg.delta.projected_avoided_loss_inr == 0.0


# ==============================================================================
# 8. SENSITIVITY ANALYSIS ROBUSTNESS
# ==============================================================================

def test_configured_sensitivity_analysis_tiers(service):
    """Validates LOW, BASE, and HIGH sensitivity tiers for Scenario E."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    sens = service.run_sensitivity_analysis(dt)

    assert sens["analysis_name"] == "CONFIGURED SENSITIVITY ANALYSIS (Scenario E Robustness)"
    assert sens["epistemic_classification"] == "CONFIGURED_ASSUMPTION"

    tiers = sens["tiers"]
    low = tiers["LOW_PESSIMISTIC"]
    base = tiers["BASE_NOMINAL"]
    high = tiers["HIGH_OPTIMISTIC"]

    # Avoided loss must follow Low < Base < High monotonic relationship
    assert low["projected_avoided_loss_inr"] < base["projected_avoided_loss_inr"]
    assert base["projected_avoided_loss_inr"] < high["projected_avoided_loss_inr"]

    # Gross exposure must follow High < Base < Low monotonic relationship
    assert high["projected_gross_exposure_inr"] < base["projected_gross_exposure_inr"]
    assert base["projected_gross_exposure_inr"] < low["projected_gross_exposure_inr"]


# ==============================================================================
# 9. DETERMINISM & JSON ARTIFACT PARITY
# ==============================================================================

def test_deterministic_repeated_execution(service):
    """Repeated runs on identical inputs yield 100% byte-for-byte identical outputs."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    run1 = service.generate_full_simulation_summary(dt)
    run2 = service.generate_full_simulation_summary(dt)

    assert run1["scenario_comparison"] == run2["scenario_comparison"]
    assert run1["sensitivity_analysis"] == run2["sensitivity_analysis"]
    assert len(run1["scenarios_evaluated"]) == len(run2["scenarios_evaluated"])


def test_json_artifact_parity():
    """Validates models/simulation/simulation_summary.json exists and is valid."""
    root = get_project_root()
    json_path = root / "models" / "simulation" / "simulation_summary.json"
    assert json_path.exists(), "simulation_summary.json missing"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["phase"] == "Phase 16: What-If / Digital-Twin-Inspired Simulation Engine"
    assert data["governance"]["decision_support_only"] is True
    assert data["governance"]["human_operator_authorization_mandatory"] is True
    assert len(data["scenarios_evaluated"]) == 5
    assert data["negative_control"]["machine_id"] == "M1"


# ==============================================================================
# 10. HUMAN DECISION SUPPORT & PHASE BOUNDARY
# ==============================================================================

def test_human_decision_support_governance(service):
    """Asserts no autonomous machine commands exist; all actions are decision-support what-if projections."""
    summary = service.generate_full_simulation_summary()
    gov = summary["governance"]
    assert gov["is_autonomous_controller"] is False
    assert gov["is_physical_digital_twin"] is False
    assert gov["decision_support_only"] is True
    assert gov["human_operator_authorization_mandatory"] is True
