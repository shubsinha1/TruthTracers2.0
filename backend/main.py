"""TruthTrace REST backend. Run: uvicorn backend.main:app --reload --port 8000"""
import json
import os
import re
from pathlib import Path

import httpx
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .examples import EXAMPLES
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from .prompts import SYSTEM_PROMPT
from .schemas import ModelResponse, VerifyRequest, VerifyResponse
from .validation import verify_evidence

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="TruthTrace Backend", version="0.1.0", description="Source-grounded fact-checking API")


@app.get("/health")
def health():
    return {"status": "ok", "api_key_configured": os.getenv("GEMINI_API_KEY", "").strip() not in ("", "PASTE_YOUR_KEY_HERE"), "service": "TruthTrace"}


@app.post("/verify", response_model=VerifyResponse)
def verify(request: VerifyRequest):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "PASTE_YOUR_KEY_HERE":
        raise HTTPException(status_code=503, detail="Gemini API key is not configured. Add GEMINI_API_KEY to .env and restart the backend.")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", model):
        raise HTTPException(status_code=500, detail="Invalid GEMINI_MODEL value in local .env")
    payload = json.dumps(request.model_dump(), ensure_ascii=False, indent=2)
    user_prompt = "Evaluate the claim using only the supplied evidence JSON below.\n\n" + payload

    try:
        # The Gemini REST API avoids requiring any paid or third-party SDK.
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        api_response = httpx.post(
            endpoint,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {"temperature": 0, "responseMimeType": "application/json",
                                     "responseJsonSchema": ModelResponse.model_json_schema()},
            },
            timeout=75,
        )
        api_response.raise_for_status()
        api_data = api_response.json()
        text = "".join(part.get("text", "") for part in api_data["candidates"][0]["content"]["parts"])
        result = ModelResponse.model_validate_json(text)
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        # Do not expose full request headers, key, or Google response body to the frontend.
        raise HTTPException(
            status_code=502,
            detail="Gemini request failed. Check the model name, API key, free-tier access, and usage limits in Google AI Studio.",
        ) from exc
    return verify_evidence(result, request, model)

WEB = Path(__file__).resolve().parents[1] / "frontend" / "web"
app.mount("/assets", StaticFiles(directory=WEB), name="assets")


@app.get("/")
def home():
    return FileResponse(WEB / "index.html")


@app.get("/examples")
def examples():
    return [{"id": slug, "title": case["title"], "input": case["input"]}
            for slug, case in EXAMPLES.items()]


@app.get("/examples/{slug}/assessment", response_model=VerifyResponse)
def example_assessment(slug: str):
    case = EXAMPLES.get(slug)
    if case is None:
        raise HTTPException(404, "Example not found")
    return verify_evidence(ModelResponse.model_validate(case["assessment"]),
                           VerifyRequest.model_validate(case["input"]), "Prepared example")
