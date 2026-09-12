"""
NirmaanAI Factory Health Score Test Suite
Phase 13: Factory Health Score

Comprehensive unit, integration, and integrity test suite verifying:
1. Bounded health score [0, 100]
2. Deterministic scoring
3. Dimension normalization across all 6 dimensions
4. Configured analytical weight validation
5. Machine-level score calculation
6. Factory-level aggregation with equal baseline weighting (0.20 per asset)
7. Machine-specific baseline normalization
8. Explicit missing-data handling
9. Insufficient-data state override (< 40% coverage)
10. Partial-evidence weight renormalization
11. Separation of assessment confidence from health score
12. Critical machine detection and constraint alert override
13. Temporal causal integrity and leakage prevention
14. Historical reproducibility
15. Machine 2 controlled synthetic degradation trend (Days 17-23)
16. Post-maintenance recovery validation
17. No future data contamination
18. Human-readable explanation and penalty attribution
19. Negative Control 1: High SHAP alone does not collapse health
20. Negative Control 2: High anomaly without failure does not produce CRITICAL status
21. Health states mapping across all bands
22. Factory aggregation edge cases
23. Analytical sensitivity monotonicity
24. SHAP double-counting safeguard
25. RCA double-counting safeguard
26. End-to-end service layer execution
"""

import copy
from datetime import datetime, timezone
import pytest
import numpy as np

from src.health.health_models import (
    HealthState,
    HealthAssessmentConfidence,
    EvidenceCoverageStatus,
    HealthDimensionType,
    DimensionScoreBreakdown,
    HealthEvidenceContext,
    MachineHealthScore,
    FactoryHealthScore,
    HealthTrendPoint,
)
from src.health.health_dimensions import (
    calculate_failure_risk_health,
    calculate_anomaly_health,
    calculate_flow_health,
    calculate_energy_health,
    calculate_maintenance_health,
    calculate_diagnostic_consistency_health,
)
from src.health.health_scoring import (
    MachineHealthScoringEngine,
    CONFIGURED_HEALTH_WEIGHTS,
    DEFAULT_MACHINE_BASELINES,
)
from src.health.health_aggregation import FactoryHealthAggregationEngine
from src.health.health_service import FactoryHealthService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def scoring_engine():
    return MachineHealthScoringEngine()


@pytest.fixture
def aggregation_engine():
    return FactoryHealthAggregationEngine()


@pytest.fixture
def health_service():
    return FactoryHealthService()


@pytest.fixture
def nominal_context():
    return HealthEvidenceContext(
        machine_id="M2",
        timestamp="2026-01-18T12:00:00Z",
        prediction_probability=0.03,
        prediction_threshold=0.910,
        anomaly_score=0.05,
        anomaly_threshold=0.2405,
        cycle_time_sec=45.0,
        design_cycle_time_sec=45.0,
        bottleneck_state="NOMINAL",
        power_consumption_kw=22.0,
        baseline_power_kw=22.0,
        spare_stock_level=5,
        spare_safety_stock=2,
        has_active_unresolved_rca=False,
    )


@pytest.fixture
def critical_context():
    return HealthEvidenceContext(
        machine_id="M2",
        timestamp="2026-01-22T16:30:00Z",
        prediction_probability=0.965,
        prediction_threshold=0.910,
        anomaly_score=0.485,
        anomaly_threshold=0.2405,
        cycle_time_sec=62.0,
        design_cycle_time_sec=45.0,
        bottleneck_state="CRITICAL",
        power_consumption_kw=38.0,
        baseline_power_kw=22.0,
        spare_stock_level=0,
        spare_safety_stock=2,
        is_maintenance_overdue=True,
        has_active_unresolved_rca=True,
        active_rca_severity="CRITICAL",
        active_rca_confidence="HIGH",
    )


# ============================================================================
# 1. BOUNDED SCORE & MATHEMATICAL INTEGRITY
# ============================================================================

