"""
NirmaanAI Phase 19: Numpy Vector Store
High-performance, deterministic vector store using vectorized numpy matrix operations.
Maintains exact cosine similarity, chunk metadata, and persistence.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.knowledge.schemas import DocumentChunk


class NumpyVectorStore:
    """
    Vector store maintaining an L2-normalized numpy matrix and serialized DocumentChunks.
    Computes exact dot-product cosine similarities.
    """

    def __init__(self, dimension: int = 256):
        self.dimension = dimension
        self.vectors: Optional[np.ndarray] = None  # Shape: [N, D]
        self.chunks: List[DocumentChunk] = []

    def set_data(self, vectors: np.ndarray, chunks: List[DocumentChunk]) -> None:
        """Sets index vectors and chunk metadata."""
        if len(vectors) != len(chunks):
            raise ValueError(f"Vector count ({len(vectors)}) must match chunk count ({len(chunks)}).")
        if len(vectors) > 0 and vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension ({vectors.shape[1]}) does not match store dimension ({self.dimension}).")

        self.vectors = vectors.astype(np.float32)
        self.chunks = list(chunks)

    def search(
        self,
        query_vector: np.ndarray,
        candidate_indices: Optional[List[int]] = None,
        top_k: int = 5,
    ) -> List[Tuple[int, float]]:
        """
        Searches for top_k most similar chunks using cosine similarity (dot product on normalized vectors).
        Returns list of (chunk_index, score) tuples.
        """
        if self.vectors is None or len(self.chunks) == 0:
            return []

        # Ensure query vector is [1, D]
        q = query_vector.reshape(1, -1)

        if candidate_indices is not None:
            if not candidate_indices:
                return []
            sub_vectors = self.vectors[candidate_indices]
            sims = np.dot(sub_vectors, q.T).flatten()
            sorted_local_idx = np.argsort(-sims)[:top_k]
            results = [(candidate_indices[i], float(sims[i])) for i in sorted_local_idx]
            return results

        # Full matrix dot product
        sims = np.dot(self.vectors, q.T).flatten()
        top_indices = np.argsort(-sims)[:top_k]
        return [(int(idx), float(sims[idx])) for idx in top_indices]

    def save(self, output_dir: Path) -> None:
        """Persists index vectors (.npy) and chunk metadata (.json) to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)
        vec_path = output_dir / "vector_index.npy"
        meta_path = output_dir / "chunk_metadata.json"

        if self.vectors is not None:
            np.save(vec_path, self.vectors)
        else:
            np.save(vec_path, np.zeros((0, self.dimension), dtype=np.float32))

        chunks_data = [c.model_dump() for c in self.chunks]
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

    @classmethod
    def load(cls, input_dir: Path, dimension: int = 256) -> "NumpyVectorStore":
        """Loads index vectors and chunk metadata from disk."""
        vec_path = input_dir / "vector_index.npy"
        meta_path = input_dir / "chunk_metadata.json"

        if not vec_path.exists() or not meta_path.exists():
            raise FileNotFoundError(f"Vector store artifacts missing in {input_dir}")

        store = cls(dimension=dimension)
        vectors = np.load(vec_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        chunks = [DocumentChunk.model_validate(d) for d in chunks_data]
        store.set_data(vectors=vectors, chunks=chunks)
        return store
