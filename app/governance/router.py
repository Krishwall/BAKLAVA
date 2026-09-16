import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.governance.approval import ApprovalRequest
from app.governance.engine import GovernanceEngine
from app.governance.engine import GovernanceRequest as EngineGovernanceRequest
from app.governance.model import Policy
from app.governance.schemas import (
    ApprovalResponse,
    GovernanceRequest,
    GovernanceResponse,
    PolicyCreate,
    PolicyResponse,
)

router = APIRouter(
    prefix="/governance",
    tags=["governance"],
)


@router.post("/evaluate", response_model=GovernanceResponse | ApprovalResponse)
def evaluate_governance(
    request: GovernanceRequest,
    db: Session = Depends(get_db),
):
    engine = GovernanceEngine(db)
    engine_request = EngineGovernanceRequest(**request.model_dump())
    result = engine.evaluate(engine_request)

    if result.decision != "REQUIRE_APPROVAL":
        return result

    approval = ApprovalRequest(
        approval_id=f"approval-{uuid.uuid4().hex[:12]}",
        agent_id=request.agent_id,
        tool_id=request.tool_id,
        action=request.action,
        environment=request.environment,
        status="PENDING",
        reason=result.reason,
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


@router.get("/policies", response_model=list[PolicyResponse])
def list_policies(db: Session = Depends(get_db)):
    return db.query(Policy).all()


@router.post("/policies", response_model=PolicyResponse)
def create_policy(
    policy: PolicyCreate,
    db: Session = Depends(get_db),
):
    db_policy = Policy(
        policy_id=str(uuid.uuid4()),
        **policy.model_dump(),
    )

    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)

    return db_policy


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: str,
    db: Session = Depends(get_db),
):
    policy = db.get(Policy, policy_id)

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Policy not found",
        )

    return policy


@router.get(
    "/approvals/{approval_id}",
    response_model=ApprovalResponse,
)
def get_approval(
    approval_id: str,
    db: Session = Depends(get_db),
):
    approval = db.get(ApprovalRequest, approval_id)

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    return approval


@router.post(
    "/approvals/{approval_id}/approve",
    response_model=ApprovalResponse,
)
def approve_request(
    approval_id: str,
    db: Session = Depends(get_db),
):
    approval = db.get(ApprovalRequest, approval_id)

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    if approval.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail="Approval request is already resolved",
        )

    approval.status = "APPROVED"
    approval.resolved_at = datetime.now(UTC)

    db.commit()
    db.refresh(approval)

    return approval


@router.post(
    "/approvals/{approval_id}/reject",
    response_model=ApprovalResponse,
)
def reject_request(
    approval_id: str,
    db: Session = Depends(get_db),
):
    approval = db.get(ApprovalRequest, approval_id)

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    if approval.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail="Approval request is already resolved",
        )

    approval.status = "REJECTED"
    approval.resolved_at = datetime.now(UTC)

    db.commit()
    db.refresh(approval)

    return approval
