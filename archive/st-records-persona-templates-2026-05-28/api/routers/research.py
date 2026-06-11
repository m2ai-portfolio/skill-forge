"""Research signals API endpoints.

Provides access to research intelligence signals stored
in the ContractStore.
"""

from datetime import datetime

from fastapi import APIRouter, Query

from api.deps import get_store

router = APIRouter(prefix="/api/v1/research", tags=["research"])


@router.get("/signals")
def list_signals(
    source: str | None = Query(default=None, description="Filter by source (arxiv_hf, tool_monitor, domain_watch)"),
    relevance: str | None = Query(default=None, description="Filter by relevance (high, medium, low)"),
    domain: str | None = Query(default=None, description="Filter by domain"),
    consumed: bool | None = Query(default=None, description="Filter by consumed status"),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict]:
    """List research signals with optional filtering."""
    store = get_store()
    signals = store.query_signals(
        source=source,
        relevance=relevance,
        domain=domain,
        consumed=consumed,
        limit=limit,
    )
    return [
        {
            "signal_id": s.signal_id,
            "source": s.source.value,
            "title": s.title,
            "summary": s.summary,
            "url": s.url,
            "relevance": s.relevance.value,
            "relevance_rationale": s.relevance_rationale,
            "tags": s.tags,
            "domain": s.domain,
            "consumed_by": s.consumed_by,
            "emitted_at": s.emitted_at.isoformat(),
        }
        for s in signals
    ]


@router.get("/summary")
def get_summary() -> dict:
    """Get aggregate research signal statistics."""
    store = get_store()
    all_signals = store.query_signals(limit=10000)

    by_source: dict[str, int] = {}
    by_relevance: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    consumed = 0
    unconsumed = 0

    for s in all_signals:
        by_source[s.source.value] = by_source.get(s.source.value, 0) + 1
        by_relevance[s.relevance.value] = by_relevance.get(s.relevance.value, 0) + 1
        if s.domain:
            by_domain[s.domain] = by_domain.get(s.domain, 0) + 1
        if s.consumed_by:
            consumed += 1
        else:
            unconsumed += 1

    newest = max((s.emitted_at for s in all_signals), default=None)

    return {
        "total": len(all_signals),
        "by_source": by_source,
        "by_relevance": by_relevance,
        "by_domain": by_domain,
        "consumed": consumed,
        "unconsumed": unconsumed,
        "last_signal_at": newest.isoformat() if newest else None,
    }
