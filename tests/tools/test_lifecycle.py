def create_tool(client, tool_id="web-search"):
    response = client.post(
        "/tools",
        json={
            "tool_id": tool_id,
            "name": "Web Search",
            "description": "Search the web",
            "version": "1.0.0",
            "owner": "baklava",
            "status": "active",
            "environment": "dev",
            "risk_level": "low",
        },
    )
    assert response.status_code == 201


def test_suspend_active_tool(client):
    create_tool(client)

    response = client.post("/tools/web-search/suspend")

    assert response.status_code == 200
    assert response.json()["status"] == "suspended"


def test_suspend_suspended_tool(client):
    create_tool(client)

    client.post("/tools/web-search/suspend")

    response = client.post("/tools/web-search/suspend")

    assert response.status_code == 400


def test_reactivate_suspended_tool(client):
    create_tool(client)

    client.post("/tools/web-search/suspend")

    response = client.post("/tools/web-search/reactivate")

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_reactivate_active_tool(client):
    create_tool(client)

    response = client.post("/tools/web-search/reactivate")

    assert response.status_code == 400


def test_deregister_active_tool(client):
    create_tool(client)

    response = client.post("/tools/web-search/deregister")

    assert response.status_code == 200
    assert response.json()["status"] == "deregistered"


def test_deregister_suspended_tool(client):
    create_tool(client)

    client.post("/tools/web-search/suspend")

    response = client.post("/tools/web-search/deregister")

    assert response.status_code == 200
    assert response.json()["status"] == "deregistered"


def test_reactivate_deregistered_tool(client):
    create_tool(client)

    client.post("/tools/web-search/deregister")

    response = client.post("/tools/web-search/reactivate")

    assert response.status_code == 400


def test_suspend_deregistered_tool(client):
    create_tool(client)

    client.post("/tools/web-search/deregister")

    response = client.post("/tools/web-search/suspend")

    assert response.status_code == 400


def test_deregister_deregistered_tool(client):
    create_tool(client)

    client.post("/tools/web-search/deregister")

    response = client.post("/tools/web-search/deregister")

    assert response.status_code == 400


def test_lifecycle_missing_tool(client):
    response = client.post("/tools/missing-tool/suspend")

    assert response.status_code == 404
