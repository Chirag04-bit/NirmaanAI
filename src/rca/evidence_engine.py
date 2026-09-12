"""
NirmaanAI Root Cause Analysis (RCA) — Evidence Fusion Engine
Phase 12: Root Cause Analysis

Implements a deterministic, interpretable evidence fusion mechanism that computes
normalized evidence scores for candidate causes from multi-source signals:
1. SHAP Model Attribution (Phase 11)
2. Machine-Specific Telemetry Baseline Deviations (Phase 5/7)
3. Anomaly Scores & Principal Component Reconstructions (Phase 7)
4. Operational Flow & Cycle-Time Degradations (Phase 8)
5. Inventory & Critical Spare States (Phase 10)
6. Contradictory / Negative Evidence Penalties

SCIENTIFIC INTEGRITY:
- Every scoring component is bounded in [0.0, 1.0] with documented engineering rationale.
- Scoring weights are CONFIGURED ANALYTICAL WEIGHTS, never learned causal coefficients.
- The composite score is an analytical evidence score, NEVER a "probability of causation".
- Machine-specific baselines prevent cross-machine distribution distortion.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.rca.cause_taxonomy import (
    CauseCategory,
    CAUSE_DEFINITIONS,
    FEATURE_TO_CAUSE_MAP,
    get_cause_definition,
)
from src.rca.rca_models import (
    EvidenceSourceType,
    RCAEventContext,
    SignalEvidenceItem,
)
from src.utils.config_loader import get_project_root


# Standard machine baseline profiles (respecting machine-specific operating regimes)
DEFAULT_MACHINE_BASELINES: Dict[str, Dict[str, float]] = {
    "M1": {
        "baseline_vibration_mms": 1.2,
        "alert_vibration_mms": 3.8,
        "critical_vibration_mms": 5.5,
        "baseline_power_kw": 18.0,
        "design_cycle_time_sec": 30.0,
        "baseline_temp_c": 32.0,
    },
    "M2": {
        "baseline_vibration_mms": 1.4,
        "alert_vibration_mms": 3.8,
        "critical_vibration_mms": 5.5,
        "baseline_power_kw": 22.0,
        "design_cycle_time_sec": 45.0,
        "baseline_temp_c": 35.0,
    },
    "M3": {
        "baseline_vibration_mms": 1.1,
        "alert_vibration_mms": 3.5,
        "critical_vibration_mms": 5.0,
        "baseline_power_kw": 15.0,
        "design_cycle_time_sec": 60.0,
        "baseline_temp_c": 30.0,
    },
    "M4": {
        "baseline_vibration_mms": 0.8,
        "alert_vibration_mms": 3.0,
        "critical_vibration_mms": 4.5,
        "baseline_power_kw": 8.0,
        "design_cycle_time_sec": 15.0,
        "baseline_temp_c": 28.0,
    },
    "M5": {
        "baseline_vibration_mms": 1.0,
        "alert_vibration_mms": 3.2,
        "critical_vibration_mms": 4.8,
        "baseline_power_kw": 12.0,
        "design_cycle_time_sec": 25.0,
        "baseline_temp_c": 30.0,
    },
}

# Configured analytical weights for evidence fusion
# Documented strictly as analytical weights, not causal parameters.
WEIGHT_SHAP = 0.25
WEIGHT_ANOMALY = 0.25
WEIGHT_TELEMETRY = 0.30
WEIGHT_OPERATIONAL = 0.20
PENALTY_CONTRADICTION = 0.35


class EvidenceFusionEngine:
    """
    Deterministic evidence evaluation and scoring engine.
    Calculates multi-source evidence and applies contradiction penalties.
    """

    def __init__(self, machine_baselines: Optional[Dict[str, Dict[str, float]]] = None):
        self.machine_baselines = machine_baselines or DEFAULT_MACHINE_BASELINES

    def get_baseline(self, machine_id: str) -> Dict[str, float]:
        """Returns baseline parameter dictionary for target machine."""
        return self.machine_baselines.get(machine_id, self.machine_baselines.get("M2", {}))

    def evaluate_candidate_cause(
        self,
        category: CauseCategory,
        event: RCAEventContext,
        temporal_multiplier: float = 1.0
    ) -> Tuple[float, List[SignalEvidenceItem], List[SignalEvidenceItem]]:
        """
        Evaluates composite evidence for a specific candidate cause.
        
        Returns:
            (composite_score, supporting_signals, contradictory_signals)
        """
        if category == CauseCategory.UNKNOWN_INSUFFICIENT_EVIDENCE:
            return 0.0, [], []

        baseline = self.get_baseline(event.machine_id)
        definition = get_cause_definition(category)
        
        supporting_signals: List[SignalEvidenceItem] = []
        contradictory_signals: List[SignalEvidenceItem] = []
        
        # 1. SHAP Model Attribution Evidence
        shap_score = 0.0
        if event.shap_contributions:
            relevant_shap_vals = []
            for feat, val in event.shap_contributions.items():
                causes = FEATURE_TO_CAUSE_MAP.get(feat, [])
                if category in causes:
                    # Positive margin contribution increases failure prediction
                    if val > 0.0:
                        relevant_shap_vals.append(val)
                        supporting_signals.append(
                            SignalEvidenceItem(
                                signal_name=f"SHAP_{feat}",
                                source=EvidenceSourceType.SHAP_MODEL_ATTRIBUTION,
                                observed_value=float(val),
                                normalized_evidence=float(np.clip(val / 4.0, 0.0, 1.0)),
                                direction="ELEVATED",
                                is_corroborating=True,
                                description=f"Model attribution: {feat} increased failure prediction by +{val:.3f} in log-odds margin space"
                            )
                        )
            if relevant_shap_vals:
                # Bounded average of positive attributions
                shap_score = float(np.clip(np.mean(relevant_shap_vals) / 3.0, 0.0, 1.0))

        # 2. Machine-Specific Telemetry Baseline Deviation
        telem_score = 0.0
        telem_deviations = []
        
        # Check Vibration
        if category in [CauseCategory.VIBRATION_DEVIATION, CauseCategory.MECHANICAL_LOAD]:
            vib = event.telemetry.get("vibration_mms")
            if vib is not None:
                base_vib = baseline.get("baseline_vibration_mms", 1.4)
                crit_vib = baseline.get("critical_vibration_mms", 5.5)
                if vib > base_vib:
                    norm_vib = float(np.clip((vib - base_vib) / (crit_vib - base_vib), 0.0, 1.0))
                    telem_deviations.append(norm_vib)
                    supporting_signals.append(
                        SignalEvidenceItem(
                            signal_name="vibration_mms",
                            source=EvidenceSourceType.MACHINE_TELEMETRY,
                            observed_value=float(vib),
                            baseline_value=float(base_vib),
                            normalized_evidence=norm_vib,
                            direction="ELEVATED",
                            is_corroborating=True,
                            description=f"Vibration observed at {vib:.2f} mm/s (baseline: {base_vib:.2f}, critical: {crit_vib:.2f} mm/s)"
                        )
                    )
                else:
                    # Contradiction: Vibration is normal but vibration cause claimed
                    if category == CauseCategory.VIBRATION_DEVIATION:
                        contradictory_signals.append(
                            SignalEvidenceItem(
                                signal_name="vibration_mms",
                                source=EvidenceSourceType.MACHINE_TELEMETRY,
                                observed_value=float(vib),
                                baseline_value=float(base_vib),
                                normalized_evidence=0.0,
                                direction="NOMINAL",
                                is_corroborating=False,
                                is_contradictory=True,
                                description=f"Vibration is completely nominal ({vib:.2f} mm/s), contradicting vibration elevation cause"
                            )
                        )

        # Check Thermal Stress
        if category == CauseCategory.THERMAL_STRESS:
            temp = event.telemetry.get("temperature_c") or event.telemetry.get("process_temperature_k")
            temp_diff = event.telemetry.get("temp_diff_c") or event.telemetry.get("temp_diff_k")
            if temp is not None:
                # Convert K to C if > 250
                temp_c = temp - 273.15 if temp > 250.0 else temp
                base_temp = baseline.get("baseline_temp_c", 35.0)
                if temp_c > base_temp + 5.0:
                    norm_temp = float(np.clip((temp_c - base_temp) / 30.0, 0.0, 1.0))
                    telem_deviations.append(norm_temp)
                    supporting_signals.append(
                        SignalEvidenceItem(
                            signal_name="temperature_c",
                            source=EvidenceSourceType.MACHINE_TELEMETRY,
                            observed_value=float(temp_c),
                            baseline_value=float(base_temp),
                            normalized_evidence=norm_temp,
                            direction="ELEVATED",
                            is_corroborating=True,
                            description=f"Process temperature elevated to {temp_c:.1f} °C (baseline: {base_temp:.1f} °C)"
                        )
                    )
                else:
                    contradictory_signals.append(
                        SignalEvidenceItem(
                            signal_name="temperature_c",
                            source=EvidenceSourceType.MACHINE_TELEMETRY,
                            observed_value=float(temp_c),
                            baseline_value=float(base_temp),
                            normalized_evidence=0.0,
                            direction="NOMINAL",
                            is_corroborating=False,
                            is_contradictory=True,
                            description=f"Process temperature is nominal ({temp_c:.1f} °C), contradicting thermal stress cause"
                        )
                    )

        # Check Mechanical Load (Torque & Power)
        if category == CauseCategory.MECHANICAL_LOAD:
            torque = event.telemetry.get("torque_nm")
            power = event.telemetry.get("power_consumption_kw") or event.telemetry.get("mechanical_power_kw")
            if torque is not None and torque > 45.0:
                norm_torque = float(np.clip((torque - 40.0) / 30.0, 0.0, 1.0))
                telem_deviations.append(norm_torque)
                supporting_signals.append(
                    SignalEvidenceItem(
                        signal_name="torque_nm",
                        source=EvidenceSourceType.MACHINE_TELEMETRY,
                        observed_value=float(torque),
                        baseline_value=40.0,
                        normalized_evidence=norm_torque,
                        direction="ELEVATED",
                        is_corroborating=True,
                        description=f"Spindle torque elevated to {torque:.1f} Nm (nominal band: 30-40 Nm)"
                    )
                )

        # Check Tool Wear
        if category == CauseCategory.TOOL_WEAR:
            wear = event.telemetry.get("tool_wear_min")
            if wear is not None:
                if wear >= 180.0:
                    norm_wear = float(np.clip((wear - 150.0) / 100.0, 0.0, 1.0))
                    telem_deviations.append(norm_wear)
                    supporting_signals.append(
                        SignalEvidenceItem(
                            signal_name="tool_wear_min",
                            source=EvidenceSourceType.MACHINE_TELEMETRY,
                            observed_value=float(wear),
                            baseline_value=0.0,
                            normalized_evidence=norm_wear,
                            direction="ELEVATED",
                            is_corroborating=True,
                            description=f"Accumulated tool cutting time at {wear:.1f} min (wear limit: 200 min)"
                        )
                    )
                elif wear < 40.0:
                    # Direct contradiction: claimed tool wear when tool is freshly changed
                    contradictory_signals.append(
                        SignalEvidenceItem(
                            signal_name="tool_wear_min",
                            source=EvidenceSourceType.MACHINE_TELEMETRY,
                            observed_value=float(wear),
                            baseline_value=0.0,
                            normalized_evidence=0.0,
                            direction="NOMINAL",
                            is_corroborating=False,
                            is_contradictory=True,
                            description=f"Tool wear is minimal ({wear:.1f} min), directly contradicting tool wear failure cause"
                        )
                    )

        if telem_deviations:
            telem_score = float(np.mean(telem_deviations))

        # 3. Anomaly Detection Evidence (Phase 7)
        anomaly_evidence = 0.0
        if event.anomaly_score is not None:
            norm_anom = float(np.clip(event.anomaly_score / (event.anomaly_threshold * 2.0), 0.0, 1.0))
            if category in [CauseCategory.PROCESS_INSTABILITY, CauseCategory.VIBRATION_DEVIATION, CauseCategory.MECHANICAL_LOAD]:
                if event.anomaly_score >= event.anomaly_threshold:
                    anomaly_evidence = norm_anom
                    supporting_signals.append(
                        SignalEvidenceItem(
                            signal_name="anomaly_score",
                            source=EvidenceSourceType.ANOMALY_DETECTION,
                            observed_value=float(event.anomaly_score),
                            baseline_value=float(event.anomaly_threshold),
                            normalized_evidence=norm_anom,
                            direction="ELEVATED",
                            is_corroborating=True,
                            description=f"Phase 7 multi-sensor anomaly score {event.anomaly_score:.4f} exceeds threshold ({event.anomaly_threshold:.4f})"
                        )
                    )
                else:
                    # Low anomaly score is contradictory for severe process instability
                    if category == CauseCategory.PROCESS_INSTABILITY:
                        contradictory_signals.append(
                            SignalEvidenceItem(
                                signal_name="anomaly_score",
                                source=EvidenceSourceType.ANOMALY_DETECTION,
                                observed_value=float(event.anomaly_score),
                                baseline_value=float(event.anomaly_threshold),
                                normalized_evidence=0.0,
                                direction="NOMINAL",
                                is_corroborating=False,
                                is_contradictory=True,
                                description=f"Anomaly score is nominal ({event.anomaly_score:.4f} < {event.anomaly_threshold:.4f}), contradicting instability hypothesis"
                            )
                        )

        # 4. Operational Flow & Cycle Time Evidence (Phase 8)
        ops_score = 0.0
        ops_deviations = []
        nominal_cycle = baseline.get("design_cycle_time_sec", 45.0)
        
        # Cycle time degradation
        if event.cycle_time_sec is not None:
            cycle_ratio = event.cycle_time_sec / nominal_cycle
            if cycle_ratio > 1.10:
                norm_cycle = float(np.clip((cycle_ratio - 1.0) / 0.5, 0.0, 1.0))
                if category in [CauseCategory.CYCLE_TIME_DEGRADATION, CauseCategory.FLOW_CONGESTION, CauseCategory.MECHANICAL_LOAD]:
                    ops_deviations.append(norm_cycle)
                    supporting_signals.append(
                        SignalEvidenceItem(
                            signal_name="cycle_time_sec",
                            source=EvidenceSourceType.OPERATIONAL_FLOW,
                            observed_value=float(event.cycle_time_sec),
                            baseline_value=float(nominal_cycle),
                            normalized_evidence=norm_cycle,
                            direction="ELEVATED",
                            is_corroborating=True,
                            description=f"Cycle time expanded to {event.cycle_time_sec:.1f}s (ratio {cycle_ratio:.2f} vs nominal {nominal_cycle:.1f}s)"
                        )
                    )
            elif category == CauseCategory.CYCLE_TIME_DEGRADATION and cycle_ratio <= 1.05:
                contradictory_signals.append(
                    SignalEvidenceItem(
                        signal_name="cycle_time_sec",
                        source=EvidenceSourceType.OPERATIONAL_FLOW,
                        observed_value=float(event.cycle_time_sec),
                        baseline_value=float(nominal_cycle),
                        normalized_evidence=0.0,
                        direction="NOMINAL",
                        is_corroborating=False,
                        is_contradictory=True,
                        description=f"Cycle time is nominal ({event.cycle_time_sec:.1f}s), contradicting cycle degradation"
                    )
                )

        # Flow congestion / Bottleneck state
        if event.bottleneck_state in ["MODERATE", "CRITICAL"] and category == CauseCategory.FLOW_CONGESTION:
            norm_flow = 0.85 if event.bottleneck_state == "CRITICAL" else 0.50
            ops_deviations.append(norm_flow)
            supporting_signals.append(
                SignalEvidenceItem(
                    signal_name="bottleneck_state",
                    source=EvidenceSourceType.OPERATIONAL_FLOW,
                    observed_value=1.0 if event.bottleneck_state == "CRITICAL" else 0.5,
                    baseline_value=0.0,
                    normalized_evidence=norm_flow,
                    direction="ELEVATED",
                    is_corroborating=True,
                    description=f"Phase 8 flow assessment reports {event.bottleneck_state} bottleneck state"
                )
            )

        if ops_deviations:
            ops_score = float(np.mean(ops_deviations))

        # 5. Contradiction Penalty Calculation
        penalty = 0.0
        if contradictory_signals:
            penalty = float(len(contradictory_signals) * PENALTY_CONTRADICTION)

        # 6. Deterministic Score Composition
        raw_score = (
            WEIGHT_SHAP * shap_score +
            WEIGHT_ANOMALY * anomaly_evidence +
            WEIGHT_TELEMETRY * telem_score +
            WEIGHT_OPERATIONAL * ops_score
        )
        
        # Apply temporal multiplier and contradiction penalty
        composite_score = float(np.clip((raw_score * temporal_multiplier) - penalty, 0.0, 1.0))
        
        return composite_score, supporting_signals, contradictory_signals
