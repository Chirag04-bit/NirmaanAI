"""
NirmaanAI Feature Semantics & Manufacturing Domain Dictionary
Phase 11: Explainable AI & SHAP

Maps technical model feature names to verified human-readable manufacturing interpretations,
physical engineering units, and domain descriptions.

RESEARCH INTEGRITY:
- Interpretations reflect genuine physical definitions from dataset specifications.
- No invented physical meanings or ungrounded causal claims.
- Documents strict exclusion reasons for leakage variables (TWF, HDF, PWF, OSF, RNF, UDI, Product ID).
"""

from typing import Any, Dict, Optional


# AI4I 2020 Predictive Maintenance: 10 Model-Ready Features
AI4I_FEATURE_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "air_temperature_k": {
        "display_name": "Ambient Air Temperature",
        "unit": "Kelvin (K)",
        "domain_interpretation": "Factory ambient room temperature surrounding the machine enclosure.",
        "typical_range": "[295.0, 305.0] K",
        "risk_directionality": "High ambient temperature reduces thermal dissipation efficiency."
    },
    "process_temperature_k": {
        "display_name": "Internal Process Temperature",
        "unit": "Kelvin (K)",
        "domain_interpretation": "Operating temperature generated within the spindle and workpiece cutting zone.",
        "typical_range": "[305.0, 315.0] K",
        "risk_directionality": "High process temperature indicates heavy frictional work or inadequate cooling."
    },
    "rotational_speed_rpm": {
        "display_name": "Spindle Rotational Speed",
        "unit": "RPM",
        "domain_interpretation": "Motor angular velocity driving the cutting tool spindle.",
        "typical_range": "[1150, 2900] RPM",
        "risk_directionality": "Abnormally low speed under high torque indicates motor stalling; excessive speed induces dynamic vibration."
    },
    "torque_nm": {
        "display_name": "Spindle Torque",
        "unit": "Newton-meters (Nm)",
        "domain_interpretation": "Mechanical rotational resistance and cutting force encountered by the spindle motor.",
        "typical_range": "[3.8, 76.6] Nm",
        "risk_directionality": "High torque indicates heavy cutting load, dull tool engagement, or mechanical jamming."
    },
    "tool_wear_min": {
        "display_name": "Tool Wear Accumulated Time",
        "unit": "Minutes (min)",
        "domain_interpretation": "Cumulative cutting operating time logged on the active cutting tool insert.",
        "typical_range": "[0, 253] min",
        "risk_directionality": "Tool wear exceeding ~200 minutes drastically increases micro-chipping and catastrophic fracture risk."
    },
    "temp_diff_k": {
        "display_name": "Thermal Stress Differential (Delta T)",
        "unit": "Kelvin (K)",
        "domain_interpretation": "Difference between process temperature and ambient air temperature (Process Temp - Air Temp).",
        "typical_range": "[8.0, 12.5] K",
        "risk_directionality": "Low Delta T (< 8.6 K) at high power indicates heat dissipation failure (HDF)."
    },
    "mechanical_power_kw": {
        "display_name": "Instantaneous Mechanical Power Output",
        "unit": "Kilowatts (kW)",
        "domain_interpretation": "True mechanical power delivered to cutting interface: (2 * pi * RPM * Torque) / 60,000.",
        "typical_range": "[1.0, 9.5] kW",
        "risk_directionality": "Power outside [3.5, 9.0] kW envelope triggers power failure modes (under-power stall or over-power burn)."
    },
    "torque_speed_ratio": {
        "display_name": "Load Stress Ratio (Torque / Speed)",
        "unit": "Nm / RPM",
        "domain_interpretation": "Ratio of mechanical resistance to angular velocity; captures low-speed high-strain machine laboring.",
        "typical_range": "[0.002, 0.065]",
        "risk_directionality": "Elevated ratio indicates severe motor laboring under excessive cutting resistance."
    },
    "tool_wear_risk_index": {
        "display_name": "Non-Linear Tool Wear Penalty",
        "unit": "Dimensionless Index",
        "domain_interpretation": "Quadratic tool wear acceleration penalty: (Tool Wear / 200)^2.",
        "typical_range": "[0.0, 1.6]",
        "risk_directionality": "Quadratic rise past 1.0 models accelerated tertiary Taylor tool flank wear."
    },
    "product_type_code": {
        "display_name": "Workpiece Material Quality Grade",
        "unit": "Ordinal Code (0=L, 1=M, 2=H)",
        "domain_interpretation": "Variant grade of manufactured auto-component (L: Low quality/50% volume, M: Medium/30%, H: High/20%).",
        "typical_range": "{0, 1, 2}",
        "risk_directionality": "L-grade variants have lower tolerance margins, contributing to higher historical failure rates."
    }
}


