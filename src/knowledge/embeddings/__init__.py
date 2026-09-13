"""
NirmaanAI Phase 19 Embeddings & Representation Module
"""
from src.knowledge.embeddings.base import BaseRepresentationModel
from src.knowledge.embeddings.dense_embedder import TfidfSvdDenseRepresentation
from src.knowledge.embeddings.transformer_embedder import SentenceTransformerEmbedder

__all__ = [
    "BaseRepresentationModel",
    "TfidfSvdDenseRepresentation",
    "SentenceTransformerEmbedder",
]
