"""
NirmaanAI Factory Health Score — Dimension Calculations
Phase 13: Factory Health Score

Calculates the six bounded operational health dimensions in [0.0, 100.0]:
1. Failure Risk Dimension (Phase 6 Predictive Maintenance)
2. Anomaly Health Dimension (Phase 7 Multi-Sensor Anomaly Detection)
3. Flow & Bottleneck Health Dimension (Phase 8 Flow Intelligence)
4. Energy Health Dimension (Phase 9 Power & Energy Forecasting)
5. Maintenance & Spares Context Dimension (Phase 10 Inventory Intelligence)
6. Diagnostic Consistency Dimension (Phase 12 Root Cause Analysis)

MATHEMATICAL PRINCIPLES:
- Every dimension output is strictly bounded in [0.0, 100.0].
- Monotonic behavior: increasing operational degradation strictly decreases dimension health.
- Prevents double-counting:
  - SHAP attribution is NOT counted as a separate penalty (already captured in Failure Risk).
  - RCA is modeled as a diagnostic severity modifier rather than re-aggregating sensor telemetry.
"""

from typing import Optional, Tuple
import numpy as np


def calculate_failure_risk_health(
    prediction_probability: Optional[float],
    threshold: float = 0.910,
) -> Tuple[Optional[float], str]:
    """
    Translates failure probability into bounded health in [0.0, 100.0].
    
    Formula:
    P <= 0.50 -> H = 100 - (P / 0.50) * 30.0 (Band: 70.0 - 100.0)
    P > 0.50  -> H = 70.0 * (1 - (P - 0.50) / 0.50) (Band: 0.0 - 70.0)
    At P = 0.910 (threshold) -> H = 12.6 (Critical distress band)
    """
    if prediction_probability is None:
        return None, "Failure risk dimension unavailable (no predictive maintenance input)."

    p = float(np.clip(prediction_probability, 0.0, 1.0))
    if p <= 0.50:
        h = 100.0 - (p / 0.50) * 30.0
    else:
        h = 70.0 * (1.0 - (p - 0.50) / 0.50)
        
    score = float(np.clip(h, 0.0, 100.0))
    desc = f"Failure probability {p:.3f} (decision threshold {threshold:.3f}) yields health {score:.1f}/100."
    return score, desc


def calculate_anomaly_health(
    anomaly_score: Optional[float],
    threshold: float = 0.2405,
) -> Tuple[Optional[float], str]:
    """
    Translates unsupervised multi-sensor anomaly score into health in [0.0, 100.0].
    
    Formula:
    H = 100.0 * (1.0 - clamp(anomaly_score / (2.0 * threshold), 0.0, 1.0))
    At score = 0 -> H = 100.0
    At score = threshold (0.2405) -> H = 50.0
    At score >= 2 * threshold (0.4810) -> H = 0.0
    """
    if anomaly_score is None:
        return None, "Anomaly health dimension unavailable (no anomaly telemetry)."

    anom = float(np.clip(anomaly_score, 0.0, 1.0))
    ratio = anom / (2.0 * threshold)
    h = 100.0 * (1.0 - np.clip(ratio, 0.0, 1.0))
    score = float(np.clip(h, 0.0, 100.0))
    desc = f"Anomaly score {anom:.4f} vs threshold {threshold:.4f} yields anomaly health {score:.1f}/100."
    return score, desc


def calculate_flow_health(
    cycle_time_sec: Optional[float] = None,
    design_cycle_time_sec: Optional[float] = None,
    cycle_ratio: Optional[float] = None,
    bottleneck_state: Optional[str] = None,
    dispatch_delay_min: Optional[float] = None,
) -> Tuple[Optional[float], str]:
    """
    Translates unit cycle ratio, line bottleneck status, and dispatch delays into flow health in [0.0, 100.0].
    """
    if cycle_time_sec is None and cycle_ratio is None and bottleneck_state is None:
        return None, "Flow health dimension unavailable (no cycle or bottleneck telemetry)."

    # Determine cycle ratio
    if cycle_ratio is not None:
        r = float(cycle_ratio)
    elif cycle_time_sec is not None and design_cycle_time_sec is not None and design_cycle_time_sec > 0:
        r = float(cycle_time_sec / design_cycle_time_sec)
    else:
        r = 1.0

    # Base flow health from cycle elongation
    base_flow = 100.0 * (1.0 - np.clip((r - 1.00) / 0.50, 0.0, 1.0))

    # Bottleneck penalties
    b_state = (bottleneck_state or "NOMINAL").upper()
    b_penalty = 0.0
    if b_state == "CRITICAL":
        b_penalty = 40.0
    elif b_state == "MODERATE":
        b_penalty = 20.0

    # Delay penalties (if queue delay > 10 min)
    d_penalty = 0.0
    if dispatch_delay_min is not None and dispatch_delay_min > 10.0:
        d_penalty = min(25.0, (dispatch_delay_min - 10.0) * 0.75)

    total_flow = float(np.clip(base_flow - b_penalty - d_penalty, 0.0, 100.0))
    desc = (
        f"Cycle ratio {r:.2f}, bottleneck state {b_state}, "
        f"and delay {dispatch_delay_min or 0.0:.1f}min yield flow health {total_flow:.1f}/100."
    )
    return total_flow, desc


