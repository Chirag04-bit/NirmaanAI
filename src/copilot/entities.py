"""
NirmaanAI Phase 20: Copilot Entity Extractor
Extracts and validates plant topology entities (machines, factories),
operational metrics, and analytical phases.
"""

import re
from typing import Dict, List, Optional, Set, Tuple

KNOWN_MACHINES = {"M1", "M2", "M3", "M4", "M5"}
KNOWN_FACTORIES = {"FAC_01"}

METRIC_PATTERNS = {
    "health_score": [r"\bhealth\b", r"\bhealth score\b", r"\bhealth state\b", r"\bdegradation index\b"],
    "failure_probability": [r"\bfailure probabilit(y|ies)\b", r"\brisk of failure\b", r"\bp\(fail\)\b", r"\brul\b", r"\bremaining useful life\b"],
    "anomaly_score": [r"\banomal(y|ies)\b", r"\breconstruction error\b", r"\boutlier\b"],
    "bottleneck": [r"\bbottleneck\b", r"\bcycle ratio\b", r"\bdelayed units\b", r"\bstarvation\b", r"\bthroughput\b"],
    "inventory": [r"\binventory\b", r"\bstock\b", r"\bspares?\b", r"\bsafety stock\b", r"\breorder point\b", r"\brop\b", r"\beoq\b", r"\bbearing stock\b"],
    "rca": [r"\broot cause\b", r"\brca\b", r"\bfault tree\b", r"\bmechanical load\b", r"\bspindle wear\b", r"\bwhy is .* degrading\b"],
    "recommendation": [r"\brecommend(ation|ed)?\b", r"\baction\b", r"\bwhat should (i|we) do\b", r"\bmitigation\b", r"\bintervention\b"],
    "financial": [r"\bfinancial\b", r"\bloss(es)?\b", r"\brealized loss\b", r"\bopportunity cost\b", r"\bgross exposure\b", r"\bcost\b", r"\binr\b", r"\b₹\b"],
    "simulation": [r"\bwhat[\s-]if\b", r"\bsimulat(e|ion|ed)\b", r"\bscenario\b", r"\bavoided loss\b"],
    "forecast": [r"\bforecast\b", r"\bdemand\b", r"\bproduction forecast\b"],
}


class EntityExtractor:
    """Extracts, standardizes, and validates domain entities from natural-language queries."""

    @staticmethod
    def extract_machines(query: str) -> Tuple[List[str], List[str]]:
        """
        Extracts valid known machines and flags invalid unknown machines.
        Returns: (valid_machines, invalid_machines)
        """
        valid: List[str] = []
        invalid: List[str] = []

        # Patterns matching machine identifiers: M1, M2, M99, Machine 1, Machine M2, etc.
        patterns = [
            r"\b[Mm]([0-9]+)\b",
            r"\bmachine\s*#?([0-9]+)\b",
            r"\bmachine\s*[Mm]([0-9]+)\b",
        ]

        found_ids: Set[str] = set()
        for pat in patterns:
            for match in re.finditer(pat, query, re.IGNORECASE):
                num = match.group(1)
                mid = f"M{num}"
                found_ids.add(mid)

        for mid in sorted(found_ids):
            if mid in KNOWN_MACHINES:
                valid.append(mid)
            else:
                invalid.append(mid)

        return valid, invalid

    @staticmethod
    def extract_factories(query: str) -> Tuple[List[str], List[str]]:
        """
        Extracts valid known factories and flags invalid unknown factories.
        Returns: (valid_factories, invalid_factories)
        """
        valid: List[str] = []
        invalid: List[str] = []

        # Patterns matching factory identifiers: FAC_01, FAC_99, Factory 01, etc.
        patterns = [
            r"\bFAC_?([0-9]+)\b",
            r"\bfactory\s*#?([0-9]+)\b",
            r"\bplant\s*#?([0-9]+)\b",
        ]

        found_ids: Set[str] = set()
        for pat in patterns:
            for match in re.finditer(pat, query, re.IGNORECASE):
                raw_num = match.group(1)
                fid = f"FAC_{int(raw_num):02d}"
                found_ids.add(fid)

        for fid in sorted(found_ids):
            if fid in KNOWN_FACTORIES:
                valid.append(fid)
            else:
                invalid.append(fid)

        return valid, invalid

    @staticmethod
    def extract_metrics(query: str) -> List[str]:
        """Identifies mentioned operational metrics."""
        matched: List[str] = []
        for metric, patterns in METRIC_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, query, re.IGNORECASE):
                    matched.append(metric)
                    break
        return matched

    @staticmethod
    def extract_phases(query: str) -> List[int]:
        """Extracts referenced project phases (Phase 3 to Phase 19)."""
        phases: List[int] = []
        matches = re.finditer(r"\bphase\s*([0-9]{1,2})\b", query, re.IGNORECASE)
        for m in matches:
            val = int(m.group(1))
            if 1 <= val <= 25:
                phases.append(val)
        return sorted(list(set(phases)))

    @classmethod
    def extract_all(cls, query: str) -> Dict[str, Any]:
        """Extracts complete entity payload for downstream routing."""
        valid_m, invalid_m = cls.extract_machines(query)
        valid_f, invalid_f = cls.extract_factories(query)
        metrics = cls.extract_metrics(query)
        phases = cls.extract_phases(query)

        return {
            "valid_machines": valid_m,
            "invalid_machines": invalid_m,
            "primary_machine": valid_m[0] if valid_m else None,
            "valid_factories": valid_f,
            "invalid_factories": invalid_f,
            "primary_factory": valid_f[0] if valid_f else ("FAC_01" if not invalid_f else None),
            "metrics": metrics,
            "phases": phases,
            "has_invalid_entities": bool(invalid_m or invalid_f),
        }
