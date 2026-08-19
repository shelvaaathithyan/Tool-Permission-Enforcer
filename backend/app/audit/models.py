import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database.base import Base

class ActorType(str, Enum):
    HUMAN = "HUMAN"
    AGENT = "AGENT"

class AuditDecision(str, Enum):
    PENDING = "PENDING"
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    actor_type: Mapped[ActorType] = mapped_column(SQLEnum(ActorType, native_enum=False, length=20), nullable=False)
    operation: Mapped[str] = mapped_column(String, nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String, nullable=True)
    customer_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    original_prompt: Mapped[str] = mapped_column(String, nullable=True)
    arguments: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    status: Mapped[str] = mapped_column(String, nullable=True)
    decision: Mapped[AuditDecision] = mapped_column(SQLEnum(AuditDecision, native_enum=False, length=20), nullable=False, default=AuditDecision.PENDING)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    
    severity: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity, native_enum=False, length=20), nullable=False, default=AlertSeverity.HIGH)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[AlertStatus] = mapped_column(SQLEnum(AlertStatus, native_enum=False, length=20), nullable=False, default=AlertStatus.OPEN)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
