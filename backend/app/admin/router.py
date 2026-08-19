from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List
import datetime

from app.database.session import get_db
from app.auth import schemas as auth_schemas
from app.auth import models as auth_models
from app.auth import service as auth_service
from app.agent.models import Agent, Session as AgentSession, SessionStatus
from app.crm.models import Customer
from app.api import deps

router = APIRouter()

# ── Dashboard Stats ─────────────────────────────────────────────────────────
@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_admin)
):
    total_customers = db.scalar(select(func.count()).select_from(Customer)) or 0
    active_sessions = db.scalar(
        select(func.count()).select_from(AgentSession).where(AgentSession.status == SessionStatus.ACTIVE)
    ) or 0
    total_users = db.scalar(select(func.count()).select_from(auth_models.User)) or 0
    active_users = db.scalar(
        select(func.count()).select_from(auth_models.User).where(auth_models.User.is_active == True)
    ) or 0
    total_agents = db.scalar(select(func.count()).select_from(Agent)) or 0
    pending_signups = db.scalar(
        select(func.count()).select_from(auth_models.SignupRequest).where(
            auth_models.SignupRequest.status == auth_models.SignupStatus.PENDING
        )
    ) or 0
    return {
        "total_customers": total_customers,
        "active_sessions": active_sessions,
        "total_users": total_users,
        "active_users": active_users,
        "total_agents": total_agents,
        "pending_signups": pending_signups,
        "allowed_operations": 0,
        "blocked_operations": 0,
    }

# ── User-level Stats (for Manager/Staff) ────────────────────────────────────
@router.get("/my-stats")
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_authenticated_user)
):
    total_customers = db.scalar(select(func.count()).select_from(Customer)) or 0
    agent = current_user.agent
    active_sessions = 0
    if agent:
        active_sessions = db.scalar(
            select(func.count()).select_from(AgentSession).where(
                AgentSession.agent_id == agent.id,
                AgentSession.status == SessionStatus.ACTIVE
            )
        ) or 0
    return {
        "total_customers": total_customers,
        "active_sessions": active_sessions,
        "allowed_operations": 0,
        "blocked_operations": 0,
    }

# ── Users List (Admin only) ─────────────────────────────────────────────────
@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_admin)
):
    users = db.scalars(select(auth_models.User).order_by(auth_models.User.created_at.desc())).all()
    result = []
    for u in users:
        result.append({
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "role": u.role.value,
            "is_active": u.is_active,
            "agent_id": u.agent.agent_id if u.agent else None,
            "agent_name": u.agent.name if u.agent else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return result

# ── Agents List (Admin only) ────────────────────────────────────────────────
@router.get("/agents")
def get_agents(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_admin)
):
    agents = db.scalars(select(Agent).order_by(Agent.created_at.desc())).all()
    result = []
    for a in agents:
        result.append({
            "id": str(a.id),
            "agent_id": a.agent_id,
            "name": a.name,
            "is_active": a.is_active,
            "owner_name": a.user.name if a.user else None,
            "owner_role": a.user.role.value if a.user else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    return result

# ── Signup Requests ──────────────────────────────────────────────────────────
@router.get("/signup-requests", response_model=List[auth_schemas.SignupRequestResponse])
def get_signup_requests(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_admin)
):
    requests = db.scalars(
        select(auth_models.SignupRequest).order_by(auth_models.SignupRequest.created_at.desc())
    ).all()
    return requests

@router.post("/signup-requests/{request_id}/approve")
def approve_signup_request(
    request_id: str,
    approval: auth_schemas.ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_admin)
):
    signup_req = db.scalars(select(auth_models.SignupRequest).where(auth_models.SignupRequest.id == request_id)).first()
    
    if not signup_req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signup request not found")
        
    if signup_req.status != auth_models.SignupStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not PENDING")
        
    if approval.role == auth_models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign ADMIN role via public signup approval")

    try:
        new_user = auth_service.create_user_and_agent(
            db=db,
            name=signup_req.name,
            email=signup_req.email,
            password_hash=signup_req.password_hash,
            role=approval.role
        )
        
        signup_req.status = auth_models.SignupStatus.APPROVED
        signup_req.reviewed_by = current_user.id
        signup_req.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
        
        db.commit()
        return {"message": "Signup request approved and user created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during approval")

@router.post("/signup-requests/{request_id}/reject")
def reject_signup_request(
    request_id: str,
    rejection: auth_schemas.RejectionRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(deps.require_admin)
):
    signup_req = db.scalars(select(auth_models.SignupRequest).where(auth_models.SignupRequest.id == request_id)).first()
    
    if not signup_req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signup request not found")
        
    if signup_req.status != auth_models.SignupStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not PENDING")

    signup_req.status = auth_models.SignupStatus.REJECTED
    signup_req.rejection_reason = rejection.reason
    signup_req.reviewed_by = current_user.id
    signup_req.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    return {"message": "Signup request rejected"}

