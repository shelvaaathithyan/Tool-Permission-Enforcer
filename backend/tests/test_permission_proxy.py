import pytest
import uuid
from unittest.mock import patch, MagicMock
from app.auth.models import User, Role
from app.agent.models import Agent, Session as AgentSession, SessionStatus
from app.agent.schemas import AgentToolRequest
from app.permission_proxy.service import get_permission_proxy
from app.audit.models import AuditDecision, ActorType

@pytest.fixture
def mock_user(db_session):
    u = User(id=uuid.uuid4(), email="test@example.com", name="Test", password_hash="hash", role=Role.ADMIN)
    db_session.add(u)
    db_session.commit()
    return u

@pytest.fixture
def mock_agent(db_session, mock_user):
    a = Agent(id=uuid.uuid4(), agent_id="AGENT-123", user_id=mock_user.id, name="Test Agent")
    db_session.add(a)
    db_session.commit()
    return a

@pytest.fixture
def active_session(db_session, mock_user, mock_agent):
    s = AgentSession(
        session_id="session-123",
        user_id=mock_user.id,
        agent_id=mock_agent.id,
        status=SessionStatus.ACTIVE
    )
    db_session.add(s)
    db_session.commit()
    return s

@pytest.fixture
def inactive_session(db_session, mock_user, mock_agent):
    s = AgentSession(
        session_id="session-456",
        user_id=mock_user.id,
        agent_id=mock_agent.id,
        status=SessionStatus.INACTIVE
    )
    db_session.add(s)
    db_session.commit()
    return s

def test_proxy_list_customers_allowed(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="list_customers",
        operation="READ",
        resource="CUSTOMER",
        arguments={},
        original_prompt="List all customers"
    )
    
    with patch("app.crm.service.get_customers") as mock_crm:
        mock_crm.return_value = ([], 0)
        result = proxy.evaluate(req, mock_user, mock_agent, active_session)
        assert result["decision"] == "ALLOWED"
        mock_crm.assert_called_once()

def test_proxy_get_customer_allowed(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="get_customer",
        operation="READ",
        resource="CUSTOMER",
        arguments={"customer_id": "CUST-123"},
        original_prompt="Get customer"
    )
    
    with patch("app.permission_proxy.service.crm_service.get_customer_by_customer_id") as mock_crm:
        mock_customer = MagicMock()
        mock_customer.session_status = "ACTIVE"
        mock_customer.customer_id = "CUST-123"
        mock_customer.first_name = "Test"
        mock_customer.last_name = "User"
        mock_customer.email = "test@example.com"
        
        mock_crm.return_value = mock_customer
        
        with patch("app.crm.schemas.CustomerResponse.model_validate") as mock_validate:
            mock_validate.return_value.model_dump.return_value = {"customer_id": "CUST-123"}
            result = proxy.evaluate(req, mock_user, mock_agent, active_session)
            assert result["decision"] == "ALLOWED"
            assert result["result"] == {"customer_id": "CUST-123"}

def test_proxy_get_customer_not_found_blocked(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="get_customer",
        operation="READ",
        resource="CUSTOMER",
        arguments={"customer_id": "Naren G"},
        original_prompt="Get customer"
    )
    
    with patch("app.permission_proxy.service.crm_service.search_customers") as mock_search:
        mock_search.return_value = []
        
        result = proxy.evaluate(req, mock_user, mock_agent, active_session)
        assert result["decision"] == "BLOCKED"
        assert "Customer could not be found" in result["reason"]

def test_proxy_get_customer_by_name_allowed(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="get_customer",
        operation="READ",
        resource="CUSTOMER",
        arguments={"customer_id": "Test User"},
        original_prompt="Get customer by name"
    )
    
    with patch("app.permission_proxy.service.crm_service.search_customers") as mock_search:
        mock_customer = MagicMock()
        mock_customer.session_status = "ACTIVE"
        mock_customer.customer_id = "CUST-123"
        mock_customer.first_name = "Test"
        mock_customer.last_name = "User"
        mock_customer.email = "test@example.com"
        
        mock_search.return_value = [mock_customer]
        
        with patch("app.crm.schemas.CustomerResponse.model_validate") as mock_validate, \
             patch("app.crm.service.get_customer_by_customer_id") as mock_crm:
            mock_crm.return_value = mock_customer
            mock_validate.return_value.model_dump.return_value = {"customer_id": "CUST-123"}
            result = proxy.evaluate(req, mock_user, mock_agent, active_session)
            assert result["decision"] == "ALLOWED"
            assert req.arguments["customer_id"] == "CUST-123"
            assert result["result"] == {"customer_id": "CUST-123"}

def test_proxy_get_customer_by_name_inactive_blocked(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="get_customer",
        operation="READ",
        resource="CUSTOMER",
        arguments={"customer_id": "Inactive User"},
        original_prompt="Get inactive customer by name"
    )
    
    with patch("app.permission_proxy.service.crm_service.search_customers") as mock_search:
        mock_customer = MagicMock()
        mock_customer.session_status = "INACTIVE"
        mock_customer.customer_id = "CUST-456"
        mock_search.return_value = [mock_customer]
        
        result = proxy.evaluate(req, mock_user, mock_agent, active_session)
        assert result["decision"] == "BLOCKED"
        assert "INACTIVE" in result["reason"]
        assert req.arguments["customer_id"] == "CUST-456"

