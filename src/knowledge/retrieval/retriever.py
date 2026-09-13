"""
NirmaanAI Phase 19: Knowledge Retriever
Coordinates hybrid dense/keyword retrieval, source authority weighting,
temporal boundaries, and anti-hallucination rejection.
"""

import re
import time
from typing import Any, Dict, List, Optional

import numpy as np

from src.knowledge.embeddings.dense_embedder import TfidfSvdDenseRepresentation
from src.knowledge.indexing.vector_store import NumpyVectorStore
from src.knowledge.retrieval.filters import RetrievalFilters
from src.knowledge.schemas import EvidenceItem, RetrievalResult

# Initial heuristic retrieval rejection threshold — not statistically validated
INITIAL_HEURISTIC_THRESHOLD = 0.25
MIN_KEYWORD_ANCHOR_SCORE = 0.40
KNOWN_MACHINES = {"M1", "M2", "M3", "M4", "M5"}
KNOWN_FACTORIES = {"FAC_01"}


class KnowledgeRetriever:
    """
    Executes hybrid retrieval over the Factory Knowledge Store with source-authority weighting,
    temporal filtering, and strict anti-hallucination checks.
    """

    def __init__(
        self,
        vector_store: NumpyVectorStore,
        embedder: TfidfSvdDenseRepresentation,
        rejection_threshold: float = INITIAL_HEURISTIC_THRESHOLD,
        min_keyword_score: float = MIN_KEYWORD_ANCHOR_SCORE,
        dense_weight: float = 0.70,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.rejection_threshold = rejection_threshold
        self.min_keyword_score = min_keyword_score
        self.dense_weight = dense_weight
        self.keyword_weight = 1.0 - dense_weight

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        machine_id: Optional[str] = None,
        phase: Optional[int] = None,
        include_retrospective: bool = False,
        exclude_superseded: bool = True,
        allowed_epistemic_statuses: Optional[List[str]] = None,
    ) -> RetrievalResult:
        """
        Retrieves grounded evidence items for a given user query.
        Returns NO_SUFFICIENT_EVIDENCE if confidence is below threshold or query targets unknown entities.
        """
        start_time = time.perf_counter()

        # 1. Anti-hallucination check: Unknown machine entity
        extracted_machine = self._extract_machine_entity(query)
        if extracted_machine and extracted_machine not in KNOWN_MACHINES:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return RetrievalResult(
                query=query,
                status="NO_SUFFICIENT_EVIDENCE",
                items=[],
                total_found=0,
                retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
                execution_time_ms=round(elapsed_ms, 2),
                filters_applied={"machine_id": extracted_machine},
                rejection_reason=f"Query references unknown machine entity '{extracted_machine}' not present in plant topology.",
            )

        # 2. Anti-hallucination check: Unknown factory entity
        extracted_factory = self._extract_factory_entity(query)
        if extracted_factory and extracted_factory not in KNOWN_FACTORIES:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return RetrievalResult(
                query=query,
                status="NO_SUFFICIENT_EVIDENCE",
                items=[],
                total_found=0,
                retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
                execution_time_ms=round(elapsed_ms, 2),
                filters_applied={"factory_id": extracted_factory},
                rejection_reason=f"Query references unknown factory entity '{extracted_factory}' not present in plant topology.",
            )

        # 3. Anti-hallucination check: Unsupported causal diagnostic projection
        query_lower = query.lower()
        if (
            ("exact" in query_lower or "predicted" in query_lower or "projected" in query_lower)
            and ("post-service" in query_lower or "post-intervention" in query_lower)
            and ("failure probability" in query_lower or "health" in query_lower or "anomaly" in query_lower)
        ):
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return RetrievalResult(
                query=query,
                status="NO_SUFFICIENT_EVIDENCE",
                items=[],
                total_found=0,
                retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
                execution_time_ms=round(elapsed_ms, 2),
                filters_applied={"causal_guardrail": "NOT_PROJECTABLE"},
                rejection_reason=(
                    "Post-intervention diagnostic states (failure probability, anomaly score, health score) "
                    "are strictly NOT_PROJECTABLE under Phase 16 simulation guardrails."
                ),
            )

        target_machine = machine_id or (extracted_machine if extracted_machine in KNOWN_MACHINES else None)
        target_phase = phase or self._extract_phase_entity(query)

        # Apply hard metadata & temporal filters
        candidate_indices = RetrievalFilters.apply_filters(
            chunks=self.vector_store.chunks,
            machine_id=target_machine,
            phase=target_phase,
            include_retrospective=include_retrospective,
            exclude_superseded=exclude_superseded,
            allowed_epistemic_statuses=allowed_epistemic_statuses,
        )

        filters_applied: Dict[str, Any] = {
            "machine_id": target_machine,
            "phase": target_phase,
            "include_retrospective": include_retrospective,
            "exclude_superseded": exclude_superseded,
            "initial_heuristic_threshold": self.rejection_threshold,
            "candidate_count": len(candidate_indices),
        }

        # Check for zero candidate matches
        if not candidate_indices:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return RetrievalResult(
                query=query,
                status="NO_SUFFICIENT_EVIDENCE",
                items=[],
                total_found=0,
                retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
                execution_time_ms=round(elapsed_ms, 2),
                filters_applied=filters_applied,
                rejection_reason="No candidate knowledge chunks matched metadata and temporal filter constraints.",
            )

        # 4. Dense representation vector search
        query_vec = self.embedder.encode([query])[0]
        dense_results = self.vector_store.search(
            query_vector=query_vec,
            candidate_indices=candidate_indices,
            top_k=len(candidate_indices),
        )

        # 5. Hybrid Scoring with Keyword Match & Source Authority Weighting
        query_terms = set(re.findall(r"\b[a-zA-Z0-9_]+\b", query.lower()))
        filler_words = {
            "what", "is", "the", "of", "and", "in", "to", "for", "a", "an", "on", "was", "during",
            "retrieve", "happened", "occurred", "tell", "show", "give", "me", "how", "why", "when",
            "where", "which", "are", "were", "been", "being", "have", "has", "had", "does", "did",
            "should", "done", "about", "do", "can", "could", "would", "be", "we", "i", "one",
            "current", "currently",
        }
        # Topical anchor terms exclude generic filler words and pure digits
        informative_terms = {
            t for t in query_terms if t not in filler_words and not t.isdigit() and len(t) > 1
        }

        scored_candidates: List[EvidenceItem] = []
        for idx, d_score in dense_results:
            chunk = self.vector_store.chunks[idx]
            chunk_terms = set(re.findall(r"\b[a-zA-Z0-9_]+\b", chunk.text.lower()))

            # Lexical overlap fraction
            k_score = 0.0
            if informative_terms:
                overlap = len(informative_terms & chunk_terms)
                k_score = overlap / len(informative_terms)

            # Base hybrid score
            base_score = (self.dense_weight * max(0.0, d_score)) + (self.keyword_weight * k_score)

            # Multiply by source authority weight (1.0 for authoritative, 0.5 for superseded)
            final_score = base_score * chunk.authority_weight

            item = EvidenceItem(
                chunk_id=chunk.chunk_id,
                source_id=chunk.source_id,
                document_title=chunk.document_title,
                file_path=chunk.file_path,
                score=round(float(final_score), 4),
                dense_score=round(float(d_score), 4),
                keyword_score=round(float(k_score), 4),
                text=chunk.text,
                phase=chunk.phase,
                machine_id=chunk.machine_id,
                as_of_timestamp=chunk.as_of_timestamp,
                epistemic_status=chunk.epistemic_status,
                is_decision_input=chunk.is_decision_input,
                is_superseded=chunk.is_superseded,
                authority_weight=chunk.authority_weight,
                provenance=chunk.provenance,
            )
            scored_candidates.append(item)

        # Sort candidates descending by final score
        scored_candidates.sort(key=lambda x: x.score, reverse=True)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Confidence Gate: Initial Heuristic Rejection Threshold Check & Keyword Grounding
        if not scored_candidates or scored_candidates[0].score < self.rejection_threshold:
            top_score = scored_candidates[0].score if scored_candidates else 0.0
            return RetrievalResult(
                query=query,
                status="NO_SUFFICIENT_EVIDENCE",
                items=[],
                total_found=0,
                retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
                execution_time_ms=round(elapsed_ms, 2),
                filters_applied=filters_applied,
                rejection_reason=(
                    f"Top retrieval score ({top_score:.4f}) fell below initial heuristic "
                    f"rejection threshold ({self.rejection_threshold:.2f})."
                ),
            )

        # Substantive Grounding Check: Top candidate must have minimal lexical grounding
        if scored_candidates[0].keyword_score < self.min_keyword_score:
            top_k_score = scored_candidates[0].keyword_score
            return RetrievalResult(
                query=query,
                status="NO_SUFFICIENT_EVIDENCE",
                items=[],
                total_found=0,
                retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
                execution_time_ms=round(elapsed_ms, 2),
                filters_applied=filters_applied,
                rejection_reason=(
                    f"Top candidate lacked sufficient lexical term grounding "
                    f"(keyword match {top_k_score:.2f} < {self.min_keyword_score:.2f})."
                ),
            )

        top_items = scored_candidates[:top_k]
        return RetrievalResult(
            query=query,
            status="SUCCESS",
            items=top_items,
            total_found=len(top_items),
            retrieval_strategy="HYBRID_TFIDF_SVD_KEYWORD",
            execution_time_ms=round(elapsed_ms, 2),
            filters_applied=filters_applied,
        )

    @staticmethod
    def _extract_machine_entity(query: str) -> Optional[str]:
        """Detects machine ID mentions (e.g. M1, M2, M99, Machine 2)."""
        matches = re.findall(r"\b(M[0-9]+)\b", query.upper())
        if len(matches) == 1:
            return matches[0]
        m_digit = re.findall(r"\bmachine\s*([0-9]+)\b", query.lower())
        if len(m_digit) == 1:
            return f"M{m_digit[0]}"
        return None

    @staticmethod
    def _extract_factory_entity(query: str) -> Optional[str]:
        """Detects factory plant mentions (e.g. FAC_01, FAC_99, Factory 1)."""
        matches = re.findall(r"\b(FAC_[0-9]+)\b", query.upper())
        if len(matches) == 1:
            return matches[0]
        fac_digit = re.findall(r"\bfactory\s*([0-9]+)\b", query.lower())
        if len(fac_digit) == 1:
            return f"FAC_{int(fac_digit[0]):02d}"
        return None

    @staticmethod
    def _extract_phase_entity(query: str) -> Optional[int]:
        """Detects explicit phase mentions like 'phase 13'."""
        matches = re.findall(r"\bphase\s*([0-9]{1,2})\b", query.lower())
        if matches:
            return int(matches[0])
        return None

