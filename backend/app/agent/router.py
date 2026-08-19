from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.models import User
from app.agent.models import Agent, Session as AgentSession, SessionStatus
from app.api import deps
from app.agent import schemas
from app.permission_proxy.service import get_permission_proxy
import uuid

router = APIRouter()

@router.post("/invoke", response_model=schemas.ToolInvocationResponse)
def invoke_agent_tool(
    request: schemas.ToolInvocationRequest,
    current_user: User = Depends(deps.require_authenticated_user),
    current_agent: Agent = Depends(deps.get_current_agent),
    db: Session = Depends(get_db)
):
    active_session = db.query(AgentSession).filter(
        AgentSession.agent_id == current_agent.id,
        AgentSession.status == SessionStatus.ACTIVE
    ).first()
    
    if not active_session:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        active_session = AgentSession(
            session_id=session_id,
            user_id=current_user.id,
            agent_id=current_agent.id
        )
        db.add(active_session)
        db.commit()
        db.refresh(active_session)
        
    proxy = get_permission_proxy(db)
    result = proxy.invoke(
        agent=current_agent,
        session_id=active_session.session_id,
        tool_name=request.tool_name,
        operation=request.operation,
        arguments=request.arguments
    )
    
    return {"result": result}
