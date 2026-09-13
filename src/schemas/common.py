"""
NirmaanAI Common API Schemas (Pydantic v2)
Standardized envelope, pagination, metadata, and error structures.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResponseMetadata(BaseModel):
    """Provenance and epistemic metadata accompanying API responses."""
    model_config = ConfigDict(from_attributes=True)

    as_of_timestamp: Optional[datetime] = Field(
        default=None,
        description="Temporal cutoff timestamp for the decision or evaluation context (UTC)."
    )
    source: Optional[str] = Field(default=None, description="Originating subsystem, model, or telemetry source.")
    dataset_version: Optional[str] = Field(default=None, description="Dataset partition or synthetic version identifier.")
    model_name: Optional[str] = Field(default=None, description="Champion model name or analytical estimator.")
    model_version: Optional[str] = Field(default=None, description="Model or heuristic artifact version.")
    pipeline_version: Optional[str] = Field(default=None, description="Upstream pipeline release version.")
    provenance: Optional[str] = Field(default=None, description="Derivation lineage.")
    epistemic_status: Optional[str] = Field(
        default=None,
        description="Epistemic status: OBSERVED_HISTORICAL, MODEL_INFERENCE, COMPOSITE_INDEX, HYPOTHETICAL_COUNTERFACTUAL, etc."
    )


class Envelope(BaseModel, Generic[T]):
    """Standard API response wrapper containing typed data and metadata."""
    model_config = ConfigDict(from_attributes=True)

    data: T
    metadata: Optional[ResponseMetadata] = None


class PaginationParams(BaseModel):
    """Standard collection query parameters."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed).")
    page_size: int = Field(default=50, ge=1, le=100, description="Items per page (max 100).")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list response."""
    model_config = ConfigDict(from_attributes=True)

    items: List[T]
    total: int = Field(ge=0, description="Total number of matching records.")
    page: int = Field(ge=1, description="Current page index.")
    page_size: int = Field(ge=1, description="Current page size.")
    total_pages: int = Field(ge=0, description="Total computed pages.")
    metadata: Optional[ResponseMetadata] = None


class ErrorDetail(BaseModel):
    """Structured error payload."""
    code: str = Field(description="Machine-readable error code.")
    message: str = Field(description="Human-readable description.")
    details: Optional[Any] = Field(default=None, description="Optional diagnostic details (no secrets or stack traces).")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: ErrorDetail
