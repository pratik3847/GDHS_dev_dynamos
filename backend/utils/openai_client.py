import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_client = None

def get_openai():
    global _client
    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")  # ✅ use OpenRouter key
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY missing in .env")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"  # ✅ force OpenRouter endpoint
        )
    return _client
