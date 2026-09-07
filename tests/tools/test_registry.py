def test_create_tool(client):
    response = client.post(
        "/tools",
        json={
            "tool_id": "web-search",
            "name": "Web Search",
            "description": "Searches the web",
            "version": "1.0.0",
            "owner": "baklava",
            "status": "active",
            "environment": "dev",
            "risk_level": "low",
            "endpoint": "https://example.com/search",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["tool_id"] == "web-search"
    assert data["name"] == "Web Search"


def test_create_duplicate_tool(client):
    payload = {
        "tool_id": "web-search",
        "name": "Web Search",
        "description": "Searches the web",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
        "endpoint": "https://example.com/search",
    }

    first_response = client.post("/tools", json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/tools", json=payload)
    assert second_response.status_code == 409


def test_get_tool(client):
    payload = {
        "tool_id": "web-search",
        "name": "Web Search",
        "description": "Searches the web",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
        "endpoint": "https://example.com/search",
    }

    client.post("/tools", json=payload)

    response = client.get("/tools/web-search")

    assert response.status_code == 200

    data = response.json()
    assert data["tool_id"] == "web-search"
    assert data["name"] == "Web Search"


def test_get_missing_tool(client):
    response = client.get("/tools/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tool not found"


def test_list_tools(client):
    payload = {
        "tool_id": "web-search",
        "name": "Web Search",
        "description": "Searches the web",
        "version": "1.0.0",
        "owner": "baklava",
        "status": "active",
        "environment": "dev",
        "risk_level": "low",
        "endpoint": "https://example.com/search",
    }

    client.post("/tools", json=payload)

    response = client.get("/tools")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["tool_id"] == "web-search"
