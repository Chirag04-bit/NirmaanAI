"""
NirmaanAI Phase 19: Knowledge Index Manager
Coordinates document ingestion, chunking, representation fitting, vector indexing,
persistence, and manifest generation.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import List, Optional, Tuple

from src.knowledge.chunking.markdown_chunker import MarkdownChunker
from src.knowledge.chunking.structured_chunker import StructuredChunker
from src.knowledge.embeddings.dense_embedder import TfidfSvdDenseRepresentation
from src.knowledge.indexing.vector_store import NumpyVectorStore
from src.knowledge.ingestion.document_loader import DocumentLoader
from src.knowledge.registry import PROJECT_ROOT, KnowledgeRegistry
from src.knowledge.schemas import DocumentChunk, KnowledgeSourceType

DEFAULT_INDEX_DIR = PROJECT_ROOT / "models" / "knowledge"


class KnowledgeIndexManager:
    """Manages the lifecycle, persistence, and verification of the Factory Knowledge Vector Index."""

    def __init__(self, index_dir: Path = DEFAULT_INDEX_DIR, dimension: int = 256):
        self.index_dir = index_dir
        self.dimension = dimension
        self.embedder: Optional[TfidfSvdDenseRepresentation] = None
        self.vector_store: Optional[NumpyVectorStore] = None

    def build_index(self) -> Tuple[NumpyVectorStore, TfidfSvdDenseRepresentation]:
        """
        Ingests all approved sources, chunks them, fits representation model,
        encodes chunks, and builds the vector store.
        """
        sources = KnowledgeRegistry.get_all_sources()
        all_chunks: List[DocumentChunk] = []
        md_chunker = MarkdownChunker()
        struct_chunker = StructuredChunker()

        source_manifest: List[dict] = []

        for src in sources:
            text, meta = DocumentLoader.load_source(src)
            src_file = PROJECT_ROOT / src.file_path
            src_hash = hashlib.md5(src_file.read_bytes()).hexdigest() if src_file.exists() else "synthetic"

            if src.source_type == KnowledgeSourceType.MODEL_SUMMARY:
                chunks = struct_chunker.chunk_structured(text, meta)
            else:
                chunks = md_chunker.chunk_document(text, meta)

            all_chunks.extend(chunks)
            source_manifest.append({
                "source_id": src.source_id,
                "file_path": src.file_path,
                "md5": src_hash,
                "chunk_count": len(chunks),
                "phase": src.phase,
            })

        if not all_chunks:
            raise RuntimeError("No chunks extracted from approved sources.")

        # Fit representation model on all chunk texts
        chunk_texts = [c.text for c in all_chunks]
        self.embedder = TfidfSvdDenseRepresentation(dimension=self.dimension, random_state=42)
        self.embedder.fit(chunk_texts)

        # Encode into dense representation vectors
        vectors = self.embedder.encode(chunk_texts)

        # Initialize vector store
        self.vector_store = NumpyVectorStore(dimension=self.dimension)
        self.vector_store.set_data(vectors=vectors, chunks=all_chunks)

        # Persist index artifacts
        self.save(source_manifest=source_manifest)

        return self.vector_store, self.embedder

    def save(self, source_manifest: Optional[List[dict]] = None) -> None:
        """Persists index, chunk metadata, representation model, and manifest."""
        if self.vector_store is None or self.embedder is None:
            raise RuntimeError("Cannot save index: vector store or embedder not built.")

        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store.save(self.index_dir)
        self.embedder.save(self.index_dir / "dense_embedder.joblib")

        manifest = {
            "index_version": "v0.19.0",
            "build_timestamp": datetime.now(timezone.utc).isoformat(),
            "representation_type": self.embedder.representation_type,
            "dimension": self.dimension,
            "total_chunks": len(self.vector_store.chunks),
            "sources": source_manifest or [],
        }
        with open(self.index_dir / "index_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def load(self) -> Tuple[NumpyVectorStore, TfidfSvdDenseRepresentation]:
        """Loads persisted vector store and representation model from disk."""
        if not (self.index_dir / "vector_index.npy").exists():
            raise FileNotFoundError(f"Knowledge index not found at {self.index_dir}. Run build_index() first.")

        self.vector_store = NumpyVectorStore.load(self.index_dir, dimension=self.dimension)
        self.embedder = TfidfSvdDenseRepresentation.load(self.index_dir / "dense_embedder.joblib")
        return self.vector_store, self.embedder

    def is_built(self) -> bool:
        """Returns True if persisted index files exist on disk."""
        return (
            (self.index_dir / "vector_index.npy").exists()
            and (self.index_dir / "chunk_metadata.json").exists()
            and (self.index_dir / "dense_embedder.joblib").exists()
            and (self.index_dir / "index_manifest.json").exists()
        )
