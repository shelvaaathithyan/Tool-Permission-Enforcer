import pytest
from app.agent.llm.gemini import GeminiProvider
from app.agent.tools import agent_tools
from app.core.config import settings

def test_reproduce_gemini():
    if not settings.gemini_api_key:
        print("NO API KEY")
        return
        
    provider = GeminiProvider()
    print("Sending prompt to Gemini...")
    try:
        text, tool_call = provider.generate_response("who works in Dataworks.inc?", agent_tools)
        print("TEXT:", text)
        print("TOOL CALL:", tool_call)
    except Exception as e:
        import traceback
        traceback.print_exc()
