"""Pipeline endpoints for Ultra Magnus ideas.

Read-only access to the caught_ideas.db via UMReader.
"""

from fastapi import APIRouter, HTTPException, Query

from api.deps import get_um
from api.models.responses import IdeaDetail, IdeaSummary

router = APIRouter(prefix="/api/v1", tags=["pipeline"])


@router.get("/pipeline/ideas", response_model=list[IdeaSummary])
def list_ideas(
    stage: str | None = Query(None, description="Filter by pipeline stage"),
    status: str | None = Query(None, description="Filter by processing status"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
) -> list[IdeaSummary]:
    return get_um().list_ideas(stage=stage, status=status, limit=limit)


@router.get("/pipeline/ideas/{idea_id}", response_model=IdeaDetail)
def get_idea(idea_id: int) -> IdeaDetail:
    idea = get_um().get_idea(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail=f"Idea not found: {idea_id}")
    return idea


@router.get("/pipeline/stages", response_model=dict[str, int])
def get_stage_counts() -> dict[str, int]:
    """Count of ideas grouped by pipeline stage — for funnel visualization."""
    return get_um().count_by_stage()