# NASA C-MAPSS FD001 Turbofan Engine Degradation: 14 Informative Sensors & Operational Settings
CMAPSS_FEATURE_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "setting_1": {"display_name": "Operational Flight Altitude Setting", "unit": "Setting Value", "domain_interpretation": "Resolver throttle setting 1."},
    "setting_2": {"display_name": "Mach Number Operational Setting", "unit": "Setting Value", "domain_interpretation": "Resolver throttle setting 2."},
    "s2": {"display_name": "LPC Outlet Total Temperature", "unit": "deg R", "domain_interpretation": "Low-pressure compressor total outlet air temperature."},
    "s3": {"display_name": "HPC Outlet Total Temperature", "unit": "deg R", "domain_interpretation": "High-pressure compressor total outlet air temperature."},
    "s4": {"display_name": "LPT Outlet Total Temperature", "unit": "deg R", "domain_interpretation": "Low-pressure turbine exhaust gas temperature."},
    "s7": {"display_name": "HPC Outlet Total Pressure", "unit": "psia", "domain_interpretation": "Static bleed pressure off high-pressure compressor stage."},
    "s8": {"display_name": "Physical Fan Speed", "unit": "RPM", "domain_interpretation": "Fan rotor speed."},
    "s9": {"display_name": "Physical Core Speed", "unit": "RPM", "domain_interpretation": "Core gas turbine rotor shaft speed."},
    "s11": {"display_name": "HPC Static Outlet Pressure", "unit": "psia", "domain_interpretation": "Static pressure at high-pressure compressor exit."},
    "s12": {"display_name": "Fuel Flow to Static Pressure Ratio", "unit": "pps/psia", "domain_interpretation": "Combustion chamber fuel metering ratio."},
    "s13": {"display_name": "Corrected Fan Speed", "unit": "RPM", "domain_interpretation": "Fan shaft speed corrected for inlet total temperature."},
    "s14": {"display_name": "Corrected Core Speed", "unit": "RPM", "domain_interpretation": "Core compressor shaft speed corrected for inlet conditions."},
    "s15": {"display_name": "Bypass Ratio", "unit": "Ratio", "domain_interpretation": "Ratio of bypass duct airflow to core airflow."},
    "s17": {"display_name": "Bleed Enthalpy", "unit": "BTU/lbm", "domain_interpretation": "Enthalpy of compressor inter-stage bleed air."},
    "s20": {"display_name": "HPT Coolant Bleed Flow", "unit": "lbm/s", "domain_interpretation": "High-pressure turbine nozzle cooling flow rate."},
    "s21": {"display_name": "LPT Coolant Bleed Flow", "unit": "lbm/s", "domain_interpretation": "Low-pressure turbine cooling airflow rate."}
}


