from typing import List, Dict, Any
from app.agent.tools import agent_tools, TOOL_METADATA

class ToolRegistry:
    def __init__(self):
        self.tools = agent_tools
        self.metadata = TOOL_METADATA
        
    def get_all_tools(self) -> List[Dict[str, Any]]:
        return self.tools
        
    def get_tool_metadata(self, tool_name: str) -> Dict[str, str]:
        if tool_name not in self.metadata:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self.metadata[tool_name]
        
    def validate_tool_call(self, tool_name: str) -> bool:
        return tool_name in self.metadata

registry = ToolRegistry()
