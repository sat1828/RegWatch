from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    DashboardStats,
    DocumentDetail,
    DocumentListResponse,
    DocumentListItem,
    PipelineRunResponse,
    PipelineStatusResponse,
    PolicyDraftCreate,
    PolicyDraftResponse,
    PolicyDraftUpdate,
    SourceCreate,
    SourceResponse,
    SourceUpdate,
)
from app.core.deps import AuthDep, SessionDep
from app.models.audit_log import AuditLog
from app.models.base import DocumentStatus
from app.models.compliance_gap import ComplianceGap
from app.models.obligation import ObligationRecord, SeverityLevel
from app.models.policy import PolicyDraft
from app.models.regulatory_document import RegulatoryDocument
from app.models.regulatory_source import RegulatorySource
from app.models.risk_score import RiskScore
from app.orchestrator.pipeline import orchestrator
from app.state_machine.machine import StateTransitionError, pipeline_state_machine

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check() -> dict[str, Any]:
    return {"status": "ok", "service": "RegWatch", "version": "1.0.0"}


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(session: SessionDep, auth: AuthDep) -> DashboardStats:
    total_sources = await session.scalar(select(func.count(RegulatorySource.id)))
    total_documents = await session.scalar(select(func.count(RegulatoryDocument.id)))
    total_obligations = await session.scalar(select(func.count(ObligationRecord.id)))
    critical_obligations = await session.scalar(
        select(func.count(ObligationRecord.id)).where(
            ObligationRecord.severity == SeverityLevel.CRITICAL
        )
    )
    high_risk = await session.scalar(
        select(func.count(RiskScore.id)).where(RiskScore.overall_score >= 0.7)
    )
    pending_reviews = await session.scalar(
        select(func.count(PolicyDraft.id)).where(
            PolicyDraft.status == DocumentStatus.PENDING_REVIEW
        )
    )
    total_gaps = await session.scalar(select(func.count(ComplianceGap.id)))

    return DashboardStats(
        total_sources=total_sources or 0,
        total_documents=total_documents or 0,
        total_obligations=total_obligations or 0,
        critical_obligations=critical_obligations or 0,
        high_risk_items=high_risk or 0,
        pending_reviews=pending_reviews or 0,
        total_gaps=total_gaps or 0,
    )


