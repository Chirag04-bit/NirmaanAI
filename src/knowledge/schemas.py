"""
NirmaanAI Phase 19: Factory Knowledge Memory & RAG Schemas
Strict Pydantic v2 schemas for knowledge ingestion, chunking, retrieval, and evidence citations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EpistemicStatus(str, Enum):
    """Authoritative project epistemic taxonomy."""
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    MODEL_OUTPUT = "MODEL_OUTPUT"
    CONTROLLED_SYNTHETIC = "CONTROLLED_SYNTHETIC"
    RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH = "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"
    PROJECTED = "PROJECTED"
    NOT_PROJECTABLE = "NOT_PROJECTABLE"
    UNKNOWN = "UNKNOWN"


class KnowledgeSourceType(str, Enum):
    """Categorization of approved knowledge sources."""
    DOCUMENTATION = "DOCUMENTATION"
    FACTORY_KNOWLEDGE = "FACTORY_KNOWLEDGE"
    MODEL_SUMMARY = "MODEL_SUMMARY"
    GROUND_TRUTH_EVENT = "GROUND_TRUTH_EVENT"


class KnowledgeSource(BaseModel):
    """Registration entry for an approved knowledge source."""
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(description="Unique source identifier.")
    source_type: KnowledgeSourceType = Field(description="Type of knowledge source.")
    title: str = Field(description="Human-readable title.")
    file_path: str = Field(description="Relative path within workspace.")
    phase: int = Field(description="Project phase of origin (3 to 18).")
    default_epistemic_status: EpistemicStatus = Field(description="Default epistemic status.")
    authority_weight: float = Field(default=1.0, description="Source authority weight (0.5 to 1.0).")
    is_superseded: bool = Field(default=False, description="True if superseded historical record.")
    machine_id: Optional[str] = Field(default=None, description="Coupled machine ID, if asset-specific.")
    factory_id: Optional[str] = Field(default="FAC_01", description="Factory ID.")


class DocumentChunk(BaseModel):
    """A discrete, indexed chunk of knowledge with full provenance and metadata."""
    model_config = ConfigDict(from_attributes=True)

    chunk_id: str = Field(description="Deterministic SHA256 snippet hash.")
    source_id: str = Field(description="Origin source ID.")
    document_title: str = Field(description="Parent document title.")
    file_path: str = Field(description="Source relative file path.")
    phase: int = Field(description="Origin project phase.")
    machine_id: Optional[str] = Field(default=None, description="Coupled machine ID or None for fleet.")
    factory_id: Optional[str] = Field(default="FAC_01", description="Factory ID.")
    as_of_timestamp: Optional[str] = Field(default=None, description="ISO-8601 temporal horizon timestamp.")
    epistemic_status: str = Field(description="Epistemic classification.")
    is_decision_input: bool = Field(default=True, description="False for post-cutoff retrospective events.")
    is_superseded: bool = Field(default=False, description="True if superseded historical figure.")
    authority_weight: float = Field(default=1.0, description="Source authority multiplier (0.5 to 1.0).")
    section_heading: str = Field(default="General", description="Hierarchical section heading context.")
    text: str = Field(description="Text payload.")
    provenance: str = Field(default="NirmaanAI Project Documentation", description="Lineage details.")


class EvidenceItem(BaseModel):
    """A ranked evidence citation returned from retrieval."""
    chunk_id: str = Field(description="Chunk ID.")
    source_id: str = Field(description="Source ID.")
    document_title: str = Field(description="Document title.")
    file_path: str = Field(description="Source file path.")
    score: float = Field(description="Final retrieval score.")
    dense_score: float = Field(description="Dense representation score component.")
    keyword_score: float = Field(description="Keyword match score component.")
    text: str = Field(description="Verbatim evidence text payload.")
    phase: int = Field(description="Origin project phase.")
    machine_id: Optional[str] = Field(default=None, description="Associated machine ID.")
    as_of_timestamp: Optional[str] = Field(default=None, description="Temporal timestamp.")
    epistemic_status: str = Field(description="Epistemic classification.")
    is_decision_input: bool = Field(default=True, description="True if valid for prospective decisions.")
    is_superseded: bool = Field(default=False, description="True if superseded historical record.")
    authority_weight: float = Field(default=1.0, description="Source authority weight.")
    provenance: str = Field(description="Upstream derivation lineage.")


class RetrievalResult(BaseModel):
    """Complete response payload for a knowledge retrieval query."""
    query: str = Field(description="Original user query.")
    status: str = Field(description="Retrieval status: 'SUCCESS' or 'NO_SUFFICIENT_EVIDENCE'.")
    items: List[EvidenceItem] = Field(default_factory=list, description="Ranked evidence citations.")
    total_found: int = Field(default=0, description="Number of retrieved evidence items.")
    retrieval_strategy: str = Field(default="HYBRID_TFIDF_SVD_KEYWORD", description="Algorithm used.")
    execution_time_ms: float = Field(default=0.0, description="Search latency in milliseconds.")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Metadata filters applied.")
    rejection_reason: Optional[str] = Field(default=None, description="Reason if NO_SUFFICIENT_EVIDENCE.")
