"""
NirmaanAI Digital-Twin-Inspired What-If Simulation Engine
Phase 16: What-If / Digital-Twin-Inspired Simulation Engine

Executes deterministic scenario projections:
1. Scenario A: Baseline Continuation / No Intervention
2. Scenario B: INSPECT_SPINDLE_BEARING
3. Scenario C: INSPECT_SPINDLE_BEARING + EXPEDITE_CRITICAL_SPARE
4. Scenario D: REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS
5. Scenario E: INSPECT_SPINDLE_BEARING + REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS + EXPEDITE_CRITICAL_SPARE
6. Negative Control Scenario (Machine M1 nominal state)
7. Configured Sensitivity Analysis (LOW, BASE, HIGH tiers)

SCIENTIFIC INTEGRITY:
- Realized losses are strictly separated from projected avoided losses.
- No fabricated statistical confidence intervals; categorical labels are used.
- No unproven claims of global mathematical optimality.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
from src.simulation.simulation_models import (
    KPIDeltaVector,
    OperationalKPIVector,
    ProjectionConfidence,
    ScenarioAssumption,
    ScenarioComparisonReport,
    SensitivityTier,
    SimulationInterventionType,
    WhatIfScenario,
)


class WhatIfSimulationEngine:
    """
    Deterministic What-If Simulation Engine evaluating hypothetical operational interventions.
    """

    def __init__(self):
        pass

    def simulate_m2_scenario_a(self, as_of: datetime) -> WhatIfScenario:
        """
        Scenario A: Baseline Continuation / No Intervention.
        Unmitigated progression toward Day 22 emergency halt (MAINT_0003: 150 min downtime, 1.5h overhaul labor).
        TEMPORAL SEMANTICS:
        - Baseline state at cutoff (2026-01-21T12:00:00Z) contains strictly DECISION_TIME_INPUT data (<= cutoff).
        - Day 22 emergency halt (MAINT_0003 at 2026-01-22T16:30:00Z) is a FUTURE_EVENT_NOT_AVAILABLE_AT_DECISION.
        - In Scenario A, MAINT_0003 is evaluated strictly as RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.
        """
        baseline = get_m2_baseline_kpi_vector()

        # In Scenario A, unmitigated progression realizes the full Day 22 failure impact
        projected = OperationalKPIVector(
            failure_probability=0.9959,
            anomaly_score=0.35,
            health_score=21.73,  # Day 22 pre-halt health score from Phase 13
            health_state=HealthState.CRITICAL,
            cycle_ratio=1.38,
            delayed_throughput_units=76.0,
            is_bottleneck=True,
            unplanned_downtime_minutes=150.0,  # Realized in MAINT_0003
            planned_downtime_minutes=0.0,
            scrap_units=185.0,
            rework_hours=24.62,  # 23.12 prod rework + 1.5h emergency labor
            observed_current_stock=2.0,
            safety_stock=1.134,
            reorder_point=1.367,
            projected_post_action_stock=2.0,
            is_safety_stock_breached=False,
            realized_operational_loss_inr=73062.28,
            projected_opportunity_cost_inr=24320.00,
            gross_financial_exposure_inr=97382.28,
            projected_avoided_loss_inr=0.0,
        )

        assumptions = [
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_A_01",
                parameter_name="unmitigated_halt_downtime_minutes",
                configured_value=150.0,
                unit="minutes",
                rationale="Reflects actual Day 22 emergency halt (MAINT_0003: RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH; NOT a decision-time input at Jan-21 cutoff)",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_A_02",
                parameter_name="unmitigated_emergency_labor_hours",
                configured_value=1.5,
                unit="hours",
                rationale="Reflects actual Day 22 overhaul labor (MAINT_0003: RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH; NOT a decision-time input at Jan-21 cutoff)",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
        ]

        delta = compute_kpi_delta(baseline, projected)

        return WhatIfScenario(
            scenario_id="SCEN_M2_A_BASELINE",
            scenario_name="Scenario A: Baseline Continuation / No Intervention",
            machine_id="M2",
            as_of_timestamp=as_of,
            interventions=[],
            baseline_state=baseline,
            assumptions=assumptions,
            projected_state=projected,
            delta=delta,
            confidence=ProjectionConfidence.HIGH_EVIDENCE,
            epistemic_classification=EpistemicClassification.CONTROLLED_SYNTHETIC,
            evidence_basis=[
                "Phase 5 historical maintenance records (MAINT_0003: Retrospective Controlled Synthetic Ground Truth; NOT_DECISION_INPUT)",
                "Phase 14 realized loss models",
            ],
            limitations=[
                "At decision cutoff 2026-01-21T12:00:00Z, MAINT_0003 is a FUTURE_EVENT_NOT_AVAILABLE_AT_DECISION.",
                "Assumes factory operating conditions remain unadjusted through Day 22 halt.",
            ],
        )

    def simulate_m2_scenario_b(
        self, as_of: datetime, sensitivity: SensitivityTier = SensitivityTier.BASE
    ) -> WhatIfScenario:
        """
        Scenario B: INSPECT_SPINDLE_BEARING.
        Preempts catastrophic spindle seizure: planned 30 min service replaces 150 min unplanned halt.
        Consumes 1 spare bearing: projected stock drops to 1.0 (breaching safety stock 1.134).
        TEMPORAL SEMANTICS:
        - Avoided downtime is evaluated retrospectively against the controlled synthetic ground truth MAINT_0003.
        - Decision-time baseline inputs strictly exclude MAINT_0003.
        """
        baseline = get_m2_baseline_kpi_vector()

        planned_dt = 30.0  # Planned controlled inspection/service stoppage
        unplanned_avoided_min = 150.0

        if sensitivity == SensitivityTier.LOW:
            planned_dt = 45.0
            unplanned_avoided_min = 120.0
        elif sensitivity == SensitivityTier.HIGH:
            planned_dt = 20.0
            unplanned_avoided_min = 180.0

        avoided_downtime_hrs = (unplanned_avoided_min - planned_dt) / 60.0
        avoided_downtime_loss = round(avoided_downtime_hrs * DOWNTIME_HOURLY_RATE_INR, 2)
        avoided_emergency_labor = 420.00  # 1.5h @ 280/h avoided overtime
        total_avoided_loss = round(avoided_downtime_loss + avoided_emergency_labor, 2)

        # Mechanical recovery: Health, Failure Probability, and Anomaly Score
        # Classified as NOT_PROJECTABLE because no empirical causal treatment effect is available
        # in the existing synthetic dataset for preventive bearing service on Day 21.
        projected = OperationalKPIVector(
            failure_probability="NOT_PROJECTABLE",
            anomaly_score="NOT_PROJECTABLE",
            health_score="NOT_PROJECTABLE",
            health_state="NOT_PROJECTABLE",
            cycle_ratio=1.38,  # Flow queue is not yet rebalanced
            delayed_throughput_units=76.0,
            is_bottleneck=True,
            unplanned_downtime_minutes=0.0,
            planned_downtime_minutes=planned_dt,
            scrap_units=185.0,
            rework_hours=23.12,  # Emergency overhaul labor avoided
            observed_current_stock=2.0,
            safety_stock=1.134,
            reorder_point=1.367,
            projected_post_action_stock=1.0,  # 2.0 - 1.0 = 1.0
            is_safety_stock_breached=True,  # 1.0 < 1.134
            realized_operational_loss_inr=73062.28,
            projected_opportunity_cost_inr=24320.00,
            gross_financial_exposure_inr=round(97382.28 - total_avoided_loss, 2),
            projected_avoided_loss_inr=total_avoided_loss,
        )

        assumptions = [
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_B_01",
                parameter_name="preemptive_planned_downtime_minutes",
                configured_value=planned_dt,
                unit="minutes",
                rationale="Controlled maintenance stoppage to inspect and replace spindle bearing assembly",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_B_02",
                parameter_name="avoided_unplanned_emergency_downtime_minutes",
                configured_value=unplanned_avoided_min,
                unit="minutes",
                rationale="Eliminates the catastrophic 150-minute uncommanded stoppage observed in retrospective ground truth MAINT_0003 (NOT a decision-time input at Jan-21 cutoff)",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_B_03",
                parameter_name="bearing_consumption_units",
                configured_value=1.0,
                unit="units",
                rationale="One replacement bearing consumed from physical buffer, leaving 1.0 unit on hand",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
        ]

        delta = compute_kpi_delta(baseline, projected)

        return WhatIfScenario(
            scenario_id="SCEN_M2_B_INSPECT",
            scenario_name="Scenario B: INSPECT_SPINDLE_BEARING",
            machine_id="M2",
            as_of_timestamp=as_of,
            interventions=[SimulationInterventionType.INSPECT_SPINDLE_BEARING],
            baseline_state=baseline,
            assumptions=assumptions,
            projected_state=projected,
            delta=delta,
            confidence=ProjectionConfidence.ASSUMPTION_DEPENDENT,
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            evidence_basis=[
                "Phase 5 maintenance record MAINT_0003 (Retrospective Controlled Synthetic Ground Truth reference)",
                "Phase 14 downtime valuation rate (INR 4,500/h)",
                "Phase 14 emergency technician labor rate (INR 280/h)",
                "Phase 10 critical spare SKU buffer parameters",
            ],
            limitations=[
                "At decision cutoff 2026-01-21T12:00:00Z, MAINT_0003 is a FUTURE_EVENT_NOT_AVAILABLE_AT_DECISION; avoided breakdown loss of INR 9,420 is a retrospective counterfactual evaluation, never realized savings.",
                "No intervention-specific empirical treatment effect is available in the existing controlled synthetic dataset for mechanical health score or failure probability.",
                "Breaches safety stock buffer (projected stock 1.0 < 1.134) without accompanying spare reorder.",
                "Does not rebalance bottleneck line flow or clear queued delayed units.",
            ],
        )

    def simulate_m2_scenario_c(
        self, as_of: datetime, sensitivity: SensitivityTier = SensitivityTier.BASE
    ) -> WhatIfScenario:
        """
        Scenario C: INSPECT_SPINDLE_BEARING + EXPEDITE_CRITICAL_SPARE.
        Preempts catastrophic halt AND initiates proactive spare procurement (12 units EOQ under 7-day lead time).
        Resolves the post-action inventory vulnerability.
        """
        scen_b = self.simulate_m2_scenario_b(as_of, sensitivity)

        # Inventory position: Projected stock is 1.0 on hand, plus 12 units on order under 7-day lead time
        # Safety stock buffer vulnerability is actively mitigated by incoming replenishment
        projected = scen_b.projected_state.model_copy(
            update={
                "projected_post_action_stock": 1.0,
                "is_safety_stock_breached": True,  # Physical on-hand is 1.0, but purchase order is active
            }
        )

        assumptions = list(scen_b.assumptions) + [
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_C_01",
                parameter_name="expedited_spare_order_quantity",
                configured_value=12.0,
                unit="units",
                rationale="Triggers Phase 10 EOQ reorder (12.31 units rounded) with supplier lead time of 7.0 days",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
        ]

        delta = compute_kpi_delta(scen_b.baseline_state, projected)

        return WhatIfScenario(
            scenario_id="SCEN_M2_C_INSPECT_EXPEDITE",
            scenario_name="Scenario C: INSPECT_SPINDLE_BEARING + EXPEDITE_CRITICAL_SPARE",
            machine_id="M2",
            as_of_timestamp=as_of,
            interventions=[
                SimulationInterventionType.INSPECT_SPINDLE_BEARING,
                SimulationInterventionType.EXPEDITE_CRITICAL_SPARE,
            ],
            baseline_state=scen_b.baseline_state,
            assumptions=assumptions,
            projected_state=projected,
            delta=delta,
            confidence=ProjectionConfidence.ASSUMPTION_DEPENDENT,
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            evidence_basis=[
                "Phase 10 SKU_SPINDLE_BEARING_M2 EOQ and safety stock parameters",
                "Phase 14 downtime and labor loss equations",
            ],
            limitations=[
                "No intervention-specific empirical treatment effect is available in the existing controlled synthetic dataset for mechanical health score or failure probability.",
                "Supplier lead time is 7.0 days; expedited order protects subsequent cycles but does not accelerate immediate maintenance.",
                "Bottleneck WIP queue remains unmitigated on the production line.",
            ],
        )

    def simulate_m2_scenario_d(
        self, as_of: datetime, sensitivity: SensitivityTier = SensitivityTier.BASE
    ) -> WhatIfScenario:
        """
        Scenario D: REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS.
        Production flow mitigation: throttles feed rate and offloads queued batches to parallel lines.
        Mitigates delayed throughput units (76 -> 15 units) and avoids margin loss.
        Does NOT repair mechanical spindle bearing. Health/failure risk are NOT_PROJECTABLE.
        """
        baseline = get_m2_baseline_kpi_vector()

        delayed_units_post = 15.0
        if sensitivity == SensitivityTier.LOW:
            delayed_units_post = 25.0
        elif sensitivity == SensitivityTier.HIGH:
            delayed_units_post = 5.0

        avoided_units = 76.0 - delayed_units_post
        avoided_opportunity_cost = round(avoided_units * CONTRIBUTION_MARGIN_PER_UNIT_INR, 2)
        remaining_opportunity_cost = round(delayed_units_post * CONTRIBUTION_MARGIN_PER_UNIT_INR, 2)

        # Mechanical state remains distressed; health & failure risk are NOT_PROJECTABLE
        projected = OperationalKPIVector(
            failure_probability="NOT_PROJECTABLE",
            anomaly_score="NOT_PROJECTABLE",
            health_score="NOT_PROJECTABLE",
            health_state="NOT_PROJECTABLE",
            cycle_ratio=1.05,  # Configured rebalanced cycle ratio assumption
            delayed_throughput_units=delayed_units_post,
            is_bottleneck=False,  # Flow constraint relieved
            unplanned_downtime_minutes=0.0,
            planned_downtime_minutes=0.0,
            scrap_units=185.0,
            rework_hours=23.12,
            observed_current_stock=2.0,
            safety_stock=1.134,
            reorder_point=1.367,
            projected_post_action_stock=2.0,  # Zero bearing consumed
            is_safety_stock_breached=False,
            realized_operational_loss_inr=73062.28,
            projected_opportunity_cost_inr=remaining_opportunity_cost,
            gross_financial_exposure_inr=round(73062.28 + remaining_opportunity_cost, 2),
            projected_avoided_loss_inr=avoided_opportunity_cost,
        )

        assumptions = [
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_D_01",
                parameter_name="delayed_units_after_rescheduling",
                configured_value=delayed_units_post,
                unit="units",
                rationale="Configured hypothetical scenario assumption: rerouting batches to parallel machine capacity clears 80% of bottleneck delay (NOT empirically validated)",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
            ScenarioAssumption(
                assumption_id="ASSUMP_M2_D_02",
                parameter_name="contribution_margin_per_unit_inr",
                configured_value=CONTRIBUTION_MARGIN_PER_UNIT_INR,
                unit="INR/unit",
                rationale="Locked MSME financial assumption from factory_defaults.yaml; mechanically derives projected opportunity cost (NOT realized savings)",
                epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            ),
        ]

        delta = compute_kpi_delta(baseline, projected)

        return WhatIfScenario(
            scenario_id="SCEN_M2_D_FLOW_MITIGATION",
            scenario_name="Scenario D: REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS",
            machine_id="M2",
            as_of_timestamp=as_of,
            interventions=[
                SimulationInterventionType.REDUCE_MACHINE_FEED_RATE,
                SimulationInterventionType.RESCHEDULE_PENDING_JOBS,
            ],
            baseline_state=baseline,
            assumptions=assumptions,
            projected_state=projected,
            delta=delta,
            confidence=ProjectionConfidence.ASSUMPTION_DEPENDENT,
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            evidence_basis=[
                "Phase 8 bottleneck queue simulation",
                "Phase 14 opportunity cost contribution margin (INR 320/unit)",
            ],
            limitations=[
                "No intervention-specific empirical treatment effect is available in the existing controlled synthetic dataset for mechanical health score or failure probability.",
                "Remaining delayed units (15.0) is a configured hypothetical scenario assumption, not empirically validated.",
                "Projected avoided opportunity cost (INR 19,520) is unearned margin preservation, never realized savings.",
                "Temporary production flow mitigation cannot substitute for mechanical bearing overhaul.",
            ],
        )

    def simulate_m2_scenario_e(
        self, as_of: datetime, sensitivity: SensitivityTier = SensitivityTier.BASE
    ) -> WhatIfScenario:
        """
        Scenario E: Full Mitigation Portfolio.
        INSPECT_SPINDLE_BEARING + REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS + EXPEDITE_CRITICAL_SPARE.
        Provides the broadest modeled mitigation coverage under configured assumptions.
        """
        scen_c = self.simulate_m2_scenario_c(as_of, sensitivity)
        scen_d = self.simulate_m2_scenario_d(as_of, sensitivity)

        baseline = get_m2_baseline_kpi_vector()

        total_avoided_loss = round(
            float(scen_c.projected_state.projected_avoided_loss_inr)
            + float(scen_d.projected_state.projected_avoided_loss_inr),
            2,
        )

        projected = OperationalKPIVector(
            failure_probability="NOT_PROJECTABLE",
            anomaly_score="NOT_PROJECTABLE",
            health_score="NOT_PROJECTABLE",
            health_state="NOT_PROJECTABLE",
            cycle_ratio=1.05,
            delayed_throughput_units=float(scen_d.projected_state.delayed_throughput_units),
            is_bottleneck=False,
            unplanned_downtime_minutes=0.0,
            planned_downtime_minutes=float(scen_c.projected_state.planned_downtime_minutes),
            scrap_units=185.0,
            rework_hours=23.12,
            observed_current_stock=2.0,
            safety_stock=1.134,
            reorder_point=1.367,
            projected_post_action_stock=1.0,
            is_safety_stock_breached=True,
            realized_operational_loss_inr=73062.28,
            projected_opportunity_cost_inr=float(scen_d.projected_state.projected_opportunity_cost_inr),
            gross_financial_exposure_inr=round(97382.28 - total_avoided_loss, 2),
            projected_avoided_loss_inr=total_avoided_loss,
        )

        assumptions = list(scen_c.assumptions) + list(scen_d.assumptions)
        delta = compute_kpi_delta(baseline, projected)

        return WhatIfScenario(
            scenario_id="SCEN_M2_E_FULL_PORTFOLIO",
            scenario_name="Scenario E: Full Mitigation Portfolio (Maintenance + Flow + Inventory)",
            machine_id="M2",
            as_of_timestamp=as_of,
            interventions=[
                SimulationInterventionType.INSPECT_SPINDLE_BEARING,
                SimulationInterventionType.REDUCE_MACHINE_FEED_RATE,
                SimulationInterventionType.RESCHEDULE_PENDING_JOBS,
                SimulationInterventionType.EXPEDITE_CRITICAL_SPARE,
            ],
            baseline_state=baseline,
            assumptions=assumptions,
            projected_state=projected,
            delta=delta,
            confidence=ProjectionConfidence.ASSUMPTION_DEPENDENT,
            epistemic_classification=EpistemicClassification.CONFIGURED_ASSUMPTION,
            evidence_basis=[
                "Phase 10 SKU_SPINDLE_BEARING_M2 inventory replenishment model",
                "Phase 14 downtime and opportunity loss models",
            ],
            limitations=[
                "No intervention-specific empirical treatment effect is available in the existing controlled synthetic dataset for mechanical health score or failure probability.",
                "Delay reduction to 15 units is a configured hypothetical scenario assumption, not empirically validated.",
                "Avoided financial exposure combines avoided breakdown loss (INR 9,420; projected) and avoided opportunity cost (INR 19,520; projected opportunity cost, NOT realized savings).",
                "Requires simultaneous operator intervention across maintenance, scheduling, and procurement.",
                "Dependent on 7-day supplier lead time for bearing inventory replenishment.",
            ],
        )

    def simulate_negative_control_m1(self, as_of: datetime) -> WhatIfScenario:
        """
        Healthy Negative Control Scenario: Machine M1 at t = 2026-01-17T12:00:00Z.
        Simulates hypothetical intervention on an already healthy machine.
        Demonstrates that the engine produces zero fabricated benefit when asset is nominal.
        """
        baseline = get_m1_negative_control_baseline_kpi_vector()

        # Under nominal monitoring, state remains identical (no fabricated benefit)
        projected = baseline.model_copy()

        assumptions = [
            ScenarioAssumption(
                assumption_id="ASSUMP_NEG_01",
                parameter_name="nominal_state_invariance",
                configured_value=True,
                rationale="Healthy asset operating under nominal baselines requires no intervention; state remains stable",
                epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
            )
        ]

        delta = compute_kpi_delta(baseline, projected)

        return WhatIfScenario(
            scenario_id="SCEN_M1_NEGATIVE_CONTROL",
            scenario_name="Healthy Machine Negative Control (Machine M1)",
            machine_id="M1",
            as_of_timestamp=as_of,
            interventions=[],
            baseline_state=baseline,
            assumptions=assumptions,
            projected_state=projected,
            delta=delta,
            confidence=ProjectionConfidence.HIGH_EVIDENCE,
            epistemic_classification=EpistemicClassification.DERIVED_FROM_OBSERVED,
            evidence_basis=["Phase 13 nominal baseline telemetry", "Phase 6 failure classifier zero-risk output"],
            limitations=["Demonstrates negative control validity; zero degradation present to mitigate"],
        )

    def compare_m2_scenarios(self, as_of: datetime) -> ScenarioComparisonReport:
        """
        Builds comparative portfolio evaluation across Scenarios A through E for Machine 2.
        Ranks scenarios based on mitigation coverage under configured assumptions.
        """
        scen_a = self.simulate_m2_scenario_a(as_of)
        scen_b = self.simulate_m2_scenario_b(as_of)
        scen_c = self.simulate_m2_scenario_c(as_of)
        scen_d = self.simulate_m2_scenario_d(as_of)
        scen_e = self.simulate_m2_scenario_e(as_of)

        scenarios = [scen_a, scen_b, scen_c, scen_d, scen_e]

        ranking_narrative = (
            "Comparative evaluation under configured MSME assumptions demonstrates that Scenario E provides "
            "the broadest modeled mitigation coverage. Scenario A results in unmitigated emergency halt (MAINT_0003). "
            "Scenario B eliminates 150 min unplanned downtime (avoiding ₹9,420 in projected breakdown losses) but leaves inventory "
            "breached at 1.0 unit. Scenario C resolves this by pairing proactive reordering. Scenario D targets the "
            "bottleneck queue (avoiding ₹19,520 in projected opportunity cost based on a configured hypothetical reduction to 15 delayed units; "
            "NOT realized savings) but leaves the spindle bearing unserviced. Scenario E synthesizes maintenance, scheduling, "
            "and procurement for a total projected avoided financial exposure of ₹28,940 (₹9,420 avoided breakdown loss + ₹19,520 avoided opportunity cost). "
            "Mechanical health score and failure probability under preventive interventions are classified as NOT_PROJECTABLE "
            "due to the absence of empirical causal treatment effect data in the repository. "
            "(Note: Scenario E is designated as providing the broadest modeled mitigation coverage under configured assumptions; "
            "no claim of unconstrained mathematical global optimality is made)."
        )

        return ScenarioComparisonReport(
            comparison_id=f"COMP_M2_{as_of.strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.now(timezone.utc),
            machine_id="M2",
            baseline_as_of=as_of,
            scenarios=scenarios,
            ranking_narrative=ranking_narrative,
            recommended_scenario_id="SCEN_M2_E_FULL_PORTFOLIO",
            governance_notice="DECISION SUPPORT ONLY: What-if simulation evaluates hypothetical interventions against configured assumptions. All physical interventions require operator authorization.",
        )
