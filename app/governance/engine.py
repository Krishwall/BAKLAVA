from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.model import Agent
from app.db.agent_capability import AgentCapability
from app.db.tool_capability import ToolCapability
from app.governance.model import Policy
from app.tools.model import Tool

RISK_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@dataclass
class GovernanceRequest:
    agent_id: str
    action: str
    environment: str
    tool_id: str | None = None


@dataclass
class GovernanceDecision:
    decision: str
    reason: str


class GovernanceEngine:
    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, request: GovernanceRequest) -> GovernanceDecision:
        agent = self.db.get(Agent, request.agent_id)

        if agent is None:
            return GovernanceDecision(
                decision="DENY",
                reason="Agent does not exist",
            )

        if agent.status != "active":
            return GovernanceDecision(
                decision="DENY",
                reason=f"Agent is {agent.status}",
            )

        if agent.environment != request.environment:
            return GovernanceDecision(
                decision="DENY",
                reason="Agent environment mismatch",
            )

        if request.tool_id:
            tool = self.db.get(Tool, request.tool_id)

            if tool is None:
                return GovernanceDecision(
                    decision="DENY",
                    reason="Tool does not exist",
                )

            if tool.status != "active":
                return GovernanceDecision(
                    decision="DENY",
                    reason=f"Tool is {tool.status}",
                )

            if tool.environment != request.environment:
                return GovernanceDecision(
                    decision="DENY",
                    reason="Tool environment mismatch",
                )

            authorization = (
                self.db.query(AgentCapability)
                .join(
                    ToolCapability,
                    AgentCapability.capability_id == ToolCapability.capability_id,
                )
                .filter(
                    AgentCapability.agent_id == request.agent_id,
                    ToolCapability.tool_id == request.tool_id,
                )
                .first()
            )

            if authorization is None:
                return GovernanceDecision(
                    decision="DENY",
                    reason="Agent is not authorized to use this tool",
                )

        policies = (
            self.db.query(Policy)
            .filter(
                Policy.enabled.is_(True),
                Policy.environment == request.environment,
                Policy.action == request.action,
            )
            .order_by(
                Policy.priority.desc(),
                Policy.risk_level.desc(),
                Policy.policy_id.asc(),
            )
            .all()
        )

        print(
            [
                (p.policy_id, p.priority, p.risk_level, p.action, p.decision)
                for p in policies
            ]
        )

        policy = policies[0] if policies else None
        if policy is None:
            return GovernanceDecision(
                decision="DENY",
                reason="No matching policy",
            )

        agent_risk = RISK_LEVELS.get(agent.risk_level)
        policy_risk = RISK_LEVELS.get(policy.risk_level)

        if agent_risk is None or policy_risk is None:
            return GovernanceDecision(
                decision="DENY",
                reason="Invalid risk level",
            )

        if agent_risk < policy_risk:
            return GovernanceDecision(
                decision="DENY",
                reason="Agent risk level is below policy threshold",
            )

        return GovernanceDecision(
            decision=policy.decision,
            reason=f"Policy '{policy.policy_id}' matched",
        )