def test_health_score_bounded_0_100(scoring_engine, nominal_context, critical_context):
    """Test that calculated health scores across all contexts remain strictly in [0.0, 100.0]."""
    score_nom = scoring_engine.evaluate_machine(nominal_context)
    assert 0.0 <= score_nom.health_score <= 100.0

    score_crit = scoring_engine.evaluate_machine(critical_context)
    assert 0.0 <= score_crit.health_score <= 100.0

    # Extreme out-of-range input must raise validation error
    with pytest.raises(Exception):
        HealthEvidenceContext(
            machine_id="M1",
            timestamp="2026-01-18T12:00:00Z",
            prediction_probability=1.5,
        )

    # Valid upper-boundary input context
    boundary_ctx = HealthEvidenceContext(
        machine_id="M1",
        timestamp="2026-01-18T12:00:00Z",
        prediction_probability=1.0,
        anomaly_score=1.0,
        cycle_time_sec=500.0,
        power_consumption_kw=1000.0,
        spare_stock_level=0,
        is_maintenance_overdue=True,
        has_active_unresolved_rca=True,
        active_rca_severity="CRITICAL",
        active_rca_confidence="HIGH",
    )
    score_boundary = scoring_engine.evaluate_machine(boundary_ctx)
    assert 0.0 <= score_boundary.health_score <= 100.0


def test_deterministic_scoring(scoring_engine, critical_context):
    """Test that repeated evaluation of identical evidence yields strictly deterministic outputs."""
    res1 = scoring_engine.evaluate_machine(critical_context)
    res2 = scoring_engine.evaluate_machine(critical_context)

    assert res1.health_score == res2.health_score
    assert res1.state == res2.state
    assert res1.confidence == res2.confidence
    assert res1.top_degraders == res2.top_degraders
    assert res1.explanation_narrative == res2.explanation_narrative
    assert len(res1.dimension_breakdowns) == len(res2.dimension_breakdowns)


# ============================================================================
# 2. DIMENSION NORMALIZATION
# ============================================================================

def test_dimension_normalization():
    """Verify that all six individual dimension functions produce bounded scores [0.0, 100.0]."""
    # 1. Failure Risk
    f_score, _ = calculate_failure_risk_health(0.0, 0.910)
    assert f_score == 100.0
    f_score_high, _ = calculate_failure_risk_health(0.95, 0.910)
    assert 0.0 <= f_score_high < 10.0
    assert calculate_failure_risk_health(None)[0] is None

    # 2. Anomaly Health
    a_score, _ = calculate_anomaly_health(0.0, 0.2405)
    assert a_score == 100.0
    a_score_high, _ = calculate_anomaly_health(0.50, 0.2405)
    assert 0.0 <= a_score_high <= 100.0
    assert calculate_anomaly_health(None)[0] is None

    # 3. Flow Health
    fl_score, _ = calculate_flow_health(cycle_time_sec=45.0, design_cycle_time_sec=45.0)
    assert fl_score == 100.0
    fl_score_crit, _ = calculate_flow_health(cycle_time_sec=90.0, design_cycle_time_sec=45.0, bottleneck_state="CRITICAL")
    assert 0.0 <= fl_score_crit <= 100.0

    # 4. Energy Health
    e_score, _ = calculate_energy_health(power_kw=22.0, baseline_power_kw=22.0)
    assert e_score == 100.0
    e_score_high, _ = calculate_energy_health(power_kw=60.0, baseline_power_kw=22.0)
    assert 0.0 <= e_score_high <= 100.0

    # 5. Maintenance Context
    m_score, _ = calculate_maintenance_health(spare_stock_level=5, spare_safety_stock=2)
    assert m_score == 100.0
    m_score_out, _ = calculate_maintenance_health(spare_stock_level=0, is_overdue=True)
    assert 0.0 <= m_score_out <= 100.0

    # 6. Diagnostic Consistency
    r_score, _ = calculate_diagnostic_consistency_health(has_active_unresolved_rca=False)
    assert r_score == 100.0
    r_score_crit, _ = calculate_diagnostic_consistency_health(
        has_active_unresolved_rca=True,
        active_rca_severity="CRITICAL",
        active_rca_confidence="HIGH",
    )
    assert r_score_crit == 30.0


# ============================================================================
# 3. WEIGHT VALIDATION
# ============================================================================

