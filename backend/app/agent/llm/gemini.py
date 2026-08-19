import google.generativeai as genai
from app.core.config import settings
from app.agent.llm.base import LLMProvider
from typing import List, Dict, Any, Tuple, Optional
import json
import logging

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            
        sys_prompt = (
            "You are a CRM assistant. Follow these exact tool mapping rules:\n"
            "- Customer names should use get_customer.\n"
            "- Customer IDs should use get_customer.\n"
            "- Company-based queries should use search_customers (e.g., query='company: Pioneer Apps' or just 'Pioneer Apps').\n"
            "- Designation-based queries should use search_customers.\n"
            "- Status-based queries should use search_customers.\n"
            "Treat the following natural-language phrases as search intent (search_customers):\n"
            "- 'who works at...'\n"
            "- 'who is from...'\n"
            "- 'which customer...'\n"
            "- 'find customers...'\n"
            "- 'customers working at...'\n"
            "Do NOT use get_customer for company names or 'the requested customer'."
        )
        self.model = genai.GenerativeModel('gemini-3.6-flash', system_instruction=sys_prompt)

    def _format_tools_for_gemini(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        import copy
        formatted_tools = copy.deepcopy(tools)
        
        def _uppercase_types(node):
            if isinstance(node, dict):
                # Gemini schema does not support 'default'
                if "default" in node:
                    node.pop("default")
                if "type" in node and isinstance(node["type"], str):
                    node["type"] = node["type"].upper()
                for value in node.values():
                    _uppercase_types(value)
            elif isinstance(node, list):
                for item in node:
                    _uppercase_types(item)
                    
        _uppercase_types(formatted_tools)
        return formatted_tools

    def generate_response(self, prompt: str, tools: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
            
        try:
            gemini_tools = self._format_tools_for_gemini(tools)
            response = self.model.generate_content(
                prompt,
                tools=gemini_tools
            )
            
            # Check for candidates safely
            if not getattr(response, "candidates", None):
                logger.warning("Gemini response missing candidates")
                return "", None
                
            candidate = response.candidates[0]
            if not getattr(candidate, "content", None) or not getattr(candidate.content, "parts", None):
                logger.warning("Gemini candidate missing content or parts")
                return "", None
                
            for part in candidate.content.parts:
                if getattr(part, "function_call", None):
                    fc = part.function_call
                    name = getattr(fc, "name", "")
                    fc_args = getattr(fc, "args", {})
                    
                    def _unwrap(obj):
                        if hasattr(obj, "items"):
                            return {k: _unwrap(v) for k, v in obj.items()}
                        elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, dict)):
                            return [_unwrap(v) for v in obj]
                        else:
                            return obj
                            
                    args = _unwrap(fc_args)

                    return "", {
                        "name": name,
                        "arguments": args if isinstance(args, dict) else {}
                    }
            
            return getattr(response, "text", ""), None
            
        except Exception as e:
            logger.exception("Gemini API LLMProvider encountered an error during generation")
            raise RuntimeError("LLM API failure") from e
