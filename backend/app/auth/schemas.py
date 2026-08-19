from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
import uuid
from app.auth.models import Role
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Role

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
