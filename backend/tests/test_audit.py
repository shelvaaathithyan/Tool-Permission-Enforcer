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
