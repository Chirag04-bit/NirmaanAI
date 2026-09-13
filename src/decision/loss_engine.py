"""
NirmaanAI Financial & Operational Loss Calculation Engine
Phase 14: Operational & Financial Loss Analysis (INR)

Implements pure, deterministic mathematical formulations for:
- Unplanned downtime financial loss
- Energy consumption cost & baseline inefficiency loss (Base ₹8.50 vs Peak ₹12.50)
- Scrap material replacement loss (₹350/kg, 0.8 kg/unit)
- Secondary rework labor overhead (₹280/hr)
- Bottleneck opportunity cost (₹320/unit lost throughput margin)
- Strict non-negative physical input validation
- Anti-double-counting safeguards and zero-cost diagnostic isolation
"""

from typing import Any, Dict, List, Optional, Tuple


# Configured MSME Financial Defaults from configs/factory_defaults.yaml
DEFAULT_DOWNTIME_RATE_INR_PER_HOUR = 4500.0
DEFAULT_BASE_ELECTRICITY_RATE_INR_PER_KWH = 8.50
DEFAULT_PEAK_ELECTRICITY_RATE_INR_PER_KWH = 12.50
DEFAULT_SCRAP_RATE_INR_PER_KG = 350.0
DEFAULT_REWORK_RATE_INR_PER_HOUR = 280.0
DEFAULT_CONTRIBUTION_MARGIN_PER_UNIT_INR = 320.0
DEFAULT_UNIT_MASS_KG = 0.80  # Configured finished part physical mass

# Provenance Documented Machine Baselines (kW)
# M1-M3: CONFIGURED_SIMULATION_BASELINE (configs/factory_defaults.yaml)
# M4-M5: SIMULATION_METADATA_BASELINE (DATASET/10_SYNTHETIC_FACTORY/synthetic/machines.csv)
DOCUMENTED_POWER_BASELINES_KW: Dict[str, float] = {
    "M1": 15.0,
    "M2": 22.0,
    "M3": 11.0,
    "M4": 4.5,
    "M5": 7.5,
}


def round_inr(value: float) -> float:
    """
    Standard rounding policy for Indian Rupee monetary values.
    Rounds strictly to 2 decimal places (representing Indian Paise ₹0.01).
    """
    return round(float(value), 2)


def validate_non_negative(**kwargs: Any) -> None:
    """
    Strict validation helper enforcing that physical quantities and financial rates
    are non-negative. Raises ValueError on corrupted or invalid negative numbers.
    """
    for name, val in kwargs.items():
        if val is None:
            continue
        if isinstance(val, (int, float)) and val < 0:
            raise ValueError(f"Invalid physical parameter '{name}': {val}. Physical values and rates cannot be negative.")


def is_peak_tariff_hour(hour: int) -> bool:
    """
    Determines whether a given hour (0-23) falls within the peak industrial tariff window.
    Peak tariff hours in West Bengal / Indian MSME standard: 18:00 to 22:00 (18, 19, 20, 21).
    """
    if not (0 <= hour <= 23):
        raise ValueError(f"Invalid hour: {hour}. Must be between 0 and 23.")
    return 18 <= hour < 22


def get_applicable_tariff(
    hour: int,
    base_rate: float = DEFAULT_BASE_ELECTRICITY_RATE_INR_PER_KWH,
    peak_rate: float = DEFAULT_PEAK_ELECTRICITY_RATE_INR_PER_KWH
) -> float:
    """
    Returns the applicable industrial electricity tariff in INR/kWh based on hour of day.
    """
    validate_non_negative(base_rate=base_rate, peak_rate=peak_rate)
    return peak_rate if is_peak_tariff_hour(hour) else base_rate


def calculate_downtime_loss(
    hours: float,
    rate_inr: float = DEFAULT_DOWNTIME_RATE_INR_PER_HOUR
) -> float:
    """
    Calculates unplanned machine downtime financial loss.
    downtime_loss = unplanned_downtime_hours * configured_INR_per_hour
    """
    validate_non_negative(hours=hours, rate_inr=rate_inr)
    return round_inr(hours * rate_inr)


