"""
NirmaanAI Phase 19: Markdown Chunker
Performs header-aware semantic chunking on Markdown documents.
Preserves Markdown tables, hierarchy, and metadata provenance.
"""

import hashlib
import re
from typing import Any, Dict, List

from src.knowledge.ingestion.cleaner import TextCleaner
from src.knowledge.schemas import DocumentChunk


class MarkdownChunker:
    """Splits Markdown documents into coherent, context-rich chunks."""

    def __init__(self, min_chunk_chars: int = 300, max_chunk_chars: int = 2500):
        self.min_chunk_chars = min_chunk_chars
        self.max_chunk_chars = max_chunk_chars

    def chunk_document(self, text: str, meta: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Chunks Markdown text into DocumentChunk instances with inherited metadata.
        """
        sections = self._split_into_sections(text)
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        source_id = meta["source_id"]
        doc_title = meta["document_title"]
        file_path = meta["file_path"]
        phase = meta["phase"]
        def_epistemic = meta.get("default_epistemic_status", "DERIVED")
        auth_weight = meta.get("authority_weight", 1.0)
        is_superseded = meta.get("is_superseded", False)
        machine_id = meta.get("machine_id")
        factory_id = meta.get("factory_id", "FAC_01")
        as_of_ts = meta.get("as_of_timestamp")
        is_decision = meta.get("is_decision_input", True)

        for heading, section_body in sections:
            # Check for section-level machine tags (e.g. M1 to M5)
            section_machine = self._extract_machine_id(heading, section_body) or machine_id

            # Check if this chunk is retrospective ground truth (MAINT_0003)
            chunk_epistemic = def_epistemic
            chunk_is_decision = is_decision
            chunk_as_of = as_of_ts

            if "MAINT_0003" in section_body or "MAINT_0003" in heading:
                chunk_epistemic = "RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH"
                chunk_is_decision = False
                chunk_as_of = "2026-01-22T16:30:00Z"
            elif "not_projectable" in section_body.lower():
                # If section specifically addresses non-projectable states
                if "NOT_PROJECTABLE" in section_body:
                    chunk_epistemic = "NOT_PROJECTABLE"

            # Check if section text contains superseded notice
            chunk_superseded = is_superseded
            chunk_authority = auth_weight
            if "superseded" in section_body.lower() or "obsolete" in section_body.lower():
                chunk_superseded = True
                chunk_authority = min(chunk_authority, 0.50)

            # Subdivide if section is excessively large
            sub_bodies = self._subdivide_large_section(section_body)
            for sub_body in sub_bodies:
                if len(sub_body.strip()) < 50:
                    continue

                full_chunk_text = f"## {heading}\n\n{sub_body.strip()}"
                raw_hash = f"{source_id}_{chunk_idx}_{heading}_{sub_body[:30]}"
                chunk_id = hashlib.sha256(raw_hash.encode("utf-8")).hexdigest()[:16]

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    document_title=doc_title,
                    file_path=file_path,
                    phase=phase,
                    machine_id=section_machine,
                    factory_id=factory_id,
                    as_of_timestamp=chunk_as_of,
                    epistemic_status=chunk_epistemic,
                    is_decision_input=chunk_is_decision,
                    is_superseded=chunk_superseded,
                    authority_weight=chunk_authority,
                    section_heading=heading,
                    text=full_chunk_text,
                    provenance=f"Source: {file_path} | Section: {heading} | Phase: {phase}",
                )
                chunks.append(chunk)
                chunk_idx += 1

        return chunks

    def _split_into_sections(self, text: str) -> List[Tuple[str, str]]:
        """Splits text by markdown headings (# and ## and ###)."""
        heading_re = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
        matches = list(heading_re.finditer(text))

        if not matches:
            return [("General Overview", text)]

        sections: List[Tuple[str, str]] = []
        # Pre-heading intro if any
        if matches[0].start() > 0:
            intro = text[: matches[0].start()].strip()
            if intro:
                sections.append(("Document Overview", intro))

        for i, match in enumerate(matches):
            raw_heading = match.group(1)
            heading = TextCleaner.sanitize_heading(raw_heading)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start_pos:end_pos].strip()
            sections.append((heading, body))

        return sections

    def _subdivide_large_section(self, body: str) -> List[str]:
        """Splits section by paragraphs if it exceeds max_chunk_chars, keeping tables intact."""
        if len(body) <= self.max_chunk_chars:
            return [body]

        paragraphs = body.split("\n\n")
        sub_chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for p in paragraphs:
            p_len = len(p)
            if current_len + p_len > self.max_chunk_chars and current:
                sub_chunks.append("\n\n".join(current))
                current = [p]
                current_len = p_len
            else:
                current.append(p)
                current_len += p_len + 2

        if current:
            sub_chunks.append("\n\n".join(current))

        return sub_chunks

    @staticmethod
    def _extract_machine_id(heading: str, body: str) -> Optional[str]:
        """Detects specific machine coupling (M1, M2, M3, M4, M5) if uniquely highlighted."""
        text_to_check = f"{heading} {body[:200]}"
        matches = set(re.findall(r"\b(M[1-5])\b", text_to_check))
        if len(matches) == 1:
            return list(matches)[0]
        return None