def test_weight_sum_validation():
    """Verify that configured analytical weights sum exactly to 1.00; invalid weights raise ValueError."""
    total_w = sum(CONFIGURED_HEALTH_WEIGHTS.values())
    assert np.isclose(total_w, 1.0, atol=1e-5)

    # Creating engine with invalid weights must raise ValueError
    invalid_weights = {
        HealthDimensionType.FAILURE_RISK: 0.50,
        HealthDimensionType.ANOMALY_HEALTH: 0.20,
        HealthDimensionType.FLOW_HEALTH: 0.20,
        HealthDimensionType.ENERGY_HEALTH: 0.10,
        HealthDimensionType.MAINTENANCE_CONTEXT: 0.10,
        HealthDimensionType.DIAGNOSTIC_CONSISTENCY: 0.15,  # Sum = 1.25
    }
    with pytest.raises(ValueError, match="Configured dimension weights must sum to 1.00"):
        MachineHealthScoringEngine(weights=invalid_weights)


# ============================================================================
# 4. MACHINE SCORE & EXPLANATIONS
# ============================================================================

def test_machine_level_score(scoring_engine, nominal_context, critical_context):
    """Verify machine-level scoring, breakdown attribution, and narrative generation."""
    nom_res = scoring_engine.evaluate_machine(nominal_context)
    assert nom_res.state == HealthState.EXCELLENT
    assert nom_res.health_score >= 90.0
    assert nom_res.confidence == HealthAssessmentConfidence.HIGH
    assert nom_res.evidence_coverage_pct == 100.0

    crit_res = scoring_engine.evaluate_machine(critical_context)
    assert crit_res.state == HealthState.CRITICAL
    assert crit_res.health_score < 40.0
    assert len(crit_res.top_degraders) >= 1
    assert "Predictive Failure Risk" in crit_res.top_degraders[0]
    assert "CRITICAL" in crit_res.explanation_narrative


# ============================================================================
# 5. MACHINE-SPECIFIC BASELINE NORMALIZATION
# ============================================================================

def test_machine_specific_baseline_normalization(scoring_engine):
    """Verify that machine-specific baselines (design cycle time, nominal power) are applied per machine."""
    ctx_m1 = HealthEvidenceContext(
        machine_id="M1",
        timestamp="2026-01-18T12:00:00Z",
        cycle_time_sec=30.0,  # M1 baseline design is 30.0s
        power_consumption_kw=18.0,  # M1 baseline power is 18.0 kW
        spare_stock_level=3,
        spare_safety_stock=2,
    )
    res_m1 = scoring_engine.evaluate_machine(ctx_m1)
    flow_b = [b for b in res_m1.dimension_breakdowns if b.dimension == HealthDimensionType.FLOW_HEALTH][0]
    energy_b = [b for b in res_m1.dimension_breakdowns if b.dimension == HealthDimensionType.ENERGY_HEALTH][0]

    assert flow_b.raw_score == 100.0
    assert energy_b.raw_score == 100.0

    # If evaluated for M4 (where baseline power is 25.0 kW and design cycle is 40.0s)
    ctx_m4 = HealthEvidenceContext(
        machine_id="M4",
        timestamp="2026-01-18T12:00:00Z",
        cycle_time_sec=42.0,  # 42s vs 40s design -> ratio 1.05
        power_consumption_kw=18.5,  # 18.5 kW vs 25.0 kW baseline -> deviation
        spare_stock_level=3,
        spare_safety_stock=2,
    )
    res_m4 = scoring_engine.evaluate_machine(ctx_m4)
    flow_m4 = [b for b in res_m4.dimension_breakdowns if b.dimension == HealthDimensionType.FLOW_HEALTH][0]
    assert flow_m4.raw_score < 100.0


# ============================================================================
# 6. MISSING EVIDENCE & INSUFFICIENT DATA OVERRIDE
# ============================================================================

