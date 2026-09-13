"""
NirmaanAI Phase 20: Copilot Temporal Governance
Enforces the locked temporal decision boundary and isolates retrospective synthetic ground truth.
"""

from datetime import datetime, timezone
import re
from typing import Dict, Optional, Tuple

from src.knowledge.registry import DECISION_CUTOFF

RETROSPECTIVE_EVENT_ID = "MAINT_0003"
RETROSPECTIVE_EVENT_TIMESTAMP = "2026-01-22T16:30:00Z"


class TemporalInterpreter:
    """Interprets temporal qualifiers and enforces prospective decision isolation."""

    @staticmethod
    def get_decision_cutoff() -> str:
        """Returns the ISO-8601 string for the authoritative decision cutoff."""
        return str(DECISION_CUTOFF)

    @staticmethod
    def is_retrospective_intent(query: str) -> bool:
        """
        Detects whether the user is explicitly requesting historical / retrospective / post-cutoff events.
        """
        patterns = [
            r"\bretrospective\b",
            r"\bmaint_0003\b",
            r"\bday\s*22\b",
            r"\bpost[- ]cutoff\b",
            r"\bhistorical halt\b",
            r"\bactual emergency halt\b",
            r"\bground truth event\b",
        ]
        q_lower = query.lower()
        for pat in patterns:
            if re.search(pat, q_lower):
                return True
        return False

    @staticmethod
    def is_temporal_boundary_question(query: str) -> bool:
        """
        Detects whether the query specifically interrogates the temporal boundary status
        of MAINT_0003 or post-cutoff evidence (e.g. TQ1: 'Was MAINT_0003 part of the prospective decision evidence?').
        """
        q_lower = query.lower()
        has_maint3 = "maint_0003" in q_lower or "maint-0003" in q_lower or "day 22" in q_lower
        has_boundary_word = (
            "prospective" in q_lower
            or "decision evidence" in q_lower
            or "cutoff" in q_lower
            or "boundary" in q_lower
            or "available at decision" in q_lower
            or "part of" in q_lower
        )
        return has_maint3 and has_boundary_word

    @classmethod
    def resolve_temporal_policy(
        cls,
        query: str,
        context_include_retrospective: bool = False,
    ) -> Tuple[bool, bool, Dict[str, str]]:
        """
        Resolves temporal retrieval policy:
        Returns: (include_retrospective, is_boundary_question, filter_metadata)
        """
        is_retrospective_query = cls.is_retrospective_intent(query)
        is_boundary_q = cls.is_temporal_boundary_question(query)

        # Allow retrospective retrieval if explicitly asked in query or context
        include_retro = context_include_retrospective or is_retrospective_query

        filter_meta = {
            "decision_cutoff": cls.get_decision_cutoff(),
            "include_retrospective": str(include_retro),
            "is_retrospective_intent": str(is_retrospective_query),
            "is_boundary_inquiry": str(is_boundary_q),
        }

        return include_retro, is_boundary_q, filter_meta
