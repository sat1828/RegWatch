"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=True),
        sa.Column("actor", sa.String(255), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "enforcement_actions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("regulator", sa.String(255), nullable=False),
        sa.Column("entity_name", sa.String(512), nullable=False),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("penalty_amount", sa.Float, nullable=True),
        sa.Column("regulation_type", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("action_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("reference_url", sa.String(1024), nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "policy_documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("category", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("version", sa.Integer, default=1, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "regulatory_sources",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False, unique=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("jurisdiction", sa.String(100), nullable=False),
        sa.Column("regulator", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("scrape_interval_minutes", sa.Integer, default=1440, nullable=False),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_raw_text", sa.Text, nullable=True),
        sa.Column("last_content_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "policy_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("policy_document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("policy_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "regulatory_documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("regulatory_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("previous_raw_text", sa.Text, nullable=True),
        sa.Column("delta_text", sa.Text, nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("status", sa.Enum("DETECTED", "ANALYZED", "MAPPED", "SCORED", "NOTIFIED", "PENDING_REVIEW", "APPROVED", "REJECTED", "CLOSED", name="document_status"), nullable=False),
        sa.Column("published_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("is_amendment", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "obligation_records",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_text", sa.Text, nullable=False),
        sa.Column("obligation_category", sa.String(255), nullable=False),
        sa.Column("severity", sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", name="severity_level"), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("regulation_reference", sa.String(512), nullable=True),
        sa.Column("is_mandatory", sa.Boolean, default=True, nullable=False),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "risk_scores",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_score", sa.Float, nullable=False),
        sa.Column("penalty_score", sa.Float, nullable=False),
        sa.Column("deadline_score", sa.Float, nullable=False),
        sa.Column("enforcement_score", sa.Float, nullable=False),
        sa.Column("priority_rank", sa.Integer, nullable=False),
        sa.Column("risk_category", sa.String(50), nullable=False),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "policy_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("regulatory_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_document_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("policy_documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("status", sa.Enum("DETECTED", "ANALYZED", "MAPPED", "SCORED", "NOTIFIED", "PENDING_REVIEW", "APPROVED", "REJECTED", "CLOSED", name="draft_status"), nullable=False),
        sa.Column("change_summary", sa.Text, nullable=True),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "compliance_gaps",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("obligation_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("obligation_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_chunk_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("policy_chunks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("gap_type", sa.String(100), nullable=False),
        sa.Column("gap_description", sa.Text, nullable=False),
        sa.Column("severity", sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="gap_severity"), nullable=False),
        sa.Column("confidence_score", sa.Float, default=0.0, nullable=False),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("reasoning", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("compliance_gaps")
    op.drop_table("policy_drafts")
    op.drop_table("risk_scores")
    op.drop_table("obligation_records")
    op.drop_table("regulatory_documents")
    op.drop_table("policy_chunks")
    op.drop_table("regulatory_sources")
    op.drop_table("policy_documents")
    op.drop_table("enforcement_actions")
    op.drop_table("audit_logs")

    op.execute("DROP TYPE IF EXISTS document_status")
    op.execute("DROP TYPE IF EXISTS severity_level")
    op.execute("DROP TYPE IF EXISTS draft_status")
    op.execute("DROP TYPE IF EXISTS gap_severity")
