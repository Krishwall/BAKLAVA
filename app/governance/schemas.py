from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
    policy_id: str
    name: str
    description: str | None = None
    environment: str
    risk_level: str
    action: str
    decision: str
    enabled: bool = True


class PolicyResponse(PolicyCreate):
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
