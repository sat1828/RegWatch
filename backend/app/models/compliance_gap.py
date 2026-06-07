from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


if TYPE_CHECKING:
    from app.models.obligation import ObligationRecord
    from app.models.policy import PolicyChunk


class GapSeverity(str, __import__("enum").Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ComplianceGap(Base):
    __tablename__ = "compliance_gaps"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(__import__("uuid").uuid4())
    )
    obligation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("obligation_records.id", ondelete="CASCADE"), nullable=False
    )
    policy_chunk_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), ForeignKey("policy_chunks.id", ondelete="SET NULL"), nullable=True
    )
    gap_type: Mapped[str] = mapped_column(String(100), nullable=False, default="missing_policy")
    gap_description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[GapSeverity] = mapped_column(
        SAEnum(GapSeverity, name="gap_severity", create_constraint=True),
        default=GapSeverity.MEDIUM,
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    obligation: Mapped[ObligationRecord] = relationship(
        "ObligationRecord", back_populates="compliance_gaps"
    )
    policy_chunk: Mapped[Optional[PolicyChunk]] = relationship(
        "PolicyChunk", back_populates="compliance_gaps"
    )
