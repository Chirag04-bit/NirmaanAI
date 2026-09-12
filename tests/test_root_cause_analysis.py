"""
NirmaanAI Root Cause Analysis (RCA) Test Suite
Phase 12: Root Cause Analysis

Comprehensive unit, integration, and integrity test suite verifying:
1. RCA event schema validation
2. Cause taxonomy completeness (all 13 categories)
3. Deterministic evidence scoring
4. SHAP evidence integration
5. Anomaly evidence integration
6. Temporal precedence ordering
7. Machine-specific normalization
8. Contradictory evidence handling
9. Confidence classification logic
10. Anomaly != failure distinction
11. Synthetic Machine 2 scenario reconstruction
12. No future leakage
13. No causal-probability claims
14. Insufficient-evidence handling
15. Deterministic repeated execution
16. Service-layer end-to-end RCA
17. Invalid/missing evidence handling
"""

import json
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from src.rca.cause_taxonomy import (
    CauseCategory,
    CAUSE_DEFINITIONS,
    FEATURE_TO_CAUSE_MAP,
    get_candidate_causes_for_feature,
    get_cause_definition,
)
from src.rca.evidence_engine import (
    EvidenceFusionEngine,
    DEFAULT_MACHINE_BASELINES,
)
from src.rca.rca_engine import RootCauseAnalysisEngine
from src.rca.rca_models import (
    CandidateCauseScore,
    EvidenceSourceType,
    RCAConfidenceLevel,
    RCAEventContext,
    RCAReportResponse,
    SignalEvidenceItem,
    TemporalStage,
    TemporalStep,
)
from src.rca.rca_service import RootCauseAnalysisService
from src.rca.temporal_analysis import (
    TemporalPrecedenceEngine,
    parse_timestamp,
)


@pytest.fixture
def rca_service():
    return RootCauseAnalysisService()


@pytest.fixture
def evidence_engine():
    return EvidenceFusionEngine()


@pytest.fixture
def baseline_m2_event():
    return RCAEventContext(
        event_id="EVT_TEST_001",
        timestamp="2026-01-21T10:30:00Z",
        machine_id="M2",
        event_type="UNPLANNED_STOP",
        severity="CRITICAL",
        observed_outcome="Critical vibration exceeding threshold",
        prediction_probability=0.95,
        prediction_threshold=0.91,
        anomaly_score=0.45,
        anomaly_threshold=0.2405,
        bottleneck_state="CRITICAL",
        cycle_time_sec=60.0,
        telemetry={
            "vibration_mms": 5.4,
            "temperature_c": 52.0,
            "torque_nm": 55.0,
            "power_consumption_kw": 28.0,
        },
        shap_contributions={
            "torque_nm": 2.2,
            "rotational_speed_rpm": 1.1,
            "temp_diff_c": 1.5,
        },
        historical_telemetry=[
            {
                "timestamp": "2026-01-18T08:00:00Z",
                "vibration_mms": 2.1,
                "temperature_c": 36.0,
                "cycle_time_sec": 46.0,
                "anomaly_score": 0.14,
            },
            {
                "timestamp": "2026-01-19T12:00:00Z",
                "vibration_mms": 3.9,
                "temperature_c": 46.0,
                "cycle_time_sec": 52.0,
                "anomaly_score": 0.31,
            },
            {
                "timestamp": "2026-01-20T10:00:00Z",
                "vibration_mms": 4.7,
                "temperature_c": 50.0,
                "cycle_time_sec": 57.0,
                "anomaly_score": 0.42,
            },
        ],
        is_synthetic_scenario=True,
    )


# -----------------------------------------------------------------------------
# 1. RCA Event Schema Validation
# -----------------------------------------------------------------------------
def test_rca_event_schema_validation(baseline_m2_event):
    """Event model validates required fields and schema constraints."""
    assert baseline_m2_event.event_id == "EVT_TEST_001"
    assert baseline_m2_event.machine_id == "M2"
    assert baseline_m2_event.prediction_probability == 0.95
    assert len(baseline_m2_event.historical_telemetry) == 3

    # Invalid probability (>1.0) must fail validation
    with pytest.raises(ValidationError):
        RCAEventContext(
            event_id="ERR_01",
            timestamp="2026-01-01T00:00:00Z",
            machine_id="M1",
            prediction_probability=1.5,  # Invalid
        )


# -----------------------------------------------------------------------------
# 2. Cause Taxonomy Completeness
# -----------------------------------------------------------------------------
def test_cause_taxonomy_completeness():
    """All 13 controlled cause categories are defined with valid metadata."""
    assert len(CauseCategory) == 13
    assert len(CAUSE_DEFINITIONS) == 13

    for cat in CauseCategory:
        definition = get_cause_definition(cat)
        assert definition.category == cat
        assert len(definition.display_name) > 0
        assert len(definition.description) > 0
        assert len(definition.investigation_suggestion) > 0


