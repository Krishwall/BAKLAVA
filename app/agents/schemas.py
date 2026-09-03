from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AgentStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEREGISTERED = "deregistered"


class Environment(str, Enum):
    DEV = "dev"
    TEST = "test"
    QA = "qa"
    PPD = "ppd"
    PROD = "prod"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentCreate(BaseModel):
    agent_id: str
    name: str
    description: str | None = None
    version: str
    owner: str
    status: AgentStatus = AgentStatus.ACTIVE
    environment: Environment = Environment.DEV
    risk_level: RiskLevel = RiskLevel.MEDIUM
    endpoint: str | None = None


class AgentResponse(AgentCreate):
    created_at: datetime
    updated_at: datetime
