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
    policy_id="dev-tool-execution",
    environment="dev",
    risk_level="medium",
    action="execute_tool",
    decision="ALLOW",
):
    response = client.post(
        "/governance/policies",
        json={
            "policy_id": policy_id,
            "name": "Test Policy",
            "description": "Governance test policy",
            "environment": environment,
            "risk_level": risk_level,
            "action": action,
            "decision": decision,
            "enabled": True,
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
        policy_id="prod-high-risk-execution",
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