@router.get("/sources", response_model=list[SourceResponse])
async def list_sources(
    session: SessionDep,
    auth: AuthDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[SourceResponse]:
    result = await session.execute(
        select(RegulatorySource).offset(skip).limit(limit).order_by(RegulatorySource.created_at.desc())
    )
    sources = result.scalars().all()
    return [
        SourceResponse(
            id=s.id,
            name=s.name,
            url=s.url,
            source_type=s.source_type,
            jurisdiction=s.jurisdiction,
            regulator=s.regulator,
            is_active=s.is_active,
            last_scraped_at=s.last_scraped_at,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sources
    ]


@router.post("/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: SourceCreate,
    session: SessionDep,
    auth: AuthDep,
) -> SourceResponse:
    existing = await session.execute(
        select(RegulatorySource).where(RegulatorySource.url == source_data.url)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source with this URL already exists",
        )

    source = RegulatorySource(
        name=source_data.name,
        url=source_data.url,
        source_type=source_data.source_type,
        jurisdiction=source_data.jurisdiction,
        regulator=source_data.regulator,
        is_active=source_data.is_active,
    )
    session.add(source)
    await session.commit()
    await session.refresh(source)

    return SourceResponse(
        id=source.id,
        name=source.name,
        url=source.url,
        source_type=source.source_type,
        jurisdiction=source.jurisdiction,
        regulator=source.regulator,
        is_active=source.is_active,
        last_scraped_at=source.last_scraped_at,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str,
    session: SessionDep,
    auth: AuthDep,
) -> SourceResponse:
    source = await session.get(RegulatorySource, source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return SourceResponse(
        id=source.id,
        name=source.name,
        url=source.url,
        source_type=source.source_type,
        jurisdiction=source.jurisdiction,
        regulator=source.regulator,
        is_active=source.is_active,
        last_scraped_at=source.last_scraped_at,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: str,
    update_data: SourceUpdate,
    session: SessionDep,
    auth: AuthDep,
) -> SourceResponse:
    source = await session.get(RegulatorySource, source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    if update_data.name is not None:
        source.name = update_data.name
    if update_data.url is not None:
        source.url = update_data.url
    if update_data.is_active is not None:
        source.is_active = update_data.is_active
    if update_data.scrape_interval_minutes is not None:
        source.scrape_interval_minutes = update_data.scrape_interval_minutes

    session.add(source)
    await session.commit()
    await session.refresh(source)

    return SourceResponse(
        id=source.id,
        name=source.name,
        url=source.url,
        source_type=source.source_type,
        jurisdiction=source.jurisdiction,
        regulator=source.regulator,
        is_active=source.is_active,
        last_scraped_at=source.last_scraped_at,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: str, session: SessionDep, auth: AuthDep) -> None:
    source = await session.get(RegulatorySource, source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    await session.delete(source)
    await session.commit()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    session: SessionDep,
    auth: AuthDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: str | None = Query(None, alias="status"),
    source_id: str | None = Query(None),
) -> DocumentListResponse:
    query = select(RegulatoryDocument).order_by(RegulatoryDocument.created_at.desc())

    if status_filter:
        try:
            doc_status = DocumentStatus(status_filter.upper())
            query = query.where(RegulatoryDocument.status == doc_status)
        except ValueError:
            pass

    if source_id:
        query = query.where(RegulatoryDocument.source_id == source_id)

    total = await session.scalar(
        select(func.count()).select_from(query.subquery())
    )
    result = await session.execute(query.offset(skip).limit(limit))
    docs = result.scalars().all()

    items = []
    for doc in docs:
        risk_score = None
        if doc.risk_scores:
            risk_score = max(doc.risk_scores, key=lambda rs: rs.overall_score).overall_score

        items.append(
            DocumentListItem(
                id=doc.id,
                title=doc.title,
                source_name=doc.source.name if doc.source else "Unknown",
                document_type=doc.document_type,
                status=doc.status.value,
                risk_score=risk_score,
                obligation_count=len(doc.obligations) if doc.obligations else 0,
                published_date=doc.published_date,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
        )

    return DocumentListResponse(items=items, total=total or 0)


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    session: SessionDep,
    auth: AuthDep,
) -> DocumentDetail:
    doc = await session.get(RegulatoryDocument, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    obligations = [
        {
            "id": o.id,
            "obligation_text": o.obligation_text,
            "obligation_category": o.obligation_category,
            "severity": o.severity.value,
            "deadline": o.deadline,
            "regulation_reference": o.regulation_reference,
            "is_mandatory": o.is_mandatory,
        }
        for o in (doc.obligations or [])
    ]

    risk_scores_list = [
        {
            "id": rs.id,
            "overall_score": rs.overall_score,
            "penalty_score": rs.penalty_score,
            "deadline_score": rs.deadline_score,
            "enforcement_score": rs.enforcement_score,
            "priority_rank": rs.priority_rank,
            "risk_category": rs.risk_category,
            "reasoning": rs.reasoning,
        }
        for rs in (doc.risk_scores or [])
    ]

    gaps = []
    for o in (doc.obligations or []):
        for g in (o.compliance_gaps or []):
            gaps.append({
                "id": g.id,
                "gap_type": g.gap_type,
                "gap_description": g.gap_description,
                "severity": g.severity.value,
                "confidence_score": g.confidence_score,
                "recommendation": g.recommendation,
            })

    drafts = [
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "status": d.status.value,
            "change_summary": d.change_summary,
            "created_at": d.created_at,
        }
        for d in (doc.policy_drafts or [])
    ]

    return DocumentDetail(
        id=doc.id,
        title=doc.title,
        url=doc.url,
        source_name=doc.source.name if doc.source else "Unknown",
        document_type=doc.document_type,
        status=doc.status.value,
        raw_text=doc.raw_text,
        delta_text=doc.delta_text,
        published_date=doc.published_date,
        effective_date=doc.effective_date,
        is_amendment=doc.is_amendment,
        obligations=obligations,
        risk_scores=risk_scores_list,
        gaps=gaps,
        drafts=drafts,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("/documents/{document_id}/transition")
async def transition_document(
    document_id: str,
    target_status: str,
    session: SessionDep,
    auth: AuthDep,
) -> dict[str, str]:
    doc = await session.get(RegulatoryDocument, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    try:
        target = DocumentStatus(target_status.upper())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {target_status}")

    try:
        pipeline_state_machine.transition(doc.status, target)
        doc.status = target
        session.add(doc)
        await session.commit()
        return {"status": target.value, "message": f"Transitioned to {target.value}"}
    except StateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/pipeline/status/{pipeline_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(pipeline_id: str, auth: AuthDep) -> PipelineStatusResponse:
    status_data = orchestrator.get_pipeline_status(pipeline_id)
    if not status_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline run not found")
    return PipelineStatusResponse(
        pipeline_id=pipeline_id,
        status=status_data.get("status", "unknown"),
        started_at=status_data.get("started_at"),
        completed_at=status_data.get("completed_at"),
        error=status_data.get("error"),
    )


@router.post("/pipeline/run", response_model=PipelineRunResponse)
async def run_pipeline(
    session: SessionDep,
    auth: AuthDep,
    mode: str = Query("full", regex="^(full|watcher)$"),
) -> PipelineRunResponse:
    if mode == "watcher":
        pipeline_id = await orchestrator.run_watcher_only({"trigger": "manual"})
    else:
        pipeline_id = await orchestrator.run_full_pipeline({"trigger": "manual"})
    return PipelineRunResponse(pipeline_id=pipeline_id, status="started")


@router.get("/drafts", response_model=list[PolicyDraftResponse])
async def list_drafts(
    session: SessionDep,
    auth: AuthDep,
    status_filter: str | None = Query(None, alias="status"),
) -> list[PolicyDraftResponse]:
    query = select(PolicyDraft).order_by(PolicyDraft.created_at.desc())
    if status_filter:
        try:
            draft_status = DocumentStatus(status_filter.upper())
            query = query.where(PolicyDraft.status == draft_status)
        except ValueError:
            pass

    result = await session.execute(query)
    drafts = result.scalars().all()

    return [
        PolicyDraftResponse(
            id=d.id,
            document_id=d.document_id,
            title=d.title,
            content=d.content,
            status=d.status.value,
            change_summary=d.change_summary,
            reviewed_by=d.reviewed_by,
            reviewed_at=d.reviewed_at,
            review_notes=d.review_notes,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in drafts
    ]


@router.post("/drafts", response_model=PolicyDraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    draft_data: PolicyDraftCreate,
    session: SessionDep,
    auth: AuthDep,
) -> PolicyDraftResponse:
    doc = await session.get(RegulatoryDocument, draft_data.document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    draft = PolicyDraft(
        document_id=draft_data.document_id,
        title=draft_data.title,
        content=draft_data.content,
        change_summary=draft_data.change_summary,
    )
    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    return PolicyDraftResponse(
        id=draft.id,
        document_id=draft.document_id,
        title=draft.title,
        content=draft.content,
        status=draft.status.value,
        change_summary=draft.change_summary,
        reviewed_by=draft.reviewed_by,
        reviewed_at=draft.reviewed_at,
        review_notes=draft.review_notes,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


@router.put("/drafts/{draft_id}/review", response_model=PolicyDraftResponse)
async def review_draft(
    draft_id: str,
    review_data: PolicyDraftUpdate,
    session: SessionDep,
    auth: AuthDep,
) -> PolicyDraftResponse:
    draft = await session.get(PolicyDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")

    try:
        target = DocumentStatus(review_data.status.upper())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {review_data.status}")

    try:
        pipeline_state_machine.transition(draft.status, target)
    except StateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    draft.status = target
    draft.reviewed_by = review_data.reviewed_by
    draft.review_notes = review_data.review_notes

    from datetime import datetime, timezone
    draft.reviewed_at = datetime.now(timezone.utc)

    session.add(draft)

    if target == DocumentStatus.APPROVED:
        doc = draft.document
        if doc and doc.status == DocumentStatus.NOTIFIED:
            try:
                pipeline_state_machine.transition(doc.status, DocumentStatus.PENDING_REVIEW)
                doc.status = DocumentStatus.PENDING_REVIEW
                session.add(doc)
            except StateTransitionError:
                pass

    await session.commit()
    await session.refresh(draft)

    return PolicyDraftResponse(
        id=draft.id,
        document_id=draft.document_id,
        title=draft.title,
        content=draft.content,
        status=draft.status.value,
        change_summary=draft.change_summary,
        reviewed_by=draft.reviewed_by,
        reviewed_at=draft.reviewed_at,
        review_notes=draft.review_notes,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


@router.get("/audit-logs", response_model=list[dict[str, Any]])
async def list_audit_logs(
    session: SessionDep,
    auth: AuthDep,
    limit: int = Query(50, ge=1, le=500),
) -> list[dict[str, Any]]:
    result = await session.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "actor": log.actor,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]
