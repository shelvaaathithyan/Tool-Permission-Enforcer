from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from app.audit.models import ActorType, AuditDecision, AlertSeverity, AlertStatus

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    actor_type: ActorType
    operation: str
    resource: str
    tool_name: Optional[str] = None
    customer_id: Optional[str] = None
    original_prompt: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    decision: AuditDecision
    reason: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SecurityAlertResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    severity: AlertSeverity
    description: str
    status: AlertStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
