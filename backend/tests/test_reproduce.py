import pytest
from app.agent.service import AgentService
from app.agent.schemas import AgentInvokeRequest
from app.agent.models import Agent, Session, SessionStatus
from app.auth.models import User
from unittest.mock import MagicMock
from app.crm.service import normalize_search_text

def test_normalization():
    assert normalize_search_text("Dataworks.inc") == "dataworks inc"
    assert normalize_search_text("DataWorks Inc.") == "dataworks inc"
    assert normalize_search_text("DATAWORKS INC") == "dataworks inc"
    assert normalize_search_text("dataworks.inc.") == "dataworks inc"
    assert normalize_search_text(" DataWorks    Inc. ") == "dataworks inc"
    assert normalize_search_text("some-company, llc") == "some company llc"

def test_reproduce_agent_service(db_session):
    # Ensure no crash and proper validation
    user = User(id=1, email="test@example.com")
    agent = Agent(id=1, name="Test Agent")
    session = Session(
        id=1, 
        session_id="SESS-123", 
        user_id=1, 
        agent_id=1, 
        status=SessionStatus.ACTIVE
    )
    
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = (
        "", 
        {
            "name": "search_customers",
            "arguments": {"filters": {"company": "Dataworks.inc"}} # Malformed argument
        }
    )
    
    service = AgentService(mock_llm)
    resp = service.invoke(db_session, user, agent, session, "who works in Dataworks.inc?")
    assert resp.status == "ERROR"
    assert resp.decision == "ERROR"
    assert "Malformed tool arguments" in resp.reason
    assert "Unsupported argument" in resp.reason

    mock_llm.generate_response.return_value = (
        "", 
        {
            "name": "get_customer",
            "arguments": {} # Missing required
        }
    )
    resp2 = service.invoke(db_session, user, agent, session, "get customer")
    assert resp2.status == "ERROR"
    assert resp2.decision == "ERROR"
    assert "Missing required argument" in resp2.reason
