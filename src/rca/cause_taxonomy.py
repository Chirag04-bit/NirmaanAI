"""
NirmaanAI Root Cause Analysis (RCA) — Controlled Cause Taxonomy
Phase 12: Root Cause Analysis

Defines the controlled taxonomy of 13 operational candidate causes.
Prevents arbitrary or hallucinated root causes by strictly restricting candidates
to operational categories backed by available sensors, telemetry, and engineering features.

RESEARCH INTEGRITY RULES:
- Candidate causes represent operational factors associated with an observed event, NOT proven physical causes.
- Does NOT claim causal proof without experimental or interventional evidence.
- Features are mapped deterministically based on engineering domain principles.
"""

from enum import Enum
from typing import Any, Dict, List, Set


class CauseCategory(str, Enum):
    """Controlled taxonomy of candidate contributing causes."""
    THERMAL_STRESS = "THERMAL_STRESS"
    MECHANICAL_LOAD = "MECHANICAL_LOAD"
    TOOL_WEAR = "TOOL_WEAR"
    SPEED_DEVIATION = "SPEED_DEVIATION"
    VIBRATION_DEVIATION = "VIBRATION_DEVIATION"
    PROCESS_INSTABILITY = "PROCESS_INSTABILITY"
    CYCLE_TIME_DEGRADATION = "CYCLE_TIME_DEGRADATION"
    FLOW_CONGESTION = "FLOW_CONGESTION"
    ENERGY_DEVIATION = "ENERGY_DEVIATION"
    MATERIAL_OR_SPARE_CONSTRAINT = "MATERIAL_OR_SPARE_CONSTRAINT"
    MAINTENANCE_STATE = "MAINTENANCE_STATE"
    SENSOR_OR_DATA_QUALITY_ANOMALY = "SENSOR_OR_DATA_QUALITY_ANOMALY"
    UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"


class CauseDefinition:
    """Metadata describing each controlled candidate cause."""
    def __init__(
        self,
        category: CauseCategory,
        display_name: str,
        description: str,
        primary_signals: List[str],
        corroborating_signals: List[str],
        contradictory_signals: List[str],
        investigation_suggestion: str,
    ):
        self.category = category
        self.display_name = display_name
        self.description = description
        self.primary_signals = primary_signals
        self.corroborating_signals = corroborating_signals
        self.contradictory_signals = contradictory_signals
        self.investigation_suggestion = investigation_suggestion


