from fastapi.testclient import TestClient


def test_register_capability(client: TestClient):
    response = client.post(
        "/capabilities",
        json={
            "capability_id": "web-search",
            "name": "Web Search",
            "description": "Allows an agent to search the web",
            "version": "1.0.0",
            "risk_level": "medium",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["capability_id"] == "web-search"
    assert data["name"] == "Web Search"
    assert data["risk_level"] == "medium"


def test_duplicate_capability_registration(client: TestClient):
    payload = {
        "capability_id": "duplicate-capability",
        "name": "Duplicate Capability",
        "description": "Test capability",
        "version": "1.0.0",
        "risk_level": "low",
    }

    first_response = client.post("/capabilities", json=payload)
    second_response = client.post("/capabilities", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_list_capabilities(client: TestClient):
    client.post(
        "/capabilities",
        json={
            "capability_id": "capability-one",
            "name": "Capability One",
            "description": "First capability",
            "version": "1.0.0",
            "risk_level": "low",
        },
    )

    response = client.get("/capabilities")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_capability(client: TestClient):
    client.post(
        "/capabilities",
        json={
            "capability_id": "web-search",
            "name": "Web Search",
            "description": "Search capability",
            "version": "1.0.0",
            "risk_level": "medium",
        },
    )

    response = client.get("/capabilities/web-search")

    assert response.status_code == 200
    assert response.json()["capability_id"] == "web-search"


def test_get_nonexistent_capability(client: TestClient):
    response = client.get("/capabilities/does-not-exist")

    assert response.status_code == 404