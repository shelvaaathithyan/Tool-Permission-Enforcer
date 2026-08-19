from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, tools: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Takes a natural language prompt and a list of tool definitions.
        Returns a tuple of (natural_language_response, tool_call_dict).
        
        tool_call_dict format:
        {
            "name": "tool_name",
            "arguments": {"arg1": "val1"}
        }
        
        If no tool is called, tool_call_dict is None.
        """
        pass
