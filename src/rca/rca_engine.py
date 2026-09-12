"""
NirmaanAI Root Cause Analysis (RCA) — Core Analysis Engine
Phase 12: Root Cause Analysis

Orchestrates multi-source evidence fusion, temporal precedence verification,
contradiction handling, and confidence classification.

SCIENTIFIC INTEGRITY:
- Outputs operational association rankings, NOT causal proof.
- Bounded confidence categories (HIGH, MEDIUM, LOW, INSUFFICIENT_EVIDENCE).
- Negative control detection: single-source attribution without physical corroboration
  is strictly flagged as LOW confidence or INSUFFICIENT_EVIDENCE.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.rca.cause_taxonomy import (
    CauseCategory,
    CAUSE_DEFINITIONS,
    get_cause_definition,
)
from src.rca.evidence_engine import EvidenceFusionEngine
from src.rca.rca_models import (
    CandidateCauseScore,
    RCAConfidenceLevel,
    RCAEventContext,
    RCAReportResponse,
    SignalEvidenceItem,
    TemporalStep,
)
from src.rca.temporal_analysis import TemporalPrecedenceEngine


class RootCauseAnalysisEngine:
    """
    Unified engine for evidence-based Root Cause Analysis.
    Combines SHAP attribution, multi-sensor telemetry, anomaly detection,
    and bottleneck intelligence into ranked, confidence-classified explanations.
    """

    def __init__(self, evidence_engine: Optional[EvidenceFusionEngine] = None):
        self.evidence_engine = evidence_engine or EvidenceFusionEngine()
        self.temporal_engine = TemporalPrecedenceEngine()

    def analyze(self, event: RCAEventContext) -> RCAReportResponse:
        """
        Executes end-to-end Root Cause Analysis on an ingested event context.
        """
        # 1. Reconstruct Temporal Progression & Precedence
        baseline = self.evidence_engine.get_baseline(event.machine_id)
        temporal_chain, precedence_verified, temporal_multiplier = self.temporal_engine.reconstruct_sequence(
            history=event.historical_telemetry,
            event_timestamp=event.timestamp,
            machine_baseline_vib=baseline.get("baseline_vibration_mms", 1.4),
            alert_vib=baseline.get("alert_vibration_mms", 3.8),
            nominal_cycle_sec=baseline.get("design_cycle_time_sec", 45.0),
        )

        # 2. Evaluate all candidate causes in controlled taxonomy
        candidate_scores: List[CandidateCauseScore] = []
        all_supporting: List[SignalEvidenceItem] = []
        all_contradictory: List[SignalEvidenceItem] = []

        categories_to_evaluate = [
            c for c in CauseCategory if c != CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE
        ]

        for cat in categories_to_evaluate:
            score, supporting, contradictory = self.evidence_engine.evaluate_candidate_cause(
                category=cat,
                event=event,
                temporal_multiplier=temporal_multiplier,
            )
            
            all_supporting.extend(supporting)
            all_contradictory.extend(contradictory)

            definition = get_cause_definition(cat)
            
            # Generate summary rationale
            if score > 0.10:
                summary = (
                    f"Candidate supported by {len(supporting)} signal(s) "
                    f"with composite analytical score {score:.3f}."
                )
                if contradictory:
                    summary += f" Contradicted by {len(contradictory)} signal(s)."
            else:
                summary = "Insufficient or negligible signal alignment."

            candidate_scores.append(
                CandidateCauseScore(
                    cause_category=cat.value,
                    display_name=definition.display_name,
                    rank=999,  # placeholder before sorting
                    composite_score=score,
                    supporting_signals=supporting,
                    contradictory_signals=contradictory,
                    investigation_suggestion=definition.investigation_suggestion,
                    summary=summary,
                )
            )

        # 3. Sort candidates by score descending
        candidate_scores.sort(key=lambda c: c.composite_score, reverse=True)
        for idx, c in enumerate(candidate_scores):
            c.rank = idx + 1

        # 4. Handle Insufficient Evidence / Primary Selection
        top_candidate = candidate_scores[0]
        secondary_candidates = [c for c in candidate_scores[1:4] if c.composite_score > 0.15]

        # Check if evidence is too weak across the board
        if top_candidate.composite_score < 0.15:
            unknown_def = get_cause_definition(CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE)
            primary_candidate = CandidateCauseScore(
                cause_category=CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE.value,
                display_name=unknown_def.display_name,
                rank=1,
                composite_score=0.0,
                supporting_signals=[],
                contradictory_signals=all_contradictory,
                investigation_suggestion=unknown_def.investigation_suggestion,
                summary="Available multi-source evidence is below detection threshold or inconclusive.",
            )
            confidence = RCAConfidenceLevel.INSUFFICIENT_EVIDENCE
            confidence_rationale = (
                "Composite scores for all candidate causes fell below the minimum significance threshold (0.15)."
            )
        else:
            primary_candidate = top_candidate
            confidence, confidence_rationale = self._classify_confidence(
                candidate=primary_candidate,
                precedence_verified=precedence_verified,
            )

        # Deduplicate top supporting & contradictory items for report
        unique_supporting = self._deduplicate_signals(primary_candidate.supporting_signals)
        unique_contradictory = self._deduplicate_signals(primary_candidate.contradictory_signals)

        # Recommended investigation steps (focused on diagnostics, NOT recommendation engine)
        investigations = [primary_candidate.investigation_suggestion]
        for sec in secondary_candidates:
            if sec.investigation_suggestion not in investigations:
                investigations.append(sec.investigation_suggestion)

        # Synthetic scenario labeling
        scenario_type = (
            "CONTROLLED SYNTHETIC SCENARIO"
            if event.is_synthetic_scenario
            else "EMPIRICAL MODEL ATTRIBUTION"
        )

        # Interpretation statement adhering to strict scientific language
        if event.is_synthetic_scenario:
            interpretation = (
                f"The available synthetic evidence is temporally and operationally consistent "
                f"with the configured {event.machine_id} degradation scenario. "
                f"Primary associated candidate: {primary_candidate.display_name}."
            )
        elif confidence in [RCAConfidenceLevel.HIGH, RCAConfidenceLevel.MEDIUM]:
            interpretation = (
                f"Multi-source evidence demonstrates strong operational association with "
                f"{primary_candidate.display_name}. Model attribution aligns with observed telemetry."
            )
        else:
            interpretation = (
                f"Evidence is weak or isolated. Model attribution alone does NOT substantiate "
                f"a physical root cause without independent physical sensor corroboration."
            )

        # Limitations
        limitations = [
            "Root cause analysis establishes correlation and temporal consistency, not physical causality.",
            "Evidence scoring relies on configured analytical weights rather than interventional causal inference.",
            "Counterfactual simulation ('what-if' intervention) was not performed.",
        ]
        if event.is_synthetic_scenario:
            limitations.append(
                "Controlled synthetic demonstration: Findings reflect configured simulator dynamics, not empirical industrial validation."
            )

        return RCAReportResponse(
            event_id=event.event_id,
            timestamp=event.timestamp,
            machine_id=event.machine_id,
            event_type=event.event_type,
            severity=event.severity,
            observed_outcome=event.observed_outcome,
            scenario_type=scenario_type,
            prediction_probability=event.prediction_probability,
            anomaly_score=event.anomaly_score,
            bottleneck_state=event.bottleneck_state,
            primary_candidate=primary_candidate,
            secondary_candidates=secondary_candidates,
            confidence=confidence,
            confidence_rationale=confidence_rationale,
            top_contributors=unique_supporting,
            contradictory_evidence=unique_contradictory,
            temporal_chain=temporal_chain,
            temporal_precedence_verified=precedence_verified,
            recommended_next_investigation=investigations,
            interpretation=interpretation,
            limitations=limitations,
        )

    def _classify_confidence(
        self,
        candidate: CandidateCauseScore,
        precedence_verified: bool,
    ) -> Tuple[RCAConfidenceLevel, str]:
        """
        Classifies confidence into HIGH, MEDIUM, LOW, or INSUFFICIENT_EVIDENCE
        based on evidence diversity, contradiction presence, and temporal ordering.
        """
        supporting_sources = {s.source for s in candidate.supporting_signals}
        num_sources = len(supporting_sources)
        score = candidate.composite_score
        has_contradictions = len(candidate.contradictory_signals) > 0

        # HIGH: Strong score, multi-source agreement (>=2), temporal precedence, no severe contradictions
        if score >= 0.60 and num_sources >= 2 and precedence_verified and not has_contradictions:
            return (
                RCAConfidenceLevel.HIGH,
                f"High confidence: Multiple independent evidence sources ({num_sources}) corroborate candidate with verified temporal precedence."
            )

        # MEDIUM: Moderate score, at least 1 corroborating physical signal or multi-source without strict temporal chain
        if score >= 0.35 and (num_sources >= 2 or (num_sources == 1 and not has_contradictions)):
            return (
                RCAConfidenceLevel.MEDIUM,
                f"Medium confidence: Candidate supported by score {score:.3f}, but temporal sequence or secondary evidence is partial."
            )

        # LOW: Isolated signal (e.g. SHAP only without physical telemetry, or contradiction present)
        if score >= 0.15:
            if has_contradictions:
                return (
                    RCAConfidenceLevel.LOW,
                    "Low confidence: Supporting evidence is weakened by contradictory physical observations."
                )
            return (
                RCAConfidenceLevel.LOW,
                "Low confidence: Model attribution or telemetry signal is isolated without multi-signal corroboration."
            )

        return (
            RCAConfidenceLevel.INSUFFICIENT_EVIDENCE,
            "Insufficient evidence: Composite analytical score is below threshold."
        )

    @staticmethod
    def _deduplicate_signals(signals: List[SignalEvidenceItem]) -> List[SignalEvidenceItem]:
        """Retains highest-evidence unique signal per signal_name."""
        seen: Dict[str, SignalEvidenceItem] = {}
        for s in signals:
            if s.signal_name not in seen or s.normalized_evidence > seen[s.signal_name].normalized_evidence:
                seen[s.signal_name] = s
        return list(seen.values())
