from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.audit.models import AuditLog, SecurityAlert, ActorType, AuditDecision, AlertSeverity, AlertStatus
import uuid

def log_audit_event(
    db: Session,
    user_id: uuid.UUID,
    actor_type: ActorType,
    operation: str,
    resource: str,
    agent_id: uuid.UUID | None = None,
    session_id: str | None = None,
    tool_name: str | None = None,
    customer_id: str | None = None,
    original_prompt: str | None = None,
    arguments: dict | None = None,
    decision: AuditDecision = AuditDecision.PENDING,
    reason: str | None = None
) -> AuditLog:
    
    log = AuditLog(
        user_id=user_id,
        agent_id=agent_id,
        session_id=session_id,
        actor_type=actor_type,
        operation=operation,
        resource=resource,
        tool_name=tool_name,
        customer_id=customer_id,
        original_prompt=original_prompt,
        arguments=arguments,
        decision=decision,
        reason=reason
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def check_violation_threshold(
    db: Session,
    user_id: uuid.UUID,
    agent_id: uuid.UUID,
    session_id: str
):
    """
    Checks if there are MORE THAN 3 blocked mutating Agent operations
    within ONE session. If so, creates a SecurityAlert if one hasn't
    been created for this threshold crossing.
    """
    
    # 1. Count blocked mutating requests
    blocked_count = db.scalar(
        select(func.count()).select_from(AuditLog)
        .where(
            AuditLog.user_id == user_id,
            AuditLog.agent_id == agent_id,
            AuditLog.session_id == session_id,
            AuditLog.actor_type == ActorType.AGENT,
            AuditLog.operation.in_(["CREATE", "UPDATE", "DELETE"]),
            AuditLog.decision == AuditDecision.BLOCKED
        )
    )
    
    # Threshold is MORE THAN 3 (so 4 or more)
    if blocked_count >= 4:
        # 2. Check if alert already exists for this session
        existing_alert = db.scalar(
            select(SecurityAlert)
            .where(
                SecurityAlert.user_id == user_id,
                SecurityAlert.agent_id == agent_id,
                SecurityAlert.session_id == session_id
            )
        )
        
        if not existing_alert:
            # 3. Create alert
            alert = SecurityAlert(
                user_id=user_id,
                agent_id=agent_id,
                session_id=session_id,
                severity=AlertSeverity.HIGH,
                description=f"Multiple blocked mutating operations detected (count: {blocked_count})."
            )
            db.add(alert)
            db.commit()

def get_audit_logs(db: Session, limit: int = 100, offset: int = 0):
    return db.scalars(
        select(AuditLog)
        .where(AuditLog.decision != AuditDecision.PENDING)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

def get_security_alerts(db: Session, limit: int = 100, offset: int = 0):
    return db.scalars(
        select(SecurityAlert).order_by(SecurityAlert.created_at.desc()).limit(limit).offset(offset)
    ).all()
