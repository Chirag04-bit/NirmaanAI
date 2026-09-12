"""
NirmaanAI Factory Health Score — Plant-Level Aggregation
Phase 13: Factory Health Score

Aggregates individual machine health scores into plant-wide factory health:
- Configured equal baseline weighting (0.20 per machine for M1-M5)
- Dynamic weight renormalization if a machine is offline or missing
- Critical machine isolation (argmin_m H_m)
- Constraint override alert: Prevents healthy machines from masking a critical asset failure

RESEARCH INTEGRITY:
- Machine weights are configured baseline assumptions, not learned causal coefficients.
- High average scores across healthy machines cannot conceal a critical failing station.
"""

from typing import Dict, List, Optional
import numpy as np

from src.health.health_models import (
    EvidenceCoverageStatus,
    FactoryHealthScore,
    HealthAssessmentConfidence,
    HealthState,
    MachineHealthScore,
)

# Configured baseline equal weighting across the 5 sequential line machines
DEFAULT_MACHINE_WEIGHTS: Dict[str, float] = {
    "M1": 0.20,
    "M2": 0.20,
    "M3": 0.20,
    "M4": 0.20,
    "M5": 0.20,
}


from typing import Dict, List, Optional, Union


class FactoryHealthAggregator:
    """
    Aggregates machine-level health scores into plant-wide Factory Health Score.
    """

    def __init__(self, machine_weights: Optional[Dict[str, float]] = None):
        self.machine_weights = machine_weights or DEFAULT_MACHINE_WEIGHTS

    def aggregate(
        self,
        machine_scores: Union[Dict[str, MachineHealthScore], List[MachineHealthScore]],
        timestamp: str,
    ) -> FactoryHealthScore:
        """
        Calculates plant-wide factory health, identifies critical machine,
        and enforces critical constraint alert overrides.
        """
        if isinstance(machine_scores, list):
            machine_scores = {s.machine_id: s for s in machine_scores}

        if not machine_scores:
            return FactoryHealthScore(
                timestamp=timestamp,
                factory_health_score=0.0,
                state=HealthState.INSUFFICIENT_DATA,
                confidence=HealthAssessmentConfidence.LOW,
                evidence_coverage_pct=0.0,
                coverage_status=EvidenceCoverageStatus.INSUFFICIENT_DATA,
                machine_scores={},
                critical_machine_id="NONE",
                critical_machine_score=0.0,
                critical_machine_alert=False,
                limitations=["No machine health assessments available for factory aggregation."],
            )

        # Filter active machines with valid health scores
        active_machines = {
            m_id: score for m_id, score in machine_scores.items()
            if score.state != HealthState.INSUFFICIENT_DATA
        }

        # Calculate coverage of configured plant assets
        total_cfg_weight = sum(self.machine_weights.get(m, 0.20) for m in machine_scores.keys())
        active_cfg_weight = sum(self.machine_weights.get(m, 0.20) for m in active_machines.keys())
        coverage_pct = float(np.clip(active_cfg_weight * 100.0, 0.0, 100.0))

        if len(active_machines) < 2 or coverage_pct < 40.0:
            return FactoryHealthScore(
                timestamp=timestamp,
                factory_health_score=0.0,
                state=HealthState.INSUFFICIENT_DATA,
                confidence=HealthAssessmentConfidence.LOW,
                evidence_coverage_pct=coverage_pct,
                coverage_status=EvidenceCoverageStatus.INSUFFICIENT_DATA,
                machine_scores=machine_scores,
                critical_machine_id="NONE",
                critical_machine_score=0.0,
                critical_machine_alert=False,
                limitations=["Fewer than 2 operational machines available; plant status is INSUFFICIENT_DATA."],
            )

        # Renormalize weights across active machines
        weighted_sum = 0.0
        for m_id, m_score in active_machines.items():
            base_w = self.machine_weights.get(m_id, 0.20)
            eff_w = base_w / active_cfg_weight
            weighted_sum += m_score.health_score * eff_w

        raw_factory_score = float(np.clip(weighted_sum, 0.0, 100.0))

        # Identify critical machine (lowest operational health score)
        critical_m_id = min(active_machines.keys(), key=lambda m: active_machines[m].health_score)
        critical_score = active_machines[critical_m_id].health_score

        # Critical Machine Logic: Detect if a machine is in CRITICAL state (< 40.0)
        critical_alert = critical_score < 40.0
        alert_msg = None

        # State determination
        if raw_factory_score >= 90.0:
            state = HealthState.EXCELLENT
        elif raw_factory_score >= 75.0:
            state = HealthState.HEALTHY
        elif raw_factory_score >= 60.0:
            state = HealthState.WATCH
        elif raw_factory_score >= 40.0:
            state = HealthState.DEGRADED
        else:
            state = HealthState.CRITICAL

        # CONSTRAINT OVERRIDE: If a critical machine is failing, cap plant state at WATCH / DEGRADED
        # preventing a healthy average from masking an active bottleneck or breakdown.
        if critical_alert:
            alert_msg = (
                f"CRITICAL MACHINE ALERT: Factory health is constrained by critical asset {critical_m_id} "
                f"(Health: {critical_score:.1f}/100, CRITICAL). Plant operations are constrained by an active "
                f"breakdown despite healthy telemetry across decoupled stations."
            )
            if state in [HealthState.EXCELLENT, HealthState.HEALTHY]:
                state = HealthState.WATCH

        # Confidence: aggregate of individual machine confidences
        high_conf_count = sum(1 for m in active_machines.values() if m.confidence == HealthAssessmentConfidence.HIGH)
        if high_conf_count >= len(active_machines) * 0.75 and coverage_pct >= 80.0:
            confidence = HealthAssessmentConfidence.HIGH
        elif coverage_pct >= 50.0:
            confidence = HealthAssessmentConfidence.MEDIUM
        else:
            confidence = HealthAssessmentConfidence.LOW

        coverage_status = (
            EvidenceCoverageStatus.FULL_EVIDENCE if coverage_pct >= 99.9
            else EvidenceCoverageStatus.PARTIAL_EVIDENCE
        )

        limitations = [
            "Plant aggregation assumes configured equal machine baseline weighting (0.20 per station).",
            "Critical machine constraint override prevents decoupled healthy averages from concealing active breakdown.",
            "Health score is an analytical decision-support metric, not a physical failure probability.",
        ]

        return FactoryHealthScore(
            timestamp=timestamp,
            factory_health_score=raw_factory_score,
            state=state,
            confidence=confidence,
            evidence_coverage_pct=coverage_pct,
            coverage_status=coverage_status,
            machine_scores=machine_scores,
            critical_machine_id=critical_m_id,
            critical_machine_score=critical_score,
            critical_machine_alert=critical_alert,
            critical_alert_message=alert_msg,
            machine_weights=dict(self.machine_weights),
            limitations=limitations,
        )

    aggregate_factory_health = aggregate


FactoryHealthAggregationEngine = FactoryHealthAggregator

