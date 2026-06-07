from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


if TYPE_CHECKING:
    from app.models.regulatory_document import RegulatoryDocument


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(__import__("uuid").uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    penalty_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deadline_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    enforcement_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=999)
    risk_category: Mapped[str] = mapped_column(String(50), nullable=False, default="UNASSIGNED")
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    document: Mapped[RegulatoryDocument] = relationship(
        "RegulatoryDocument", back_populates="risk_scores"
    )
