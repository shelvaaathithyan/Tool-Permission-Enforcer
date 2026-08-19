from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.auth.models import User, Role, SignupRequest, SignupStatus
from app.auth.schemas import UserCreate, SignupRequestCreate
from app.core.security import get_password_hash
from app.agent.models import Agent
import uuid

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.scalars(select(User).where(User.id == user_id)).first()

def get_signup_request_by_email(db: Session, email: str) -> SignupRequest | None:
    return db.scalars(select(SignupRequest).where(SignupRequest.email == email)).first()

def create_signup_request(db: Session, request_in: SignupRequestCreate) -> SignupRequest:
    # Check if user already exists
    if get_user_by_email(db, request_in.email):
        raise ValueError("User with this email already exists")
    
    # Check if pending request exists
    existing_request = get_signup_request_by_email(db, request_in.email)
    if existing_request and existing_request.status == SignupStatus.PENDING:
        raise ValueError("A pending signup request with this email already exists")

    hashed_password = get_password_hash(request_in.password)
    
    db_request = SignupRequest(
        name=request_in.name,
        email=request_in.email,
        password_hash=hashed_password,
        requested_role=request_in.requested_role,
        status=SignupStatus.PENDING
    )
    db.add(db_request)
    try:
        db.commit()
        db.refresh(db_request)
        return db_request
    except IntegrityError:
        db.rollback()
        raise ValueError("A signup request with this email already exists")

def create_user_and_agent(db: Session, name: str, email: str, password_hash: str, role: Role) -> User:
    db_user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        
        # Every user MUST have exactly one agent
        agent_id = f"agent-{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
        db_agent = Agent(
            agent_id=agent_id,
            user_id=db_user.id,
            name=f"{name} CRM Assistant"
        )
        db.add(db_agent)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email already exists")
