import google.generativeai as genai
from app.core.config import settings
from app.agent.llm.base import LLMProvider
from typing import List, Dict, Any, Tuple, Optional
import json

class GeminiProvider(LLMProvider):
    def __init__(self):
        # We assume settings.gemini_api_key might be None in testing, 
        # but in production it must be set.
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, prompt: str, tools: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        if not settings.gemini_api_key:
            # Fallback or mock behavior for tests if API key isn't provided
            raise ValueError("GEMINI_API_KEY is not configured")
            
        try:
            # Note: The google-generativeai SDK requires tools to be formatted as google.ai.generativelanguage.Tool
            # Alternatively, we can pass them directly if the dictionary format matches OpenAPI schemas expected by genai.
            # In google-generativeai==0.8.3, `tools` can be passed as a list of dicts.
            response = self.model.generate_content(
                prompt,
                tools=tools
            )
            
            # Check for function call
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        fc = part.function_call
                        # Extract arguments safely
                        args = {}
                        for key, value in fc.args.items():
                            args[key] = value
                        
                        return "", {
                            "name": fc.name,
                            "arguments": args
                        }
            
            # No tool call, just text
            return response.text, None
            
        except Exception as e:
            raise RuntimeError(f"LLM API failure: {str(e)}")