def test_missing_evidence_handling(scoring_engine):
    """Verify that dimensions with missing telemetry return None without crashing."""
    ctx_sparse = HealthEvidenceContext(
        machine_id="M3",
        timestamp="2026-01-18T12:00:00Z",
        prediction_probability=0.04,
        anomaly_score=0.08,
        # Flow, Energy, Maintenance omitted
    )
    res = scoring_engine.evaluate_machine(ctx_sparse)
    unavailable_dims = [b.dimension for b in res.dimension_breakdowns if not b.is_available]
    assert HealthDimensionType.FLOW_HEALTH in unavailable_dims
    assert HealthDimensionType.ENERGY_HEALTH in unavailable_dims
    assert HealthDimensionType.MAINTENANCE_CONTEXT in unavailable_dims


def test_insufficient_data_state_override(scoring_engine):
    """Verify that when evidence coverage is < 40%, health state is overridden to INSUFFICIENT_DATA."""
    # Only anomaly score available (weight 0.20 = 20% coverage < 40%)
    ctx_insufficient = HealthEvidenceContext(
        machine_id="M3",
        timestamp="2026-01-18T12:00:00Z",
        anomaly_score=0.08,
    )
    res = scoring_engine.evaluate_machine(ctx_insufficient)
    assert res.state == HealthState.INSUFFICIENT_DATA
    assert res.coverage_status == EvidenceCoverageStatus.INSUFFICIENT_DATA
    assert res.health_score == 0.0
    assert res.confidence == HealthAssessmentConfidence.LOW
    assert "INSUFFICIENT_DATA" in res.explanation_narrative


def test_partial_evidence_coverage_renormalization(scoring_engine):
    """Verify that when coverage is in [40%, 99.9%], available weights are proportionally re-normalized."""
    # Prediction (0.25) + Anomaly (0.20) = 0.45 available weight (45% coverage)
    ctx_partial = HealthEvidenceContext(
        machine_id="M3",
        timestamp="2026-01-18T12:00:00Z",
        prediction_probability=0.0,  # raw score 100
        anomaly_score=0.0,  # raw score 100
    )
    res = scoring_engine.evaluate_machine(ctx_partial)
    assert res.coverage_status == EvidenceCoverageStatus.PARTIAL_EVIDENCE
    assert res.state == HealthState.EXCELLENT
    assert np.isclose(res.health_score, 100.0, atol=1e-2)

    # Check effective weights sum to 1.00
    avail_breakdowns = [b for b in res.dimension_breakdowns if b.is_available]
    effective_weight_sum = sum(b.effective_weight for b in avail_breakdowns)
    assert np.isclose(effective_weight_sum, 1.0, atol=1e-5)


# ============================================================================
# 7. SEPARATION OF CONFIDENCE FROM HEALTH SCORE
# ============================================================================

def test_confidence_vs_health_separation(scoring_engine, critical_context):
    """Verify that confidence reflects evidence quality/coverage, NOT healthiness."""
    crit_res = scoring_engine.evaluate_machine(critical_context)

    # Machine is in severe breakdown (CRITICAL, score < 40)
    assert crit_res.state == HealthState.CRITICAL
    assert crit_res.health_score < 40.0
    # But assessment confidence is HIGH because all 6 dimensions are fully corroborated
    assert crit_res.confidence == HealthAssessmentConfidence.HIGH


# ============================================================================
# 8. FACTORY AGGREGATION & CRITICAL MACHINE CONSTRAINTS
# ============================================================================

def test_factory_level_aggregation(aggregation_engine, nominal_context, critical_context, scoring_engine):
    """Verify plant-level aggregation with equal 0.20 weighting and critical machine constraint alert."""
    scores = []
    # 4 nominal machines (M1, M3, M4, M5)
    for m_id in ["M1", "M3", "M4", "M5"]:
        ctx = copy.deepcopy(nominal_context)
        ctx.machine_id = m_id
        scores.append(scoring_engine.evaluate_machine(ctx))

    # 1 critical machine (M2)
    scores.append(scoring_engine.evaluate_machine(critical_context))

    factory_res = aggregation_engine.aggregate_factory_health(scores, timestamp="2026-01-22T16:30:00Z")

    assert factory_res.critical_machine_id == "M2"
    assert factory_res.critical_machine_score < 40.0
    assert factory_res.critical_machine_alert is True
    # Constraint alert override: plant state must NOT be HEALTHY or EXCELLENT when an asset is in breakdown
    assert factory_res.state == HealthState.WATCH
    assert len(factory_res.machine_weights) == 5
    for w in factory_res.machine_weights.values():
        assert np.isclose(w, 0.20, atol=1e-5)


