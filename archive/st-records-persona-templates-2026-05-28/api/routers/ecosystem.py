"""Ecosystem snapshot endpoint.

Aggregates data from ContractStore to produce a full ecosystem view
with node metrics, edge metrics, and loop health — mirroring the logic
in scripts/loop_status.py.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter

from api.deps import get_store
from api.models.responses import (
    EcosystemSnapshot,
    EdgeMetrics,
    NodeMetrics,
)

router = APIRouter(prefix="/api/v1", tags=["ecosystem"])

STALE_THRESHOLD_DAYS = 7


def _health_status(record_count: int, last_activity: datetime | None) -> str:
    if record_count == 0:
        return "idle"
    if last_activity and (datetime.now() - last_activity).days > STALE_THRESHOLD_DAYS:
        return "stale"
    return "healthy"


def _recent_count(records: list, days: int = 7) -> int:
    cutoff = datetime.now() - timedelta(days=days)
    return sum(1 for r in records if r.emitted_at >= cutoff)


@router.get("/ecosystem", response_model=EcosystemSnapshot)
def get_ecosystem() -> EcosystemSnapshot:
    store = get_store()

    outcomes = store.read_outcomes(limit=10000)
    recommendations = store.read_recommendations(limit=10000)
    patches = store.read_patches(limit=10000)
    signals = store.read_signals(limit=10000)

    # --- Node: Ultra Magnus (outcomes) ---
    outcome_counts: dict[str, int] = {}
    for o in outcomes:
        outcome_counts[o.outcome.value] = outcome_counts.get(o.outcome.value, 0) + 1

    um_last = max((o.emitted_at for o in outcomes), default=None)
    um_node = NodeMetrics(
        node_id="ultra_magnus",
        display_name="Ultra Magnus",
        record_count=len(outcomes),
        pending_count=0,  # outcomes are terminal, no pending state
        last_activity=um_last,
        health_status=_health_status(len(outcomes), um_last),
        breakdown=outcome_counts if outcome_counts else None,
    )

    # --- Node: Sky-Lynx (recommendations) ---
    pending_recs = [r for r in recommendations if r.status == "pending"]
    rec_breakdown: dict[str, int] = {}
    for r in pending_recs:
        key = f"pending_{r.target_system}"
        rec_breakdown[key] = rec_breakdown.get(key, 0) + 1
    applied_count = sum(1 for r in recommendations if r.status == "applied")
    rec_breakdown["applied"] = applied_count

    sl_last = max((r.emitted_at for r in recommendations), default=None)
    sl_node = NodeMetrics(
        node_id="sky_lynx",
        display_name="Sky-Lynx",
        record_count=len(recommendations),
        pending_count=len(pending_recs),
        last_activity=sl_last,
        health_status=_health_status(len(recommendations), sl_last),
        breakdown=rec_breakdown if rec_breakdown else None,
    )

    # --- Node: Academy (patches) ---
    proposed = [p for p in patches if p.status == "proposed"]
    applied_patches = [p for p in patches if p.status == "applied"]
    rejected = [p for p in patches if p.status == "rejected"]
    patch_breakdown = {
        "proposed": len(proposed),
        "applied": len(applied_patches),
        "rejected": len(rejected),
    }

    ac_last = max((p.emitted_at for p in patches), default=None)
    ac_node = NodeMetrics(
        node_id="academy",
        display_name="Academy",
        record_count=len(patches),
        pending_count=len(proposed),
        last_activity=ac_last,
        health_status=_health_status(len(patches), ac_last),
        breakdown=patch_breakdown,
    )

    # --- Node: Research Agents (signals) ---
    signal_by_source: dict[str, int] = {}
    for s in signals:
        signal_by_source[s.source.value] = signal_by_source.get(s.source.value, 0) + 1

    ra_last = max((s.emitted_at for s in signals), default=None)
    ra_node = NodeMetrics(
        node_id="research_agents",
        display_name="Research Agents",
        record_count=len(signals),
        pending_count=0,
        last_activity=ra_last,
        health_status=_health_status(len(signals), ra_last),
        breakdown=signal_by_source if signal_by_source else None,
    )

    # --- Edges ---
    edges = [
        EdgeMetrics(
            source="ultra_magnus",
            target="sky_lynx",
            label="OutcomeRecord",
            total_records=len(outcomes),
            recent_count=_recent_count(outcomes),
        ),
        EdgeMetrics(
            source="sky_lynx",
            target="academy",
            label="ImprovementRecommendation",
            total_records=len(recommendations),
            recent_count=_recent_count(recommendations),
        ),
        EdgeMetrics(
            source="academy",
            target="ultra_magnus",
            label="PersonaUpgradePatch",
            total_records=len(patches),
            recent_count=_recent_count(patches),
        ),
        EdgeMetrics(
            source="research_agents",
            target="sky_lynx",
            label="ResearchSignal",
            total_records=len(signals),
            recent_count=_recent_count(signals),
        ),
    ]

    # --- Cycle count (patches with source_recommendation_ids that are applied) ---
    patch_source_ids: set[str] = set()
    for p in applied_patches:
        patch_source_ids.update(p.source_recommendation_ids)
    cycle_count = len(patch_source_ids)

    # --- Loop health ---
    if not outcomes and not recommendations and not patches:
        loop_health = "idle"
    elif outcomes and recommendations and patches:
        loop_health = "flowing"
    else:
        loop_health = "partial"

    return EcosystemSnapshot(
        timestamp=datetime.now(),
        cycle_count=cycle_count,
        nodes=[um_node, sl_node, ac_node, ra_node],
        edges=edges,
        loop_health=loop_health,
    )
