from pydantic import BaseModel
from typing import Any, Dict

class ToolInvocationRequest(BaseModel):
    tool_name: str
    operation: str
    arguments: Dict[str, Any]

class ToolInvocationResponse(BaseModel):
    result: Any
