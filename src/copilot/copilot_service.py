"""
NirmaanAI Phase 20: AI Factory Copilot Service
Core service engine coordinating intent classification, entity extraction,
temporal/epistemic policies, Phase 19 retrieval, and grounded answer synthesis.
"""

from typing import Any, Dict, Optional

from src.copilot.composer import GroundedAnswerComposer
from src.copilot.entities import EntityExtractor
from src.copilot.intent import IntentClassifier
from src.copilot.policies import CopilotPolicyEngine
from src.copilot.schemas import CopilotContext, CopilotIntent, CopilotResponse, CopilotStatus
from src.copilot.temporal import TemporalInterpreter
from src.knowledge.indexing.index_manager import KnowledgeIndexManager
from src.knowledge.retrieval.retriever import KnowledgeRetriever


class FactoryCopilotService:
    """
    Production service interface for the Grounded AI Factory Copilot.
    Translates natural-language operational inquiries into verified, evidence-backed answers.
    """

    def __init__(self, retriever: Optional[KnowledgeRetriever] = None):
        if retriever is None:
            manager = KnowledgeIndexManager()
            if not manager.is_built():
                vector_store, embedder = manager.build_index()
            else:
                vector_store, embedder = manager.load()
            self.retriever = KnowledgeRetriever(vector_store, embedder)
        else:
            self.retriever = retriever

    def ask(self, query: str, context: Optional[CopilotContext] = None) -> CopilotResponse:
        """
        Executes end-to-end grounded query answering.
        Guarantees:
        - Rejection of non-existent machines/factories.
        - Zero prospective temporal leakage of retrospective events.
        - Enforcement of NOT_PROJECTABLE counterfactual guardrails.
        - Surface of authoritative Phase 14 financials over superseded drafts.
        - Traceable provenance citations across all substantive answers.
        """
        if context is None:
            context = CopilotContext()

        query_clean = query.strip()
        if not query_clean:
            return CopilotResponse(
                query=query,
                intent=CopilotIntent.UNSUPPORTED_QUERY,
                status=CopilotStatus.NO_SUFFICIENT_EVIDENCE,
                answer="NO_SUFFICIENT_EVIDENCE: Empty query received.",
                confidence="NO_EVIDENCE",
                rejection_reason="Empty query string.",
            )

        # 1. Entity Extraction & Plant Topology Validation
        entities = EntityExtractor.extract_all(query_clean)
        if entities["has_invalid_entities"]:
            return GroundedAnswerComposer.compose(
                query=query_clean,
                intent=CopilotIntent.UNSUPPORTED_QUERY,
                entities=entities,
                evidence=[],
                filters_applied={"context": context.model_dump()},
                rejection_reason=(
                    f"Query references uncataloged asset or factory topology: "
                    f"invalid_machines={entities['invalid_machines']}, invalid_factories={entities['invalid_factories']}."
                ),
            )

        # Allow context machine_id to populate primary_machine if not in query
        if not entities["primary_machine"] and context.machine_id:
            entities["primary_machine"] = context.machine_id

        # 2. Intent Classification
        intent = IntentClassifier.classify(query_clean)
        if intent == CopilotIntent.UNSUPPORTED_QUERY:
            return GroundedAnswerComposer.compose(
                query=query_clean,
                intent=intent,
                entities=entities,
                evidence=[],
                filters_applied={"context": context.model_dump()},
                rejection_reason="Query targets an out-of-scope domain or unapproved external subject.",
            )

        # 3. Unprojectable Counterfactual / Causal Guardrail
        unprojectable_limitation = CopilotPolicyEngine.check_unprojectable_causal_inquiry(query_clean)
        if unprojectable_limitation:
            return GroundedAnswerComposer.compose(
                query=query_clean,
                intent=intent,
                entities=entities,
                evidence=[],
                filters_applied={"context": context.model_dump()},
                unprojectable_limitation=unprojectable_limitation,
            )

        # 4. Temporal Policy Interpretation
        include_retro, is_boundary_q, temporal_meta = TemporalInterpreter.resolve_temporal_policy(
            query=query_clean,
            context_include_retrospective=context.include_retrospective,
        )

        # 5. Phase 19 Grounded Retrieval
        retrieval_res = self.retriever.retrieve(
            query=query_clean,
            top_k=5,
            machine_id=entities["primary_machine"],
            include_retrospective=include_retro,
            exclude_superseded=not context.include_superseded,
        )

        filters_applied = {
            **temporal_meta,
            "machine_filter": entities["primary_machine"],
            "include_superseded": str(context.include_superseded),
            "retriever_filters": retrieval_res.filters_applied,
        }

        # 6. Check for Retrieval Rejection
        if retrieval_res.status == "NO_SUFFICIENT_EVIDENCE" and not is_boundary_q:
            return GroundedAnswerComposer.compose(
                query=query_clean,
                intent=intent,
                entities=entities,
                evidence=[],
                filters_applied=filters_applied,
                rejection_reason=retrieval_res.rejection_reason or "No matching evidence items met confidence threshold.",
            )

        # 7. Apply Source Authority Filtering
        authoritative_evidence = CopilotPolicyEngine.filter_evidence_by_authority(
            retrieval_res.items,
            include_superseded=context.include_superseded,
        )

        # 8. Grounded Answer Synthesis
        return GroundedAnswerComposer.compose(
            query=query_clean,
            intent=intent,
            entities=entities,
            evidence=authoritative_evidence,
            filters_applied=filters_applied,
            is_retrospective=include_retro,
            is_boundary_inquiry=is_boundary_q,
            rejection_reason=None,
        )
