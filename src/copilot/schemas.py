"""
NirmaanAI Phase 20: AI Factory Copilot Schemas
Strict Pydantic v2 schemas for queries, context, intent classification,
evidence citations, and grounded decision-support responses.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.knowledge.schemas import EpistemicStatus, EvidenceItem


class CopilotIntent(str, Enum):
    """Authoritative taxonomy of 15 deterministic factory decision intents."""
    FACT_LOOKUP = "FACT_LOOKUP"
    MACHINE_HEALTH = "MACHINE_HEALTH"
    MACHINE_DEGRADATION = "MACHINE_DEGRADATION"
    PREDICTIVE_MAINTENANCE = "PREDICTIVE_MAINTENANCE"
    ANOMALY_STATUS = "ANOMALY_STATUS"
    BOTTLENECK_STATUS = "BOTTLENECK_STATUS"
    PRODUCTION_FORECAST = "PRODUCTION_FORECAST"
    INVENTORY_STATUS = "INVENTORY_STATUS"
    ROOT_CAUSE = "ROOT_CAUSE"
    RECOMMENDATION = "RECOMMENDATION"
    FINANCIAL_IMPACT = "FINANCIAL_IMPACT"
    WHAT_IF = "WHAT_IF"
    TEMPORAL_HISTORY = "TEMPORAL_HISTORY"
    SYSTEM_CAPABILITY = "SYSTEM_CAPABILITY"
    UNSUPPORTED_QUERY = "UNSUPPORTED_QUERY"


class CopilotStatus(str, Enum):
    """Operational status of the Copilot response."""
    SUCCESS = "SUCCESS"
    NO_SUFFICIENT_EVIDENCE = "NO_SUFFICIENT_EVIDENCE"
    INVALID_ENTITY = "INVALID_ENTITY"
    UNSUPPORTED_QUERY = "UNSUPPORTED_QUERY"
    TEMPORAL_VIOLATION = "TEMPORAL_VIOLATION"


class CopilotContext(BaseModel):
    """Contextual metadata passed along with a user query."""
    model_config = ConfigDict(extra="ignore")

    user_role: Optional[str] = Field(default="OPERATOR", description="Role of the querying user (OPERATOR, ENGINEER, MANAGER).")
    factory_id: str = Field(default="FAC_01", description="Factory identifier.")
    machine_id: Optional[str] = Field(default=None, description="Explicit machine focus if specified in UI context.")
    as_of_timestamp: Optional[str] = Field(default=None, description="Temporal horizon override (ISO-8601).")
    include_retrospective: bool = Field(default=False, description="Whether to permit access to post-cutoff controlled synthetic events.")
    include_superseded: bool = Field(default=False, description="Whether to surface historical superseded draft metrics.")


class CopilotResponse(BaseModel):
    """Complete, structured, evidence-backed decision-support response."""
    model_config = ConfigDict(from_attributes=True)

    query: str = Field(description="Original natural language query.")
    intent: CopilotIntent = Field(description="Classified operational intent.")
    status: CopilotStatus = Field(description="Operational response status.")
    answer: str = Field(description="Grounded, synthesized decision-support answer.")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Ranked evidence citations retrieved from Phase 19.")
    evidence_count: int = Field(default=0, description="Total retrieved evidence citations.")
    confidence: str = Field(default="HIGH", description="Confidence assessment (HIGH, MEDIUM, LOW, NO_EVIDENCE, ASSUMPTION_DEPENDENT).")
    machine_id: Optional[str] = Field(default=None, description="Associated plant asset identifier, if applicable.")
    factory_id: Optional[str] = Field(default="FAC_01", description="Associated factory facility identifier.")
    epistemic_status: str = Field(default=EpistemicStatus.DERIVED.value, description="Primary epistemic classification of the response.")
    as_of_timestamp: Optional[str] = Field(default=None, description="Temporal timestamp associated with the primary evidence.")
    sources: List[str] = Field(default_factory=list, description="List of source document titles cited.")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Metadata and temporal filters applied.")
    limitations: List[str] = Field(default_factory=list, description="Explicit epistemic boundaries, assumptions, and counterfactual caveats.")
    retrospective: bool = Field(default=False, description="True if answer incorporates post-cutoff retrospective ground truth.")
    provenance: List[Dict[str, Any]] = Field(default_factory=list, description="Traceability records mapping to source phases and headings.")
    rejection_reason: Optional[str] = Field(default=None, description="Explanation if status is not SUCCESS.")
