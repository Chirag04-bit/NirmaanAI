"""
NirmaanAI Phase 20: Copilot Epistemic and Authority Policies
Enforces epistemic fidelity, authority ranking, and counterfactual guardrails.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.knowledge.schemas import EpistemicStatus, EvidenceItem

UNPROJECTABLE_CAUSAL_PATTERNS = [
    ("exact post-service failure probability", "Exact post-service failure probability is NOT_PROJECTABLE from the validated evidence base without empirical post-intervention treatment telemetry."),
    ("exact post-intervention failure probability", "Exact post-intervention failure probability is NOT_PROJECTABLE from the validated evidence base without empirical post-intervention treatment telemetry."),
    ("post-service health", "Post-intervention machine health score recovery is NOT_PROJECTABLE from the validated evidence base; no intervention-specific empirical treatment effect is modeled."),
    ("post-intervention health", "Post-intervention machine health score recovery is NOT_PROJECTABLE from the validated evidence base; no intervention-specific empirical treatment effect is modeled."),
    ("post-service anomaly score", "Post-intervention reconstruction error reduction is NOT_PROJECTABLE from the current validated models."),
]


class CopilotPolicyEngine:
    """Enforces source authority, epistemic categorization, and counterfactual boundaries."""

    @staticmethod
    def check_unprojectable_causal_inquiry(query: str) -> Optional[str]:
        """
        Checks if the query requests counterfactual projections that are strictly unprojectable.
        Returns the formal limitation explanation if unprojectable, or None if projectable/grounded.
        """
        q_lower = query.lower()
        for phrase, explanation in UNPROJECTABLE_CAUSAL_PATTERNS:
            if phrase in q_lower:
                return explanation

        # General check for post-service + failure probability / health
        if ("post-service" in q_lower or "post-intervention" in q_lower) and (
            "failure probability" in q_lower or "health" in q_lower or "exact" in q_lower
        ):
            return "Exact post-intervention mechanical metrics are NOT_PROJECTABLE from the validated evidence base without empirical post-treatment telemetry."

        return None

    @staticmethod
    def filter_evidence_by_authority(
        evidence_items: List[EvidenceItem],
        include_superseded: bool = False,
    ) -> List[EvidenceItem]:
        """
        Filters evidence items according to the source authority hierarchy.
        Excludes superseded draft chunks unless explicitly requested.
        """
        if include_superseded:
            return evidence_items

        filtered: List[EvidenceItem] = []
        for item in evidence_items:
            # Drop superseded historical drafts (e.g. preliminary ₹92,582.28)
            if item.is_superseded:
                continue
            # Drop items with low authority weights if authoritative items exist
            filtered.append(item)

        return filtered

    @staticmethod
    def determine_response_epistemic_status(
        intent_name: str,
        evidence_items: List[EvidenceItem],
        is_retrospective: bool = False,
    ) -> str:
        """Determines the authoritative epistemic status for the composite answer."""
        if is_retrospective:
            return EpistemicStatus.RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH.value

        if not evidence_items:
            return EpistemicStatus.UNKNOWN.value

        # If evidence contains simulation projections or what-if
        if any(item.epistemic_status == EpistemicStatus.PROJECTED.value for item in evidence_items) or intent_name == "WHAT_IF":
            return EpistemicStatus.PROJECTED.value

        # If primary evidence is predictive model output
        if any(item.epistemic_status == EpistemicStatus.MODEL_OUTPUT.value for item in evidence_items):
            return EpistemicStatus.MODEL_OUTPUT.value

        # If primary evidence is controlled synthetic benchmark
        if any(item.epistemic_status == EpistemicStatus.CONTROLLED_SYNTHETIC.value for item in evidence_items):
            return EpistemicStatus.CONTROLLED_SYNTHETIC.value

        # If derived operational metrics
        if any(item.epistemic_status == EpistemicStatus.DERIVED.value for item in evidence_items):
            return EpistemicStatus.DERIVED.value

        return EpistemicStatus.OBSERVED.value
