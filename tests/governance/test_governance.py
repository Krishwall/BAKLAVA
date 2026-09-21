from app.governance.audit import PolicyAuditLog


def create_agent(
    client,
    agent_id="agent-001",
    status="active",
    environment="dev",
    risk_level="medium",
):
    response = client.post(
        "/agents",
        json={
            "agent_id": agent_id,
            "name": "Test Agent",
            "description": "Governance test agent",
            "version": "1.0.0",
            "owner": "BAKLAVA",
            "status": status,
            "environment": environment,
            "risk_level": risk_level,
            "endpoint": "http://localhost:9000",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_capability(client, capability_id="database-read"):
    response = client.post(
        "/capabilities",
        json={
            "capability_id": capability_id,
            "name": "Database Read",
            "description": "Database read capability",
            "version": "1.0.0",
            "risk_level": "medium",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_tool(
    client,
    tool_id="database-tool",
    status="active",
    environment="dev",
    risk_level="medium",
):
    response = client.post(
        "/tools",
        json={
            "tool_id": tool_id,
            "name": "Database Tool",
            "description": "Database access tool",
            "version": "1.0.0",
            "owner": "BAKLAVA",
            "status": status,
            "environment": environment,
            "risk_level": risk_level,
            "endpoint": "http://localhost:9100",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_policy(
    client,
    environment="dev",
    risk_level="medium",
    action="execute_tool",
    decision="ALLOW",
    priority=0,
):
    response = client.post(
        "/governance/policies",
        json={
            "name": "Test Policy",
            "description": "Governance test policy",
            "environment": environment,
            "risk_level": risk_level,
            "action": action,
            "decision": decision,
            "enabled": True,
            "priority": priority,
        },
    )

    assert response.status_code == 200
    return response.json()


def authorize_tool(client, agent_id="agent-001", tool_id="database-tool"):
    response = client.post(
        f"/agents/{agent_id}/capabilities/database-read",
    )
    assert response.status_code == 201

    response = client.post(
        f"/tools/{tool_id}/capabilities/database-read",
    )
    assert response.status_code == 201


def evaluate(
    client,
    agent_id="agent-001",
    tool_id="database-tool",
    environment="dev",
    action="execute_tool",
):
    return client.post(
        "/governance/evaluate",
        json={
            "agent_id": agent_id,
            "action": action,
            "environment": environment,
            "tool_id": tool_id,
        },
    )


def test_authorized_agent_is_allowed(client):
    create_agent(client)
    create_capability(client)
    create_tool(client)
    authorize_tool(client)
    create_policy(client)

    response = evaluate(client)

    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"


def test_unauthorized_agent_is_denied(client):
    create_agent(client)
    create_capability(client)
    create_tool(client)
    create_policy(client)

    response = evaluate(client)

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
    assert response.json()["reason"] == ("Agent is not authorized to use this tool")


def test_suspended_agent_is_denied(client):
    create_agent(client, status="suspended")
    create_capability(client)
    create_tool(client)
    authorize_tool(client)
    create_policy(client)

    response = evaluate(client)

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
    assert response.json()["reason"] == "Agent is suspended"


def test_inactive_tool_is_denied(client):
    create_agent(client)
    create_capability(client)
    create_tool(client, status="suspended")
    create_policy(client)

    response = evaluate(client)

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
    assert response.json()["reason"] == "Tool is suspended"


def test_missing_policy_is_denied(client):
    create_agent(client)
    create_capability(client)
    create_tool(client)
    authorize_tool(client)

    response = evaluate(client)

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
    assert response.json()["reason"] == "No matching policy"


def test_high_risk_policy_requires_approval(client):
    create_agent(
        client,
        environment="prod",
        risk_level="high",
    )
    create_capability(client)
    create_tool(
        client,
        environment="prod",
        risk_level="high",
    )
    authorize_tool(client)

    create_policy(
        client,
        environment="prod",
        risk_level="high",
        decision="REQUIRE_APPROVAL",
    )

    response = evaluate(
        client,
        environment="prod",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "PENDING"
    assert body["agent_id"] == "agent-001"
    assert body["tool_id"] == "database-tool"
    assert body["action"] == "execute_tool"


def test_higher_priority_policy_wins(client):
    create_agent(client)
    create_capability(client)
    create_tool(client)

    authorize_tool(client)

    low_priority_policy = {
        "name": "Low priority allow",
        "description": "Lower priority policy",
        "environment": "dev",
        "risk_level": "low",
        "action": "execute",
        "decision": "ALLOW",
        "enabled": True,
        "priority": 10,
    }

    high_priority_policy = {
        "name": "High priority deny",
        "description": "Higher priority policy",
        "environment": "dev",
        "risk_level": "low",
        "action": "execute",
        "decision": "DENY",
        "enabled": True,
        "priority": 100,
    }

    response = client.post(
        "/governance/policies",
        json=low_priority_policy,
    )
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
    assert response.status_code == 200

    response = client.post(
        "/governance/policies",
        json=high_priority_policy,
    )
    assert response.status_code == 200

    response = evaluate(
        client,
        agent_id="agent-001",
        tool_id="database-tool",
        action="execute",
        environment="dev",
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)
    assert response.json()["decision"] == "DENY"


def test_same_priority_policy_uses_deterministic_tiebreaker(client):
    create_agent(client, environment="prod")
    create_capability(client)
    create_tool(client, environment="prod")
    authorize_tool(client)

    first_policy = {
        "policy_id": "a-policy-1",
        "name": "same-priority-policy-1",
        "description": "First policy",
        "environment": "prod",
        "risk_level": "low",
        "action": "read",
        "decision": "ALLOW",
        "enabled": True,
        "priority": 50,
    }

    second_policy = {
        "policy_id": "a-policy-2",
        "name": "same-priority-policy-2",
        "description": "Second policy",
        "environment": "prod",
        "risk_level": "low",
        "action": "read",
        "decision": "DENY",
        "enabled": True,
        "priority": 50,
    }

    first_response = client.post(
        "/governance/policies",
        json=first_policy,
    )
    assert first_response.status_code == 200
    first_policy_id = first_response.json()["policy_id"]

    second_response = client.post(
        "/governance/policies",
        json=second_policy,
    )
    assert second_response.status_code == 200
    second_policy_id = second_response.json()["policy_id"]

    response = evaluate(
        client,
        environment="prod",
        action="read",
    )

    expected_decision = "ALLOW" if first_policy_id < second_policy_id else "DENY"

    assert response.status_code == 200
    # print("First policy ID:", first_policy_id)
    # print("Second policy ID:", second_policy_id)
    # print(
    #     "Expected by UUID order:",
    #     "ALLOW" if first_policy_id < second_policy_id else "DENY",
    # )
    # print("Actual decision:", response.json()["decision"])
    assert response.json()["decision"] == expected_decision


def test_negative_policy_priority_is_rejected(client):
    response = client.post(
        "/governance/policies",
        json={
            "policy_id": "negative-priority-policy",
            "name": "Invalid priority policy",
            "description": "Priority cannot be negative",
            "environment": "dev",
            "risk_level": "low",
            "action": "execute_tool",
            "decision": "ALLOW",
            "enabled": True,
            "priority": -1,
        },
    )

    assert response.status_code == 422


def test_governance_decision_creates_audit_log(client, db):
    response = evaluate(
        client,
        environment="dev",
        action="execute_tool",
    )

    assert response.status_code == 200

    audit_log = db.query(PolicyAuditLog).order_by(PolicyAuditLog.id.desc()).first()

    assert audit_log is not None
    assert audit_log.agent_id == "agent-001"
    assert audit_log.tool_id == "database-tool"
    assert audit_log.action == "execute_tool"
    assert audit_log.environment == "dev"
    assert audit_log.decision == response.json()["decision"]
