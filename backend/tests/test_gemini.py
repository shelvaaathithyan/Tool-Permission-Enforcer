import pytest
from unittest.mock import MagicMock, patch
from app.agent.llm.gemini import GeminiProvider
import google.generativeai as genai
from app.core.config import settings

class MockPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call

class MockContent:
    def __init__(self, parts):
        self.parts = parts

class MockCandidate:
    def __init__(self, content=None):
        self.content = content

class MockResponse:
    def __init__(self, text="", candidates=None):
        self.text = text
        self.candidates = candidates or []

@pytest.fixture
def provider():
    with patch("app.core.config.settings.gemini_api_key", "dummy"):
        return GeminiProvider()

def test_gemini_text_response(provider):
    mock_resp = MockResponse(
        text="Here is some text.",
        candidates=[MockCandidate(MockContent([MockPart(text="Here is some text.")]))]
    )
    with patch.object(provider.model, "generate_content", return_value=mock_resp):
        text, tool_call = provider.generate_response("hello", [])
        assert text == "Here is some text."
        assert tool_call is None

def test_gemini_function_call_response(provider):
    class MockFunctionCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args

    fc = MockFunctionCall("get_customer", {"customer_id": "CUST-123"})
    mock_resp = MockResponse(
        candidates=[MockCandidate(MockContent([MockPart(function_call=fc)]))]
    )
    
    with patch.object(provider.model, "generate_content", return_value=mock_resp):
        text, tool_call = provider.generate_response("hello", [])
        assert text == ""
        assert tool_call is not None
        assert tool_call["name"] == "get_customer"
        assert tool_call["arguments"]["customer_id"] == "CUST-123"

def test_gemini_missing_empty_response(provider):
    # Empty candidates
    mock_resp = MockResponse(candidates=[])
    with patch.object(provider.model, "generate_content", return_value=mock_resp):
        text, tool_call = provider.generate_response("hello", [])
        assert text == ""
        assert tool_call is None

def test_gemini_malformed_function_call(provider):
    # Missing args attribute
    class MalformedFunctionCall:
        def __init__(self, name):
            self.name = name
            # intentionally no args
            
    fc = MalformedFunctionCall("bad_tool")
    mock_resp = MockResponse(
        candidates=[MockCandidate(MockContent([MockPart(function_call=fc)]))]
    )
    
    with patch.object(provider.model, "generate_content", return_value=mock_resp):
        text, tool_call = provider.generate_response("hello", [])
        assert text == ""
        assert tool_call is not None
        assert tool_call["name"] == "bad_tool"
        assert tool_call["arguments"] == {}

def test_regression_object_error(provider):
    # This tests the exact failure that produced "LLM API failure: 'object'"
    # We pass a tool schema with lowercase "type": "object" which used to throw a KeyError
    # inside google.generativeai.
    tools = [
        {
            "name": "test_tool",
            "description": "A test tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "prop1": {"type": "string"}
                }
            }
        }
    ]
    
    # We mock the grpc / inner generate_content so it doesn't actually hit the network,
    # but we allow the SDK's preparation phase to run.
    with patch("google.generativeai.generative_models.GenerativeModel.generate_content") as mock_gen:
        # Instead of mocking provider.model.generate_content (which skips the SDK's logic entirely),
        # we can just test the formatter directly to see it uppercase it:
        formatted = provider._format_tools_for_gemini(tools)
        assert formatted[0]["parameters"]["type"] == "OBJECT"
        assert formatted[0]["parameters"]["properties"]["prop1"]["type"] == "STRING"
        
        # We can also verify that the SDK's content_types doesn't throw a KeyError
        from google.generativeai.types import content_types
        # If this does not throw a KeyError, the regression is fixed
        content_types.to_function_library(formatted)