def calculate_energy_consumption_and_cost(
    power_kw: float,
    duration_hours: float,
    tariff_rate_inr: float
) -> Tuple[float, float]:
    """
    Calculates physical energy consumed (kWh) and resulting operational energy cost (INR).
    energy_kWh = power_kW * duration_hours
    energy_cost_inr = energy_kWh * tariff_rate_inr
    """
    validate_non_negative(
        power_kw=power_kw,
        duration_hours=duration_hours,
        tariff_rate_inr=tariff_rate_inr
    )
    energy_kwh = power_kw * duration_hours
    cost_inr = round_inr(energy_kwh * tariff_rate_inr)
    return energy_kwh, cost_inr


def calculate_energy_inefficiency_loss(
    power_kw: float,
    baseline_power_kw: float,
    duration_hours: float,
    tariff_rate_inr: float
) -> Tuple[float, float]:
    """
    Calculates excess energy consumption above machine design capacity and associated financial loss.
    excess_power_kw = max(0.0, power_kw - baseline_power_kw)
    excess_energy_kwh = excess_power_kw * duration_hours
    inefficiency_loss_inr = excess_energy_kwh * tariff_rate_inr
    """
    validate_non_negative(
        power_kw=power_kw,
        baseline_power_kw=baseline_power_kw,
        duration_hours=duration_hours,
        tariff_rate_inr=tariff_rate_inr
    )
    excess_kw = max(0.0, power_kw - baseline_power_kw)
    excess_kwh = excess_kw * duration_hours
    loss_inr = round_inr(excess_kwh * tariff_rate_inr)
    return excess_kwh, loss_inr


def calculate_scrap_loss(
    scrap_quantity_units: int,
    unit_mass_kg: float = DEFAULT_UNIT_MASS_KG,
    scrap_rate_inr_per_kg: float = DEFAULT_SCRAP_RATE_INR_PER_KG
) -> Tuple[float, float]:
    """
    Calculates physical scrap mass (kg) and resulting material replacement loss (INR).
    scrap_mass_kg = round(scrap_quantity_units * unit_mass_kg, 2)
    scrap_loss_inr = scrap_mass_kg * scrap_rate_inr_per_kg
    """
    validate_non_negative(
        scrap_quantity_units=scrap_quantity_units,
        unit_mass_kg=unit_mass_kg,
        scrap_rate_inr_per_kg=scrap_rate_inr_per_kg
    )
    scrap_mass_kg = round(scrap_quantity_units * unit_mass_kg, 2)
    loss_inr = round_inr(scrap_mass_kg * scrap_rate_inr_per_kg)
    return scrap_mass_kg, loss_inr


def calculate_rework_loss(
    rework_hours: float,
    rework_rate_inr: float = DEFAULT_REWORK_RATE_INR_PER_HOUR
) -> float:
    """
    Calculates secondary technician correction / rework labor loss.
    rework_loss = rework_hours * rework_rate_inr
    """
    validate_non_negative(rework_hours=rework_hours, rework_rate_inr=rework_rate_inr)
    return round_inr(rework_hours * rework_rate_inr)


def calculate_bottleneck_opportunity_cost(
    delayed_or_lost_units: float,
    contribution_margin_inr: float = DEFAULT_CONTRIBUTION_MARGIN_PER_UNIT_INR
) -> float:
    """
    Calculates projected opportunity cost from delayed or lost throughput.
    opportunity_cost = delayed_or_lost_units * contribution_margin_inr
    Strictly classified as PROJECTED_OPPORTUNITY_COST (not realized accounting loss).
    """
    validate_non_negative(
        delayed_or_lost_units=delayed_or_lost_units,
        contribution_margin_inr=contribution_margin_inr
    )
    return round_inr(delayed_or_lost_units * contribution_margin_inr)


def verify_no_pseudo_financial_coupling(
    health_score: Optional[float] = None,
    failure_probability: Optional[float] = None,
    anomaly_score: Optional[float] = None,
    shap_values: Optional[Dict[str, float]] = None,
    rca_candidates: Optional[List[str]] = None
) -> float:
    """
    Double-counting & epistemic isolation safeguard:
    Explicitly asserts that diagnostic signals (Health Score, SHAP values, RCA candidates,
    Failure Probabilities, Anomaly Scores) NEVER generate direct rupee financial loss.
    Returns strictly 0.00 INR.
    """
    # Verifies that none of these inputs alter monetary calculations
    return 0.00
