import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
try:
    for m in genai.list_models():
        print(f"name: {m.name}")
except Exception as e:
    import traceback
    traceback.print_exc()
