"""Pydantic response models for the Snow-Town visualization API."""

from datetime import datetime

from pydantic import BaseModel, Field


# --- Ecosystem ---


class NodeMetrics(BaseModel):
    """Metrics for a single ecosystem node (UM, SL, or Academy)."""

    node_id: str
    display_name: str
    record_count: int
    pending_count: int
    last_activity: datetime | None = None
    health_status: str  # "healthy" | "idle" | "stale"
    breakdown: dict[str, int] | None = None


class EdgeMetrics(BaseModel):
    """Metrics for data flow between two nodes."""

    source: str
    target: str
    label: str
    total_records: int
    recent_count: int  # last 7 days


class EcosystemSnapshot(BaseModel):
    """Full ecosystem state at a point in time."""

    timestamp: datetime
    cycle_count: int
    nodes: list[NodeMetrics]
    edges: list[EdgeMetrics]
    loop_health: str  # "flowing" | "partial" | "idle"


# --- Agents / Personas ---


class AgentSummary(BaseModel):
    """Lightweight persona summary for list views."""

    id: str
    name: str
    role: str
    category: str
    framework_count: int
    case_study_count: int
    status: str = "available"


class AgentDetail(AgentSummary):
    """Full persona detail including voice, frameworks, case studies."""

    background: str
    era: str | None = None
    notable_works: list[str] = Field(default_factory=list)
    voice_tone: list[str] = Field(default_factory=list)
    voice_phrases: list[str] = Field(default_factory=list)
    voice_style: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    case_studies: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# --- Pipeline (Ultra Magnus ideas) ---


class IdeaSummary(BaseModel):
    """Lightweight idea summary for list views."""

    id: int
    title: str
    stage: str
    status: str
    overall_score: float | None = None
    recommendation: str | None = None
    caught_at: datetime
    tags: list[str] = Field(default_factory=list)


class IdeaDetail(IdeaSummary):
    """Full idea detail with pipeline results."""

    raw_content: str
    source_context: str | None = None
    enrichment_result: dict | None = None
    evaluation_result: dict | None = None
    scaffolding_result: dict | None = None
    build_result: dict | None = None
    review_decision: str | None = None
    review_notes: str | None = None
    github_url: str | None = None
    completed_at: datetime | None = None


# --- Node Detail ---


class RecentRecord(BaseModel):
    """A recent record from any contract type, for node detail views."""

    record_type: str  # "outcome" | "recommendation" | "patch"
    id: str
    title: str
    status: str
    emitted_at: datetime
    extra: dict = Field(default_factory=dict)


class NodeDetail(BaseModel):
    """Detailed view of a single ecosystem node."""

    node_id: str
    display_name: str
    health_status: str
    last_activity: datetime | None = None
    metrics: NodeMetrics
    recent_records: list[RecentRecord] = Field(default_factory=list)


# --- Health ---


class ActivityEvent(BaseModel):
    """Unified activity event from any contract type."""

    event_type: str  # "outcome" | "recommendation" | "patch"
    id: str
    title: str
    status: str
    node_id: str  # "ultra_magnus" | "sky_lynx" | "academy"
    timestamp: datetime
    detail: dict = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Lightweight health check response."""

    status: str = "ok"
    timestamp: datetime
    sources: dict[str, str] = Field(default_factory=dict)
