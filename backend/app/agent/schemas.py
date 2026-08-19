from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import uuid

class AgentInvokeRequest(BaseModel):
    prompt: str = Field(..., description="Natural language prompt for the agent.")

class AgentToolRequest(BaseModel):
    tool_name: str
    operation: str
    resource: str
    arguments: Dict[str, Any]
    original_prompt: str

class AgentInvokeResponse(BaseModel):
    status: str
    response: str
    tool_request: Optional[AgentToolRequest] = None
