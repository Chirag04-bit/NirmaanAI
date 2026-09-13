"""
NirmaanAI Phase 19: Retrieval Filters & Temporal Guardrails
Enforces temporal decision boundary (DECISION_CUTOFF), machine scoping,
and epistemic status isolation.
"""

from typing import List, Optional
from src.knowledge.registry import DECISION_CUTOFF
from src.knowledge.schemas import DocumentChunk


class RetrievalFilters:
    """Evaluates candidate chunks against operational and epistemic filter constraints."""

    @staticmethod
    def apply_filters(
        chunks: List[DocumentChunk],
        machine_id: Optional[str] = None,
        phase: Optional[int] = None,
        phases: Optional[List[int]] = None,
        include_retrospective: bool = False,
        exclude_superseded: bool = True,
        allowed_epistemic_statuses: Optional[List[str]] = None,
    ) -> List[int]:
        """
        Returns the indices of candidate chunks that satisfy all filter predicates.
        """
        matching_indices: List[int] = []

        for idx, c in enumerate(chunks):
            # 1. Temporal Decision Boundary Filter
            # Default prospective queries MUST exclude post-cutoff retrospective ground truth (MAINT_0003)
            if not include_retrospective:
                if not c.is_decision_input:
                    continue
                if c.as_of_timestamp and c.as_of_timestamp > DECISION_CUTOFF:
                    continue

            # 2. Machine Filter
            if machine_id:
                # If query targets specific machine (e.g. M2), match chunks for M2 or fleet-wide (None)
                if c.machine_id is not None and c.machine_id != machine_id:
                    continue

            # 3. Phase Filter
            if phase is not None and c.phase != phase:
                continue
            if phases is not None and c.phase not in phases:
                continue

            # 4. Superseded / Obsolete Filter
            if exclude_superseded and c.is_superseded:
                continue

            # 5. Epistemic Status Filter
            if allowed_epistemic_statuses is not None:
                if c.epistemic_status not in allowed_epistemic_statuses:
                    continue

            matching_indices.append(idx)

        return matching_indices
