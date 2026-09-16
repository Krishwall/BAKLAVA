from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class GovernanceRequest(BaseModel):
    agent_id: str
    action: str
    environment: str
    tool_id: str | None = None


class GovernanceResponse(BaseModel):
    decision: str
    reason: str


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class PolicyCreate(BaseModel):
    policy_id: str | None = None
    name: str
    description: str | None = None
    environment: str
    risk_level: str
    action: str
    decision: str
    enabled: bool = True
    priority: int = Field(default=0, ge=0)


class PolicyResponse(PolicyCreate):
    policy_id: str | None = None
    priority: int = 0
    created_at: datetime
    updated_at: datetime


class ApprovalResponse(BaseModel):
    approval_id: str
    agent_id: str
    tool_id: str | None
    action: str
    environment: str
    status: str
    reason: str
    requested_at: datetime
    resolved_at: datetime | None