def test_proxy_search_customers_allowed(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="search_customers",
        operation="READ",
        resource="CUSTOMER",
        arguments={"query": "Test"},
        original_prompt="Search customer"
    )
    
    with patch("app.permission_proxy.service.crm_service.search_customers") as mock_crm:
        mock_crm.return_value = []
        result = proxy.evaluate(req, mock_user, mock_agent, active_session)
        assert result["decision"] == "ALLOWED"
        assert result["result"] == {"items": [], "total": 0}

def test_proxy_list_customers_allowed(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="list_customers",
        operation="READ",
        resource="CUSTOMER",
        arguments={},
        original_prompt="List all customers"
    )
    
    with patch("app.crm.service.get_customers") as mock_crm:
        mock_crm.return_value = ([], 0)
        result = proxy.evaluate(req, mock_user, mock_agent, active_session)
        assert result["decision"] == "ALLOWED"
        mock_crm.assert_called_once()

def test_proxy_inactive_session_blocked(db_session, mock_user, mock_agent, inactive_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="list_customers",
        operation="READ",
        resource="CUSTOMER",
        arguments={},
        original_prompt="List all customers"
    )
    
    with patch("app.crm.service.get_customers") as mock_crm:
        result = proxy.evaluate(req, mock_user, mock_agent, inactive_session)
        assert result["decision"] == "BLOCKED"
        assert "inactive or invalid" in result["reason"]
        mock_crm.assert_not_called()

def test_proxy_mutations_blocked(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    for tool, op in [("create_customer", "CREATE"), ("update_customer", "UPDATE"), ("delete_customer", "DELETE")]:
        req = AgentToolRequest(
            tool_name=tool,
            operation=op,
            resource="CUSTOMER",
            arguments={"customer_id": "CUST-123", "fields": {}},
            original_prompt="Do mutation"
        )
        
        with patch(f"app.crm.service.{tool}") as mock_crm, \
             patch("app.permission_proxy.service.crm_service.get_customer_by_customer_id") as mock_get_cust:
            mock_cust = MagicMock()
            mock_cust.session_status = "ACTIVE"
            mock_cust.customer_id = "CUST-123"
            mock_get_cust.return_value = mock_cust
            
            result = proxy.evaluate(req, mock_user, mock_agent, active_session)
            assert result["decision"] == "BLOCKED"
            assert "mutation operations are not permitted" in result["reason"]
            mock_crm.assert_not_called()

def test_proxy_invalid_tool_blocked(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="fake_tool",
        operation="READ",
        resource="CUSTOMER",
        arguments={},
        original_prompt="Fake"
    )
    result = proxy.evaluate(req, mock_user, mock_agent, active_session)
    assert result["decision"] == "BLOCKED"
    assert "Invalid Agent tool definition" in result["reason"]

def test_proxy_mismatch_tool_op_blocked(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="get_customer",
        operation="UPDATE",
        resource="CUSTOMER",
        arguments={},
        original_prompt="Fake"
    )
    result = proxy.evaluate(req, mock_user, mock_agent, active_session)
    assert result["decision"] == "BLOCKED"
    assert "Invalid Agent tool definition" in result["reason"]

def test_proxy_inactive_customer_blocked(db_session, mock_user, mock_agent, active_session):
    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="get_customer",
        operation="READ",
        resource="CUSTOMER",
        arguments={"customer_id": "CUST-999"},
        original_prompt="Get bad customer"
    )
    
    mock_customer = MagicMock()
    mock_customer.session_status = "INACTIVE"
    mock_customer.customer_id = "CUST-999"
    
    with patch("app.permission_proxy.service.crm_service.get_customer_by_customer_id") as mock_crm:
        mock_crm.return_value = mock_customer
        result = proxy.evaluate(req, mock_user, mock_agent, active_session)
        assert result["decision"] == "BLOCKED"
        assert "Customer session is INACTIVE" in result["reason"]

def test_proxy_4_strike_rule(db_session, mock_user, mock_agent, active_session):

    proxy = get_permission_proxy(db_session)
    req = AgentToolRequest(
        tool_name="update_customer",
        operation="UPDATE",
        resource="CUSTOMER",
        arguments={"customer_id": "CUST-123", "fields": {}},
        original_prompt="Strike"
    )
    
    with patch("app.permission_proxy.service.crm_service.get_customer_by_customer_id") as mock_get_cust:
        mock_cust = MagicMock()
        mock_cust.session_status = "ACTIVE"
        mock_cust.customer_id = "CUST-123"
        mock_get_cust.return_value = mock_cust
        
        for i in range(5):
            result = proxy.evaluate(req, mock_user, mock_agent, active_session)
            assert result["decision"] == "BLOCKED"
        
    # Check that exactly one SecurityAlert was created
    from app.audit.models import SecurityAlert
    alerts = db_session.query(SecurityAlert).filter(
        SecurityAlert.session_id == active_session.session_id
    ).all()
    assert len(alerts) == 1
    assert alerts[0].severity.name == "HIGH"
