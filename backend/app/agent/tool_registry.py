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

    def validate_tool_arguments(self, tool_name: str, arguments: dict) -> list[str]:
        errors = []
        if tool_name not in self.metadata:
            errors.append(f"Unknown tool: {tool_name}")
            return errors
            
        if not isinstance(arguments, dict):
            errors.append("Arguments must be a dictionary.")
            return errors

        tool_schema = next((t for t in self.tools if t["name"] == tool_name), None)
        if not tool_schema:
            return errors

        schema_params = tool_schema.get("parameters", {})
        properties = schema_params.get("properties", {})
        required = schema_params.get("required", [])

        for req in required:
            if req not in arguments:
                errors.append(f"Missing required argument: {req}")

        for key, value in arguments.items():
            if key not in properties:
                errors.append(f"Unsupported argument: {key}")
            else:
                # Basic type checking
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Argument '{key}' should be a string.")
                elif expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"Argument '{key}' should be an integer.")
                elif expected_type == "object" and not isinstance(value, dict):
                    errors.append(f"Argument '{key}' should be an object.")
                    
        return errors

registry = ToolRegistry()
