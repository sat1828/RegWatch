from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class DocumentStatus(str, Enum):
    DETECTED = "DETECTED"
    ANALYZED = "ANALYZED"
    MAPPED = "MAPPED"
    SCORED = "SCORED"
    NOTIFIED = "NOTIFIED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"
