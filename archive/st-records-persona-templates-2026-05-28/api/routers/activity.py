"""Activity feed endpoint.

Aggregates recent events from all three contract types into a unified
chronological feed for the operator dashboard.
"""

from datetime import datetime

from fastapi import APIRouter, Query

from api.deps import get_store
from api.models.responses import ActivityEvent

router = APIRouter(prefix="/api/v1", tags=["activity"])


@router.get("/activity", response_model=list[ActivityEvent])
def get_activity(limit: int = Query(default=50, ge=1, le=200)) -> list[ActivityEvent]:
    store = get_store()

    events: list[ActivityEvent] = []

    # OutcomeRecords -> "outcome" events
    for o in store.query_outcomes(limit=200):
        events.append(ActivityEvent(
            event_type="outcome",
            id=str(o.idea_id),
            title=o.idea_title,
            status=o.outcome.value,
            node_id="ultra_magnus",
            timestamp=o.emitted_at,
            detail={
                "idea_id": o.idea_id,
                "overall_score": o.overall_score,
                "recommendation": o.recommendation,
                "github_url": o.github_url,
            },
        ))

    # ImprovementRecommendations -> "recommendation" events
    for r in store.query_recommendations(limit=200):
        events.append(ActivityEvent(
            event_type="recommendation",
            id=r.recommendation_id,
            title=r.title,
            status=r.status,
            node_id="sky_lynx",
            timestamp=r.emitted_at,
            detail={
                "recommendation_type": r.recommendation_type.value,
                "priority": r.priority,
                "target_system": r.target_system,
            },
        ))

    # PersonaUpgradePatches -> "patch" events
    for p in store.query_patches(limit=200):
        events.append(ActivityEvent(
            event_type="patch",
            id=p.patch_id,
            title=f"Patch for {p.persona_id}",
            status=p.status,
            node_id="academy",
            timestamp=p.emitted_at,
            detail={
                "persona_id": p.persona_id,
                "from_version": p.from_version,
                "to_version": p.to_version,
                "rationale": p.rationale,
            },
        ))

    # Sort by timestamp descending, then limit
    events.sort(key=lambda e: e.timestamp, reverse=True)
    return events[:limit]
