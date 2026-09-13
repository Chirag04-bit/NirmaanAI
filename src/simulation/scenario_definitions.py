"""
NirmaanAI Digital-Twin-Inspired What-If Scenario Definitions
Phase 16: What-If / Digital-Twin-Inspired Simulation Engine

Defines authoritative scenario configurations and transition logic for:
1. Baseline Machine 2 Operational State at t = 2026-01-21T12:00:00Z.
2. Machine 2 Scenarios A through E:
   - Scenario A: Baseline continuation / No intervention (unmitigated Day 22 halt)
   - Scenario B: INSPECT_SPINDLE_BEARING (preempts halt; consumes 1 spare)
   - Scenario C: INSPECT_SPINDLE_BEARING + EXPEDITE_CRITICAL_SPARE (preempts halt + reorders spare)
   - Scenario D: REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS (mitigates bottleneck delay)
   - Scenario E: INSPECT_SPINDLE_BEARING + REDUCE_MACHINE_FEED_RATE + RESCHEDULE_PENDING_JOBS + EXPEDITE_CRITICAL_SPARE
3. Healthy Negative Control Scenario (Machine M1 at t = 2026-01-17T12:00:00Z).
4. Configured Sensitivity Tiers (LOW, BASE, HIGH).

SCIENTIFIC INTEGRITY:
- Derived counterfactually from existing synthetic controlled scenario transitions.
- Configured assumptions are explicitly declared with documented rationale.
- Realized loss is strictly separated from projected loss and projected avoided loss.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from src.decision.loss_models import EpistemicClassification
from src.health.health_models import HealthState
from src.simulation.simulation_models import (
    KPIDeltaVector,
    OperationalKPIVector,
    ProjectionConfidence,
    ScenarioAssumption,
    SensitivityTier,
    SimulationInterventionType,
    WhatIfScenario,
)


# Configured financial MSME rates from factory_defaults.yaml
DOWNTIME_HOURLY_RATE_INR = 4500.00
REWORK_HOURLY_RATE_INR = 280.00
CONTRIBUTION_MARGIN_PER_UNIT_INR = 320.00


def get_m2_baseline_kpi_vector() -> OperationalKPIVector:
    """
    Authoritative baseline state vector of Machine 2 at t = 2026-01-21T12:00:00Z.
    Strictly causal: excludes future Day 22 emergency halt, MAINT_0003, and recovery.
    """
    return OperationalKPIVector(
        failure_probability=0.9959,
        anomaly_score=0.35,
        health_score=26.88,
        health_state=HealthState.CRITICAL,
        cycle_ratio=1.38,
        delayed_throughput_units=76.0,
        is_bottleneck=True,
        unplanned_downtime_minutes=0.0,
        planned_downtime_minutes=0.0,
        scrap_units=185.0,
        rework_hours=23.12,
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


def get_m1_negative_control_baseline_kpi_vector() -> OperationalKPIVector:
    """
    Authoritative baseline state vector of Machine M1 at t = 2026-01-17T12:00:00Z.
    Nominal operating conditions.
    """
    return OperationalKPIVector(
        failure_probability=0.02,
        anomaly_score=0.04,
        health_score=97.47,
        health_state=HealthState.EXCELLENT,
        cycle_ratio=1.00,
        delayed_throughput_units=0.0,
        is_bottleneck=False,
        unplanned_downtime_minutes=0.0,
        planned_downtime_minutes=0.0,
        scrap_units=0.0,
        rework_hours=0.0,
        observed_current_stock=12.0,
        safety_stock=0.233,
        reorder_point=1.033,
        projected_post_action_stock=12.0,
        is_safety_stock_breached=False,
        realized_operational_loss_inr=0.0,
        projected_opportunity_cost_inr=0.0,
        gross_financial_exposure_inr=0.0,
        projected_avoided_loss_inr=0.0,
    )


def compute_kpi_delta(baseline: OperationalKPIVector, projected: OperationalKPIVector) -> KPIDeltaVector:
    """Computes transparent delta = projected - baseline."""
    # Failure prob delta
    fail_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.failure_probability, (int, float)) and isinstance(projected.failure_probability, (int, float)):
        fail_delta = round(float(projected.failure_probability) - float(baseline.failure_probability), 4)

    # Anomaly score delta
    anom_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.anomaly_score, (int, float)) and isinstance(projected.anomaly_score, (int, float)):
        anom_delta = round(float(projected.anomaly_score) - float(baseline.anomaly_score), 4)

    # Health score delta
    health_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.health_score, (int, float)) and isinstance(projected.health_score, (int, float)):
        health_delta = round(float(projected.health_score) - float(baseline.health_score), 2)

    # Health state change
    if str(projected.health_state) == "NOT_PROJECTABLE" or str(baseline.health_state) == "NOT_PROJECTABLE":
        health_change = "NOT_PROJECTABLE"
    elif baseline.health_state != projected.health_state:
        health_change = f"{baseline.health_state} -> {projected.health_state}"
    else:
        health_change = "UNCHANGED"

    # Cycle ratio delta
    cycle_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.cycle_ratio, (int, float)) and isinstance(projected.cycle_ratio, (int, float)):
        cycle_delta = round(float(projected.cycle_ratio) - float(baseline.cycle_ratio), 2)

    # Delayed units delta
    delay_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.delayed_throughput_units, (int, float)) and isinstance(projected.delayed_throughput_units, (int, float)):
        delay_delta = round(float(projected.delayed_throughput_units) - float(baseline.delayed_throughput_units), 1)

    # Downtime deltas
    unplanned_dt_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.unplanned_downtime_minutes, (int, float)) and isinstance(projected.unplanned_downtime_minutes, (int, float)):
        unplanned_dt_delta = round(float(projected.unplanned_downtime_minutes) - float(baseline.unplanned_downtime_minutes), 1)

    planned_dt_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.planned_downtime_minutes, (int, float)) and isinstance(projected.planned_downtime_minutes, (int, float)):
        planned_dt_delta = round(float(projected.planned_downtime_minutes) - float(baseline.planned_downtime_minutes), 1)

    # Scrap and rework deltas
    scrap_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.scrap_units, (int, float)) and isinstance(projected.scrap_units, (int, float)):
        scrap_delta = round(float(projected.scrap_units) - float(baseline.scrap_units), 1)

    rework_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.rework_hours, (int, float)) and isinstance(projected.rework_hours, (int, float)):
        rework_delta = round(float(projected.rework_hours) - float(baseline.rework_hours), 2)

    # Stock delta
    stock_delta: Union[float, str] = "NOT_PROJECTABLE"
    if isinstance(baseline.observed_current_stock, (int, float)) and isinstance(projected.projected_post_action_stock, (int, float)):
        stock_delta = round(float(projected.projected_post_action_stock) - float(baseline.observed_current_stock), 1)

    # Financial avoided loss & gross exposure delta
    avoided_loss = float(projected.projected_avoided_loss_inr) if isinstance(projected.projected_avoided_loss_inr, (int, float)) else 0.0
    exposure_delta = round(float(projected.gross_financial_exposure_inr) - float(baseline.gross_financial_exposure_inr), 2)

    return KPIDeltaVector(
        failure_probability_delta=fail_delta,
        anomaly_score_delta=anom_delta,
        health_score_delta=health_delta,
        health_state_change=health_change,
        cycle_ratio_delta=cycle_delta,
        delayed_units_delta=delay_delta,
        unplanned_downtime_delta_minutes=unplanned_dt_delta,
        planned_downtime_delta_minutes=planned_dt_delta,
        scrap_units_delta=scrap_delta,
        rework_hours_delta=rework_delta,
        stock_delta_units=stock_delta,
        projected_avoided_loss_inr=avoided_loss,
        gross_exposure_delta_inr=exposure_delta,
    )
