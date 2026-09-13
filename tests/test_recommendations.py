"""
NirmaanAI Operational Recommendation Engine — Unit & Integration Test Suite
Phase 15: Recommendation Engine

Validates:
1. Locked upstream threshold adherence (P6 = 0.91, P7 = 0.2405, P8 = 1.20, P13 bands).
2. Closed action taxonomy enforcement (strictly 24 approved actions).
3. Inventory state integrity (observed stock 2.0 vs projected stock 1.0; no false stockout claims).
4. Atomic epistemic provenance preservation on every EvidenceItem.
5. Evidence strength calibration across 5 genuine physical domains (financial exposure excluded).
6. Temporal causality compliance (zero future lookahead in retrospective evaluation).
7. Controlled Machine 2 degradation portfolio generation.
8. Healthy machine negative control generation (zero critical actions, only nominal monitoring).
9. Deduplication and conflict resolution matrices.
10. Deterministic repeated execution and artifact parity.
11. Reference dataset operational_losses.csv MD5 invariance.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pytest

from src.decision.recommendation_engine import (
    OperationalRecommendationEngine,
    PRIORITY_RANK,
    URGENCY_RANK,
)
from src.decision.recommendation_models import (
    ActionUrgency,
    EpistemicClassification,
    EvidenceDomain,
    EvidenceItem,
    EvidenceStrength,
    FinancialEvidenceContext,
    InventoryEvidenceContext,
    OperationalRecommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationPriority,
)
from src.decision.recommendation_rules import (
    P6_CONFIGURED_WARNING_THRESHOLD,
    P6_LOCKED_FAILURE_THRESHOLD,
    P7_LOCKED_ANOMALY_THRESHOLD,
    P8_LOCKED_CYCLE_RATIO_TARGET,
    P14_CONFIGURED_MATERIALITY_THRESHOLD_INR,
    calculate_evidence_strength,
    evaluate_rule_r_e01,
    evaluate_rule_r_i01,
    evaluate_rule_r_m01,
    evaluate_rule_r_m02,
    evaluate_rule_r_m03,
    evaluate_rule_r_o01,
    evaluate_rule_r_p01,
)
from src.decision.recommendation_service import RecommendationService
from src.health.health_models import HealthState
from src.utils.config_loader import get_project_root


@pytest.fixture
def service():
    return RecommendationService()


@pytest.fixture
def engine():
    return OperationalRecommendationEngine()


# ==============================================================================
# 1. LOCKED UPSTREAM THRESHOLDS & TAXONOMY
# ==============================================================================

def test_closed_action_taxonomy():
    """Validates that exactly 26 approved actions exist in RecommendationAction as enumerated in Section 4."""
    assert len(RecommendationAction) == 26
    expected_actions = {
        # MAINTENANCE (7)
        "INSPECT_SPINDLE_BEARING",
        "SCHEDULE_PREVENTIVE_MAINTENANCE",
        "REPLACE_WORN_COMPONENT",
        "INSPECT_LUBRICATION",
        "REPLACE_TOOLING",
        "CALIBRATE_AXIS_ALIGNMENT",
        "OVERHAUL_ASSEMBLY",
        # PRODUCTION_FLOW (6)
        "REDUCE_MACHINE_FEED_RATE",
        "RESCHEDULE_PENDING_JOBS",
        "REBALANCE_LINE_WORKLOAD",
        "BUFFER_DOWNSTREAM_INVENTORY",
        "PAUSE_NEW_JOB_RELEASE",
        "BYPASS_TO_PARALLEL_LINE",
        # INVENTORY (5)
        "EXPEDITE_CRITICAL_SPARE",
        "TRIGGER_STANDARD_REORDER",
        "INCREASE_SAFETY_STOCK_BUFFER",
        "MONITOR_SUPPLIER_LEAD_TIME",
        "HOLD_UNNECESSARY_PROCUREMENT",
        # ENERGY (4)
        "INVESTIGATE_POWER_EXCURSION",
        "SHIFT_HIGH_LOAD_OFF_PEAK",
        "INSPECT_ELECTROMECHANICAL_DRIVE",
        "MONITOR_IDLE_STANDBY_POWER",
        # MONITORING (4)
        "CONTINUE_NOMINAL_MONITORING",
        "INCREASE_TELEMETRY_SAMPLING_FREQUENCY",
        "MANDATE_OPERATOR_VISUAL_CHECK",
        "VERIFY_SENSOR_CALIBRATION",
    }
    actual_actions = {a.value for a in RecommendationAction}
    assert actual_actions == expected_actions


def test_phase13_health_bands_match_locked_definition():
    """Validates that Phase 15 consumes authoritative locked Phase 13 health bands."""
    assert HealthState.EXCELLENT.value == "EXCELLENT"
    assert HealthState.HEALTHY.value == "HEALTHY"
    assert HealthState.WATCH.value == "WATCH"
    assert HealthState.DEGRADED.value == "DEGRADED"
    assert HealthState.CRITICAL.value == "CRITICAL"


def test_phase8_bottleneck_semantics_alignment():
    """Proves Phase 15 uses locked Phase 8 bottleneck semantics (cycle_ratio >= 1.20)."""
    assert P8_LOCKED_CYCLE_RATIO_TARGET == 1.20
    # An action should trigger when cycle_ratio is 1.20, but not when below 1.20
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    recs_sub = evaluate_rule_r_p01(
        machine_id="M2", as_of=dt, is_bottleneck=True, cycle_ratio=1.15, delayed_units=50.0
    )
    assert len(recs_sub) == 0  # 1.15 is below 1.20 target

    recs_target = evaluate_rule_r_p01(
        machine_id="M2", as_of=dt, is_bottleneck=True, cycle_ratio=1.20, delayed_units=50.0
    )
    assert len(recs_target) == 2  # REDUCE_MACHINE_FEED_RATE and RESCHEDULE_PENDING_JOBS


def test_phase_6_locked_threshold_0_91():
    """Verifies P(fail) >= 0.91 triggers critical maintenance, while 0.75 <= P < 0.91 triggers warning."""
    assert P6_LOCKED_FAILURE_THRESHOLD == 0.91
    assert P6_CONFIGURED_WARNING_THRESHOLD == 0.75
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)

    # Sub-warning
    r_sub = evaluate_rule_r_m01("M2", dt, failure_prob=0.70, anomaly_score=0.35, rca_candidate="MECHANICAL_LOAD")
    assert r_sub is None

    # Warning band [0.75, 0.91)
    r_warn = evaluate_rule_r_m02("M2", dt, failure_prob=0.85, vibration_deviation_mms=0.45, rca_candidate="MECHANICAL_LOAD")
    assert r_warn is not None
    assert len(r_warn) == 2
    assert r_warn[0].priority == RecommendationPriority.HIGH
    assert r_warn[0].action == RecommendationAction.INSPECT_LUBRICATION

    # Critical breach >= 0.91
    r_crit = evaluate_rule_r_m01("M2", dt, failure_prob=0.91, anomaly_score=0.25, rca_candidate="MECHANICAL_LOAD")
    assert r_crit is not None
    assert r_crit.priority == RecommendationPriority.CRITICAL
    assert r_crit.action == RecommendationAction.INSPECT_SPINDLE_BEARING


def test_phase_7_normalized_anomaly_scale():
    """Verifies threshold evaluation against 0.2405 scale (rejects sigma confusion)."""
    assert P7_LOCKED_ANOMALY_THRESHOLD == 0.2405
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)

    # Below calibrated threshold
    r_sub = evaluate_rule_r_m01("M2", dt, failure_prob=0.95, anomaly_score=0.20, rca_candidate="MECHANICAL_LOAD")
    assert r_sub is None

    # At or above calibrated threshold
    r_hit = evaluate_rule_r_m01("M2", dt, failure_prob=0.95, anomaly_score=0.2405, rca_candidate="MECHANICAL_LOAD")
    assert r_hit is not None


# ==============================================================================
# 2. INVENTORY STATE: CURRENT VS PROJECTED
# ==============================================================================

def test_m2_current_bearing_stock_not_below_safety_stock(service):
    """Asserts observed current stock is 2.0, above safety stock 1.134 (NOT currently stocked out)."""
    scen = service.evaluate_machine_2_controlled_scenario()
    inputs = scen["operational_inputs"]
    assert inputs["inventory_observed_current_stock"] == 2.0
    assert inputs["inventory_safety_stock"] == 1.134
    assert inputs["inventory_observed_current_stock"] > inputs["inventory_safety_stock"]


def test_projected_post_action_stock_breaches_safety_stock(service):
    """Asserts projected post-action stock (1.0) is below safety stock (1.134)."""
    scen = service.evaluate_machine_2_controlled_scenario()
    inputs = scen["operational_inputs"]
    hypothetical_consumption = inputs["inventory_hypothetical_consumption"]
    projected = inputs["inventory_observed_current_stock"] - hypothetical_consumption
    assert projected == 1.0
    assert projected < inputs["inventory_safety_stock"]


def test_inventory_recommendation_distinguishes_observed_and_projected(service):
    """Verifies recommendation narrative cites projected post-action stock constraint, not current stockout."""
    scen = service.evaluate_machine_2_controlled_scenario()
    inv_recs = [r for r in scen["recommendations"] if r["category"] == "INVENTORY"]
    assert len(inv_recs) == 1
    rec = inv_recs[0]
    assert rec["action"] == "EXPEDITE_CRITICAL_SPARE"
    assert rec["priority"] == "HIGH"
    assert rec["urgency"] == "SAME_DAY"

    # Narrative assertions
    reason = rec["reason"]
    assert "Current stock of SKU_SPINDLE_BEARING_M2 is 2.0 units and above safety stock" in reason
    assert "projecting post-action stock to 1.0 units, which breaches the safety stock buffer" in reason
    assert "supplier lead time is 7.0 days" in reason
    assert "current stockout" not in reason.lower()

    # Context structure assertions
    ctx = rec["inventory_context"]
    assert ctx["observed_current_stock"] == 2.0
    assert ctx["is_current_stock_below_safety"] is False
    assert ctx["projected_post_action_stock"] == 1.0
    assert ctx["is_projected_stock_below_safety"] is True


# ==============================================================================
# 3. EPISTEMIC PROVENANCE PRESERVATION
# ==============================================================================

def test_m2_evidence_preserves_individual_epistemic_provenance(service):
    """Confirms individual evidence items preserve their own provenance, not overwritten by scenario wrapper."""
    scen = service.evaluate_machine_2_controlled_scenario()
    assert scen["epistemic_classification"] == "CONTROLLED_SYNTHETIC"

    all_evidence = [ev for r in scen["recommendations"] for ev in r["evidence"]]

    # Verify P6 is DERIVED_FROM_OBSERVED
    p6_ev = next(ev for ev in all_evidence if ev["source_phase"] == "Phase 6")
    assert p6_ev["epistemic_classification"] == "DERIVED_FROM_OBSERVED"

    # Verify P10 current stock is OBSERVED
    p10_stock_ev = next(ev for ev in all_evidence if ev["metric"] == "observed_current_stock")
    assert p10_stock_ev["epistemic_classification"] == "OBSERVED"

    # Verify P10 projection is PROJECTED
    p10_proj_ev = next(ev for ev in all_evidence if ev["metric"] == "projected_post_action_stock")
    assert p10_proj_ev["epistemic_classification"] == "PROJECTED"

    # Verify P10 lead time is CONFIGURED_ASSUMPTION
    p10_lead_ev = next(ev for ev in all_evidence if ev["metric"] == "supplier_lead_time_days")
    assert p10_lead_ev["epistemic_classification"] == "CONFIGURED_ASSUMPTION"


# ==============================================================================
# 4. SCIENTIFIC BOUNDARIES & ISOLATION
# ==============================================================================

def test_no_tooling_rul_dependency():
    """Verifies tooling replacement relies on tool_wear_min and scrap, not nonexistent RUL cycles."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    rec = evaluate_rule_r_m03(
        machine_id="M1",
        as_of=dt,
        tool_wear_min=210.0,
        scrap_rate_pct=6.5,
        shap_top_feature="tool_wear_min",
    )
    assert rec is not None
    assert rec.action == RecommendationAction.REPLACE_TOOLING
    assert rec.priority == RecommendationPriority.HIGH
    assert rec.urgency == ActionUrgency.NEXT_SHIFT

    # Assert no RUL metrics exist in evidence
    metrics = [ev.metric for ev in rec.evidence]
    assert "tool_wear_min" in metrics
    assert "scrap_rate_pct" in metrics
    assert "tooling_rul" not in metrics
    assert "rul_cycles" not in metrics


