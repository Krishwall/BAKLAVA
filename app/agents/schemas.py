from datetime import datetime

from pydantic import BaseModel


class AgentCreate(BaseModel):
    agent_id: str
    name: str
    description: str | None = None
    version: str
    owner: str
    status: str = "active"
    environment: str = "dev"
    risk_level: str = "medium"
    endpoint: str | None = None


class AgentResponse(AgentCreate):
    created_at: datetime
    updated_at: datetime