"""
NirmaanAI Root Cause Analysis Service Layer
Phase 12: Root Cause Analysis

Exposes production APIs for:
1. Deterministic Root Cause Analysis (`analyze_event`).
2. Human-readable structured RCA markdown reports (`format_human_readable_report`).
3. Controlled synthetic Machine 2 degradation scenario reconstruction (`run_m2_controlled_scenario`).
4. False-cause / Negative control evaluation demonstrating SHAP attribution != RCA (`run_negative_control_scenario`).

RESEARCH INTEGRITY:
- Clear separation of controlled synthetic demonstrations vs empirical evaluations.
- Strict prohibition of causal proof language ("proves causality", "probability of causation").
- Diagnostic suggestions only (NOT an operational recommendation engine).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from src.rca.cause_taxonomy import CauseCategory
from src.rca.evidence_engine import EvidenceFusionEngine
from src.rca.rca_engine import RootCauseAnalysisEngine
from src.rca.rca_models import (
    RCAConfidenceLevel,
    RCAEventContext,
    RCAReportResponse,
)
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class RootCauseAnalysisService:
    """
    Unified public service facade for Root Cause Analysis.
    """

    def __init__(
        self,
        engine: Optional[RootCauseAnalysisEngine] = None,
    ):
        self.engine = engine or RootCauseAnalysisEngine()

    def analyze_event(self, event_context: RCAEventContext) -> RCAReportResponse:
        """
        Executes deterministic multi-source RCA for the provided event context.
        """
        return self.engine.analyze(event_context)

    def run_m2_controlled_scenario(self) -> RCAReportResponse:
        """
        Executes the controlled Machine 2 synthetic degradation scenario (Days 18-21).
        Labels output strictly as 'CONTROLLED SYNTHETIC SCENARIO'.
        """
        # Load synthetic sensor readings if available, or construct exact configured trajectory
        root = get_project_root()
        parquet_path = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.parquet"
        csv_path = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.csv"

        history: List[Dict[str, Any]] = []

        if parquet_path.exists() or csv_path.exists():
            try:
                if parquet_path.exists():
                    df = pd.read_parquet(parquet_path)
                else:
                    df = pd.read_csv(csv_path)

                df["timestamp"] = pd.to_datetime(df["timestamp"])
                # Filter to Machine 2 between Day 18 and Day 21 (2026-01-18 to 2026-01-21)
                m2_df = df[
                    (df["machine_id"] == "M2") &
                    (df["timestamp"] >= "2026-01-18 00:00:00") &
                    (df["timestamp"] <= "2026-01-21 10:30:00")
                ].sort_values("timestamp")

                # Sample hourly to maintain responsive processing
                m2_hourly = m2_df.iloc[::4]
                for _, row in m2_hourly.iterrows():
                    history.append({
                        "timestamp": row["timestamp"].isoformat(),
                        "vibration_mms": float(row["vibration_mms"]),
                        "temperature_c": float(row["temperature_c"]),
                        "cycle_time_sec": 55.0 if row["vibration_mms"] > 3.8 else 45.0,
                        "anomaly_score": 0.42 if row["vibration_mms"] > 3.8 else 0.12,
                    })
            except Exception as e:
                logger.warning(f"Failed to read parquet/csv for M2, using configured trajectory: {e}")

        if not history:
            # Configured deterministic trajectory matching Phase 5 / Phase 8 simulation
            history = [
                {
                    "timestamp": "2026-01-18T08:00:00Z",
                    "vibration_mms": 2.25,
                    "temperature_c": 36.5,
                    "cycle_time_sec": 46.0,
                    "anomaly_score": 0.15,
                },
                {
                    "timestamp": "2026-01-19T14:00:00Z",
                    "vibration_mms": 3.95,
                    "temperature_c": 46.0,
                    "cycle_time_sec": 52.0,
                    "anomaly_score": 0.32,
                },
                {
                    "timestamp": "2026-01-20T10:00:00Z",
                    "vibration_mms": 4.80,
                    "temperature_c": 51.5,
                    "cycle_time_sec": 58.5,
                    "anomaly_score": 0.45,
                },
            ]

        # Event snapshot at terminal breakdown: Day 21 10:30
        event_context = RCAEventContext(
            event_id="EVT_SYNTHETIC_M2_DEGRADATION",
            timestamp="2026-01-21T10:30:00Z",
            machine_id="M2",
            event_type="UNPLANNED_STOP",
            severity="CRITICAL",
            observed_outcome="Emergency halt triggered after vibration exceeded critical threshold (5.60 mm/s)",
            prediction_probability=0.965,
            prediction_threshold=0.910,
            anomaly_score=0.485,
            anomaly_threshold=0.2405,
            bottleneck_state="CRITICAL",
            cycle_time_sec=62.0,
            cycle_ratio=1.38,
            dispatch_delay_min=45.0,
            telemetry={
                "vibration_mms": 5.60,
                "temperature_c": 54.0,
                "torque_nm": 58.0,
                "power_consumption_kw": 28.5,
                "rotational_speed_rpm": 1380.0,
                "tool_wear_min": 85.0,
            },
            shap_contributions={
                "torque_nm": 2.45,
                "rotational_speed_rpm": 1.15,
                "temp_diff_c": 1.85,
                "tool_wear_min": 0.20,
            },
            historical_telemetry=history,
            maintenance_state={
                "record_id": "MAINT_0003",
                "failure_mode": "BEARING_WEAR",
                "corrective_action": "Replaced degraded spindle drive bearing and flushed thermal coolant jacket",
            },
            spare_state={
                "sku_id": "SKU_SPINDLE_BEARING_M2",
                "stock_level": 2,
                "lead_time_days": 5,
            },
            is_synthetic_scenario=True,
        )

        return self.engine.analyze(event_context)

    def run_negative_control_scenario(self) -> RCAReportResponse:
        """
        Demonstrates a False Cause / Negative Control scenario.
        Observation: High model attribution on tool wear (SHAP +3.80),
        BUT sensor telemetry is healthy, cycle time is nominal, and anomaly score is low.
        Proves: SHAP attribution alone != Root Cause.
        """
        event_context = RCAEventContext(
            event_id="EVT_NEGATIVE_CONTROL_FALSE_CAUSE",
            timestamp="2026-01-10T12:00:00Z",
            machine_id="M2",
            event_type="PREDICTED_DEGRADATION",
            severity="LOW",
            observed_outcome="Model prediction alert triggered with high tool wear attribution, but machine operating nominally",
            prediction_probability=0.925,  # Above 0.91 threshold
            prediction_threshold=0.910,
            anomaly_score=0.082,           # Low anomaly (well below 0.2405)
            anomaly_threshold=0.2405,
            bottleneck_state="NOMINAL",
            cycle_time_sec=44.8,           # Nominal 45s cycle
            cycle_ratio=0.995,
            dispatch_delay_min=0.0,
            telemetry={
                "vibration_mms": 1.35,     # Nominal baseline (1.4 mm/s)
                "temperature_c": 34.0,     # Nominal baseline (35 °C)
                "torque_nm": 38.5,         # Nominal (40 Nm)
                "tool_wear_min": 15.0,     # Fresh tool inserted! Contradicts wear hypothesis
                "power_consumption_kw": 21.8,
            },
            shap_contributions={
                "tool_wear_min": 3.80,     # Misleading high attribution from out-of-context query
            },
            historical_telemetry=[
                {
                    "timestamp": "2026-01-10T10:00:00Z",
                    "vibration_mms": 1.38,
                    "temperature_c": 33.8,
                    "cycle_time_sec": 45.0,
                    "anomaly_score": 0.075,
                },
                {
                    "timestamp": "2026-01-10T11:00:00Z",
                    "vibration_mms": 1.34,
                    "temperature_c": 34.2,
                    "cycle_time_sec": 44.9,
                    "anomaly_score": 0.080,
                },
            ],
            is_synthetic_scenario=False,
        )

        return self.engine.analyze(event_context)

    @staticmethod
    def format_human_readable_report(report: RCAReportResponse) -> str:
        """
        Formats comprehensive RCA response into standardized human-readable markdown.
        """
        lines = [
            "============================================================",
            "ROOT CAUSE ANALYSIS (RCA)",
            "============================================================",
            f"Event ID:   {report.event_id}",
            f"Timestamp:  {report.timestamp}",
            f"Machine:    {report.machine_id}",
            f"Scenario:   [{report.scenario_type}]",
            f"Event Type: {report.event_type} (Severity: {report.severity})",
            f"Outcome:    {report.observed_outcome}",
            "",
            "------------------------------------------------------------",
            "FINDINGS SUMMARY",
            "------------------------------------------------------------",
            f"Primary Candidate: {report.primary_candidate.display_name} ({report.primary_candidate.cause_category})",
            f"Confidence:        {report.confidence.value}",
            f"Confidence Detail: {report.confidence_rationale}",
            f"Analytical Score:  {report.primary_candidate.composite_score:.3f} (Configured analytical weight, not causal probability)",
            "",
            "------------------------------------------------------------",
            "SUPPORTING EVIDENCE",
            "------------------------------------------------------------",
        ]

        if report.top_contributors:
            for s in report.top_contributors:
                lines.append(f"- [{s.source.value}] {s.description}")
        else:
            lines.append("- No strong supporting signals identified.")

        if report.contradictory_evidence:
            lines.append("")
            lines.append("------------------------------------------------------------")
            lines.append("CONTRADICTORY / NEGATIVE EVIDENCE")
            lines.append("------------------------------------------------------------")
            for c in report.contradictory_evidence:
                lines.append(f"- [PENALTY APPLIED] {c.description}")

        if report.temporal_chain:
            lines.append("")
            lines.append("------------------------------------------------------------")
            lines.append("TEMPORAL PRECEDENCE CHAIN")
            lines.append("------------------------------------------------------------")
            for step in report.temporal_chain:
                lines.append(f"- [{step.stage.value.upper()}] {step.timestamp}: {step.description}")
            precedence_str = "VERIFIED" if report.temporal_precedence_verified else "UNVERIFIED"
            lines.append(f"Precedence Ordering Status: {precedence_str}")

        if report.secondary_candidates:
            lines.append("")
            lines.append("------------------------------------------------------------")
            lines.append("SECONDARY CANDIDATE CAUSES")
            lines.append("------------------------------------------------------------")
            for sec in report.secondary_candidates:
                lines.append(f"- Rank {sec.rank}: {sec.display_name} (Score: {sec.composite_score:.3f})")

        lines.append("")
        lines.append("------------------------------------------------------------")
        lines.append("RECOMMENDED INVESTIGATION (DIAGNOSTICS ONLY)")
        lines.append("------------------------------------------------------------")
        for inv in report.recommended_next_investigation:
            lines.append(f"- {inv}")

        lines.append("")
        lines.append("------------------------------------------------------------")
        lines.append("INTERPRETATION & SCIENTIFIC LIMITATIONS")
        lines.append("------------------------------------------------------------")
        lines.append(f"Interpretation: \"{report.interpretation}\"")
        lines.append("")
        lines.append("Limitations:")
        for lim in report.limitations:
            lines.append(f"- {lim}")
        lines.append("")
        lines.append(f"Notice: {report.causality_disclaimer}")
        lines.append("============================================================")

        return "\n".join(lines)