# -----------------------------------------------------------------------------
# 3. Deterministic Evidence Scoring
# -----------------------------------------------------------------------------
def test_deterministic_evidence_scoring(evidence_engine, baseline_m2_event):
    """Same input produces bitwise identical composite evidence scores."""
    score1, sup1, cont1 = evidence_engine.evaluate_candidate_cause(
        CauseCategory.MECHANICAL_LOAD, baseline_m2_event, temporal_multiplier=1.0
    )
    score2, sup2, cont2 = evidence_engine.evaluate_candidate_cause(
        CauseCategory.MECHANICAL_LOAD, baseline_m2_event, temporal_multiplier=1.0
    )

    assert score1 == score2
    assert len(sup1) == len(sup2)
    assert len(cont1) == len(cont2)
    assert 0.0 <= score1 <= 1.0


# -----------------------------------------------------------------------------
# 4. SHAP Evidence Integration
# -----------------------------------------------------------------------------
def test_shap_evidence_integration(evidence_engine):
    """Positive SHAP contributions correctly increase candidate cause score."""
    event_no_shap = RCAEventContext(
        event_id="EVT_SHAP_0",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        telemetry={"torque_nm": 42.0},
        shap_contributions={},
    )
    event_with_shap = RCAEventContext(
        event_id="EVT_SHAP_1",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        telemetry={"torque_nm": 42.0},
        shap_contributions={"torque_nm": 3.50},
    )

    score_no_shap, _, _ = evidence_engine.evaluate_candidate_cause(
        CauseCategory.MECHANICAL_LOAD, event_no_shap
    )
    score_with_shap, sup_shap, _ = evidence_engine.evaluate_candidate_cause(
        CauseCategory.MECHANICAL_LOAD, event_with_shap
    )

    assert score_with_shap > score_no_shap
    assert any(s.source == EvidenceSourceType.SHAP_MODEL_ATTRIBUTION for s in sup_shap)


# -----------------------------------------------------------------------------
# 5. Anomaly Evidence Integration
# -----------------------------------------------------------------------------
def test_anomaly_evidence_integration(evidence_engine):
    """Elevated anomaly score above Phase 7 threshold corroborates instability and mechanical load."""
    event_normal = RCAEventContext(
        event_id="EVT_ANOM_0",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        anomaly_score=0.08,
        anomaly_threshold=0.2405,
    )
    event_anom = RCAEventContext(
        event_id="EVT_ANOM_1",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        anomaly_score=0.48,
        anomaly_threshold=0.2405,
    )

    score_norm, _, cont_norm = evidence_engine.evaluate_candidate_cause(
        CauseCategory.PROCESS_INSTABILITY, event_normal
    )
    score_anom, sup_anom, _ = evidence_engine.evaluate_candidate_cause(
        CauseCategory.PROCESS_INSTABILITY, event_anom
    )

    assert score_anom > score_norm
    assert any(s.source == EvidenceSourceType.ANOMALY_DETECTION for s in sup_anom)
    # Low anomaly contradicts process instability
    assert any(c.source == EvidenceSourceType.ANOMALY_DETECTION for c in cont_norm)


# -----------------------------------------------------------------------------
# 6. Temporal Precedence Ordering
# -----------------------------------------------------------------------------
def test_temporal_precedence_ordering(baseline_m2_event):
    """Reconstructed progression sequence verifies chronological ordering t0 < t1 < t2 < t3."""
    steps, verified, score = TemporalPrecedenceEngine.reconstruct_sequence(
        history=baseline_m2_event.historical_telemetry,
        event_timestamp=baseline_m2_event.timestamp,
        machine_baseline_vib=1.4,
        alert_vib=3.8,
        nominal_cycle_sec=45.0,
    )

    assert verified is True
    assert score == 1.0
    assert len(steps) >= 3

    # Check stage ordering
    stages = [s.stage for s in steps]
    assert TemporalStage.T0_PRECURSOR in stages
    assert TemporalStage.T3_EVENT in stages

    dts = [parse_timestamp(s.timestamp) for s in steps]
    for i in range(len(dts) - 1):
        assert dts[i] <= dts[i + 1]


