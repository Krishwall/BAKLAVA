def test_assign_tool(client):
    agent = {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    tool = {
        "tool_id": "web-search",
        "name": "Web Search",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    assert client.post("/agents", json=agent).status_code == 201
    assert client.post("/tools", json=tool).status_code == 201

    response = client.post("/agents/research-agent/tools/web-search")

    assert response.status_code == 201
    assert response.json() == {
        "agent_id": "research-agent",
        "tool_id": "web-search",
    }


def test_assign_duplicate_tool(client):
    agent = {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    tool = {
        "tool_id": "web-search",
        "name": "Web Search",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    client.post("/agents", json=agent)
    client.post("/tools", json=tool)
    client.post("/agents/research-agent/tools/web-search")

    response = client.post("/agents/research-agent/tools/web-search")

    assert response.status_code == 409


def test_assign_tool_agent_not_found(client):
    response = client.post("/agents/missing-agent/tools/web-search")

    assert response.status_code == 404
    assert response.json()["detail"] == "Agent not found"


def test_assign_tool_tool_not_found(client):
    agent = {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    client.post("/agents", json=agent)

    response = client.post("/agents/research-agent/tools/missing-tool")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tool not found"


def test_list_agent_tools(client):
    agent = {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    tool = {
        "tool_id": "web-search",
        "name": "Web Search",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    client.post("/agents", json=agent)
    client.post("/tools", json=tool)
    client.post("/agents/research-agent/tools/web-search")

    response = client.get("/agents/research-agent/tools")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["tool_id"] == "web-search"


def test_remove_tool(client):
    agent = {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    tool = {
        "tool_id": "web-search",
        "name": "Web Search",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
    }

    client.post("/agents", json=agent)
    client.post("/tools", json=tool)
    client.post("/agents/research-agent/tools/web-search")

    response = client.delete("/agents/research-agent/tools/web-search")

    assert response.status_code == 204

    response = client.get("/agents/research-agent/tools")

    assert response.status_code == 200
    assert response.json() == []
