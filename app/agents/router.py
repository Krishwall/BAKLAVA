from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.model import Agent
from app.agents.schemas import AgentCreate, AgentResponse
from app.capabilities.model import Capability
from app.db.agent_capability import AgentCapability
from app.db.agent_tool import AgentTool
from app.db.database import get_db
from app.tools.model import Tool

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.post(
    "/{agent_id}/capabilities/{capability_id}", status_code=status.HTTP_201_CREATED
)
def assign_capability(
    agent_id: str,
    capability_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    capability = db.get(Capability, capability_id)

    if not capability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability not found",
        )

    existing = db.get(
        AgentCapability,
        (agent_id, capability_id),
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capability already assigned to agent",
        )

    assignment = AgentCapability(
        agent_id=agent_id,
        capability_id=capability_id,
    )

    db.add(assignment)
    db.commit()

    return {
        "agent_id": agent_id,
        "capability_id": capability_id,
    }


@router.get("/{agent_id}/capabilities")
def list_agent_capabilities(
    agent_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    capabilities = (
        db.query(Capability)
        .join(
            AgentCapability,
            Capability.capability_id == AgentCapability.capability_id,
        )
        .filter(AgentCapability.agent_id == agent_id)
        .all()
    )

    return capabilities


@router.delete(
    "/{agent_id}/capabilities/{capability_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_capability(
    agent_id: str,
    capability_id: str,
    db: Session = Depends(get_db),
):
    assignment = db.get(
        AgentCapability,
        (agent_id, capability_id),
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability assignment not found",
        )

    db.delete(assignment)
    db.commit()


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
) -> Agent:
    existing_agent = db.get(Agent, agent.agent_id)

    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent already registered",
        )
    db_agent = Agent(**agent.model_dump())

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    return db_agent


@router.get("", response_model=list[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return agent


@router.post("/{agent_id}/suspend", response_model=AgentResponse)
def suspend_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.status == "deregistered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deregistered agent cannot be suspended",
        )

    agent.status = "suspended"
    db.commit()
    db.refresh(agent)

    return agent


@router.post("/{agent_id}/reactivate", response_model=AgentResponse)
def reactivate_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.status == "deregistered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deregistered agent cannot be reactivated",
        )

    agent.status = "active"
    db.commit()
    db.refresh(agent)

    return agent


@router.post("/{agent_id}/deregister", response_model=AgentResponse)
def deregister_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    agent.status = "deregistered"
    db.commit()
    db.refresh(agent)

    return agent


@router.post(
    "/{agent_id}/tools/{tool_id}",
    status_code=status.HTTP_201_CREATED,
)
def assign_tool(
    agent_id: str,
    tool_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    tool = db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found",
        )

    existing = db.get(
        AgentTool,
        {
            "agent_id": agent_id,
            "tool_id": tool_id,
        },
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tool already assigned to agent",
        )

    association = AgentTool(
        agent_id=agent_id,
        tool_id=tool_id,
    )

    db.add(association)
    db.commit()

    return {
        "agent_id": agent_id,
        "tool_id": tool_id,
    }


@router.delete(
    "/{agent_id}/tools/{tool_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_tool(
    agent_id: str,
    tool_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    association = db.get(
        AgentTool,
        {
            "agent_id": agent_id,
            "tool_id": tool_id,
        },
    )

    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool association not found",
        )

    db.delete(association)
    db.commit()


@router.get("/{agent_id}/tools")
def list_agent_tools(
    agent_id: str,
    db: Session = Depends(get_db),
):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    tools = (
        db.query(Tool)
        .join(
            AgentTool,
            AgentTool.tool_id == Tool.tool_id,
        )
        .filter(AgentTool.agent_id == agent_id)
        .all()
    )

    return tools
