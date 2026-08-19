from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.auth.models import User, Role
from app.auth.schemas import UserCreate
from app.core.security import get_password_hash
from app.agent.models import Agent
import uuid

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.scalars(select(User).where(User.id == user_id)).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role=user_in.role
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        
        # Every user MUST have an agent
        agent_id = f"agent-{user_in.name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
        db_agent = Agent(
            agent_id=agent_id,
            user_id=db_user.id,
            name=f"{user_in.name} CRM Assistant"
        )
        db.add(db_agent)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email already exists")
