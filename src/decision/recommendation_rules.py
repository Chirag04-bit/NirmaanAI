"""
NirmaanAI Operational Recommendation Rules
Phase 15: Recommendation Engine

Defines deterministic, auditable decision rules mapping upstream operational evidence
from Phases 6–14 into prioritized operational recommendations:
- R-M01: Spindle Bearing Critical Failure Preemption (P(fail) >= 0.91, Anomaly >= 0.2405, RCA = MECHANICAL_LOAD)
- R-M02: Spindle Degradation Warning (0.75 <= P(fail) < 0.91, Vib dev > 0.30 mm/s, RCA = MECHANICAL_LOAD)
- R-M03: Predictive Tooling Replacement (tool_wear_min >= 200, scrap > 5%, SHAP top attribution)
- R-P01: Bottleneck Load Rebalancing & Rescheduling (is_bottleneck = True, cycle_ratio >= 1.20, delayed units > 0)
- R-I01: Proactive Spare Replenishment Before Consumption (projected post-action stock < safety stock, lead time = 7d)
- R-E01: Peak Tariff Load Shifting (peak hour 18:00-22:00, non-bottleneck, non-urgent)
- R-O01: Nominal Monitoring Negative Control (Health >= 75.0, Anomaly < 0.2405, P(fail) < 0.75, no bottleneck)

SCIENTIFIC & OPERATIONAL INTEGRITY:
- Locked upstream decision thresholds: P6 = 0.91, P7 = 0.2405, P8 cycle_ratio = 1.20, P13 bands.
- P6 warning boundary 0.75 is explicitly tagged CONFIGURED_ASSUMPTION.
- P10 inventory explicitly distinguishes current stock (2.0) from projected stock (1.0).
- NO pseudo-financial formulas (Rupees != f(Health), Rupees != f(SHAP), Rupees != f(RCA)).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

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
from src.health.health_models import HealthState


# Locked Upstream Constants
P6_LOCKED_FAILURE_THRESHOLD = 0.91
P6_CONFIGURED_WARNING_THRESHOLD = 0.75  # Phase 15 CONFIGURED_ASSUMPTION
P7_LOCKED_ANOMALY_THRESHOLD = 0.2405
P8_LOCKED_CYCLE_RATIO_TARGET = 1.20
P14_CONFIGURED_MATERIALITY_THRESHOLD_INR = 25000.0  # Phase 15 CONFIGURED_ASSUMPTION


def calculate_evidence_strength(evidence_items: List[EvidenceItem]) -> EvidenceStrength:
    """
    Computes categorical evidence strength across the 5 genuine physical/operational domains.
    Financial exposure is strictly excluded from physical corroboration.
    STRONG: >= 3 distinct physical domains
    MODERATE: 2 distinct physical domains
    WEAK: 1 distinct physical domain
    INSUFFICIENT: 0 physical domains
    """
    physical_domains = {item.domain for item in evidence_items}
    count = len(physical_domains)

    if count >= 3:
        return EvidenceStrength.STRONG
    elif count == 2:
        return EvidenceStrength.MODERATE
    elif count == 1:
        return EvidenceStrength.WEAK
    else:
        return EvidenceStrength.INSUFFICIENT


def evaluate_rule_r_m01(
    machine_id: str,
    as_of: datetime,
    failure_prob: float,
    anomaly_score: float,
    rca_candidate: Optional[str],
    financial_context: Optional[FinancialEvidenceContext] = None,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> Optional[OperationalRecommendation]:
    """
    Rule R-M01: Spindle Bearing Critical Failure Preemption.
    IF: P(fail) >= 0.91 AND anomaly >= 0.2405 AND RCA = MECHANICAL_LOAD
    THEN: INSPECT_SPINDLE_BEARING (Priority: CRITICAL, Urgency: IMMEDIATE)
    """
    if failure_prob >= P6_LOCKED_FAILURE_THRESHOLD and anomaly_score >= P7_LOCKED_ANOMALY_THRESHOLD and rca_candidate == "MECHANICAL_LOAD":
        ev1 = EvidenceItem(
            evidence_id=f"EVID_P06_FAIL_{machine_id}",
            source_phase="Phase 6",
            source_module="AI4I_XGBoostClassifier",
            domain=EvidenceDomain.PREDICTIVE_FAILURE,
            metric="failure_probability",
            value=round(failure_prob, 4),
            threshold_applied=P6_LOCKED_FAILURE_THRESHOLD,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Failure probability {failure_prob:.4f} exceeds locked operational threshold {P6_LOCKED_FAILURE_THRESHOLD}",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )
        ev2 = EvidenceItem(
            evidence_id=f"EVID_P07_ANOM_{machine_id}",
            source_phase="Phase 7",
            source_module="PCAReconstructionDetector",
            domain=EvidenceDomain.TELEMETRY_ANOMALY,
            metric="normalized_reconstruction_error",
            value=round(anomaly_score, 4),
            threshold_applied=P7_LOCKED_ANOMALY_THRESHOLD,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Normalized anomaly score {anomaly_score:.4f} exceeds calibrated threshold {P7_LOCKED_ANOMALY_THRESHOLD}",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )
        ev3 = EvidenceItem(
            evidence_id=f"EVID_P12_RCA_{machine_id}",
            source_phase="Phase 12",
            source_module="RootCauseAnalysisEngine",
            domain=EvidenceDomain.DIAGNOSTIC_RCA,
            metric="primary_candidate_cause",
            value="MECHANICAL_LOAD",
            timestamp=as_of,
            machine_id=machine_id,
            interpretation="Diagnostic evidence is operationally consistent with mechanical overload and torque surge on spindle assembly",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )

        evidence = [ev1, ev2, ev3]
        strength = calculate_evidence_strength(evidence)

        return OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_MAINT_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.MAINTENANCE,
            action=RecommendationAction.INSPECT_SPINDLE_BEARING,
            priority=RecommendationPriority.CRITICAL,
            urgency=ActionUrgency.IMMEDIATE,
            evidence_strength=strength,
            reason=(
                f"Machine {machine_id} exhibits critical mechanical degradation: failure probability ({failure_prob:.4f}) "
                f"breaches locked threshold ({P6_LOCKED_FAILURE_THRESHOLD}), anomaly score ({anomaly_score:.4f}) breaches "
                f"reconstruction threshold ({P7_LOCKED_ANOMALY_THRESHOLD}), and RCA identifies MECHANICAL_LOAD."
            ),
            evidence=evidence,
            source_phases=["Phase 6", "Phase 7", "Phase 12"],
            operational_impact="Imminent uncommanded spindle seizure causing complete unplanned line shutdown and tool breakage.",
            financial_context=financial_context,
            expected_benefit="Preempts catastrophic spindle seizure and avoids extended unplanned repair downtime.",
            requires_operator_verification=True,
            rule_id="R-M01",
            epistemic_classification=scenario_epistemic,
        )
    return None


def evaluate_rule_r_m02(
    machine_id: str,
    as_of: datetime,
    failure_prob: float,
    vibration_deviation_mms: float,
    rca_candidate: Optional[str],
    financial_context: Optional[FinancialEvidenceContext] = None,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> Optional[List[OperationalRecommendation]]:
    """
    Rule R-M02: Spindle Degradation Warning.
    IF: 0.75 <= P(fail) < 0.91 AND vibration deviation > 0.30 mm/s AND RCA = MECHANICAL_LOAD
    THEN: INSPECT_LUBRICATION and SCHEDULE_PREVENTIVE_MAINTENANCE (Priority: HIGH, Urgency: SAME_DAY)
    """
    if P6_CONFIGURED_WARNING_THRESHOLD <= failure_prob < P6_LOCKED_FAILURE_THRESHOLD and vibration_deviation_mms > 0.30 and rca_candidate == "MECHANICAL_LOAD":
        ev1 = EvidenceItem(
            evidence_id=f"EVID_P06_WARN_{machine_id}",
            source_phase="Phase 6",
            source_module="AI4I_XGBoostClassifier",
            domain=EvidenceDomain.PREDICTIVE_FAILURE,
            metric="failure_probability",
            value=round(failure_prob, 4),
            threshold_applied=P6_CONFIGURED_WARNING_THRESHOLD,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Failure probability {failure_prob:.4f} is in configured warning band [{P6_CONFIGURED_WARNING_THRESHOLD}, {P6_LOCKED_FAILURE_THRESHOLD})",
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
        )
        ev2 = EvidenceItem(
            evidence_id=f"EVID_TELEM_VIB_{machine_id}",
            source_phase="Phase 7",
            source_module="TelemetryDeviationMonitor",
            domain=EvidenceDomain.TELEMETRY_ANOMALY,
            metric="vibration_deviation_mms",
            value=round(vibration_deviation_mms, 2),
            unit="mms",
            threshold_applied=0.30,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Vibration deviation of {vibration_deviation_mms:.2f} mm/s exceeds operational tolerance of 0.30 mm/s",
            epistemic_classification=EpistemicClassification.OBSERVED,
        )
        ev3 = EvidenceItem(
            evidence_id=f"EVID_P12_RCA_{machine_id}",
            source_phase="Phase 12",
            source_module="RootCauseAnalysisEngine",
            domain=EvidenceDomain.DIAGNOSTIC_RCA,
            metric="primary_candidate_cause",
            value="MECHANICAL_LOAD",
            timestamp=as_of,
            machine_id=machine_id,
            interpretation="Diagnostic evidence is operationally consistent with early mechanical bearing overload",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )

        evidence = [ev1, ev2, ev3]
        strength = calculate_evidence_strength(evidence)

        rec1 = OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_MAINT_002A",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.MAINTENANCE,
            action=RecommendationAction.INSPECT_LUBRICATION,
            priority=RecommendationPriority.HIGH,
            urgency=ActionUrgency.SAME_DAY,
            evidence_strength=strength,
            reason=f"Machine {machine_id} exhibits elevated vibration (+{vibration_deviation_mms:.2f} mm/s) and failure risk in warning band ({failure_prob:.4f}).",
            evidence=evidence,
            source_phases=["Phase 6", "Phase 7", "Phase 12"],
            operational_impact="Accelerated mechanical wear leading to thermal breakdown and spindle seizure.",
            financial_context=financial_context,
            expected_benefit="Restores lubrication film and slows bearing mechanical fatigue.",
            requires_operator_verification=True,
            rule_id="R-M02",
            epistemic_classification=scenario_epistemic,
        )
        rec2 = OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_MAINT_002B",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.MAINTENANCE,
            action=RecommendationAction.SCHEDULE_PREVENTIVE_MAINTENANCE,
            priority=RecommendationPriority.HIGH,
            urgency=ActionUrgency.SAME_DAY,
            evidence_strength=strength,
            reason=f"Schedule proactive bearing maintenance before machine enters critical failure threshold.",
            evidence=evidence,
            source_phases=["Phase 6", "Phase 7", "Phase 12"],
            operational_impact="Unaddressed degradation will progress to unplanned stoppage.",
            financial_context=financial_context,
            expected_benefit="Transitions corrective downtime into planned maintenance window.",
            requires_operator_verification=True,
            rule_id="R-M02",
            epistemic_classification=scenario_epistemic,
        )
        return [rec1, rec2]
    return None


def evaluate_rule_r_m03(
    machine_id: str,
    as_of: datetime,
    tool_wear_min: float,
    scrap_rate_pct: float,
    shap_top_feature: str,
    financial_context: Optional[FinancialEvidenceContext] = None,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> Optional[OperationalRecommendation]:
    """
    Rule R-M03: Predictive Tooling Replacement.
    IF: tool_wear_min >= 200.0 AND scrap rate > 5.0% AND SHAP identifies tool_wear_min as top feature
    THEN: REPLACE_TOOLING (Priority: HIGH, Urgency: NEXT_SHIFT)
    """
    if tool_wear_min >= 200.0 and scrap_rate_pct > 5.0 and shap_top_feature == "tool_wear_min":
        ev1 = EvidenceItem(
            evidence_id=f"EVID_TELEM_TOOL_{machine_id}",
            source_phase="Phase 4",
            source_module="TelemetryProcessor",
            domain=EvidenceDomain.TELEMETRY_ANOMALY,
            metric="tool_wear_min",
            value=round(tool_wear_min, 1),
            unit="min",
            threshold_applied=200.0,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Accumulated tool cutting time of {tool_wear_min:.1f} min exceeds recommended tool life threshold (200 min)",
            epistemic_classification=EpistemicClassification.OBSERVED,
        )
        ev2 = EvidenceItem(
            evidence_id=f"EVID_FLOW_SCRAP_{machine_id}",
            source_phase="Phase 8",
            source_module="ProductionJobLogger",
            domain=EvidenceDomain.PRODUCTION_FLOW,
            metric="scrap_rate_pct",
            value=round(scrap_rate_pct, 2),
            unit="pct",
            threshold_applied=5.0,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Job scrap rate ({scrap_rate_pct:.2f}%) exceeds acceptable quality tolerance (5.0%)",
            epistemic_classification=EpistemicClassification.OBSERVED,
        )
        ev3 = EvidenceItem(
            evidence_id=f"EVID_P11_SHAP_{machine_id}",
            source_phase="Phase 11",
            source_module="SHAPExplainabilityEngine",
            domain=EvidenceDomain.PREDICTIVE_FAILURE,
            metric="top_feature_attribution",
            value="tool_wear_min",
            timestamp=as_of,
            machine_id=machine_id,
            interpretation="Model explanation: tool_wear_min is the primary driver of failure classifier prediction",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )

        evidence = [ev1, ev2, ev3]
        strength = calculate_evidence_strength(evidence)

        return OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_MAINT_TOOL_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.MAINTENANCE,
            action=RecommendationAction.REPLACE_TOOLING,
            priority=RecommendationPriority.HIGH,
            urgency=ActionUrgency.NEXT_SHIFT,
            evidence_strength=strength,
            reason=(
                f"Machine {machine_id} tool wear ({tool_wear_min:.1f} min) exceeds life limit, causing elevated scrap "
                f"({scrap_rate_pct:.2f}%). SHAP model explanation confirms tool wear as primary risk driver."
            ),
            evidence=evidence,
            source_phases=["Phase 4", "Phase 8", "Phase 11"],
            operational_impact="Continued production with worn tooling leads to dimensional non-conformance and surface finish reject.",
            financial_context=financial_context,
            expected_benefit="Restores part machining tolerance and eliminates scrap material losses.",
            requires_operator_verification=True,
            rule_id="R-M03",
            epistemic_classification=scenario_epistemic,
        )
    return None


def evaluate_rule_r_p01(
    machine_id: str,
    as_of: datetime,
    is_bottleneck: bool,
    cycle_ratio: float,
    delayed_units: float,
    financial_context: Optional[FinancialEvidenceContext] = None,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> List[OperationalRecommendation]:
    """
    Rule R-P01: Bottleneck Load Rebalancing & Rescheduling.
    IF: is_bottleneck = True AND cycle_ratio >= 1.20 AND delayed_units > 0
    THEN: REDUCE_MACHINE_FEED_RATE and RESCHEDULE_PENDING_JOBS (Priority: HIGH, Urgency: SAME_DAY)
    """
    if is_bottleneck and cycle_ratio >= P8_LOCKED_CYCLE_RATIO_TARGET and delayed_units > 0:
        ev1 = EvidenceItem(
            evidence_id=f"EVID_P08_BOTTLENECK_{machine_id}",
            source_phase="Phase 8",
            source_module="BottleneckPredictor",
            domain=EvidenceDomain.PRODUCTION_FLOW,
            metric="is_bottleneck",
            value=True,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Machine {machine_id} is classified as an active production flow constraint",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )
        ev2 = EvidenceItem(
            evidence_id=f"EVID_P08_CYCLE_{machine_id}",
            source_phase="Phase 8",
            source_module="FlowIntelligenceService",
            domain=EvidenceDomain.PRODUCTION_FLOW,
            metric="cycle_ratio",
            value=round(cycle_ratio, 2),
            threshold_applied=P8_LOCKED_CYCLE_RATIO_TARGET,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Actual cycle time expanded to {cycle_ratio:.2f}x of nominal design cycle time",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )
        ev3 = EvidenceItem(
            evidence_id=f"EVID_P08_DELAY_{machine_id}",
            source_phase="Phase 8",
            source_module="JobScheduler",
            domain=EvidenceDomain.PRODUCTION_FLOW,
            metric="delayed_throughput_units",
            value=float(delayed_units),
            unit="units",
            threshold_applied=0.0,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Delayed throughput of {delayed_units:.0f} units accumulated behind bottleneck",
            epistemic_classification=EpistemicClassification.OBSERVED,
        )

        evidence = [ev1, ev2, ev3]
        strength = calculate_evidence_strength(evidence)

        rec1 = OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_FLOW_FEED_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.PRODUCTION_FLOW,
            action=RecommendationAction.REDUCE_MACHINE_FEED_RATE,
            priority=RecommendationPriority.HIGH,
            urgency=ActionUrgency.SAME_DAY,
            evidence_strength=strength,
            reason=(
                f"Machine {machine_id} is an active bottleneck with cycle ratio {cycle_ratio:.2f} (exceeding target {P8_LOCKED_CYCLE_RATIO_TARGET}) "
                f"and {delayed_units:.0f} delayed units. Reducing feed rate prevents thermal torque buildup and mechanical seizure."
            ),
            evidence=evidence,
            source_phases=["Phase 8"],
            operational_impact="Severe line starvation downstream and order delivery slippage.",
            financial_context=financial_context,
            expected_benefit="Stabilizes machine mechanical stress while relieving downstream starvation.",
            requires_operator_verification=True,
            rule_id="R-P01",
            epistemic_classification=scenario_epistemic,
        )
        rec2 = OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_FLOW_RESCHED_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.PRODUCTION_FLOW,
            action=RecommendationAction.RESCHEDULE_PENDING_JOBS,
            priority=RecommendationPriority.HIGH,
            urgency=ActionUrgency.SAME_DAY,
            evidence_strength=strength,
            reason=(
                f"Reschedule pending jobs queued on bottleneck {machine_id} to rebalance factory cycle time and avoid margin loss."
            ),
            evidence=evidence,
            source_phases=["Phase 8"],
            operational_impact="WIP queue buildup and delivery backlog.",
            financial_context=financial_context,
            expected_benefit="Reduces work-in-progress congestion and clears order backlog.",
            requires_operator_verification=True,
            rule_id="R-P01",
            epistemic_classification=scenario_epistemic,
        )
        return [rec1, rec2]
    return []


def evaluate_rule_r_i01(
    machine_id: str,
    as_of: datetime,
    has_spindle_maintenance_action: bool,
    sku_id: str,
    observed_current_stock: float,
    safety_stock: float,
    reorder_point: float,
    lead_time_days: float,
    hypothetical_consumption: float = 1.0,
    financial_context: Optional[FinancialEvidenceContext] = None,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> Optional[OperationalRecommendation]:
    """
    Rule R-I01: Proactive Spare Replenishment Before Maintenance Consumption.
    IF: Maintenance action requires one spare (consumption = 1.0)
        AND observed_current_stock = 2.0 (NOT below safety stock)
        AND projected_post_action_stock (1.0) < safety_stock (1.134)
        AND lead_time = 7.0 days
    THEN: EXPEDITE_CRITICAL_SPARE (Priority: HIGH, Urgency: SAME_DAY)
    CRITICAL DISTINCTION:
    - Never describes M2 as currently stocked out or currently below safety stock.
    - Explicitly labels recommendation as a PROACTIVE PROJECTED-STOCK consequence.
    """
    projected_post_action_stock = observed_current_stock - hypothetical_consumption
    is_projected_below_safety = projected_post_action_stock < safety_stock
    is_current_below_safety = observed_current_stock < safety_stock

    if has_spindle_maintenance_action and is_projected_below_safety and lead_time_days > 0:
        inv_ctx = InventoryEvidenceContext(
            sku_id=sku_id,
            observed_current_stock=observed_current_stock,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            supplier_lead_time_days=lead_time_days,
            is_current_stock_below_safety=is_current_below_safety,
            hypothetical_consumption_units=hypothetical_consumption,
            projected_post_action_stock=projected_post_action_stock,
            is_projected_stock_below_safety=is_projected_below_safety,
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
        )

        ev1 = EvidenceItem(
            evidence_id=f"EVID_P10_STOCK_{sku_id}",
            source_phase="Phase 10",
            source_module="InventoryOptimizer",
            domain=EvidenceDomain.INVENTORY_SPARE,
            metric="observed_current_stock",
            value=float(observed_current_stock),
            unit="units",
            threshold_applied=safety_stock,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Current on-hand stock is {observed_current_stock:.1f} units (above safety stock {safety_stock:.3f})",
            epistemic_classification=EpistemicClassification.OBSERVED,
        )
        ev2 = EvidenceItem(
            evidence_id=f"EVID_P10_PROJ_{sku_id}",
            source_phase="Phase 10",
            source_module="DecisionSupportInventoryProjection",
            domain=EvidenceDomain.INVENTORY_SPARE,
            metric="projected_post_action_stock",
            value=float(projected_post_action_stock),
            unit="units",
            threshold_applied=safety_stock,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=(
                f"Projected post-maintenance stock ({projected_post_action_stock:.1f} units) falls below "
                f"safety stock ({safety_stock:.3f} units) after consuming {hypothetical_consumption:.1f} unit"
            ),
            epistemic_classification=EpistemicClassification.PROJECTED,
        )
        ev3 = EvidenceItem(
            evidence_id=f"EVID_P10_LEAD_{sku_id}",
            source_phase="Phase 10",
            source_module="SupplierLeadTimeCatalog",
            domain=EvidenceDomain.INVENTORY_SPARE,
            metric="supplier_lead_time_days",
            value=float(lead_time_days),
            unit="days",
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Supplier replenishment lead time is {lead_time_days:.1f} days; delivery is not instantaneous",
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
        )

        evidence = [ev1, ev2, ev3]
        strength = calculate_evidence_strength(evidence)

        reason_text = (
            f"Current stock of {sku_id} is {observed_current_stock:.1f} units and above safety stock ({safety_stock:.3f}). "
            f"However, executing the recommended spindle bearing replacement consumes {hypothetical_consumption:.1f} unit, "
            f"projecting post-action stock to {projected_post_action_stock:.1f} units, which breaches the safety stock buffer. "
            f"Because supplier lead time is {lead_time_days:.1f} days, replenishment must be expedited proactively."
        )

        return OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_INV_EXPEDITE_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.INVENTORY,
            action=RecommendationAction.EXPEDITE_CRITICAL_SPARE,
            priority=RecommendationPriority.HIGH,
            urgency=ActionUrgency.SAME_DAY,
            evidence_strength=strength,
            reason=reason_text,
            evidence=evidence,
            source_phases=["Phase 10"],
            operational_impact="Exhaustion of safety buffer leaves factory exposed to unrecoverable downtime if secondary failure occurs.",
            financial_context=financial_context,
            inventory_context=inv_ctx,
            expected_benefit="Guarantees spare availability for subsequent maintenance cycles without causing machine downtime.",
            requires_operator_verification=True,
            rule_id="R-I01",
            epistemic_classification=scenario_epistemic,
        )
    return None


def evaluate_rule_r_e01(
    machine_id: str,
    as_of: datetime,
    is_bottleneck: bool,
    is_urgent_batch: bool,
    financial_context: Optional[FinancialEvidenceContext] = None,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> Optional[OperationalRecommendation]:
    """
    Rule R-E01: Peak Tariff Load Shifting.
    IF: Hour within 18:00-22:00 AND peak tariff applies AND machine is non-bottleneck AND non-urgent batch
    THEN: SHIFT_HIGH_LOAD_OFF_PEAK (Priority: LOW, Urgency: ROUTINE)
    """
    is_peak_hour = (18 <= as_of.hour < 22)
    if is_peak_hour and not is_bottleneck and not is_urgent_batch:
        ev1 = EvidenceItem(
            evidence_id=f"EVID_P09_PEAK_{machine_id}",
            source_phase="Phase 9",
            source_module="EnergyTariffScheduler",
            domain=EvidenceDomain.PRODUCTION_FLOW,
            metric="is_peak_tariff_window",
            value=True,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation="Current evaluation is within factory peak tariff window (18:00 - 22:00, INR 12.50/kWh vs INR 8.50 base)",
            epistemic_classification=EpistemicClassification.OBSERVED,
        )
        evidence = [ev1]
        strength = calculate_evidence_strength(evidence)

        return OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_ENERGY_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.ENERGY,
            action=RecommendationAction.SHIFT_HIGH_LOAD_OFF_PEAK,
            priority=RecommendationPriority.LOW,
            urgency=ActionUrgency.ROUTINE,
            evidence_strength=strength,
            reason=f"Machine {machine_id} is running non-critical jobs during peak energy tariff window (18:00-22:00).",
            evidence=evidence,
            source_phases=["Phase 9", "Phase 14"],
            operational_impact="Higher utility power bills without throughput gain.",
            financial_context=financial_context,
            expected_benefit="Captures peak-to-base tariff differential (INR 4.00/kWh) on non-urgent machining cycles.",
            requires_operator_verification=True,
            rule_id="R-E01",
            epistemic_classification=scenario_epistemic,
        )
    return None


def evaluate_rule_r_o01(
    machine_id: str,
    as_of: datetime,
    health_score: float,
    anomaly_score: float,
    failure_prob: float,
    is_bottleneck: bool,
    scenario_epistemic: EpistemicClassification = EpistemicClassification.DERIVED_FROM_OBSERVED,
) -> Optional[OperationalRecommendation]:
    """
    Rule R-O01: Nominal Monitoring Negative Control.
    IF: Health >= 75.0 (Phase 13 locked HEALTHY or EXCELLENT band)
        AND anomaly < 0.2405
        AND P(fail) < 0.75
        AND is_bottleneck = False
    THEN: CONTINUE_NOMINAL_MONITORING (Priority: MONITOR, Urgency: ROUTINE)
    """
    if health_score >= 75.0 and anomaly_score < P7_LOCKED_ANOMALY_THRESHOLD and failure_prob < P6_CONFIGURED_WARNING_THRESHOLD and not is_bottleneck:
        ev1 = EvidenceItem(
            evidence_id=f"EVID_P13_HEALTH_{machine_id}",
            source_phase="Phase 13",
            source_module="FactoryHealthScoreEngine",
            domain=EvidenceDomain.TELEMETRY_ANOMALY,
            metric="health_score",
            value=round(health_score, 2),
            threshold_applied=75.0,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Machine health score {health_score:.2f} is in locked HEALTHY/EXCELLENT band (>= 75.0)",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )
        ev2 = EvidenceItem(
            evidence_id=f"EVID_P07_ANOM_NOM_{machine_id}",
            source_phase="Phase 7",
            source_module="PCAReconstructionDetector",
            domain=EvidenceDomain.TELEMETRY_ANOMALY,
            metric="normalized_reconstruction_error",
            value=round(anomaly_score, 4),
            threshold_applied=P7_LOCKED_ANOMALY_THRESHOLD,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Anomaly score {anomaly_score:.4f} is within nominal noise envelope (< {P7_LOCKED_ANOMALY_THRESHOLD})",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )
        ev3 = EvidenceItem(
            evidence_id=f"EVID_P06_FAIL_NOM_{machine_id}",
            source_phase="Phase 6",
            source_module="AI4I_XGBoostClassifier",
            domain=EvidenceDomain.PREDICTIVE_FAILURE,
            metric="failure_probability",
            value=round(failure_prob, 4),
            threshold_applied=P6_CONFIGURED_WARNING_THRESHOLD,
            timestamp=as_of,
            machine_id=machine_id,
            interpretation=f"Failure probability {failure_prob:.4f} is well below warning threshold (< {P6_CONFIGURED_WARNING_THRESHOLD})",
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
        )

        evidence = [ev1, ev2, ev3]
        # In a nominal healthy state, evidence indicates absence of defect (INSUFFICIENT for physical intervention)
        strength = EvidenceStrength.INSUFFICIENT

        return OperationalRecommendation(
            recommendation_id=f"REC_{machine_id}_MONITOR_001",
            timestamp=as_of,
            machine_id=machine_id,
            category=RecommendationCategory.MONITORING,
            action=RecommendationAction.CONTINUE_NOMINAL_MONITORING,
            priority=RecommendationPriority.MONITOR,
            urgency=ActionUrgency.ROUTINE,
            evidence_strength=strength,
            reason=(
                f"Machine {machine_id} operates within all nominal baselines: Health Score ({health_score:.1f}) is in "
                f"healthy band, anomaly score ({anomaly_score:.4f}) is sub-threshold, and failure risk is negligible."
            ),
            evidence=evidence,
            source_phases=["Phase 6", "Phase 7", "Phase 13"],
            operational_impact="Nominal operation; zero physical intervention required.",
            expected_benefit="Avoids unnecessary machine shutdowns, false alarm fatigue, and unwarranted procurement.",
            requires_operator_verification=True,
            rule_id="R-O01",
            epistemic_classification=scenario_epistemic,
        )
    return None