def test_evidence_strength_excludes_finance():
    """Verifies that financial exposure does NOT count towards physical corroboration strength."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    # Single physical domain (TELEMETRY_ANOMALY)
    ev = EvidenceItem(
        evidence_id="EVID_01",
        source_phase="Phase 7",
        source_module="Telemetry",
        domain=EvidenceDomain.TELEMETRY_ANOMALY,
        metric="vibration",
        value=3.5,
        timestamp=dt,
        machine_id="M1",
        interpretation="Vibration elevation",
        epistemic_classification=EpistemicClassification.OBSERVED,
    )
    # 1 physical domain -> WEAK
    assert calculate_evidence_strength([ev]) == EvidenceStrength.WEAK

    # 2 physical domains -> MODERATE
    ev2 = EvidenceItem(
        evidence_id="EVID_02",
        source_phase="Phase 6",
        source_module="Predictor",
        domain=EvidenceDomain.PREDICTIVE_FAILURE,
        metric="failure_prob",
        value=0.92,
        timestamp=dt,
        machine_id="M1",
        interpretation="Failure risk",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )
    assert calculate_evidence_strength([ev, ev2]) == EvidenceStrength.MODERATE

    # 3 physical domains -> STRONG
    ev3 = EvidenceItem(
        evidence_id="EVID_03",
        source_phase="Phase 12",
        source_module="RCA",
        domain=EvidenceDomain.DIAGNOSTIC_RCA,
        metric="primary_cause",
        value="MECHANICAL_LOAD",
        timestamp=dt,
        machine_id="M1",
        interpretation="RCA cause",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )
    assert calculate_evidence_strength([ev, ev2, ev3]) == EvidenceStrength.STRONG


def test_financial_threshold_classified_as_configured():
    """Verifies that the ₹25,000 threshold is tagged as a configured decision-support assumption."""
    assert P14_CONFIGURED_MATERIALITY_THRESHOLD_INR == 25000.0
    fin = FinancialEvidenceContext(
        realized_loss_inr=73062.28,
        gross_exposure_inr=97382.28,
        projected_opportunity_cost_inr=24320.0,
        is_material_exposure=True,
        materiality_threshold_inr=P14_CONFIGURED_MATERIALITY_THRESHOLD_INR,
    )
    assert fin.materiality_threshold_inr == 25000.0


def test_no_money_multiplied_by_diagnostics():
    """Verifies that no pseudo-financial formula coupling exists in recommendation output."""
    # Check that financial exposure is simply quoted from Phase 14 verbatim
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    fin_ctx = FinancialEvidenceContext(
        realized_loss_inr=73062.28,
        gross_exposure_inr=97382.28,
        projected_opportunity_cost_inr=24320.0,
        is_material_exposure=True,
    )
    rec = evaluate_rule_r_m01("M2", dt, 0.9959, 0.35, "MECHANICAL_LOAD", financial_context=fin_ctx)
    assert rec.financial_context.gross_exposure_inr == 97382.28
    assert rec.financial_context.realized_loss_inr == 73062.28


# ==============================================================================
# 5. TEMPORAL CAUSALITY & RETROSPECTIVE EVALUATION
# ==============================================================================

def test_temporal_causality_retrospective(service):
    """Validates that Day 21 retrospective evaluation contains zero Day 22 halt/repair data."""
    dt_day21 = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    scen = service.evaluate_machine_2_controlled_scenario(as_of=dt_day21)

    # All evidence timestamps must be <= decision_timestamp
    for rec in scen["recommendations"]:
        rec_ts = datetime.fromisoformat(rec["timestamp"].replace("Z", "+00:00"))
        assert rec_ts <= dt_day21
        for ev in rec["evidence"]:
            ev_ts = datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00"))
            assert ev_ts <= dt_day21

        # Assert no post-event downtime or repair labor is cited in the retrospective recommendations
        assert "MAINT_0003" not in rec["reason"]
        assert "150 min downtime" not in rec["reason"].lower()
        assert "420" not in rec["reason"]


# ==============================================================================
# 6. M2 CONTROLLED SCENARIO & NEGATIVE CONTROL
# ==============================================================================

def test_m2_controlled_scenario_chain(service):
    """Validates the expected 4-recommendation portfolio for M2 controlled degradation."""
    scen = service.evaluate_machine_2_controlled_scenario()
    assert scen["machine_id"] == "M2"
    assert scen["recommendation_count"] == 4

    actions = [r["action"] for r in scen["recommendations"]]
    expected_actions = [
        "INSPECT_SPINDLE_BEARING",
        "REDUCE_MACHINE_FEED_RATE",
        "RESCHEDULE_PENDING_JOBS",
        "EXPEDITE_CRITICAL_SPARE",
    ]
    for exp in expected_actions:
        assert exp in actions

    # Spindle bearing inspection must be CRITICAL and IMMEDIATE
    maint_rec = next(r for r in scen["recommendations"] if r["action"] == "INSPECT_SPINDLE_BEARING")
    assert maint_rec["priority"] == "CRITICAL"
    assert maint_rec["urgency"] == "IMMEDIATE"
    assert maint_rec["evidence_strength"] == "STRONG"

    # Feed rate reduction must be HIGH and SAME_DAY
    feed_rec = next(r for r in scen["recommendations"] if r["action"] == "REDUCE_MACHINE_FEED_RATE")
    assert feed_rec["priority"] == "HIGH"
    assert feed_rec["urgency"] == "SAME_DAY"

    # Reschedule jobs must be HIGH and SAME_DAY
    resched_rec = next(r for r in scen["recommendations"] if r["action"] == "RESCHEDULE_PENDING_JOBS")
    assert resched_rec["priority"] == "HIGH"
    assert resched_rec["urgency"] == "SAME_DAY"

    # Expedite spare must be HIGH and SAME_DAY
    inv_rec = next(r for r in scen["recommendations"] if r["action"] == "EXPEDITE_CRITICAL_SPARE")
    assert inv_rec["priority"] == "HIGH"
    assert inv_rec["urgency"] == "SAME_DAY"


def test_negative_control_healthy_machine(service):
    """Validates healthy machine emits ONLY CONTINUE_NOMINAL_MONITORING with MONITOR priority."""
    scen = service.evaluate_negative_control_scenario(machine_id="M1")
    assert scen["machine_id"] == "M1"
    assert scen["recommendation_count"] == 1

    rec = scen["recommendations"][0]
    assert rec["action"] == "CONTINUE_NOMINAL_MONITORING"
    assert rec["priority"] == "MONITOR"
    assert rec["urgency"] == "ROUTINE"
    assert rec["evidence_strength"] == "INSUFFICIENT"

    # Assert ZERO critical or high actions
    priorities = [r["priority"] for r in scen["recommendations"]]
    assert "CRITICAL" not in priorities
    assert "HIGH" not in priorities

    actions = [r["action"] for r in scen["recommendations"]]
    assert "INSPECT_SPINDLE_BEARING" not in actions
    assert "EXPEDITE_CRITICAL_SPARE" not in actions
    assert "REDUCE_MACHINE_FEED_RATE" not in actions


# ==============================================================================
# 7. DEDUPLICATION & CONFLICT RESOLUTION
# ==============================================================================

def test_deduplication_consolidation(engine):
    """Tests that multiple occurrences of the same action consolidate and merge evidence."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    ev1 = EvidenceItem(
        evidence_id="EVID_01",
        source_phase="Phase 6",
        source_module="Mod1",
        domain=EvidenceDomain.PREDICTIVE_FAILURE,
        metric="p_fail",
        value=0.95,
        timestamp=dt,
        machine_id="M2",
        interpretation="High risk",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )
    ev2 = EvidenceItem(
        evidence_id="EVID_02",
        source_phase="Phase 7",
        source_module="Mod2",
        domain=EvidenceDomain.TELEMETRY_ANOMALY,
        metric="anomaly",
        value=0.35,
        timestamp=dt,
        machine_id="M2",
        interpretation="High anomaly",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )

    rec1 = OperationalRecommendation(
        recommendation_id="REC_01",
        timestamp=dt,
        machine_id="M2",
        category=RecommendationCategory.MAINTENANCE,
        action=RecommendationAction.INSPECT_SPINDLE_BEARING,
        priority=RecommendationPriority.HIGH,
        urgency=ActionUrgency.SAME_DAY,
        evidence_strength=EvidenceStrength.WEAK,
        reason="Trigger 1",
        evidence=[ev1],
        source_phases=["Phase 6"],
        operational_impact="Wear",
        expected_benefit="Prevention",
        rule_id="R-M02",
        epistemic_classification=EpistemicClassification.CONTROLLED_SYNTHETIC,
    )
    rec2 = OperationalRecommendation(
        recommendation_id="REC_02",
        timestamp=dt,
        machine_id="M2",
        category=RecommendationCategory.MAINTENANCE,
        action=RecommendationAction.INSPECT_SPINDLE_BEARING,
        priority=RecommendationPriority.CRITICAL,
        urgency=ActionUrgency.IMMEDIATE,
        evidence_strength=EvidenceStrength.WEAK,
        reason="Trigger 2",
        evidence=[ev2],
        source_phases=["Phase 7"],
        operational_impact="Seizure",
        expected_benefit="Preemption",
        rule_id="R-M01",
        epistemic_classification=EpistemicClassification.CONTROLLED_SYNTHETIC,
    )

    deduped = engine.deduplicate_recommendations([rec1, rec2])
    assert len(deduped) == 1
    consolidated = deduped[0]
    assert consolidated.action == RecommendationAction.INSPECT_SPINDLE_BEARING
    assert consolidated.priority == RecommendationPriority.CRITICAL
    assert consolidated.urgency == ActionUrgency.IMMEDIATE
    assert len(consolidated.evidence) == 2
    assert "Phase 6" in consolidated.source_phases
    assert "Phase 7" in consolidated.source_phases
    assert consolidated.rule_id == "R-M01,R-M02"
    assert consolidated.evidence_strength == EvidenceStrength.MODERATE


