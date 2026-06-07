from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.base import DocumentStatus

if TYPE_CHECKING:
    from app.models.regulatory_document import RegulatoryDocument


class RegulatorySource(Base):
    __tablename__ = "regulatory_sources"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(__import__("uuid").uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="html_index"
    )
    jurisdiction: Mapped[str] = mapped_column(String(100), nullable=False, default="IN")
    regulator: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scrape_interval_minutes: Mapped[int] = mapped_column(default=1440, nullable=False)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    documents: Mapped[list[RegulatoryDocument]] = relationship(
        "RegulatoryDocument", back_populates="source", cascade="all, delete-orphan"
    )
