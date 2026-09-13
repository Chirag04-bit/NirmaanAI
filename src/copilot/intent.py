"""
NirmaanAI Phase 20: Deterministic Intent Classifier
Maps natural-language factory queries to the authoritative 15-intent taxonomy.
"""

import re
from typing import Dict, List, Optional, Tuple

from src.copilot.schemas import CopilotIntent

# Patterns for out-of-scope / unsupported questions
UNSUPPORTED_PATTERNS = [
    r"\bweather\b",
    r"\bstock market\b",
    r"\bpolitics\b",
    r"\bsports\b",
    r"\bcelebrity\b",
    r"\bexpansion budget\b",
    r"\b2027\b",
    r"\bcoolant explosion\b",
    r"\bwho won\b",
    r"\btell me a joke\b",
    r"\bunrelated\b",
    r"\bnot in the knowledge base\b",
    r"\bgeneral knowledge\b",
]

INTENT_RULES: List[Tuple[CopilotIntent, List[str]]] = [
    # 1. Temporal History & Retrospective Events
    (
        CopilotIntent.TEMPORAL_HISTORY,
        [
            r"\bretrospective\b",
            r"\bmaint_0003\b",
            r"\bday\s*22\b",
            r"\bwas maint_0003\b",
            r"\btemporal boundary\b",
            r"\bdecision cutoff\b",
            r"\bhistorical halt\b",
            r"\bprospective decision evidence\b",
        ],
    ),
    # 2. What-If & Simulation Scenarios
    (
        CopilotIntent.WHAT_IF,
        [
            r"\bwhat[\s-]if\b",
            r"\bscenario\s*[a-e]\b",
            r"\bsimulat(e|ion|ed)\b",
            r"\bavoided loss\b",
            r"\bcounterfactual\b",
            r"\bflow mitigation\b",
            r"\bspindle inspection scenario\b",
        ],
    ),
    # 3. Root Cause Analysis
    (
        CopilotIntent.ROOT_CAUSE,
        [
            r"\bwhy is .* degrading\b",
            r"\bwhy did .* fail\b",
            r"\bwhat caused\b",
            r"\broot cause\b",
            r"\brca\b",
            r"\bmechanical load\b",
            r"\bfault tree\b",
            r"\bunderlying cause\b",
            r"\bprimary candidate\b",
        ],
    ),
    # 4. Recommendations & Mitigations
    (
        CopilotIntent.RECOMMENDATION,
        [
            r"\bwhat should (be done|we do|i do|one do)\b",
            r"\bwhat to do\b",
            r"\bmaintenance action\b",
            r"\brecommend(ation|ed)?\b",
            r"\bmitigat(e|ion)\b",
            r"\bprescriptive action\b",
            r"\bactionable step\b",
            r"\bintervention\b",
            r"\binspect_spindle_bearing\b",
        ],
    ),
    # 5. Financial Impact & Losses
    (
        CopilotIntent.FINANCIAL_IMPACT,
        [
            r"\brealized (financial )?loss\b",
            r"\bgross (financial )?exposure\b",
            r"\bprojected opportunity\b",
            r"\bopportunity cost\b",
            r"\bfinancial impact\b",
            r"\bfinancial exposure\b",
            r"\bhow much money\b",
            r"\bcost of downtime\b",
            r"\bmonetary impact\b",
        ],
    ),
    # 6. Inventory & Spare Parts
    (
        CopilotIntent.INVENTORY_STATUS,
        [
            r"\bbearing (stock|inventory)\b",
            r"\bspare parts?\b",
            r"\binventory status\b",
            r"\bsafety stock\b",
            r"\breorder point\b",
            r"\brop\b",
            r"\bstock level\b",
            r"\bcurrent stock\b",
            r"\bpost-action stock\b",
            r"\bunits on hand\b",
        ],
    ),
    # 7. Bottleneck & Flow Constraints
    (
        CopilotIntent.BOTTLENECK_STATUS,
        [
            r"\bbottleneck\b",
            r"\bcycle ratio\b",
            r"\bdelayed units\b",
            r"\bthroughput delay\b",
            r"\bline starvation\b",
            r"\bflow constraint\b",
        ],
    ),
    # 8. Machine Health & State
    (
        CopilotIntent.MACHINE_HEALTH,
        [
            r"\bhealth of\b",
            r"\bhealth status\b",
            r"\bhealth state\b",
            r"\bhealth score\b",
            r"\bcurrent health\b",
            r"\bmachine health\b",
            r"\bis .* critical\b",
            r"\bhealth condition\b",
        ],
    ),
    # 9. Machine Degradation
    (
        CopilotIntent.MACHINE_DEGRADATION,
        [
            r"\bdegradation\b",
            r"\bspindle wear\b",
            r"\bwear rate\b",
            r"\btool wear\b",
            r"\bvibration trend\b",
            r"\bmechanical distress\b",
        ],
    ),
    # 10. Predictive Maintenance & Failure Risk
    (
        CopilotIntent.PREDICTIVE_MAINTENANCE,
        [
            r"\bfailure probabilit(y|ies)\b",
            r"\brisk of failure\b",
            r"\bp\(fail\)\b",
            r"\brul\b",
            r"\bremaining useful life\b",
            r"\btime to failure\b",
            r"\bpredictive maintenance\b",
            r"\bpdm\b",
        ],
    ),
    # 11. Anomaly Status
    (
        CopilotIntent.ANOMALY_STATUS,
        [
            r"\banomal(y|ies)\b",
            r"\banomaly score\b",
            r"\breconstruction error\b",
            r"\bpca anomaly\b",
            r"\boutlier detection\b",
        ],
    ),
    # 12. Production Forecast
    (
        CopilotIntent.PRODUCTION_FORECAST,
        [
            r"\bproduction forecast\b",
            r"\bdemand forecast\b",
            r"\bthroughput forecast\b",
            r"\btarget units\b",
        ],
    ),
    # 13. System Capability
    (
        CopilotIntent.SYSTEM_CAPABILITY,
        [
            r"\bwhat can you do\b",
            r"\bcapabilities\b",
            r"\bwho are you\b",
            r"\bhelp\b",
            r"\bwhat is nirmaanai\b",
        ],
    ),
    # 14. Fact Lookup
    (
        CopilotIntent.FACT_LOOKUP,
        [
            r"\bwhat is machine\b",
            r"\bwhat sensors\b",
            r"\bhow many machines\b",
            r"\bwhere is\b",
            r"\btelemetry specs\b",
            r"\bsensor list\b",
            r"\bdataset\b",
        ],
    ),
]


class IntentClassifier:
    """Classifies natural-language queries into discrete operational intents."""

    @classmethod
    def classify(cls, query: str) -> CopilotIntent:
        """Determines the operational intent of the given user query."""
        q_lower = query.lower().strip()

        # 1. First check for explicitly unsupported out-of-scope queries
        for pat in UNSUPPORTED_PATTERNS:
            if re.search(pat, q_lower):
                return CopilotIntent.UNSUPPORTED_QUERY

        # 2. Check each intent in prioritized order
        for intent, patterns in INTENT_RULES:
            for pat in patterns:
                if re.search(pat, q_lower):
                    return intent

        # 3. Default fallback: If query asks generic questions or doesn't match factory domain
        return CopilotIntent.FACT_LOOKUP
