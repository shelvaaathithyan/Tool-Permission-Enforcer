import pytest
import uuid
from sqlalchemy import select
from app.audit.models import AuditLog, SecurityAlert, ActorType, AuditDecision
from app.audit.service import log_audit_event, check_violation_threshold
from app.auth.service import create_user_and_agent
from app.auth.models import Role
from app.core.security import get_password_hash

def test_log_audit_event(db_session):
    user = create_user_and_agent(db_session, "Test", "test@t.com", get_password_hash("p"), Role.MANAGER)
    user_id = user.id
    agent_id = user.agent.id
    session_id = "sess-123"
    
    log = log_audit_event(
        db=db_session,
        user_id=user_id,
        agent_id=agent_id,
        session_id=session_id,
        actor_type=ActorType.AGENT,
        operation="READ",
        resource="CUSTOMER",
        tool_name="get_customer",
        original_prompt="test",
        decision=AuditDecision.PENDING
    )
    
    assert log.id is not None
    assert log.operation == "READ"
    assert log.decision == AuditDecision.PENDING

def test_check_violation_threshold(db_session):
    user = create_user_and_agent(db_session, "Test2", "test2@t.com", get_password_hash("p"), Role.MANAGER)
    user_id = user.id
    agent_id = user.agent.id
    session_id = "sess-violation-test"
    
    # Insert 3 blocked operations
    for _ in range(3):
        log_audit_event(
            db=db_session,
            user_id=user_id,
            agent_id=agent_id,
            session_id=session_id,
            actor_type=ActorType.AGENT,
            operation="UPDATE",
            resource="CUSTOMER",
            decision=AuditDecision.BLOCKED
        )
        
    check_violation_threshold(db_session, user_id, agent_id, session_id)
    
    alerts = db_session.scalars(select(SecurityAlert)).all()
    assert len(alerts) == 0  # 3 blocked operations should not trigger an alert

    # Insert 4th blocked operation
    log_audit_event(
        db=db_session,
        user_id=user_id,
        agent_id=agent_id,
        session_id=session_id,
        actor_type=ActorType.AGENT,
        operation="DELETE",
        resource="CUSTOMER",
        decision=AuditDecision.BLOCKED
    )
    
    check_violation_threshold(db_session, user_id, agent_id, session_id)
    
    alerts = db_session.scalars(select(SecurityAlert)).all()
    assert len(alerts) == 1  # Alert triggered!
    assert alerts[0].session_id == session_id
    
    # Ensure a 5th operation doesn't create a duplicate alert
    log_audit_event(
        db=db_session,
        user_id=user_id,
        agent_id=agent_id,
        session_id=session_id,
        actor_type=ActorType.AGENT,
        operation="CREATE",
        resource="CUSTOMER",
        decision=AuditDecision.BLOCKED
    )
    
    check_violation_threshold(db_session, user_id, agent_id, session_id)
    
    alerts = db_session.scalars(select(SecurityAlert)).all()
    assert len(alerts) == 1  # Still 1 alert

def test_pending_does_not_trigger_alert(db_session):
    user = create_user_and_agent(db_session, "Test3", "test3@t.com", get_password_hash("p"), Role.MANAGER)
    user_id = user.id
    agent_id = user.agent.id
    session_id = "sess-pending-test"
    
    # Insert 5 PENDING operations
    for _ in range(5):
        log_audit_event(
            db=db_session,
            user_id=user_id,
            agent_id=agent_id,
            session_id=session_id,
            actor_type=ActorType.AGENT,
            operation="UPDATE",
            resource="CUSTOMER",
            decision=AuditDecision.PENDING
        )
        
    check_violation_threshold(db_session, user_id, agent_id, session_id)
    
    alerts = db_session.scalars(select(SecurityAlert)).all()
    assert len(alerts) == 0 

def test_audit_logs_api_admin(client, admin_token):
    resp = client.get("/api/v1/audit/logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_audit_alerts_api_admin(client, admin_token):
    resp = client.get("/api/v1/audit/alerts", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_audit_api_forbidden_staff(client, admin_token):
    # Create approved staff
    signup_resp = client.post("/api/v1/auth/signup", json={
        "name": "Audit Staff",
        "email": "auditstaff@test.com",
        "password": "testpassword",
        "requested_role": "STAFF"
    })
    req_id = signup_resp.json()["id"]
    client.post(f"/api/v1/admin/signup-requests/{req_id}/approve", headers={"Authorization": f"Bearer {admin_token}"}, json={"role": "STAFF"})
    
    login_resp = client.post("/api/v1/auth/login", data={"username": "auditstaff@test.com", "password": "testpassword"})
    staff_token = login_resp.json()["access_token"]
    
    logs_resp = client.get("/api/v1/audit/logs", headers={"Authorization": f"Bearer {staff_token}"})
    assert logs_resp.status_code == 403
    
    alerts_resp = client.get("/api/v1/audit/alerts", headers={"Authorization": f"Bearer {staff_token}"})
    assert alerts_resp.status_code == 403

def test_audit_api_unauthorized(client):
    logs_resp = client.get("/api/v1/audit/logs")
    assert logs_resp.status_code == 401
    
    alerts_resp = client.get("/api/v1/audit/alerts")
    assert alerts_resp.status_code == 401
