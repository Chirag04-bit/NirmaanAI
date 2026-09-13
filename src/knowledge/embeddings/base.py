"""
NirmaanAI Phase 19: Base Embedding & Representation Model Interface
Defines the standard contract for vector representations in the RAG retrieval layer.
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseRepresentationModel(ABC):
    """Abstract interface for text vector representation models."""

    @abstractmethod
    def fit(self, texts: List[str]) -> "BaseRepresentationModel":
        """Fits the representation model (e.g. TF-IDF vocabulary, SVD basis)."""
        pass

    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encodes a list of texts into an L2-normalized 2D float32 numpy array of shape [N, D].
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the dimensionality of the representation vector space."""
        pass

    @property
    @abstractmethod
    def representation_type(self) -> str:
        """Returns the explicit algorithmic nature of this representation."""
        pass
