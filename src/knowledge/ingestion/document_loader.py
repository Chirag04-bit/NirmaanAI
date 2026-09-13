"""
NirmaanAI Phase 19: Document Loader
Loads approved Markdown documents and structured JSON summaries.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.knowledge.ingestion.cleaner import TextCleaner
from src.knowledge.registry import PROJECT_ROOT, KnowledgeRegistry
from src.knowledge.schemas import KnowledgeSource, KnowledgeSourceType


class DocumentLoader:
    """Safely reads and pre-processes approved knowledge documents."""

    @staticmethod
    def load_source(source: KnowledgeSource) -> Tuple[str, Dict[str, Any]]:
        """
        Loads the raw text or structured contents of an approved KnowledgeSource.
        Returns cleaned text content and a metadata dictionary.
        """
        full_path = PROJECT_ROOT / source.file_path
        KnowledgeRegistry.validate_file_safety(full_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Knowledge source file missing: {source.file_path}")

        meta: Dict[str, Any] = {
            "source_id": source.source_id,
            "document_title": source.title,
            "file_path": source.file_path,
            "phase": source.phase,
            "default_epistemic_status": source.default_epistemic_status.value,
            "authority_weight": source.authority_weight,
            "is_superseded": source.is_superseded,
            "machine_id": source.machine_id,
            "factory_id": source.factory_id,
        }

        if source.source_type == KnowledgeSourceType.MODEL_SUMMARY:
            # Parse structured JSON and convert to narrative facts
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta["raw_json"] = data
            narrative = DocumentLoader._json_to_narrative(source, data)
            return TextCleaner.clean(narrative), meta

        elif source.source_type == KnowledgeSourceType.GROUND_TRUTH_EVENT:
            # Controlled synthetic event MAINT_0003 narrative
            event_text = (
                "# Controlled Retrospective Ground Truth: Event MAINT_0003\n\n"
                "- Maintenance Event ID: MAINT_0003\n"
                "- Machine ID: M2 (VMC Milling)\n"
                "- Event Timestamp: 2026-01-22T16:30:00Z\n"
                "- Decision Cutoff: 2026-01-21T12:00:00Z\n"
                "- Temporal Classification: Post-Cutoff Retrospective Ground Truth\n"
                "- Epistemic Status: RETROSPECTIVE_CONTROLLED_SYNTHETIC_GROUND_TRUTH\n"
                "- Prospective Decision Input: False (is_decision_input = False)\n"
                "- Failure Mode: Complete spindle bearing mechanical seizure\n"
                "- Root Cause: Lubrication starvation and bearing cage thermal failure\n"
                "- Total Downtime: 240 minutes (unplanned emergency breakdown)\n"
                "- Realized Breakdown Loss: ₹11,250 downtime loss + ₹420 emergency technician labor\n"
                "- Epistemic Boundary Note: This event occurred AFTER the decision cutoff (2026-01-21T12:00:00Z). "
                "It represents retrospective ground truth and MUST NOT be used as prospective operational evidence "
                "or contaminate decision-state calculations.\n"
            )
            meta["is_decision_input"] = False
            meta["as_of_timestamp"] = "2026-01-22T16:30:00Z"
            return TextCleaner.clean(event_text), meta

        else:
            # Standard Markdown document
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return TextCleaner.clean(content), meta

    @staticmethod
    def _json_to_narrative(source: KnowledgeSource, data: Dict[str, Any]) -> str:
        """Converts structured JSON dictionaries into readable, well-formed markdown sections."""
        lines = [f"# {source.title}\n"]
        lines.append(f"Source ID: {source.source_id} | Phase: {source.phase}\n")

        for key, value in data.items():
            k_title = key.replace("_", " ").title()
            if isinstance(value, dict):
                lines.append(f"## {k_title}")
                for sub_k, sub_v in value.items():
                    sub_title = sub_k.replace("_", " ").title()
                    lines.append(f"- **{sub_title}**: {sub_v}")
                lines.append("")
            elif isinstance(value, list):
                lines.append(f"## {k_title}")
                for item in value:
                    if isinstance(item, dict):
                        sub_items = [f"{ik.replace('_', ' ').title()}: {iv}" for ik, iv in item.items()]
                        lines.append(f"- {', '.join(sub_items)}")
                    else:
                        lines.append(f"- {item}")
                lines.append("")
            else:
                lines.append(f"- **{k_title}**: {value}")

        return "\n".join(lines)