# -----------------------------------------------------------------------------
# 7. Machine-Specific Normalization
# -----------------------------------------------------------------------------
def test_machine_specific_normalization(evidence_engine):
    """Machine-specific baseline differences are preserved (M4 baseline 0.8 vs M2 baseline 1.4)."""
    # 1.5 mm/s on M4 (where base=0.8, alert=3.0) is a moderate elevation.
    # 1.5 mm/s on M2 (where base=1.4, alert=3.8) is virtually nominal.
    event_m4 = RCAEventContext(
        event_id="EVT_M4",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M4",
        telemetry={"vibration_mms": 1.5},
    )
    event_m2 = RCAEventContext(
        event_id="EVT_M2",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        telemetry={"vibration_mms": 1.5},
    )

    score_m4, sup_m4, _ = evidence_engine.evaluate_candidate_cause(
        CauseCategory.VIBRATION_DEVIATION, event_m4
    )
    score_m2, sup_m2, _ = evidence_engine.evaluate_candidate_cause(
        CauseCategory.VIBRATION_DEVIATION, event_m2
    )

    assert score_m4 > score_m2


# -----------------------------------------------------------------------------
# 8. Contradictory Evidence Handling
# -----------------------------------------------------------------------------
def test_contradictory_evidence_handling(evidence_engine):
    """Nominal physical readings contradict and penalize misattributed causes."""
    event_wear_contradicted = RCAEventContext(
        event_id="EVT_CONT_01",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        telemetry={"tool_wear_min": 10.0},  # Fresh tool!
        shap_contributions={"tool_wear_min": 2.50},  # Misleading SHAP
    )

    score, sup, cont = evidence_engine.evaluate_candidate_cause(
        CauseCategory.TOOL_WEAR, event_wear_contradicted
    )

    assert len(cont) > 0
    assert any(c.signal_name == "tool_wear_min" and c.is_contradictory for c in cont)
    # Contradiction penalty severely reduces or eliminates score
    assert score < 0.20


# -----------------------------------------------------------------------------
# 9. Confidence Classification Logic
# -----------------------------------------------------------------------------
def test_confidence_classification_logic(rca_service, baseline_m2_event):
    """Engine classifies confidence as HIGH for multi-signal corroborated events."""
    report = rca_service.analyze_event(baseline_m2_event)
    assert report.confidence in [RCAConfidenceLevel.HIGH, RCAConfidenceLevel.MEDIUM]
    assert report.primary_candidate.rank == 1
    assert report.primary_candidate.composite_score >= 0.50


# -----------------------------------------------------------------------------
# 10. Anomaly != Failure Distinction
# -----------------------------------------------------------------------------
def test_anomaly_not_equal_failure(rca_service):
    """High anomaly without high failure probability does NOT declare critical failure cause."""
    event = RCAEventContext(
        event_id="EVT_ANOM_NON_FAIL",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        prediction_probability=0.15,  # Well below tau=0.91!
        prediction_threshold=0.91,
        anomaly_score=0.45,           # High anomaly score
        anomaly_threshold=0.2405,
        telemetry={
            "vibration_mms": 1.4,
            "temperature_c": 35.0,
            "torque_nm": 40.0,
        },
    )
    report = rca_service.analyze_event(event)

    # Primary candidate should be Process Instability or Unknown, NOT severe Mechanical Overload
    assert report.primary_candidate.cause_category in [
        CauseCategory.PROCESS_INSTABILITY.value,
        CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE.value,
    ]
    # Prediction probability is low, so catastrophic failure cause is not confirmed
    assert report.confidence != RCAConfidenceLevel.HIGH


# -----------------------------------------------------------------------------
# 11. Synthetic Machine 2 Scenario Reconstruction
# -----------------------------------------------------------------------------
def test_synthetic_m2_scenario_reconstruction(rca_service):
    """Reconstructs the configured synthetic Machine 2 degradation episode."""
    report = rca_service.run_m2_controlled_scenario()

    assert report.scenario_type == "CONTROLLED SYNTHETIC SCENARIO"
    assert report.machine_id == "M2"
    assert report.primary_candidate.cause_category in [
        CauseCategory.MECHANICAL_LOAD.value,
        CauseCategory.VIBRATION_DEVIATION.value,
    ]
    assert report.confidence == RCAConfidenceLevel.HIGH
    assert report.temporal_precedence_verified is True
    assert len(report.temporal_chain) >= 3


# -----------------------------------------------------------------------------
# 12. No Future Leakage
# -----------------------------------------------------------------------------
def test_temporal_leakage_prevention():
    """History observations occurring after event_timestamp are strictly rejected."""
    history = [
        {"timestamp": "2026-01-20T08:00:00Z", "vibration_mms": 2.0},
        {"timestamp": "2026-01-20T10:00:00Z", "vibration_mms": 3.0},
        {"timestamp": "2026-01-20T14:00:00Z", "vibration_mms": 5.8},  # FUTURE!
    ]
    event_timestamp = "2026-01-20T10:00:00Z"

    causal_history = TemporalPrecedenceEngine.filter_causal_history(
        history=history, event_timestamp=event_timestamp
    )

    assert len(causal_history) == 2
    for r in causal_history:
        assert parse_timestamp(r["timestamp"]) <= parse_timestamp(event_timestamp)