def test_conflict_resolution_margin_over_tariff(engine):
    """Tests that bottleneck throughput mitigation suppresses off-peak energy shifting."""
    dt = datetime(2026, 1, 21, 19, 0, 0, tzinfo=timezone.utc)
    rec_flow = OperationalRecommendation(
        recommendation_id="REC_FLOW",
        timestamp=dt,
        machine_id="M2",
        category=RecommendationCategory.PRODUCTION_FLOW,
        action=RecommendationAction.REDUCE_MACHINE_FEED_RATE,
        priority=RecommendationPriority.HIGH,
        urgency=ActionUrgency.SAME_DAY,
        evidence_strength=EvidenceStrength.MODERATE,
        reason="Bottleneck delay",
        evidence=[],
        source_phases=["Phase 8"],
        operational_impact="Starvation",
        expected_benefit="Throughput",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )
    rec_energy = OperationalRecommendation(
        recommendation_id="REC_ENERGY",
        timestamp=dt,
        machine_id="M2",
        category=RecommendationCategory.ENERGY,
        action=RecommendationAction.SHIFT_HIGH_LOAD_OFF_PEAK,
        priority=RecommendationPriority.LOW,
        urgency=ActionUrgency.ROUTINE,
        evidence_strength=EvidenceStrength.WEAK,
        reason="Peak tariff window",
        evidence=[],
        source_phases=["Phase 9"],
        operational_impact="Tariff cost",
        expected_benefit="Savings",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )

    resolved = engine.resolve_conflicts([rec_flow, rec_energy])
    actions = [r.action for r in resolved]
    assert RecommendationAction.REDUCE_MACHINE_FEED_RATE in actions
    assert RecommendationAction.SHIFT_HIGH_LOAD_OFF_PEAK not in actions


