import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from fastapi.security import OAuth2PasswordRequestForm
from app.database.session import get_db
from app.auth import schemas, service, models
from app.core import security
from app.api import deps
from app.agent.models import Session as AgentSession, SessionStatus

router = APIRouter()

@router.post("/signup", response_model=schemas.SignupRequestResponse, status_code=status.HTTP_201_CREATED)
def signup(request_in: schemas.SignupRequestCreate, db: DBSession = Depends(get_db)):
    if request_in.requested_role == models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot signup as ADMIN")
        
    try:
        signup_req = service.create_signup_request(db, request_in)
        return signup_req
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DBSession = Depends(get_db)):
    user = service.get_user_by_email(db, email=form_data.username)
    if not user:
        # Check if there is a pending or rejected signup request
        signup_req = service.get_signup_request_by_email(db, form_data.username)
        if signup_req:
            if signup_req.status == models.SignupStatus.PENDING:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is awaiting administrator approval.")
            if signup_req.status == models.SignupStatus.REJECTED:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your registration request was rejected.")
                
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account has been disabled.")
        
    if not user.agent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User has no associated Agent.")

    # Deactivate existing active sessions
    db.query(AgentSession).filter(
        AgentSession.user_id == user.id,
        AgentSession.status == SessionStatus.ACTIVE
    ).update({"status": SessionStatus.INACTIVE})
    
    # Create new active session
    new_session = AgentSession(
        session_id=f"SESSION-{uuid.uuid4().hex[:8].upper()}",
        user_id=user.id,
        agent_id=user.agent.id,
        status=SessionStatus.ACTIVE
    )
    db.add(new_session)
    db.commit()

    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@router.post("/logout")
def logout(db: DBSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    # Deactivate active session
    db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id,
        AgentSession.status == SessionStatus.ACTIVE
    ).update({"status": SessionStatus.INACTIVE})
    db.commit()
    return {"message": "Successfully logged out"}

@router.get("/session")
def get_session(db: DBSession = Depends(get_db), current_user: models.User = Depends(deps.get_current_user)):
    active_session = db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id,
        AgentSession.agent_id == current_user.agent.id,
        AgentSession.status == SessionStatus.ACTIVE
    ).first()
    
    if not active_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session found")
        
    return {
        "session_id": active_session.session_id,
        "user_id": str(active_session.user_id),
        "agent_id": str(active_session.agent_id),
        "status": active_session.status.value
    }