# Excluded Leakage Variables (Documented for Research Integrity Audits)
EXCLUDED_LEAKAGE_DICTIONARY: Dict[str, Dict[str, str]] = {
    "UDI": {
        "category": "Identifier Leakage",
        "reason_for_exclusion": "Row index counter (1..10000); perfectly uninformative and causes spurious shortcut learning."
    },
    "Product ID": {
        "category": "Identifier Leakage",
        "reason_for_exclusion": "Variant serial string (e.g. 'L47181'); carries identifier memorization risks."
    },
    "TWF": {
        "category": "Target / Failure Mode Leakage",
        "reason_for_exclusion": "Tool Wear Failure indicator (binary component of target 'Machine failure'). Revealing failure mode directly leaks ground-truth label."
    },
    "HDF": {
        "category": "Target / Failure Mode Leakage",
        "reason_for_exclusion": "Heat Dissipation Failure indicator. Sub-component of binary failure target."
    },
    "PWF": {
        "category": "Target / Failure Mode Leakage",
        "reason_for_exclusion": "Power Failure indicator. Sub-component of binary failure target."
    },
    "OSF": {
        "category": "Target / Failure Mode Leakage",
        "reason_for_exclusion": "Overstrain Failure indicator. Sub-component of binary failure target."
    },
    "RNF": {
        "category": "Target / Failure Mode Leakage",
        "reason_for_exclusion": "Random Failure indicator. Sub-component of binary failure target."
    }
}


# Phase 9 Autoregressive Forecasting Feature Dictionary
FORECASTING_FEATURE_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "power_lag_1h": {
        "display_name": "Immediate Preceding Load (t-1h)",
        "unit": "kW",
        "domain_interpretation": "Active electrical power consumed 1 hour prior; captures immediate short-term inertia."
    },
    "power_lag_2h": {
        "display_name": "Recent Load (t-2h)",
        "unit": "kW",
        "domain_interpretation": "Active electrical power consumed 2 hours prior."
    },
    "power_lag_24h": {
        "display_name": "Diurnal Seasonal Load (t-24h)",
        "unit": "kW",
        "domain_interpretation": "Active electrical power consumed at the exact same hour on the previous operating day."
    },
    "power_lag_168h": {
        "display_name": "Weekly Seasonal Load (t-168h)",
        "unit": "kW",
        "domain_interpretation": "Active electrical power consumed at the exact same hour on the previous week (same day-of-week)."
    },
    "hour_of_day": {
        "display_name": "Hour of Day",
        "unit": "Hour (0-23)",
        "domain_interpretation": "Cyclic diurnal manufacturing shift operating window (captures plant start, lunch break, shutdown)."
    }
}


def get_feature_metadata(feature_name: str) -> Dict[str, Any]:
    """Retrieves human-readable metadata for any recognized technical feature name."""
    if feature_name in AI4I_FEATURE_DICTIONARY:
        return AI4I_FEATURE_DICTIONARY[feature_name]
    if feature_name in CMAPSS_FEATURE_DICTIONARY:
        return CMAPSS_FEATURE_DICTIONARY[feature_name]
    if feature_name in FORECASTING_FEATURE_DICTIONARY:
        return FORECASTING_FEATURE_DICTIONARY[feature_name]

    # Handle rolling statistics for CMAPSS (e.g. s2_roll_mean, s2_roll_std)
    for base_sensor in CMAPSS_FEATURE_DICTIONARY:
        if feature_name == f"{base_sensor}_roll_mean":
            base_meta = CMAPSS_FEATURE_DICTIONARY[base_sensor]
            return {
                "display_name": f"{base_meta['display_name']} (5-Cycle Moving Average)",
                "unit": base_meta["unit"],
                "domain_interpretation": f"5-cycle short-term rolling mean of {base_meta['domain_interpretation']}"
            }
        if feature_name == f"{base_sensor}_roll_std":
            base_meta = CMAPSS_FEATURE_DICTIONARY[base_sensor]
            return {
                "display_name": f"{base_meta['display_name']} (5-Cycle Moving Volatility)",
                "unit": base_meta["unit"],
                "domain_interpretation": f"5-cycle short-term rolling standard deviation of {base_meta['domain_interpretation']}"
            }

    # Fallback generic metadata
    return {
        "display_name": feature_name.replace("_", " ").title(),
        "unit": "Engineered Value",
        "domain_interpretation": f"Engineered machine feature: {feature_name}"
    }