# ==============================================================================
# 8. DETERMINISM, ARTIFACT PARITY & REPRODUCIBILITY
# ==============================================================================

def test_deterministic_repeated_execution(service):
    """Repeated runs on identical inputs yield 100% identical recommendation portfolios."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    run1 = service.generate_factory_recommendation_summary(as_of=dt)
    run2 = service.generate_factory_recommendation_summary(as_of=dt)

    assert run1["portfolio_summary"] == run2["portfolio_summary"]
    assert len(run1["all_active_recommendations"]) == len(run2["all_active_recommendations"])
    for r1, r2 in zip(run1["all_active_recommendations"], run2["all_active_recommendations"]):
        assert r1["recommendation_id"] == r2["recommendation_id"]
        assert r1["action"] == r2["action"]
        assert r1["priority"] == r2["priority"]


def test_json_artifact_parity(service):
    """Validates models/recommendations/recommendation_summary.json parses and matches engine output."""
    root = get_project_root()
    json_path = root / "models" / "recommendations" / "recommendation_summary.json"
    assert json_path.exists(), "recommendation_summary.json does not exist"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["phase"] == "Phase 15: Recommendation Engine"
    assert data["governance"]["decision_support_only"] is True
    assert data["governance"]["human_in_the_loop_mandatory"] is True
    assert data["m2_controlled_scenario"]["recommendation_count"] == 4
    assert data["negative_control_scenario"]["recommendation_count"] == 1


def test_operational_losses_md5_unchanged():
    """Verifies that reference operational_losses.csv remains 100% unmodified."""
    root = get_project_root()
    ref_path = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "operational_losses.csv"
    assert ref_path.exists(), "operational_losses.csv missing"

    with open(ref_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    assert file_hash == "34b12582b32d81e3121429c55ebf74e8", f"MD5 mismatch: {file_hash}"


def test_human_in_the_loop_governance(service):
    """Asserts requires_operator_verification = True across all recommendations."""
    scen = service.evaluate_machine_2_controlled_scenario()
    for rec in scen["recommendations"]:
        assert rec["requires_operator_verification"] is True


def test_c_mapss_rul_cycles_not_hours():
    """Asserts NASA C-MAPSS RUL is treated in remaining cycles and never converted to hours."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    ev = EvidenceItem(
        evidence_id="EVID_RUL_TEST",
        source_phase="Phase 6",
        source_module="C_MAPSS_RULRegressor",
        domain=EvidenceDomain.PREDICTIVE_FAILURE,
        metric="predicted_rul_cycles",
        value=14.0,
        unit="cycles",
        threshold_applied=15.0,
        timestamp=dt,
        machine_id="M2",
        interpretation="RUL is 14.0 cycles",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )
    assert ev.unit == "cycles"
    assert ev.value == 14.0


