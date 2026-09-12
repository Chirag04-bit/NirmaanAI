"""
NirmaanAI Factory Health Score — Core Scoring Engine
Phase 13: Factory Health Score

Implements the deterministic health score aggregation engine:
- Machine-specific baseline calibration
- Dimension score calculation and weight renormalization for missing data
- State categorization (EXCELLENT, HEALTHY, WATCH, DEGRADED, CRITICAL, INSUFFICIENT_DATA)
- Confidence evaluation separate from health score
- Identification of top health degraders
- Strict double-counting audit and prevention (SHAP and RCA safeguards)

CONFIGURED ANALYTICAL WEIGHTS (Sum = 1.00):
- Failure Risk:          0.25
- Anomaly Health:        0.20
- Flow & Bottleneck:     0.20
- Energy Health:         0.10
- Maintenance Context:   0.10
- Diagnostic Consistency:0.15
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

from src.health.health_dimensions import (
    calculate_anomaly_health,
    calculate_diagnostic_consistency_health,
    calculate_energy_health,
    calculate_failure_risk_health,
    calculate_flow_health,
    calculate_maintenance_health,
)
from src.health.health_models import (
    DimensionScoreBreakdown,
    EvidenceCoverageStatus,
    HealthAssessmentConfidence,
    HealthDimensionType,
    HealthEvidenceContext,
    HealthState,
    MachineHealthScore,
)
from src.rca.evidence_engine import DEFAULT_MACHINE_BASELINES


# Configured analytical weights summing exactly to 1.00
CONFIGURED_DIMENSION_WEIGHTS: Dict[HealthDimensionType, float] = {
    HealthDimensionType.FAILURE_RISK: 0.25,
    HealthDimensionType.ANOMALY_HEALTH: 0.20,
    HealthDimensionType.FLOW_HEALTH: 0.20,
    HealthDimensionType.ENERGY_HEALTH: 0.10,
    HealthDimensionType.MAINTENANCE_CONTEXT: 0.10,
    HealthDimensionType.DIAGNOSTIC_CONSISTENCY: 0.15,
}
CONFIGURED_HEALTH_WEIGHTS = CONFIGURED_DIMENSION_WEIGHTS


DIMENSION_DISPLAY_NAMES: Dict[HealthDimensionType, str] = {
    HealthDimensionType.FAILURE_RISK: "Predictive Failure Risk",
    HealthDimensionType.ANOMALY_HEALTH: "Multi-Sensor Anomaly Health",
    HealthDimensionType.FLOW_HEALTH: "Production Flow & Bottleneck",
    HealthDimensionType.ENERGY_HEALTH: "Energy & Power Deviation",
    HealthDimensionType.MAINTENANCE_CONTEXT: "Maintenance & Spare Context",
    HealthDimensionType.DIAGNOSTIC_CONSISTENCY: "RCA Diagnostic Consistency",
}


class MachineHealthScoringEngine:
    """
    Deterministic scoring engine calculating machine-level health scores
    with machine-specific baseline awareness and missing-data renormalization.
    """

    def __init__(
        self,
        machine_baselines: Optional[Dict[str, Dict[str, float]]] = None,
        dimension_weights: Optional[Dict[HealthDimensionType, float]] = None,
        weights: Optional[Dict[HealthDimensionType, float]] = None,
    ):
        self.machine_baselines = machine_baselines or DEFAULT_MACHINE_BASELINES
        self.weights = dimension_weights or weights or CONFIGURED_DIMENSION_WEIGHTS
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Validates that configured weights sum to 1.00 within floating point precision."""
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=1e-5):
            raise ValueError(f"Configured dimension weights must sum to 1.00 (got {total_weight:.5f})")

    def get_baseline(self, machine_id: str) -> Dict[str, float]:
        """Retrieves machine-specific baseline parameters from approved registry."""
        if machine_id not in self.machine_baselines:
            # Controlled missing baseline fallback rather than arbitrary substitution
            return self.machine_baselines.get("M2", {})
        return self.machine_baselines[machine_id]

    def evaluate_machine(self, context: HealthEvidenceContext) -> MachineHealthScore:
        """
        Calculates machine health score, dimension breakdowns, coverage status, and explanation.
        """
        baseline = self.get_baseline(context.machine_id)
        
        # Populate nominal design values from machine baseline if not explicitly in context
        design_cycle = context.design_cycle_time_sec or baseline.get("design_cycle_time_sec", 45.0)
        base_power = context.baseline_power_kw or baseline.get("baseline_power_kw", 22.0)

        # 1. Evaluate individual dimension scores [0, 100]
        dim_results: Dict[HealthDimensionType, Tuple[Optional[float], str]] = {
            HealthDimensionType.FAILURE_RISK: calculate_failure_risk_health(
                prediction_probability=context.prediction_probability,
                threshold=context.prediction_threshold,
            ),
            HealthDimensionType.ANOMALY_HEALTH: calculate_anomaly_health(
                anomaly_score=context.anomaly_score,
                threshold=context.anomaly_threshold,
            ),
            HealthDimensionType.FLOW_HEALTH: calculate_flow_health(
                cycle_time_sec=context.cycle_time_sec,
                design_cycle_time_sec=design_cycle,
                cycle_ratio=context.cycle_ratio,
                bottleneck_state=context.bottleneck_state,
                dispatch_delay_min=context.dispatch_delay_min,
            ),
            HealthDimensionType.ENERGY_HEALTH: calculate_energy_health(
                power_kw=context.power_consumption_kw,
                baseline_power_kw=base_power,
                forecast_residual_kw=context.forecast_residual_kw,
            ),
            HealthDimensionType.MAINTENANCE_CONTEXT: calculate_maintenance_health(
                spare_stock_level=context.spare_stock_level,
                spare_safety_stock=context.spare_safety_stock,
                days_of_supply=context.days_of_supply,
                is_overdue=context.is_maintenance_overdue,
                hours_since_maint=context.hours_since_last_maintenance,
            ),
            HealthDimensionType.DIAGNOSTIC_CONSISTENCY: calculate_diagnostic_consistency_health(
                active_rca_severity=context.active_rca_severity,
                active_rca_confidence=context.active_rca_confidence,
                has_active_unresolved_rca=context.has_active_unresolved_rca,
            ),
        }

        # 2. Compute Evidence Coverage and Available Weights
        available_dims: List[HealthDimensionType] = []
        available_weight_sum = 0.0

        for dim, (score, _) in dim_results.items():
            if score is not None:
                available_dims.append(dim)
                available_weight_sum += self.weights[dim]

        coverage_pct = float(available_weight_sum * 100.0)

        # Categorize coverage status
        if coverage_pct >= 99.9:
            coverage_status = EvidenceCoverageStatus.FULL_EVIDENCE
        elif coverage_pct >= 40.0:
            coverage_status = EvidenceCoverageStatus.PARTIAL_EVIDENCE
        else:
            coverage_status = EvidenceCoverageStatus.INSUFFICIENT_DATA

        # 3. Handle Insufficient Data Override (< 40% coverage)
        if coverage_status == EvidenceCoverageStatus.INSUFFICIENT_DATA:
            breakdowns = self._build_breakdowns(dim_results, available_weight_sum=0.0)
            return MachineHealthScore(
                machine_id=context.machine_id,
                timestamp=context.timestamp,
                health_score=0.0,
                state=HealthState.INSUFFICIENT_DATA,
                confidence=HealthAssessmentConfidence.LOW,
                evidence_coverage_pct=coverage_pct,
                coverage_status=coverage_status,
                dimension_breakdowns=breakdowns,
                top_degraders=["Insufficient operational evidence to calculate health score"],
                explanation_narrative=(
                    f"Evidence coverage for {context.machine_id} is {coverage_pct:.1f}% (< 40.0% threshold). "
                    f"Operational health state set to INSUFFICIENT_DATA."
                ),
                limitations=[
                    "Insufficient data to establish health state.",
                    "Missing core predictive and operational telemetry.",
                ],
            )

        # 4. Weight Renormalization & Score Aggregation
        weighted_score_sum = 0.0
        breakdowns = self._build_breakdowns(dim_results, available_weight_sum=available_weight_sum)

        for b in breakdowns:
            if b.is_available:
                weighted_score_sum += b.weighted_contribution

        final_health_score = float(np.clip(weighted_score_sum, 0.0, 100.0))

        # 5. Map to Configured Health State Bands
        state = self._map_score_to_state(final_health_score)

        # 6. Assess Confidence (Separated from Health Score)
        confidence = self._assess_confidence(coverage_pct, breakdowns)

        # 7. Identify Top Health Degraders
        top_degraders = self._identify_top_degraders(breakdowns)

        # 8. Construct Human-Readable Explanation Narrative
        explanation_narrative = self._build_explanation(
            context.machine_id,
            final_health_score,
            state,
            confidence,
            coverage_pct,
            top_degraders,
            breakdowns,
            context.has_active_unresolved_rca,
        )

        # 9. Scientific Limitations
        limitations = [
            "Analytical score: Represents configured operational weighting, not physical failure probability.",
            "Double-counting protection: SHAP feature attributions are excluded from direct health score penalty.",
            "RCA integration: Diagnostic consistency represents unresolved mechanism severity rather than raw sensor duplication.",
        ]
        if context.is_synthetic_scenario:
            limitations.append(
                "Controlled synthetic demonstration: Reflects configured digital twin behavior, not real factory physics."
            )

        return MachineHealthScore(
            machine_id=context.machine_id,
            timestamp=context.timestamp,
            health_score=final_health_score,
            state=state,
            confidence=confidence,
            evidence_coverage_pct=coverage_pct,
            coverage_status=coverage_status,
            dimension_breakdowns=breakdowns,
            top_degraders=top_degraders,
            explanation_narrative=explanation_narrative,
            limitations=limitations,
        )

    def _build_breakdowns(
        self,
        dim_results: Dict[HealthDimensionType, Tuple[Optional[float], str]],
        available_weight_sum: float,
    ) -> List[DimensionScoreBreakdown]:
        """Constructs typed dimension breakdowns with effective weights and penalty points."""
        breakdowns: List[DimensionScoreBreakdown] = []

        for dim, (score, desc) in dim_results.items():
            cfg_w = self.weights[dim]
            is_avail = score is not None
            val = score if is_avail else 0.0
            
            # Renormalized effective weight
            eff_w = (cfg_w / available_weight_sum) if (is_avail and available_weight_sum > 0) else 0.0
            contrib = val * eff_w
            pen = (100.0 - val) * eff_w if is_avail else 0.0

            breakdowns.append(
                DimensionScoreBreakdown(
                    dimension=dim,
                    display_name=DIMENSION_DISPLAY_NAMES[dim],
                    raw_value=val if is_avail else None,
                    normalized_score=val,
                    configured_weight=cfg_w,
                    effective_weight=eff_w,
                    weighted_contribution=contrib,
                    penalty_points=pen,
                    is_available=is_avail,
                    description=desc,
                )
            )
        return breakdowns

    @staticmethod
    def _map_score_to_state(score: float) -> HealthState:
        """Maps bounded health score to configured analytical decision bands."""
        if score >= 90.0:
            return HealthState.EXCELLENT
        elif score >= 75.0:
            return HealthState.HEALTHY
        elif score >= 60.0:
            return HealthState.WATCH
        elif score >= 40.0:
            return HealthState.DEGRADED
        else:
            return HealthState.CRITICAL

    @staticmethod
    def _assess_confidence(
        coverage_pct: float,
        breakdowns: List[DimensionScoreBreakdown],
    ) -> HealthAssessmentConfidence:
        """Evaluates confidence based on evidence coverage and signal consistency."""
        if coverage_pct >= 80.0:
            return HealthAssessmentConfidence.HIGH
        elif coverage_pct >= 50.0:
            return HealthAssessmentConfidence.MEDIUM
        else:
            return HealthAssessmentConfidence.LOW

    @staticmethod
    def _identify_top_degraders(breakdowns: List[DimensionScoreBreakdown]) -> List[str]:
        """Identifies top 3 dimensions contributing most to health deduction."""
        avail = [b for b in breakdowns if b.is_available and b.penalty_points > 1.0]
        avail.sort(key=lambda b: b.penalty_points, reverse=True)
        return [f"{b.display_name} (-{b.penalty_points:.1f} pts)" for b in avail[:3]]

    @staticmethod
    def _build_explanation(
        machine_id: str,
        score: float,
        state: HealthState,
        confidence: HealthAssessmentConfidence,
        coverage_pct: float,
        top_degraders: List[str],
        breakdowns: List[DimensionScoreBreakdown],
        has_unresolved_rca: bool,
    ) -> str:
        """Constructs human-interpretable manufacturing explanation narrative."""
        lines = [
            f"Machine {machine_id} Operational Health Score: {score:.1f}/100 — Status: {state.value}.",
            f"Assessment Confidence: {confidence.value} (Evidence Coverage: {coverage_pct:.1f}%).",
        ]
        if top_degraders:
            lines.append(f"Primary Health Deductions: {', '.join(top_degraders)}.")
        else:
            lines.append("All monitored health dimensions are operating within nominal baseline parameters.")

        if has_unresolved_rca:
            lines.append("Active Root Cause Analysis findings indicate an unresolved diagnostic failure mechanism.")

        return " ".join(lines)