def test_factory_aggregation_all_healthy(aggregation_engine, nominal_context, scoring_engine):
    """Verify that when all machines are healthy, plant state is EXCELLENT with no alert."""
    scores = []
    for m_id in ["M1", "M2", "M3", "M4", "M5"]:
        ctx = copy.deepcopy(nominal_context)
        ctx.machine_id = m_id
        scores.append(scoring_engine.evaluate_machine(ctx))

    factory_res = aggregation_engine.aggregate_factory_health(scores, timestamp="2026-01-18T12:00:00Z")
    assert factory_res.state == HealthState.EXCELLENT
    assert factory_res.critical_machine_alert is False
    assert factory_res.factory_health_score >= 90.0


def test_factory_aggregation_edge_cases(aggregation_engine, scoring_engine):
    """Verify factory aggregation handles empty machine lists and insufficient-data machines."""
    empty_res = aggregation_engine.aggregate_factory_health([], timestamp="2026-01-18T12:00:00Z")
    assert empty_res.state == HealthState.INSUFFICIENT_DATA
    assert empty_res.factory_health_score == 0.0

    # When all machines have insufficient data
    insufficient_scores = [
        scoring_engine.evaluate_machine(HealthEvidenceContext(machine_id=m_id, timestamp="2026-01-18T12:00:00Z"))
        for m_id in ["M1", "M2", "M3"]
    ]
    all_insuf_res = aggregation_engine.aggregate_factory_health(insufficient_scores, timestamp="2026-01-18T12:00:00Z")
    assert all_insuf_res.state == HealthState.INSUFFICIENT_DATA


# ============================================================================
# 9. TEMPORAL INTEGRITY & HISTORICAL REPRODUCIBILITY
# ============================================================================

def test_temporal_leakage_prevention(health_service):
    """Verify that evaluating health at Day 18 does not use future Day 22 maintenance records."""
    trend = health_service.evaluate_historical_trend(
        machine_id="M2",
        start_timestamp="2026-01-17T00:00:00Z",
        end_timestamp="2026-01-18T23:59:59Z",
    )
    # Day 18 evaluation must be HEALTHY, not influenced by future emergency halt
    for pt in trend:
        if "2026-01-18" in pt.timestamp:
            assert pt.state in [HealthState.EXCELLENT, HealthState.HEALTHY]
            assert pt.score >= 85.0
            assert pt.is_post_maintenance_recovery is False


def test_historical_score_reproducibility(health_service):
    """Verify evaluating the same historical timestamp repeatedly yields identical scores."""
    pt1 = health_service.evaluate_historical_trend(
        machine_id="M2",
        start_timestamp="2026-01-20T00:00:00Z",
        end_timestamp="2026-01-20T23:59:59Z",
    )[0]
    pt2 = health_service.evaluate_historical_trend(
        machine_id="M2",
        start_timestamp="2026-01-20T00:00:00Z",
        end_timestamp="2026-01-20T23:59:59Z",
    )[0]
    assert pt1.score == pt2.score
    assert pt1.state == pt2.state


# ============================================================================
# 10. MACHINE 2 CONTROLLED SYNTHETIC SCENARIO & RECOVERY
# ============================================================================

