from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


if TYPE_CHECKING:
    from app.models.regulatory_document import RegulatoryDocument
    from app.models.compliance_gap import ComplianceGap


class SeverityLevel(str, __import__("enum").Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ObligationRecord(Base):
    __tablename__ = "obligation_records"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(__import__("uuid").uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False
    )
    obligation_text: Mapped[str] = mapped_column(Text, nullable=False)
    obligation_category: Mapped[str] = mapped_column(String(255), nullable=False, default="general")
    severity: Mapped[SeverityLevel] = mapped_column(
        SAEnum(SeverityLevel, name="severity_level", create_constraint=True),
        default=SeverityLevel.MEDIUM,
        nullable=False,
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    regulation_reference: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(default=True, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    document: Mapped[RegulatoryDocument] = relationship(
        "RegulatoryDocument", back_populates="obligations"
    )
    compliance_gaps: Mapped[list[ComplianceGap]] = relationship(
        "ComplianceGap", back_populates="obligation", cascade="all, delete-orphan"
    )
