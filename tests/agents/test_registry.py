def agent_payload():
    return {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "description": "Performs research and generates summaries",
        "version": "1.0.0",
        "owner": "research-team",
        "status": "active",
        "environment": "dev",
        "risk_level": "medium",
        "endpoint": "http://research-agent:8001",
    }


def test_register_agent(client):
    response = client.post("/agents", json=agent_payload())

    assert response.status_code == 201

    data = response.json()

    assert data["agent_id"] == "research-agent"
    assert data["name"] == "Research Agent"
    assert data["version"] == "1.0.0"


def test_duplicate_agent_registration(client):
    payload = agent_payload()

    first_response = client.post("/agents", json=payload)
    second_response = client.post("/agents", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_list_agents(client):
    client.post("/agents", json=agent_payload())

    response = client.get("/agents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["agent_id"] == "research-agent"


def test_get_agent(client):
    client.post("/agents", json=agent_payload())

    response = client.get("/agents/research-agent")

    assert response.status_code == 200
    assert response.json()["agent_id"] == "research-agent"


def test_get_nonexistent_agent(client):
    response = client.get("/agents/does-not-exist")

    assert response.status_code == 404


def test_invalid_agent(client):
    payload = agent_payload()
    del payload["name"]

    response = client.post("/agents", json=payload)

    assert response.status_code == 422