def calculate_energy_health(
    power_kw: Optional[float] = None,
    baseline_power_kw: Optional[float] = None,
    forecast_residual_kw: Optional[float] = None,
) -> Tuple[Optional[float], str]:
    """
    Translates power consumption deviations from nominal machine baseline into energy health in [0.0, 100.0].
    """
    if power_kw is None or baseline_power_kw is None or baseline_power_kw <= 0:
        return None, "Energy health dimension unavailable (no power telemetry)."

    p_obs = float(power_kw)
    p_base = float(baseline_power_kw)
    dev_pct = abs(p_obs - p_base) / p_base

    # Deviations within +/- 10% are completely nominal
    excess_dev = max(0.0, dev_pct - 0.10)
    # Scales down to 0 at +90% excess deviation (i.e. double baseline)
    h = 100.0 * (1.0 - np.clip(excess_dev / 0.80, 0.0, 1.0))
    score = float(np.clip(h, 0.0, 100.0))
    desc = f"Power draw {p_obs:.1f} kW vs baseline {p_base:.1f} kW (dev {dev_pct*100:.1f}%) yields energy health {score:.1f}/100."
    return score, desc


def calculate_maintenance_health(
    spare_stock_level: Optional[int] = None,
    spare_safety_stock: Optional[int] = None,
    days_of_supply: Optional[float] = None,
    is_overdue: Optional[bool] = None,
    hours_since_maint: Optional[float] = None,
) -> Tuple[Optional[float], str]:
    """
    Translates critical replacement spare availability and servicing intervals into maintenance context health.
    """
    if (
        spare_stock_level is None
        and days_of_supply is None
        and is_overdue is None
        and hours_since_maint is None
    ):
        return None, "Maintenance context dimension unavailable (no inventory or servicing records)."

    base = 100.0
    penalties = 0.0

    # Spare stockout or critical deficit
    if spare_stock_level is not None and spare_stock_level == 0:
        penalties += 40.0
    elif days_of_supply is not None and days_of_supply == 0.0:
        penalties += 40.0
    elif (
        spare_stock_level is not None
        and spare_safety_stock is not None
        and spare_stock_level < spare_safety_stock
    ):
        penalties += 20.0

    # Servicing overdue
    if is_overdue is True:
        penalties += 25.0
    elif hours_since_maint is not None and hours_since_maint > 500.0:
        penalties += 15.0

    score = float(np.clip(base - penalties, 0.0, 100.0))
    desc = f"Maintenance & spare context evaluation with {penalties:.0f} penalty points yields {score:.1f}/100."
    return score, desc


def calculate_diagnostic_consistency_health(
    active_rca_severity: Optional[str] = None,
    active_rca_confidence: Optional[str] = None,
    has_active_unresolved_rca: bool = False,
) -> Tuple[Optional[float], str]:
    """
    Translates Root Cause Analysis status into a diagnostic consistency health score in [0.0, 100.0].
    
    DOUBLE-COUNTING SAFEGUARD:
    Does NOT re-aggregate raw vibration, temperature, or cycle times.
    Instead, represents the operational severity of active unresolved diagnostic findings.
    """
    if not has_active_unresolved_rca and active_rca_severity is None:
        return 100.0, "No active unresolved root-cause diagnostic findings. Consistency health is 100/100."

    sev = (active_rca_severity or "WARNING").upper()
    conf = (active_rca_confidence or "MEDIUM").upper()

    if sev == "CRITICAL" and conf == "HIGH":
        score = 30.0
    elif sev == "CRITICAL" and conf == "MEDIUM":
        score = 50.0
    elif sev == "WARNING" and conf == "HIGH":
        score = 65.0
    elif sev == "WARNING" and conf == "MEDIUM":
        score = 75.0
    else:  # LOW or INSUFFICIENT_EVIDENCE
        score = 88.0

    desc = f"Active RCA finding with severity={sev}, confidence={conf} yields diagnostic health {score:.1f}/100."
    return score, desc
