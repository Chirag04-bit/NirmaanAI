"""
NirmaanAI Phase 19: SentenceTransformer Pluggable Adapter (Optional Extension)
Provided as an architectural adapter for future phases when sentence-transformers is installed.
Not active in the Phase 19 baseline environment.
"""

from typing import List, Optional
import numpy as np
from src.knowledge.embeddings.base import BaseRepresentationModel


class SentenceTransformerEmbedder(BaseRepresentationModel):
    """Optional adapter for deep neural Sentence-Transformer models."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dim = 384

    @classmethod
    def is_available(cls) -> bool:
        """Checks if sentence-transformers is installed in the current environment."""
        try:
            import sentence_transformers  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def representation_type(self) -> str:
        return f"Neural Transformer Embeddings ({self.model_name})"

    def fit(self, texts: List[str]) -> "SentenceTransformerEmbedder":
        """No-op for pre-trained neural models."""
        return self

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes texts using sentence-transformers if installed."""
        if not self.is_available():
            raise RuntimeError(
                "SentenceTransformer is not installed in this environment. "
                "Use TfidfSvdDenseRepresentation for the verified deterministic baseline."
            )
        from sentence_transformers import SentenceTransformer
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32)
