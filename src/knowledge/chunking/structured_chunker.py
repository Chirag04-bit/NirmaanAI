"""
NirmaanAI Phase 19: Structured Data Chunker
Converts structured model and scenario JSON summaries into discrete, factual chunks.
"""

import hashlib
from typing import Any, Dict, List

from src.knowledge.chunking.markdown_chunker import MarkdownChunker
from src.knowledge.schemas import DocumentChunk


class StructuredChunker:
    """Specialized chunker for structured model outputs and scenario summaries."""

    def __init__(self):
        self._md_chunker = MarkdownChunker(min_chunk_chars=100, max_chunk_chars=1500)

    def chunk_structured(self, narrative_text: str, meta: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Chunks structured model summaries while preserving high authority and precise metrics.
        """
        raw_json = meta.get("raw_json", {})
        chunks: List[DocumentChunk] = []
        source_id = meta["source_id"]
        doc_title = meta["document_title"]
        file_path = meta["file_path"]
        phase = meta["phase"]
        epistemic = meta.get("default_epistemic_status", "MODEL_OUTPUT")
        auth_weight = meta.get("authority_weight", 1.0)
        machine_id = meta.get("machine_id")
        factory_id = meta.get("factory_id", "FAC_01")

        # First use markdown chunker on the rendered narrative
        base_chunks = self._md_chunker.chunk_document(narrative_text, meta)
        for c in base_chunks:
            # Enrich with specific domain provenance
            if "M2" in c.text:
                c.machine_id = "M2"
            c.provenance = f"Model Artifact: {file_path} | Phase: {phase} | Epistemic: {epistemic}"
            chunks.append(c)

        return chunks
