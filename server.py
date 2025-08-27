from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from proxy_client import analyze_text_with_proxy
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # אפשר להחליף לרשימת דומיינים מורשים בלבד
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

def load_system_prompt(path: str = None) -> str:
    if path is None:
        path = os.getenv("SYSTEM_PROMPT_PATH", "system_prompt_level_3.md")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


SYSTEM_PROMPT = load_system_prompt()

@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    text = body.get("text", "")
    print(f"[DEBUG] Got text: {text}")
    if not text:
        print("[DEBUG] Missing text in request body")
        return JSONResponse({"error": "Missing text"}, status_code=400)
    try:
        import asyncio
        import json
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, analyze_text_with_proxy, text, SYSTEM_PROMPT)
        print(f"[DEBUG] LLM result: {result}")
        # Validate the result: must be a JSON with compliance, risk, and category
        try:
            data = json.loads(result)
        except Exception as e:
            print(f"[DEBUG] LLM response is not valid JSON: {e}")
            return JSONResponse({"error": "Invalid JSON from LLM", "llm_response": result}, status_code=500)

        compliance = data.get("compliance")
        risk = data.get("risk")
        category = data.get("category")
        allowed_compliance = ["high", "medium", "low", "none"]
        allowed_risk = ["green", "yellow", "red"]
        if (
            compliance not in allowed_compliance
            or risk not in allowed_risk
            or not isinstance(category, str)
        ):
            print(f"[DEBUG] Invalid compliance, risk or category in LLM response: {data}")
            return JSONResponse({"error": "Invalid compliance, risk or category in LLM response", "llm_response": data}, status_code=500)
        return {"compliance": compliance, "risk": risk, "category": category}
    except Exception as e:
        import traceback 
        print(f"[DEBUG] Exception: {e}")
        traceback.print_exc()
        # If the exception has a response attribute (from openai/httpx), return its content and status code
        response = getattr(e, 'response', None)
        if response is not None:
            try:
                content = response.text
                status_code = response.status_code
                return JSONResponse({"proxy_error": content}, status_code=status_code)
            except Exception:
                pass
        return JSONResponse({"error": str(e)}, status_code=500)