def test_m2_controlled_synthetic_health_trend(health_service):
    """
    [CONTROLLED SYNTHETIC SCENARIO]
    Verify Machine 2 health progression across Days 17-23:
    NORMAL -> degradation -> worsening -> CRITICAL -> post-maintenance recovery.
    """
    trend = health_service.evaluate_historical_trend("M2")
    assert len(trend) == 7

    scores_by_date = {pt.timestamp[:10]: pt for pt in trend}

    # Day 17: Normal baseline
    assert scores_by_date["2026-01-17"].state == HealthState.EXCELLENT
    assert scores_by_date["2026-01-17"].score > 90.0

    # Day 18: Degradation onset
    assert scores_by_date["2026-01-18"].score < scores_by_date["2026-01-17"].score

    # Day 20: Severe degradation
    assert scores_by_date["2026-01-20"].state in [HealthState.DEGRADED, HealthState.WATCH]

    # Day 21 & Day 22: Peak degradation and Emergency Halt (MAINT_0003 at 16:30 UTC)
    assert scores_by_date["2026-01-21"].state == HealthState.CRITICAL
    assert scores_by_date["2026-01-22"].state == HealthState.CRITICAL
    assert scores_by_date["2026-01-22"].score < 30.0

    # Day 23: Post-maintenance recovery
    assert scores_by_date["2026-01-23"].state == HealthState.EXCELLENT
    assert scores_by_date["2026-01-23"].score > 90.0
    assert scores_by_date["2026-01-23"].is_post_maintenance_recovery is True


# ============================================================================
# 11. NEGATIVE CONTROLS
# ============================================================================

def test_negative_control_shap_alone_not_health_penalty(scoring_engine):
    """
    CONTROL 1: High SHAP attribution (+3.80 on tool wear) with nominal operational telemetry.
    Expected: SHAP alone must NOT cause a health collapse (score must remain >= 85.0).
    """
    ctx = HealthEvidenceContext(
        machine_id="M2",
        timestamp="2026-01-18T12:00:00Z",
        prediction_probability=0.03,
        anomaly_score=0.05,
        cycle_time_sec=45.0,
        power_consumption_kw=22.0,
        spare_stock_level=5,
        spare_safety_stock=2,
        shap_contributions={"tool_wear_min": 3.80, "rotational_speed_rpm": 2.10},
    )
    res = scoring_engine.evaluate_machine(ctx)
    assert res.state in [HealthState.EXCELLENT, HealthState.HEALTHY]
    assert res.health_score >= 85.0
    # Confirm SHAP has 0 weight in breakdown
    shap_breakdown = [b for b in res.dimension_breakdowns if b.dimension_name == "SHAP"]
    assert len(shap_breakdown) == 0  # Not a scoring dimension


def test_negative_control_anomaly_without_failure_not_critical(scoring_engine):
    """
    CONTROL 2: High anomaly score (0.45) with low failure probability and nominal flow.
    Expected: Health may decline, but anomaly alone must NOT produce CRITICAL state.
    """
    ctx = HealthEvidenceContext(
        machine_id="M2",
        timestamp="2026-01-18T12:00:00Z",
        prediction_probability=0.04,  # low failure probability
        anomaly_score=0.45,  # high anomaly
        cycle_time_sec=45.0,
        power_consumption_kw=22.0,
        spare_stock_level=5,
        spare_safety_stock=2,
    )
    res = scoring_engine.evaluate_machine(ctx)
    assert res.state != HealthState.CRITICAL
    assert res.health_score >= 50.0  # Confirms Anomaly != Failure


# ============================================================================
# 12. DOUBLE-COUNTING AUDIT TESTS
# ============================================================================

def test_shap_double_counting_prevention():
    """Verify that SHAP does not enter the analytical health weighting formula."""
    assert "SHAP" not in [dim.value for dim in CONFIGURED_HEALTH_WEIGHTS.keys()]
    assert HealthDimensionType.FAILURE_RISK in CONFIGURED_HEALTH_WEIGHTS


def test_rca_double_counting_prevention():
    """
    Verify that RCA acts strictly as a diagnostic-resolution/severity modifier,
    and does not re-add raw telemetry or sensor drift.
    """
    # Context with no active RCA
    score_nom, desc_nom = calculate_diagnostic_consistency_health(
        has_active_unresolved_rca=False,
        active_rca_severity=None,
    )
    assert score_nom == 100.0

    # Context with active unresolved CRITICAL RCA
    score_rca, desc_rca = calculate_diagnostic_consistency_health(
        has_active_unresolved_rca=True,
        active_rca_severity="CRITICAL",
        active_rca_confidence="HIGH",
    )
    assert score_rca == 30.0
    assert "Active RCA finding" in desc_rca


# ============================================================================
# 13. ANALYTICAL SENSITIVITY MONOTONICITY
# ============================================================================

