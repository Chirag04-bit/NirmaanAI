"""
NirmaanAI Root Cause Analysis Evaluation Pipeline
Phase 12: Root Cause Analysis

Executes:
1. Controlled Machine 2 synthetic degradation episode reconstruction (Days 18-21).
2. False-Cause / Negative Control scenario evaluation (demonstrating SHAP attribution != RCA).
3. Deterministic verification and persistence of evaluation artifacts to models/rca/rca_summary.json.

RESEARCH INTEGRITY:
- Clear separation between controlled synthetic scenario and empirical benchmark.
- Strictly adheres to scientific causality disclosures and bounds.
"""

import json
from pathlib import Path
from src.rca.rca_service import RootCauseAnalysisService
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


def run_rca_evaluation():
    """Runs RCA pipeline evaluation and serializes results."""
    root = get_project_root()
    output_dir = root / "models" / "rca"
    output_dir.mkdir(parents=True, exist_ok=True)

    service = RootCauseAnalysisService()

    logger.info("Running Controlled Machine 2 Synthetic Degradation Scenario...")
    m2_result = service.run_m2_controlled_scenario()
    logger.info(f"Machine 2 Primary Candidate: {m2_result.primary_candidate.display_name} (Confidence: {m2_result.confidence.value})")

    logger.info("Running Negative Control Scenario (Isolated SHAP attribution)...")
    neg_result = service.run_negative_control_scenario()
    logger.info(f"Negative Control Primary Candidate: {neg_result.primary_candidate.display_name} (Confidence: {neg_result.confidence.value})")

    summary_payload = {
        "phase": "Phase 12: Root Cause Analysis",
        "m2_controlled_scenario": {
            "event_id": m2_result.event_id,
            "scenario_type": m2_result.scenario_type,
            "primary_candidate": m2_result.primary_candidate.cause_category,
            "display_name": m2_result.primary_candidate.display_name,
            "composite_score": m2_result.primary_candidate.composite_score,
            "confidence": m2_result.confidence.value,
            "temporal_precedence_verified": m2_result.temporal_precedence_verified,
            "steps_count": len(m2_result.temporal_chain),
            "top_contributors_count": len(m2_result.top_contributors),
            "interpretation": m2_result.interpretation,
        },
        "negative_control_scenario": {
            "event_id": neg_result.event_id,
            "scenario_type": neg_result.scenario_type,
            "primary_candidate": neg_result.primary_candidate.cause_category,
            "composite_score": neg_result.primary_candidate.composite_score,
            "confidence": neg_result.confidence.value,
            "has_contradictions": len(neg_result.contradictory_evidence) > 0,
            "interpretation": neg_result.interpretation,
        },
        "taxonomy_categories_count": 13,
        "causality_disclaimer": m2_result.causality_disclaimer,
    }

    summary_path = output_dir / "rca_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    logger.info(f"RCA evaluation summary successfully written to {summary_path}")

    # Generate human readable report snippet
    human_report = service.format_human_readable_report(m2_result)
    print("\n" + human_report + "\n")
    return summary_payload


if __name__ == "__main__":
    run_rca_evaluation()
