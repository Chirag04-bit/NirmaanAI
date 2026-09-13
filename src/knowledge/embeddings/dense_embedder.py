"""
NirmaanAI Phase 19: TF-IDF/SVD Dense Retrieval Representation
Provides deterministic, offline, lexical/statistical dense representations.
Explicitly documented: This is a deterministic statistical baseline, NOT equivalent to
deep neural Sentence-Transformer semantic embeddings.
"""

from pathlib import Path
from typing import List, Optional
import joblib
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from src.knowledge.embeddings.base import BaseRepresentationModel


class TfidfSvdDenseRepresentation(BaseRepresentationModel):
    """
    Deterministic TF-IDF + TruncatedSVD Dense Retrieval Representation.
    Produces a 256-dimensional unit-normalized vector for fast cosine similarity scoring.
    """

    def __init__(self, dimension: int = 256, random_state: int = 42):
        self._dim = dimension
        self._random_state = random_state
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._svd: Optional[TruncatedSVD] = None
        self._is_fitted = False

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def representation_type(self) -> str:
        return "TF-IDF/SVD Dense Retrieval Representation (Deterministic Statistical Baseline)"

    def fit(self, texts: List[str]) -> "TfidfSvdDenseRepresentation":
        """Fits TF-IDF vectorizer and TruncatedSVD decomposition on knowledge text."""
        if not texts:
            raise ValueError("Cannot fit representation on empty text corpus.")

        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            sublinear_tf=True,
            ngram_range=(1, 3),
            max_features=10000,
            token_pattern=r"(?u)\b[A-Za-z0-9_]+\b",  # Retain alphanumeric codes like M1-M5, MAINT_0003
        )
        tfidf_mat = self._vectorizer.fit_transform(texts)
        n_features = tfidf_mat.shape[1]

        # SVD requires n_components < n_features
        actual_comp = min(self._dim, n_features - 1) if n_features > 1 else 1
        actual_comp = max(1, actual_comp)

        self._svd = TruncatedSVD(
            n_components=actual_comp,
            algorithm="randomized",
            random_state=self._random_state,
        )
        self._svd.fit(tfidf_mat)
        self._is_fitted = True
        return self

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes texts into L2-normalized [N, 256] float32 matrix."""
        if not self._is_fitted or self._vectorizer is None or self._svd is None:
            raise RuntimeError("Representation model must be fitted before calling encode().")

        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)

        tfidf_mat = self._vectorizer.transform(texts)
        dense = self._svd.transform(tfidf_mat)

        # Pad with zeros if actual SVD components were fewer than target dimension
        if dense.shape[1] < self._dim:
            pad_width = self._dim - dense.shape[1]
            dense = np.pad(dense, ((0, 0), (0, pad_width)), mode="constant")
        elif dense.shape[1] > self._dim:
            dense = dense[:, : self._dim]

        # Unit L2-normalization for exact cosine dot product
        norms = np.linalg.norm(dense, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = (dense / norms).astype(np.float32)
        return normalized

    def save(self, filepath: Path) -> None:
        """Persists fitted vectorizer and SVD transformers to disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "vectorizer": self._vectorizer,
                "svd": self._svd,
                "dim": self._dim,
                "is_fitted": self._is_fitted,
                "random_state": self._random_state,
            },
            filepath,
        )

    @classmethod
    def load(cls, filepath: Path) -> "TfidfSvdDenseRepresentation":
        """Loads fitted vectorizer and SVD transformers from disk."""
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        data = joblib.load(filepath)
        instance = cls(dimension=data["dim"], random_state=data["random_state"])
        instance._vectorizer = data["vectorizer"]
        instance._svd = data["svd"]
        instance._is_fitted = data["is_fitted"]
        return instance
