from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.models import User
from app.agent.models import Agent, Session as AgentSession, SessionStatus
from app.api import deps
from app.agent import schemas
from app.agent.service import AgentService
from app.agent.llm.gemini import GeminiProvider
import uuid

router = APIRouter()

# Instantiate provider and service globally for the router
llm_provider = GeminiProvider()
agent_service = AgentService(llm_provider=llm_provider)

@router.post("/invoke", response_model=schemas.AgentInvokeResponse)
def invoke_agent_tool(
    request: schemas.AgentInvokeRequest,
    current_user: User = Depends(deps.require_authenticated_user),
    current_agent: Agent = Depends(deps.get_current_agent),
    db: Session = Depends(get_db)
):
    active_session = db.query(AgentSession).filter(
        AgentSession.agent_id == current_agent.id,
        AgentSession.status == SessionStatus.ACTIVE
    ).first()
    
    if not active_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active session found")
        
    try:
        response = agent_service.invoke(
            db=db,
            user=current_user,
            agent=current_agent,
            active_session=active_session,
            prompt=request.prompt
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
