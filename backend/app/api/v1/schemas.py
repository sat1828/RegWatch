from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    total_sources: int = 0
    total_documents: int = 0
    total_obligations: int = 0
    critical_obligations: int = 0
    high_risk_items: int = 0
    pending_reviews: int = 0
    total_gaps: int = 0


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=1024)
    source_type: str = Field(default="html_index")
    jurisdiction: str = Field(default="IN")
    regulator: str = Field(default="SEBI")
    is_active: bool = Field(default=True)


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
    scrape_interval_minutes: Optional[int] = None


class SourceResponse(BaseModel):
    id: str
    name: str
    url: str
    source_type: str
    jurisdiction: str
    regulator: str
    is_active: bool
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListItem(BaseModel):
    id: str
    title: str
    source_name: str
    document_type: str
    status: str
    risk_score: Optional[float] = None
    obligation_count: int = 0
    published_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int


class DocumentDetail(BaseModel):
    id: str
    title: str
    url: str
    source_name: str
    document_type: str
    status: str
    raw_text: Optional[str] = None
    delta_text: Optional[str] = None
    published_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    is_amendment: bool = False
    obligations: list[dict[str, Any]] = []
    risk_scores: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    drafts: list[dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime


class PipelineRunResponse(BaseModel):
    pipeline_id: str
    status: str = "started"


class PipelineStatusResponse(BaseModel):
    pipeline_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class PolicyDraftCreate(BaseModel):
    document_id: str
    title: str = Field(..., min_length=1, max_length=512)
    content: str = Field(..., min_length=1)
    change_summary: Optional[str] = None


class PolicyDraftUpdate(BaseModel):
    status: str = Field(..., pattern="^(APPROVED|REJECTED|PENDING_REVIEW)$")
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class PolicyDraftResponse(BaseModel):
    id: str
    document_id: str
    title: str
    content: str
    status: str
    change_summary: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
