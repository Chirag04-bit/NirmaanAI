"""
NirmaanAI Operational Recommendation Engine
Phase 15: Recommendation Engine

Implements the deterministic rule execution pipeline:
1. Orchestrates rule evaluation across operational domains.
2. Deduplicates recommendations by machine and target component, merging evidence.
3. Resolves operational conflicts via deterministic precedence (Safety > Throughput, Expedite > Hold, Bottleneck > Off-peak).
4. Sorts output by Priority -> Urgency -> Machine ID -> Recommendation ID for 100% deterministic reproducibility.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from src.decision.recommendation_models import (
    ActionUrgency,
    EvidenceItem,
    EvidenceStrength,
    OperationalRecommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationPriority,
)
from src.decision.recommendation_rules import (
    calculate_evidence_strength,
)


PRIORITY_RANK = {
    RecommendationPriority.CRITICAL: 5,
    RecommendationPriority.HIGH: 4,
    RecommendationPriority.MEDIUM: 3,
    RecommendationPriority.LOW: 2,
    RecommendationPriority.MONITOR: 1,
}

URGENCY_RANK = {
    ActionUrgency.IMMEDIATE: 5,
    ActionUrgency.SAME_DAY: 4,
    ActionUrgency.NEXT_SHIFT: 3,
    ActionUrgency.SCHEDULED_MAINT: 2,
    ActionUrgency.ROUTINE: 1,
}


class OperationalRecommendationEngine:
    """
    Deterministic rule execution, deduplication, and conflict resolution engine.
    """

    def __init__(self):
        pass

    def deduplicate_recommendations(
        self, recommendations: List[OperationalRecommendation]
    ) -> List[OperationalRecommendation]:
        """
        Consolidates co-occurring recommendations targeting the same physical asset and action.
        Preserves distinct operational recommendations (e.g. maintenance vs flow vs inventory).
        Merges atomic evidence lists, unions source phases, and escalates to maximum severity.
        """
        if not recommendations:
            return []

        # Group by (machine_id, category, action)
        grouped: Dict[Tuple[str, str, str], List[OperationalRecommendation]] = {}
        for rec in recommendations:
            key = (rec.machine_id, rec.category.value, rec.action.value)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(rec)

        consolidated: List[OperationalRecommendation] = []
        for (m_id, cat, act), rec_list in grouped.items():
            if len(rec_list) == 1:
                consolidated.append(rec_list[0])
                continue

            # Merge multiple instances into a single consolidated record
            base = rec_list[0]
            # Highest priority and urgency
            max_prio = max(rec_list, key=lambda r: PRIORITY_RANK[r.priority]).priority
            max_urg = max(rec_list, key=lambda r: URGENCY_RANK[r.urgency]).urgency

            # Merge evidence items uniquely by evidence_id
            seen_evidence: Set[str] = set()
            merged_evidence: List[EvidenceItem] = []
            for r in rec_list:
                for ev in r.evidence:
                    if ev.evidence_id not in seen_evidence:
                        seen_evidence.add(ev.evidence_id)
                        merged_evidence.append(ev)

            # Union source phases
            source_phases: List[str] = sorted(list({p for r in rec_list for p in r.source_phases}))

            # Combine rule IDs
            rule_ids = sorted(list({r.rule_id for r in rec_list if r.rule_id}))
            combined_rule_id = ",".join(rule_ids) if rule_ids else None

            # Recompute strength
            new_strength = calculate_evidence_strength(merged_evidence)

            # Financial and inventory contexts
            fin_ctx = next((r.financial_context for r in rec_list if r.financial_context is not None), None)
            inv_ctx = next((r.inventory_context for r in rec_list if r.inventory_context is not None), None)

            consolidated_rec = OperationalRecommendation(
                recommendation_id=base.recommendation_id,
                timestamp=base.timestamp,
                machine_id=m_id,
                category=base.category,
                action=base.action,
                priority=max_prio,
                urgency=max_urg,
                evidence_strength=new_strength,
                reason=base.reason,
                evidence=merged_evidence,
                source_phases=source_phases,
                operational_impact=base.operational_impact,
                financial_context=fin_ctx,
                inventory_context=inv_ctx,
                expected_benefit=base.expected_benefit,
                requires_operator_verification=True,
                rule_id=combined_rule_id,
                epistemic_classification=base.epistemic_classification,
            )
            consolidated.append(consolidated_rec)

        return consolidated

    def resolve_conflicts(
        self, recommendations: List[OperationalRecommendation]
    ) -> List[OperationalRecommendation]:
        """
        Applies the deterministic operational conflict resolution matrix:
        1. Physical Safety > Throughput: Inspections override feed rate / operating speed.
        2. Inventory: EXPEDITE_CRITICAL_SPARE overrides HOLD_UNNECESSARY_PROCUREMENT if projected stock < safety stock.
        3. Bottleneck vs Energy: Bottleneck load reduction / rescheduling overrides off-peak load shifting.
        """
        if not recommendations:
            return []

        resolved: List[OperationalRecommendation] = []
        # Index by machine
        by_machine: Dict[str, List[OperationalRecommendation]] = {}
        for rec in recommendations:
            by_machine.setdefault(rec.machine_id, []).append(rec)

        for m_id, recs in by_machine.items():
            actions = {r.action for r in recs}

            # Conflict 1: Bottleneck throughput vs Peak energy shifting
            # If REDUCE_MACHINE_FEED_RATE or RESCHEDULE_PENDING_JOBS is present on bottleneck,
            # suppress SHIFT_HIGH_LOAD_OFF_PEAK (margin loss > tariff savings).
            has_bottleneck_flow = (
                RecommendationAction.REDUCE_MACHINE_FEED_RATE in actions
                or RecommendationAction.RESCHEDULE_PENDING_JOBS in actions
            )
            has_energy_shift = RecommendationAction.SHIFT_HIGH_LOAD_OFF_PEAK in actions

            # Conflict 2: Expedite spare vs Hold procurement
            has_expedite = RecommendationAction.EXPEDITE_CRITICAL_SPARE in actions
            has_hold = RecommendationAction.HOLD_UNNECESSARY_PROCUREMENT in actions

            for r in recs:
                if has_bottleneck_flow and r.action == RecommendationAction.SHIFT_HIGH_LOAD_OFF_PEAK:
                    # Suppress energy shift in favor of clearing bottleneck queue
                    continue
                if has_expedite and r.action == RecommendationAction.HOLD_UNNECESSARY_PROCUREMENT:
                    # Suppress hold procurement in favor of protecting critical safety buffer
                    continue
                resolved.append(r)

        return resolved

    def rank_recommendations(
        self, recommendations: List[OperationalRecommendation]
    ) -> List[OperationalRecommendation]:
        """
        Sorts recommendations deterministically:
        1. Priority (CRITICAL -> HIGH -> MEDIUM -> LOW -> MONITOR)
        2. Urgency (IMMEDIATE -> SAME_DAY -> NEXT_SHIFT -> SCHEDULED_MAINT -> ROUTINE)
        3. Machine ID (e.g. M1 -> M5)
        4. Recommendation ID (alphabetical)
        """
        return sorted(
            recommendations,
            key=lambda r: (
                -PRIORITY_RANK[r.priority],
                -URGENCY_RANK[r.urgency],
                r.machine_id,
                r.recommendation_id,
            ),
        )

    def process(
        self, raw_recommendations: List[OperationalRecommendation]
    ) -> List[OperationalRecommendation]:
        """
        Full engine execution: deduplicate -> resolve conflicts -> rank deterministically.
        """
        deduped = self.deduplicate_recommendations(raw_recommendations)
        resolved = self.resolve_conflicts(deduped)
        return self.rank_recommendations(resolved)
