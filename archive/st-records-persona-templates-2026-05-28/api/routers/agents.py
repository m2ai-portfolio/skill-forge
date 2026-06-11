"""Agent/persona endpoints.

Lists and details for all personas from the Agent Persona Academy.
"""

from fastapi import APIRouter, HTTPException

from api.deps import get_academy
from api.models.responses import AgentDetail, AgentSummary

router = APIRouter(prefix="/api/v1", tags=["agents"])


@router.get("/agents", response_model=list[AgentSummary])
def list_agents() -> list[AgentSummary]:
    return get_academy().list_agents()


@router.get("/agents/{agent_id}", response_model=AgentDetail)
def get_agent(agent_id: str) -> AgentDetail:
    agent = get_academy().get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent not found: '{agent_id}'")
    return agent
