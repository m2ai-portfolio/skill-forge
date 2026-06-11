"""Snow-Town Visualization API.

FastAPI server aggregating data from Snow-Town ContractStore,
Agent Persona Academy, and Ultra Magnus for the dashboard.

Usage:
    uvicorn api.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import deps
from api.models.responses import HealthResponse
from api.routers import activity, agents, ecosystem, nodes, pipeline, research


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: eagerly initialize data sources so first request isn't slow
    deps.get_store()
    deps.get_academy()
    deps.get_um()
    yield
    # Shutdown: clean up
    deps.shutdown()


app = FastAPI(
    title="Snow-Town Visualization API",
    description="Data server for the Snow-Town ecosystem dashboard",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(activity.router)
app.include_router(ecosystem.router)
app.include_router(nodes.router)
app.include_router(agents.router)
app.include_router(pipeline.router)
app.include_router(research.router)


@app.get("/api/v1/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    sources: dict[str, str] = {}

    # Check ContractStore
    try:
        store = deps.get_store()
        store.read_outcomes(limit=1)
        sources["contract_store"] = "ok"
    except Exception as e:
        sources["contract_store"] = f"error: {e}"

    # Check Academy
    try:
        academy = deps.get_academy()
        agents_list = academy.list_agents()
        sources["academy"] = f"ok ({len(agents_list)} personas)"
    except Exception as e:
        sources["academy"] = f"error: {e}"

    # Check Ultra Magnus DB
    try:
        um = deps.get_um()
        if um.available():
            sources["ultra_magnus"] = "ok"
        else:
            sources["ultra_magnus"] = "unavailable (db not found)"
    except Exception as e:
        sources["ultra_magnus"] = f"error: {e}"

    all_ok = all(v.startswith("ok") for v in sources.values())

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        timestamp=datetime.now(),
        sources=sources,
    )