# -----------------------------------------------------------------------------
# 13. No Causal Probability Claims
# -----------------------------------------------------------------------------
def test_no_causal_probability_claims(rca_service, baseline_m2_event):
    """Outputs and human reports strictly contain NO pseudo-probabilistic causation strings."""
    report = rca_service.analyze_event(baseline_m2_event)
    text = rca_service.format_human_readable_report(report)

    prohibited_phrases = [
        "probability of causation",
        "percent probability",
        "% probability",
        "caused by vibration",
        "proves causality",
        "causal proof",
        "proven physical cause",
    ]

    for phrase in prohibited_phrases:
        assert phrase not in text.lower(), f"Prohibited phrase '{phrase}' found in RCA text!"

    assert "SCIENTIFIC CAUSALITY NOTICE" in text
    assert report.causality_disclaimer is not None


# -----------------------------------------------------------------------------
# 14. Insufficient Evidence Handling
# -----------------------------------------------------------------------------
def test_insufficient_evidence_handling(rca_service):
    """Flat nominal telemetry with no anomalies correctly yields INSUFFICIENT_EVIDENCE."""
    flat_event = RCAEventContext(
        event_id="EVT_FLAT_01",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M2",
        telemetry={
            "vibration_mms": 1.4,
            "temperature_c": 35.0,
            "torque_nm": 39.0,
        },
        anomaly_score=0.05,
    )
    report = rca_service.analyze_event(flat_event)

    assert report.confidence == RCAConfidenceLevel.INSUFFICIENT_EVIDENCE
    assert report.primary_candidate.cause_category == CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE.value


# -----------------------------------------------------------------------------
# 15. Deterministic Repeated Execution
# -----------------------------------------------------------------------------
def test_deterministic_repeated_execution(rca_service, baseline_m2_event):
    """Repeated runs of analyze_event produce identical candidate rankings and scores."""
    first_report = rca_service.analyze_event(baseline_m2_event)

    for _ in range(5):
        repeat_report = rca_service.analyze_event(baseline_m2_event)
        assert first_report.primary_candidate.cause_category == repeat_report.primary_candidate.cause_category
        assert first_report.primary_candidate.composite_score == repeat_report.primary_candidate.composite_score
        assert first_report.confidence == repeat_report.confidence
        assert len(first_report.top_contributors) == len(repeat_report.top_contributors)


# -----------------------------------------------------------------------------
# 16. Service-Layer End-to-End RCA
# -----------------------------------------------------------------------------
def test_service_layer_end_to_end(rca_service, baseline_m2_event):
    """Service layer provides end-to-end analysis and valid human-readable report."""
    report = rca_service.analyze_event(baseline_m2_event)
    text = rca_service.format_human_readable_report(report)

    assert isinstance(text, str)
    assert "ROOT CAUSE ANALYSIS (RCA)" in text
    assert "FINDINGS SUMMARY" in text
    assert "SUPPORTING EVIDENCE" in text
    assert "RECOMMENDED INVESTIGATION (DIAGNOSTICS ONLY)" in text
    assert "INTERPRETATION & SCIENTIFIC LIMITATIONS" in text


# -----------------------------------------------------------------------------
# 17. Invalid/Missing Evidence Handling
# -----------------------------------------------------------------------------
def test_invalid_missing_evidence_graceful_fallback(rca_service):
    """Completely empty optional fields execute gracefully without crashing."""
    minimal_event = RCAEventContext(
        event_id="EVT_MINIMAL",
        timestamp="2026-01-20T00:00:00Z",
        machine_id="M1",
    )
    report = rca_service.analyze_event(minimal_event)

    assert report.event_id == "EVT_MINIMAL"
    assert report.confidence == RCAConfidenceLevel.INSUFFICIENT_EVIDENCE
    assert report.primary_candidate.cause_category == CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE.value


# -----------------------------------------------------------------------------
# Negative Control / False Cause Test
# -----------------------------------------------------------------------------
def test_negative_control_shap_alone_not_rca(rca_service):
    """Negative control scenario: SHAP attribution alone does NOT declare a physical root cause."""
    report = rca_service.run_negative_control_scenario()

    # Must NOT have HIGH confidence
    assert report.confidence in [RCAConfidenceLevel.LOW, RCAConfidenceLevel.INSUFFICIENT_EVIDENCE]
    # Primary candidate must NOT be declared as HIGH confidence TOOL_WEAR
    if report.primary_candidate.cause_category == CauseCategory.TOOL_WEAR.value:
        assert report.confidence == RCAConfidenceLevel.LOW
        assert len(report.contradictory_evidence) > 0
    else:
        assert report.primary_candidate.cause_category == CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE.value
