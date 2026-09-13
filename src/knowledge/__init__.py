"""
NirmaanAI Phase 19: Factory Knowledge Memory & RAG Retrieval Layer
Provides grounded, deterministic evidence retrieval across manufacturing documentation and models.
"""

from src.knowledge.embeddings.dense_embedder import TfidfSvdDenseRepresentation
from src.knowledge.indexing.index_manager import KnowledgeIndexManager
from src.knowledge.indexing.vector_store import NumpyVectorStore
from src.knowledge.registry import DECISION_CUTOFF, KnowledgeRegistry
from src.knowledge.retrieval.filters import RetrievalFilters
from src.knowledge.retrieval.retriever import INITIAL_HEURISTIC_THRESHOLD, KnowledgeRetriever
from src.knowledge.schemas import (
    DocumentChunk,
    EpistemicStatus,
    EvidenceItem,
    KnowledgeSource,
    KnowledgeSourceType,
    RetrievalResult,
)

__version__ = "0.19.0"

__all__ = [
    "__version__",
    "DECISION_CUTOFF",
    "INITIAL_HEURISTIC_THRESHOLD",
    "DocumentChunk",
    "EvidenceItem",
    "RetrievalResult",
    "EpistemicStatus",
    "KnowledgeSource",
    "KnowledgeSourceType",
    "KnowledgeRegistry",
    "TfidfSvdDenseRepresentation",
    "NumpyVectorStore",
    "KnowledgeIndexManager",
    "RetrievalFilters",
    "KnowledgeRetriever",
]
