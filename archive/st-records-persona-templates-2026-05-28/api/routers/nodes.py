"""Node detail endpoints.

Returns detailed view for each ecosystem node including recent records
and per-node metrics breakdown.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.deps import get_store
from api.models.responses import NodeDetail, NodeMetrics, RecentRecord
from api.routers.ecosystem import _health_status

router = APIRouter(prefix="/api/v1", tags=["nodes"])

VALID_NODES = {"ultra_magnus", "sky_lynx", "academy"}
DISPLAY_NAMES = {
    "ultra_magnus": "Ultra Magnus",
    "sky_lynx": "Sky-Lynx",
    "academy": "Academy",
}


@router.get("/nodes/{node_id}", response_model=NodeDetail)
def get_node_detail(node_id: str) -> NodeDetail:
    if node_id not in VALID_NODES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown node: '{node_id}'. Valid: {', '.join(sorted(VALID_NODES))}",
        )

    store = get_store()

    if node_id == "ultra_magnus":
        return _build_um_detail(store)
    elif node_id == "sky_lynx":
        return _build_sl_detail(store)
    else:
        return _build_academy_detail(store)


def _build_um_detail(store) -> NodeDetail:
    outcomes = store.read_outcomes(limit=10000)
    breakdown: dict[str, int] = {}
    for o in outcomes:
        breakdown[o.outcome.value] = breakdown.get(o.outcome.value, 0) + 1

    last = max((o.emitted_at for o in outcomes), default=None)
    recent = sorted(outcomes, key=lambda o: o.emitted_at, reverse=True)[:20]

    return NodeDetail(
        node_id="ultra_magnus",
        display_name="Ultra Magnus",
        health_status=_health_status(len(outcomes), last),
        last_activity=last,
        metrics=NodeMetrics(
            node_id="ultra_magnus",
            display_name="Ultra Magnus",
            record_count=len(outcomes),
            pending_count=0,
            last_activity=last,
            health_status=_health_status(len(outcomes), last),
            breakdown=breakdown if breakdown else None,
        ),
        recent_records=[
            RecentRecord(
                record_type="outcome",
                id=str(o.idea_id),
                title=o.idea_title,
                status=o.outcome.value,
                emitted_at=o.emitted_at,
                extra={
                    "overall_score": o.overall_score,
                    "recommendation": o.recommendation,
                    "github_url": o.github_url,
                },
            )
            for o in recent
        ],
    )


def _build_sl_detail(store) -> NodeDetail:
    recs = store.read_recommendations(limit=10000)
    pending = [r for r in recs if r.status == "pending"]
    breakdown: dict[str, int] = {}
    for r in recs:
        key = f"{r.target_system}_{r.status}"
        breakdown[key] = breakdown.get(key, 0) + 1

    last = max((r.emitted_at for r in recs), default=None)
    recent = sorted(recs, key=lambda r: r.emitted_at, reverse=True)[:20]

    return NodeDetail(
        node_id="sky_lynx",
        display_name="Sky-Lynx",
        health_status=_health_status(len(recs), last),
        last_activity=last,
        metrics=NodeMetrics(
            node_id="sky_lynx",
            display_name="Sky-Lynx",
            record_count=len(recs),
            pending_count=len(pending),
            last_activity=last,
            health_status=_health_status(len(recs), last),
            breakdown=breakdown if breakdown else None,
        ),
        recent_records=[
            RecentRecord(
                record_type="recommendation",
                id=r.recommendation_id,
                title=r.title,
                status=r.status,
                emitted_at=r.emitted_at,
                extra={
                    "recommendation_type": r.recommendation_type.value,
                    "target_system": r.target_system,
                    "priority": r.priority,
                },
            )
            for r in recent
        ],
    )


def _build_academy_detail(store) -> NodeDetail:
    patches = store.read_patches(limit=10000)
    proposed = [p for p in patches if p.status == "proposed"]
    breakdown = {
        "proposed": sum(1 for p in patches if p.status == "proposed"),
        "applied": sum(1 for p in patches if p.status == "applied"),
        "rejected": sum(1 for p in patches if p.status == "rejected"),
    }

    last = max((p.emitted_at for p in patches), default=None)
    recent = sorted(patches, key=lambda p: p.emitted_at, reverse=True)[:20]

    return NodeDetail(
        node_id="academy",
        display_name="Academy",
        health_status=_health_status(len(patches), last),
        last_activity=last,
        metrics=NodeMetrics(
            node_id="academy",
            display_name="Academy",
            record_count=len(patches),
            pending_count=len(proposed),
            last_activity=last,
            health_status=_health_status(len(patches), last),
            breakdown=breakdown,
        ),
        recent_records=[
            RecentRecord(
                record_type="patch",
                id=p.patch_id,
                title=f"Patch for {p.persona_id}",
                status=p.status,
                emitted_at=p.emitted_at,
                extra={
                    "persona_id": p.persona_id,
                    "rationale": p.rationale,
                    "from_version": p.from_version,
                    "to_version": p.to_version,
                },
            )
            for p in recent
        ],
    )
