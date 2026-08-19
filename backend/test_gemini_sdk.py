import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "dummy"))
model = genai.GenerativeModel('gemini-1.5-flash')

tools = [
    {
        "name": "search_customers",
        "description": "Search for customers.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The search term."
                }
            },
            "required": ["query"]
        }
    }
]

try:
    response = model.generate_content("test", tools=tools)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
