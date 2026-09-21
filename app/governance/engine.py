from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.model import Agent
from app.db.agent_capability import AgentCapability
from app.db.tool_capability import ToolCapability
from app.governance.audit import PolicyAuditLog
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

    def _audit(
        self,
        request: GovernanceRequest,
        decision: str,
        reason: str,
        policy_id: str | None = None,
        approval_required: bool = False,
    ) -> GovernanceDecision:
        audit_log = PolicyAuditLog(
            agent_id=request.agent_id,
            tool_id=request.tool_id or "",
            policy_id=policy_id,
            action=request.action,
            environment=request.environment,
            decision=decision,
            approval_required=approval_required,
        )

        self.db.add(audit_log)
        self.db.commit()

        return GovernanceDecision(
            decision=decision,
            reason=reason,
        )

    def evaluate(self, request: GovernanceRequest) -> GovernanceDecision:
        agent = self.db.get(Agent, request.agent_id)

        if agent is None:
            return self._audit(
                request=request,
                decision="DENY",
                reason="Agent does not exist",
            )

        if agent.status != "active":
            return self._audit(
                request=request,
                decision="DENY",
                reason=f"Agent is {agent.status}",
            )

        if agent.environment != request.environment:
            return self._audit(
                request=request,
                decision="DENY",
                reason="Agent environment mismatch",
            )

        if request.tool_id:
            tool = self.db.get(Tool, request.tool_id)

            if tool is None:
                return self._audit(
                    request=request,
                    decision="DENY",
                    reason="Tool does not exist",
                )

            if tool.status != "active":
                return self._audit(
                    request=request,
                    decision="DENY",
                    reason=f"Tool is {tool.status}",
                )

            if tool.environment != request.environment:
                return self._audit(
                    request=request,
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
                return self._audit(
                    request=request,
                    policy_id=None,
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
            return self._audit(
                request=request,
                decision="DENY",
                reason="No matching policy",
                policy_id=None,
            )

        agent_risk = RISK_LEVELS.get(agent.risk_level)
        policy_risk = RISK_LEVELS.get(policy.risk_level)

        if agent_risk is None or policy_risk is None:
            return self._audit(
                request=request,
                decision="DENY",
                reason="Invalid risk level",
                policy_id=policy.policy_id if policy else None,
            )

        if agent_risk < policy_risk:
            return self._audit(
                request=request,
                decision="DENY",
                reason="Agent risk level is below policy threshold",
                policy_id=policy.policy_id if policy else None,
            )

        return self._audit(
            request=request,
            decision=policy.decision,
            reason=f"Policy '{policy.policy_id}' matched",
            policy_id=policy.policy_id if policy else None,
        )