def test_analytical_sensitivity_monotonicity(scoring_engine, nominal_context):
    """
    Verify analytical sensitivity monotonicity:
    Holding all other inputs constant, increasing degradation across any dimension
    must NEVER increase the health score.
    """
    base_kwargs = nominal_context.model_dump()

    # 1. Failure Probability Sensitivity
    p_scores = []
    for p in [0.0, 0.20, 0.50, 0.95]:
        ctx = HealthEvidenceContext(**{**base_kwargs, "prediction_probability": p})
        p_scores.append(scoring_engine.evaluate_machine(ctx).health_score)
    assert all(p_scores[i] >= p_scores[i+1] for i in range(len(p_scores)-1))

    # 2. Anomaly Score Sensitivity
    a_scores = []
    for a in [0.0, 0.10, 0.25, 0.45]:
        ctx = HealthEvidenceContext(**{**base_kwargs, "anomaly_score": a})
        a_scores.append(scoring_engine.evaluate_machine(ctx).health_score)
    assert all(a_scores[i] >= a_scores[i+1] for i in range(len(a_scores)-1))

    # 3. Cycle Ratio Sensitivity
    r_scores = []
    for r in [1.0, 1.15, 1.30, 1.50]:
        ctx = HealthEvidenceContext(**{**base_kwargs, "cycle_ratio": r, "cycle_time_sec": 45.0 * r})
        r_scores.append(scoring_engine.evaluate_machine(ctx).health_score)
    assert all(r_scores[i] >= r_scores[i+1] for i in range(len(r_scores)-1))

    # 4. Energy Deviation Sensitivity
    e_scores = []
    for mult in [1.0, 1.20, 1.50, 1.80]:
        ctx = HealthEvidenceContext(**{**base_kwargs, "power_consumption_kw": 22.0 * mult})
        e_scores.append(scoring_engine.evaluate_machine(ctx).health_score)
    assert all(e_scores[i] >= e_scores[i+1] for i in range(len(e_scores)-1))

    # 5. Maintenance Context Sensitivity
    m_scores = []
    for spares in [5, 2, 1, 0]:
        ctx = HealthEvidenceContext(**{**base_kwargs, "spare_stock_level": spares})
        m_scores.append(scoring_engine.evaluate_machine(ctx).health_score)
    assert all(m_scores[i] >= m_scores[i+1] for i in range(len(m_scores)-1))


# ============================================================================
# 14. HEALTH STATES MAPPING
# ============================================================================

def test_all_health_states_mapping(scoring_engine):
    """Verify that score-to-state mapping correctly covers all configured bands."""
    assert scoring_engine._map_score_to_state(95.0) == HealthState.EXCELLENT
    assert scoring_engine._map_score_to_state(90.0) == HealthState.EXCELLENT
    assert scoring_engine._map_score_to_state(89.9) == HealthState.HEALTHY
    assert scoring_engine._map_score_to_state(75.0) == HealthState.HEALTHY
    assert scoring_engine._map_score_to_state(74.9) == HealthState.WATCH
    assert scoring_engine._map_score_to_state(60.0) == HealthState.WATCH
    assert scoring_engine._map_score_to_state(59.9) == HealthState.DEGRADED
    assert scoring_engine._map_score_to_state(40.0) == HealthState.DEGRADED
    assert scoring_engine._map_score_to_state(39.9) == HealthState.CRITICAL
    assert scoring_engine._map_score_to_state(0.0) == HealthState.CRITICAL


# ============================================================================
# 15. END-TO-END SERVICE LAYER EXECUTION
# ============================================================================

def test_service_layer_end_to_end(health_service):
    """Verify that the service layer generates full factory reports and historical trends."""
    assessment = health_service.calculate_factory_health(timestamp="2026-01-22T16:30:00Z")
    assert assessment.factory_health_score > 0.0
    assert assessment.critical_machine_id == "M2"
    assert assessment.critical_machine_alert is True

    report = health_service.format_health_report(assessment)
    assert "NIRMAAN AI" in report
    assert "CRITICAL MACHINE ALERT" in report
    assert "SCIENTIFIC HEALTH DISCLAIMER" in report
