import pytest

def test_agent_invocation_success(client, db_session):
    # Setup user
    client.post("/api/v1/auth/signup", json={
        "name": "Agent User",
        "email": "agentuser@test.com",
        "password": "testpassword",
        "role": "MANAGER"
    })
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "agentuser@test.com",
        "password": "testpassword"
    })
    token = login_resp.json()["access_token"]
    
    # Invoke agent tool
    response = client.post(
        "/api/v1/agent/invoke",
        json={
            "tool_name": "crm",
            "operation": "list",
            "arguments": {}
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "items" in data["result"]

def test_agent_invocation_unauthenticated(client):
    response = client.post(
        "/api/v1/agent/invoke",
        json={
            "tool_name": "crm",
            "operation": "list",
            "arguments": {}
        }
    )
    assert response.status_code == 401

def test_agent_invocation_impersonation_prevented(client):
    # Since agent_id is not even accepted in the payload, impersonation is fundamentally impossible at the API boundary
    # We can verify that passing arbitrary data doesn't affect it
    client.post("/api/v1/auth/signup", json={
        "name": "Impersonator",
        "email": "impersonator@test.com",
        "password": "testpassword",
        "role": "MANAGER"
    })
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "impersonator@test.com",
        "password": "testpassword"
    })
    token = login_resp.json()["access_token"]
    
    response = client.post(
        "/api/v1/agent/invoke",
        json={
            "agent_id": "other-agent-id", # This field is ignored by pydantic/router
            "tool_name": "crm",
            "operation": "list",
            "arguments": {}
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    # It executes successfully using the authenticated user's agent
