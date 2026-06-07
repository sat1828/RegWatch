from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import DocumentStatus

if TYPE_CHECKING:
    from app.models.obligation import ObligationRecord
    from app.models.policy import PolicyDraft
    from app.models.risk_score import RiskScore
    from app.models.regulatory_source import RegulatorySource


class RegulatoryDocument(Base):
    __tablename__ = "regulatory_documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(__import__("uuid").uuid4())
    )
    source_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("regulatory_sources.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, default="circular")
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delta_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status", create_constraint=True),
        default=DocumentStatus.DETECTED,
        nullable=False,
    )
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_amendment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    source: Mapped[RegulatorySource] = relationship(
        "RegulatorySource", back_populates="documents"
    )
    obligations: Mapped[list[ObligationRecord]] = relationship(
        "ObligationRecord", back_populates="document", cascade="all, delete-orphan"
    )
    risk_scores: Mapped[list[RiskScore]] = relationship(
        "RiskScore", back_populates="document", cascade="all, delete-orphan"
    )
    policy_drafts: Mapped[list[PolicyDraft]] = relationship(
        "PolicyDraft", back_populates="document", cascade="all, delete-orphan"
    )
