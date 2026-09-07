def create_agent(client, agent_id="test-agent"):
    return client.post(
        "/agents",
        json={
            "agent_id": agent_id,
            "name": "Test Agent",
            "description": "Agent for testing",
            "version": "1.0.0",
            "owner": "baklava",
            "status": "active",
            "environment": "dev",
            "risk_level": "low",
        },
    )


def create_capability(client, capability_id="test-capability"):
    return client.post(
        "/capabilities",
        json={
            "capability_id": capability_id,
            "name": "Test Capability",
            "description": "Capability for testing",
            "version": "1.0.0",
            "risk_level": "medium",
        },
    )


def test_assign_capability(client):
    create_agent(client)
    create_capability(client)

    response = client.post("/agents/test-agent/capabilities/test-capability")

    assert response.status_code == 201
    assert response.json() == {
        "agent_id": "test-agent",
        "capability_id": "test-capability",
    }


def test_duplicate_capability_assignment(client):
    create_agent(client)
    create_capability(client)

    endpoint = "/agents/test-agent/capabilities/test-capability"

    first_response = client.post(endpoint)
    second_response = client.post(endpoint)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_assign_capability_to_nonexistent_agent(client):
    create_capability(client)

    response = client.post("/agents/does-not-exist/capabilities/test-capability")

    assert response.status_code == 404
    assert response.json()["detail"] == "Agent not found"


def test_assign_nonexistent_capability(client):
    create_agent(client)

    response = client.post("/agents/test-agent/capabilities/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Capability not found"


def test_list_agent_capabilities(client):
    create_agent(client)
    create_capability(client)

    client.post("/agents/test-agent/capabilities/test-capability")

    response = client.get("/agents/test-agent/capabilities")

    assert response.status_code == 200

    capabilities = response.json()

    assert len(capabilities) == 1
    assert capabilities[0]["capability_id"] == "test-capability"


def test_list_capabilities_for_nonexistent_agent(client):
    response = client.get("/agents/does-not-exist/capabilities")

    assert response.status_code == 404
    assert response.json()["detail"] == "Agent not found"


def test_remove_capability(client):
    create_agent(client)
    create_capability(client)

    endpoint = "/agents/test-agent/capabilities/test-capability"

    client.post(endpoint)

    response = client.delete(endpoint)

    assert response.status_code == 204

    response = client.get("/agents/test-agent/capabilities")

    assert response.status_code == 200
    assert response.json() == []


def test_remove_unassigned_capability(client):
    create_agent(client)
    create_capability(client)

    response = client.delete("/agents/test-agent/capabilities/test-capability")

    assert response.status_code == 404
    assert response.json()["detail"] == "Capability assignment not found"