def test_no_business_sla_invented(service):
    """Asserts absence of unconfigured customer SLA penalty math in recommendations."""
    scen = service.evaluate_machine_2_controlled_scenario()
    for rec in scen["recommendations"]:
        assert "sla" not in rec["reason"].lower()
        assert "penalty" not in rec["reason"].lower()


def test_shap_isolated_as_model_explanation():
    """Asserts SHAP is treated strictly as model feature attribution, not physical causality."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    rec = evaluate_rule_r_m03("M1", dt, 210.0, 6.0, "tool_wear_min")
    assert rec is not None
    shap_ev = next(ev for ev in rec.evidence if ev.source_phase == "Phase 11")
    assert shap_ev.metric == "top_feature_attribution"
    assert "model explanation" in shap_ev.interpretation.lower()
    assert "causality" not in shap_ev.interpretation.lower()


def test_rca_isolated_as_diagnostic_hypothesis():
    """Asserts RCA candidate causes are treated as diagnostic hypotheses, not physical truth."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    rec = evaluate_rule_r_m01("M2", dt, 0.95, 0.35, "MECHANICAL_LOAD")
    assert rec is not None
    rca_ev = next(ev for ev in rec.evidence if ev.source_phase == "Phase 12")
    assert rca_ev.metric == "primary_candidate_cause"
    assert "operationally consistent" in rca_ev.interpretation.lower()
    assert "physical truth" not in rca_ev.interpretation.lower()