CAUSE_DEFINITIONS: Dict[CauseCategory, CauseDefinition] = {
    CauseCategory.THERMAL_STRESS: CauseDefinition(
        category=CauseCategory.THERMAL_STRESS,
        display_name="Thermal Stress / Heat Dissipation Deficit",
        description="Excessive internal process or spindle temperature elevation and thermal gradient expansion.",
        primary_signals=["temp_diff_k", "temp_diff_c", "process_temperature_k", "temperature_c"],
        corroborating_signals=["power_consumption_kw", "torque_nm", "rotational_speed_rpm"],
        contradictory_signals=["ambient_temp_excessive_only"],
        investigation_suggestion="Inspect coolant flow rate, heat exchanger jacket, and thermal lubrication circuit.",
    ),
    CauseCategory.MECHANICAL_LOAD: CauseDefinition(
        category=CauseCategory.MECHANICAL_LOAD,
        display_name="Mechanical Overload / Torque Surge",
        description="Severe mechanical resistance, torque overstrain, or excessive cutting force.",
        primary_signals=["torque_nm", "power_mw", "mechanical_power_kw", "overstrain_ratio"],
        corroborating_signals=["vibration_mms", "power_consumption_kw", "cycle_time_sec"],
        contradictory_signals=["rotational_speed_overspeed"],
        investigation_suggestion="Inspect spindle drive coupling, workpiece clamp alignment, and raw stock hardness.",
    ),
    CauseCategory.TOOL_WEAR: CauseDefinition(
        category=CauseCategory.TOOL_WEAR,
        display_name="Tool Wear Accumulation",
        description="Cutting edge degradation resulting from extended tool cutting duration and material friction.",
        primary_signals=["tool_wear_min", "wear_torque_interaction", "wear_speed_ratio"],
        corroborating_signals=["cycle_time_sec", "vibration_mms", "torque_nm"],
        contradictory_signals=["tool_wear_min_nominal"],  # Low tool wear directly contradicts
        investigation_suggestion="Perform optical tool edge measurement, check insert wear land, and inspect insert indexing history.",
    ),
    CauseCategory.SPEED_DEVIATION: CauseDefinition(
        category=CauseCategory.SPEED_DEVIATION,
        display_name="Rotational Speed Deviation",
        description="Spindle rotational velocity excursion significantly outside nominal machining envelope.",
        primary_signals=["rotational_speed_rpm", "speed_torque_ratio"],
        corroborating_signals=["power_consumption_kw", "vibration_mms"],
        contradictory_signals=[],
        investigation_suggestion="Examine VFD (variable frequency drive) tachometer feedback, motor encoder, and belt tension.",
    ),
    CauseCategory.VIBRATION_DEVIATION: CauseDefinition(
        category=CauseCategory.VIBRATION_DEVIATION,
        display_name="Spindle / Axis Vibration Elevation",
        description="Harmonic or broadband mechanical vibration excursion exceeding machine baseline limits.",
        primary_signals=["vibration_mms", "vibration_std", "sound_db"],
        corroborating_signals=["temperature_c", "torque_nm", "cycle_time_sec"],
        contradictory_signals=["vibration_mms_nominal"],
        investigation_suggestion="Conduct accelerometer spectral FFT analysis, check spindle bearing pre-load, and inspect chuck balance.",
    ),
    CauseCategory.PROCESS_INSTABILITY: CauseDefinition(
        category=CauseCategory.PROCESS_INSTABILITY,
        display_name="Multi-Sensor Process Instability",
        description="Coordinated multi-sensor covariance disturbance indicating system-level instability.",
        primary_signals=["anomaly_score", "reconstruction_error", "sensor_variance"],
        corroborating_signals=["vibration_mms", "temperature_c", "power_consumption_kw"],
        contradictory_signals=[],
        investigation_suggestion="Review process parameter stability, electrical ground isolation, and hydraulic fluid pressure.",
    ),
    CauseCategory.CYCLE_TIME_DEGRADATION: CauseDefinition(
        category=CauseCategory.CYCLE_TIME_DEGRADATION,
        display_name="Cycle Time Degradation / Feed Rate Slowdown",
        description="Substantial elongation of cycle duration per unit relative to nominal machine design specification.",
        primary_signals=["cycle_time_sec", "cycle_ratio", "process_speed_loss"],
        corroborating_signals=["vibration_mms", "torque_nm", "wip_delay_sec"],
        contradictory_signals=["cycle_ratio_nominal"],
        investigation_suggestion="Audit CNC feed rate override setting, axis servo lag, and part transfer indexing mechanism.",
    ),
    CauseCategory.FLOW_CONGESTION: CauseDefinition(
        category=CauseCategory.FLOW_CONGESTION,
        display_name="Line Flow Congestion / Bottleneck Escalation",
        description="Upstream queue accumulation, inter-stage buffer saturation, and dispatch delays.",
        primary_signals=["queue_length", "dispatch_delay_min", "buffer_saturation_pct"],
        corroborating_signals=["cycle_ratio", "downstream_starvation_sec"],
        contradictory_signals=[],
        investigation_suggestion="Inspect line balancing, inter-stage conveyance buffer, and upstream batch dispatch timing.",
    ),
    CauseCategory.ENERGY_DEVIATION: CauseDefinition(
        category=CauseCategory.ENERGY_DEVIATION,
        display_name="Electrical Energy Surge / Load Discrepancy",
        description="Electrical power draw or load significantly divergent from baseline or forecasted regime.",
        primary_signals=["power_consumption_kw", "power_deviation_kw", "forecast_residual_kw"],
        corroborating_signals=["torque_nm", "temperature_c"],
        contradictory_signals=[],
        investigation_suggestion="Check electrical power meter calibration, motor winding temperature, and drive inverter harmonics.",
    ),
    CauseCategory.MATERIAL_OR_SPARE_CONSTRAINT: CauseDefinition(
        category=CauseCategory.MATERIAL_OR_SPARE_CONSTRAINT,
        display_name="Spare Part / Material Constraint",
        description="Stockout risk, extended replenishment lead time, or lack of required maintenance spares.",
        primary_signals=["spare_stock_level", "spare_lead_time_days", "days_of_supply"],
        corroborating_signals=["maintenance_pending", "degradation_severity"],
        contradictory_signals=["spare_stock_adequate"],
        investigation_suggestion="Verify spare inventory count in store room, confirm supplier lead time, and assess emergency buffer.",
    ),
    CauseCategory.MAINTENANCE_STATE: CauseDefinition(
        category=CauseCategory.MAINTENANCE_STATE,
        display_name="Maintenance State / Overdue Servicing",
        description="Prolonged elapsed operating intervals without scheduled preventive servicing or corrective overhaul.",
        primary_signals=["hours_since_last_maintenance", "maintenance_overdue_flag"],
        corroborating_signals=["vibration_mms", "tool_wear_min"],
        contradictory_signals=[],
        investigation_suggestion="Check computerized maintenance management log, review technician servicing history, and inspect lubrication intervals.",
    ),
    CauseCategory.SENSOR_OR_DATA_QUALITY_ANOMALY: CauseDefinition(
        category=CauseCategory.SENSOR_OR_DATA_QUALITY_ANOMALY,
        display_name="Sensor / Data Quality Anomaly",
        description="Isolated telemetry dropout, frozen signal, or non-physical spike lacking physical cross-corroboration.",
        primary_signals=["telemetry_dropout", "frozen_sensor_duration", "unphysical_gradient"],
        corroborating_signals=[],
        contradictory_signals=["cross_sensor_corroboration_present"],
        investigation_suggestion="Check sensor wiring, signal transmitter cabling, ADC module, and analog input calibration.",
    ),
    CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE: CauseDefinition(
        category=CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE,
        display_name="Unknown / Insufficient Evidence",
        description="Available multi-source evidence is insufficient, contradictory, or below statistical significance thresholds.",
        primary_signals=[],
        corroborating_signals=[],
        contradictory_signals=[],
        investigation_suggestion="Collect additional telemetry, conduct manual visual walk-through, and verify sensor telemetry continuity.",
    ),
}


