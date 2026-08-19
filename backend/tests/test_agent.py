import pytest
from unittest.mock import patch
from app.auth.service import create_user_and_agent
from app.auth.models import Role
from app.core.security import get_password_hash
from app.agent.models import Session as AgentSession, SessionStatus
import uuid

@pytest.fixture
def agent_user_token(client, db_session):
    user = create_user_and_agent(db_session, "Agent User", "agentuser@test.com", get_password_hash("testpassword"), Role.MANAGER)
    
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "agentuser@test.com",
        "password": "testpassword"
    })
    return login_resp.json()["access_token"]

def test_agent_invocation_success(client, agent_user_token):
    with patch("app.agent.router.llm_provider.generate_response") as mock_gen:
        mock_gen.return_value = ("I understood this as a READ request.", {
            "name": "get_customer",
            "arguments": {"customer_id": "CUST-001"}
        })
        
        response = client.post(
            "/api/v1/agent/invoke",
            json={"prompt": "Show me customer CUST-001"},
            headers={"Authorization": f"Bearer {agent_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING_PERMISSION_PROXY"
        assert data["tool_request"]["tool_name"] == "get_customer"
        assert data["tool_request"]["operation"] == "READ"
        assert data["tool_request"]["resource"] == "CUSTOMER"

def test_agent_invocation_update(client, agent_user_token):
    with patch("app.agent.router.llm_provider.generate_response") as mock_gen:
        mock_gen.return_value = ("I understood this as an UPDATE request.", {
            "name": "update_customer",
            "arguments": {"customer_id": "CUST-001", "fields": {"phone": "12345"}}
        })
        
        response = client.post(
            "/api/v1/agent/invoke",
            json={"prompt": "Update phone to 12345"},
            headers={"Authorization": f"Bearer {agent_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING_PERMISSION_PROXY"
        assert data["tool_request"]["operation"] == "UPDATE"

def test_agent_invocation_unknown_tool(client, agent_user_token):
    with patch("app.agent.router.llm_provider.generate_response") as mock_gen:
        mock_gen.return_value = ("Calling unknown tool", {
            "name": "hack_system",
            "arguments": {}
        })
        
        response = client.post(
            "/api/v1/agent/invoke",
            json={"prompt": "Hack the system"},
            headers={"Authorization": f"Bearer {agent_user_token}"}
        )
        
        assert response.status_code == 400
        assert "unknown tool" in response.json()["detail"].lower()

def test_agent_invocation_no_active_session(client, db_session):
    user = create_user_and_agent(db_session, "No Session User", "nosession@test.com", get_password_hash("testpassword"), Role.MANAGER)
    login_resp = client.post("/api/v1/auth/login", data={"username": "nosession@test.com", "password": "testpassword"})
    token = login_resp.json()["access_token"]
    
    # Logout to deactivate session
    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    
    response = client.post(
        "/api/v1/agent/invoke",
        json={"prompt": "Do something"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401
    assert "no active session" in response.json()["detail"].lower()