def test_conflict_resolution_safety_over_throughput(engine):
    """Asserts machine inspection overrides feed-rate maintenance or production throughput."""
    dt = datetime(2026, 1, 21, 12, 0, 0, tzinfo=timezone.utc)
    rec_maint = OperationalRecommendation(
        recommendation_id="REC_MAINT",
        timestamp=dt,
        machine_id="M2",
        category=RecommendationCategory.MAINTENANCE,
        action=RecommendationAction.INSPECT_SPINDLE_BEARING,
        priority=RecommendationPriority.CRITICAL,
        urgency=ActionUrgency.IMMEDIATE,
        evidence_strength=EvidenceStrength.STRONG,
        reason="Catastrophic seizure risk",
        evidence=[],
        source_phases=["Phase 6", "Phase 7"],
        operational_impact="Seizure",
        expected_benefit="Safety",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )
    rec_flow = OperationalRecommendation(
        recommendation_id="REC_FLOW",
        timestamp=dt,
        machine_id="M2",
        category=RecommendationCategory.PRODUCTION_FLOW,
        action=RecommendationAction.REDUCE_MACHINE_FEED_RATE,
        priority=RecommendationPriority.HIGH,
        urgency=ActionUrgency.SAME_DAY,
        evidence_strength=EvidenceStrength.MODERATE,
        reason="Bottleneck delay",
        evidence=[],
        source_phases=["Phase 8"],
        operational_impact="Starvation",
        expected_benefit="Throughput",
        epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
    )

    ranked = engine.process([rec_flow, rec_maint])
    # Inspection must be ranked first (CRITICAL > HIGH)
    assert ranked[0].action == RecommendationAction.INSPECT_SPINDLE_BEARING
    assert ranked[1].action == RecommendationAction.REDUCE_MACHINE_FEED_RATE

