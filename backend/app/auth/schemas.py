from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
import uuid
from app.auth.models import Role, SignupStatus
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Role

class UserUpdate(BaseModel):
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AgentResponse(BaseModel):
    id: uuid.UUID
    agent_id: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: uuid.UUID
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime
    agent: Optional[AgentResponse] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class SignupRequestCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    requested_role: Role

class SignupRequestResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    requested_role: Role
    status: SignupStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ApprovalRequest(BaseModel):
    role: Role

class RejectionRequest(BaseModel):
    reason: Optional[str] = None

