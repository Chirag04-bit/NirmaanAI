"""
NirmaanAI Root Cause Analysis (RCA) — Temporal Precedence Engine
Phase 12: Root Cause Analysis

Reconstructs the chronological progression of an observed event:
t0 = first meaningful precursor (e.g. vibration elevation)
t1 = escalation (e.g. thermal buildup / rising anomaly)
t2 = operational consequence (e.g. cycle time degradation, queue accumulation)
t3 = terminal event (e.g. failure threshold breach, emergency shutdown)

LEAKAGE PREVENTION:
- Strictly excludes any telemetry or events occurring after the event timestamp (t > t_event).
- Verifies causal ordering so consequences cannot be presented as causes of preceding events.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.rca.rca_models import TemporalStage, TemporalStep


def parse_timestamp(ts: Any) -> datetime:
    """Parses timestamp into UTC datetime."""
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts
    if isinstance(ts, str):
        # Handle ISO strings with Z or timezone offset
        clean_ts = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_ts)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    raise ValueError(f"Unsupported timestamp type: {type(ts)}")


class TemporalPrecedenceEngine:
    """
    Evaluates temporal sequence of precursors, escalations, and consequences
    leading up to an operational event without lookahead leakage.
    """

    @staticmethod
    def filter_causal_history(
        history: List[Dict[str, Any]],
        event_timestamp: str
    ) -> List[Dict[str, Any]]:
        """
        Enforces strict causal filtering: rejects any observations where t > event_timestamp.
        Sorts remaining observations in ascending chronological order.
        """
        event_dt = parse_timestamp(event_timestamp)
        causal_records = []
        for record in history:
            ts = parse_timestamp(record.get("timestamp"))
            if ts <= event_dt:
                causal_records.append(record)
        
        causal_records.sort(key=lambda r: parse_timestamp(r.get("timestamp")))
        return causal_records

    @classmethod
    def reconstruct_sequence(
        cls,
        history: List[Dict[str, Any]],
        event_timestamp: str,
        machine_baseline_vib: float = 1.4,
        alert_vib: float = 3.8,
        nominal_cycle_sec: float = 45.0,
    ) -> Tuple[List[TemporalStep], bool, float]:
        """
        Reconstructs the chronological progression [t0, t1, t2, t3].
        
        Returns:
            (steps, precedence_verified, temporal_score)
        """
        valid_history = cls.filter_causal_history(history, event_timestamp)
        event_dt = parse_timestamp(event_timestamp)
        
        steps: List[TemporalStep] = []
        t0_step: Optional[TemporalStep] = None
        t1_step: Optional[TemporalStep] = None
        t2_step: Optional[TemporalStep] = None
        
        # 1. Search for t0: Earliest significant precursor (vibration elevation > baseline + 30%)
        for r in valid_history:
            vib = float(r.get("vibration_mms", 0.0))
            if vib >= machine_baseline_vib * 1.3:
                t0_step = TemporalStep(
                    stage=TemporalStage.T0_PRECURSOR,
                    timestamp=str(r.get("timestamp")),
                    signal_name="vibration_mms",
                    observed_value=vib,
                    description=f"Initial vibration deviation detected ({vib:.2f} mm/s vs baseline {machine_baseline_vib:.2f} mm/s)"
                )
                break
        
        # 2. Search for t1: Escalation (vibration alert threshold breach >= alert_vib, thermal buildup >= 48C, or anomaly excursion >= 0.24)
        if t0_step is not None:
            t0_dt = parse_timestamp(t0_step.timestamp)
            for r in valid_history:
                r_dt = parse_timestamp(r.get("timestamp"))
                if r_dt > t0_dt:
                    vib = float(r.get("vibration_mms", 0.0))
                    temp = float(r.get("temperature_c", 0.0))
                    anom = float(r.get("anomaly_score", 0.0))
                    if vib >= alert_vib or (vib >= machine_baseline_vib * 1.5 and temp >= 48.0) or anom >= 0.2405:
                        t1_step = TemporalStep(
                            stage=TemporalStage.T1_ESCALATION,
                            timestamp=str(r.get("timestamp")),
                            signal_name="vibration_or_temperature",
                            observed_value=vib if vib >= alert_vib else temp,
                            description=f"Physical degradation escalation (vib={vib:.2f} mm/s, temp={temp:.1f} °C, anomaly={anom:.3f})"
                        )
                        break

        # 3. Search for t2: Operational consequence (cycle time expansion, queue delay) occurring after t1 (or t0)
        after_dt = parse_timestamp(t1_step.timestamp) if t1_step is not None else (parse_timestamp(t0_step.timestamp) if t0_step is not None else None)
        for r in valid_history:
            cycle = float(r.get("cycle_time_sec", 0.0))
            delay = float(r.get("dispatch_delay_min", 0.0))
            if cycle >= nominal_cycle_sec * 1.15 or delay >= 15.0:
                r_dt = parse_timestamp(r.get("timestamp"))
                if after_dt is None or r_dt >= after_dt:
                    t2_step = TemporalStep(
                        stage=TemporalStage.T2_CONSEQUENCE,
                        timestamp=str(r.get("timestamp")),
                        signal_name="cycle_time_sec",
                        observed_value=cycle if cycle > 0 else delay,
                        description=f"Operational consequence observed: cycle expansion to {cycle:.1f}s or dispatch delay {delay:.1f}min"
                    )
                    break

        # 4. Step t3: Terminal Event (at event_timestamp)
        t3_step = TemporalStep(
            stage=TemporalStage.T3_EVENT,
            timestamp=str(event_timestamp),
            signal_name="event_trigger",
            observed_value=1.0,
            description=f"Event triggered at {event_timestamp}: emergency halt or failure prediction breach"
        )
        
        # Assemble ordered chain
        if t0_step:
            steps.append(t0_step)
        if t1_step:
            steps.append(t1_step)
        if t2_step:
            steps.append(t2_step)
        steps.append(t3_step)
        
        # Verify precedence ordering
        precedence_verified = False
        temporal_score = 0.50  # Default neutral score
        
        if len(steps) >= 3 and t0_step is not None:
            # Check strict monotonic timestamp ordering
            dts = [parse_timestamp(s.timestamp) for s in steps]
            if all(dts[i] <= dts[i+1] for i in range(len(dts)-1)):
                precedence_verified = True
                temporal_score = 1.0
            else:
                precedence_verified = False
                temporal_score = 0.30
        elif len(steps) == 2 and t0_step is not None:
            # Only t0 and t3
            if parse_timestamp(t0_step.timestamp) <= event_dt:
                precedence_verified = True
                temporal_score = 0.85
        elif len(valid_history) == 0:
            # No prior history available
            precedence_verified = False
            temporal_score = 0.60
            
        return steps, precedence_verified, temporal_score