# Mapping of input feature names (from SHAP, sensors, or tabular models) to Candidate Causes
FEATURE_TO_CAUSE_MAP: Dict[str, List[CauseCategory]] = {
    # AI4I / Engineering features
    "temp_diff_k": [CauseCategory.THERMAL_STRESS],
    "temp_diff_c": [CauseCategory.THERMAL_STRESS],
    "air_temperature_k": [CauseCategory.THERMAL_STRESS],
    "process_temperature_k": [CauseCategory.THERMAL_STRESS],
    "rotational_speed_rpm": [CauseCategory.SPEED_DEVIATION, CauseCategory.MECHANICAL_LOAD],
    "torque_nm": [CauseCategory.MECHANICAL_LOAD],
    "power_mw": [CauseCategory.MECHANICAL_LOAD, CauseCategory.ENERGY_DEVIATION],
    "mechanical_power_kw": [CauseCategory.MECHANICAL_LOAD, CauseCategory.ENERGY_DEVIATION],
    "tool_wear_min": [CauseCategory.TOOL_WEAR],
    "wear_torque_interaction": [CauseCategory.TOOL_WEAR, CauseCategory.MECHANICAL_LOAD],
    "wear_speed_ratio": [CauseCategory.TOOL_WEAR, CauseCategory.SPEED_DEVIATION],
    "overstrain_ratio": [CauseCategory.MECHANICAL_LOAD],
    
    # Synthetic Factory / Sensor telemetry
    "vibration_mms": [CauseCategory.VIBRATION_DEVIATION, CauseCategory.MECHANICAL_LOAD],
    "temperature_c": [CauseCategory.THERMAL_STRESS],
    "sound_db": [CauseCategory.VIBRATION_DEVIATION],
    "power_consumption_kw": [CauseCategory.ENERGY_DEVIATION, CauseCategory.MECHANICAL_LOAD],
    "oil_level_pct": [CauseCategory.MAINTENANCE_STATE, CauseCategory.THERMAL_STRESS],
    "coolant_level_pct": [CauseCategory.THERMAL_STRESS, CauseCategory.MAINTENANCE_STATE],
    
    # Operational & Flow indicators
    "cycle_time_sec": [CauseCategory.CYCLE_TIME_DEGRADATION],
    "cycle_ratio": [CauseCategory.CYCLE_TIME_DEGRADATION, CauseCategory.FLOW_CONGESTION],
    "queue_length": [CauseCategory.FLOW_CONGESTION],
    "dispatch_delay_min": [CauseCategory.FLOW_CONGESTION],
    
    # Anomaly scores
    "anomaly_score": [CauseCategory.PROCESS_INSTABILITY],
}


def get_candidate_causes_for_feature(feature_name: str) -> List[CauseCategory]:
    """Returns list of candidate causes associated with a given feature."""
    return FEATURE_TO_CAUSE_MAP.get(feature_name, [])


def get_cause_definition(category: CauseCategory) -> CauseDefinition:
    """Returns the CauseDefinition metadata for a candidate cause category."""
    return CAUSE_DEFINITIONS.get(
        category,
        CAUSE_DEFINITIONS[CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE]
    )
