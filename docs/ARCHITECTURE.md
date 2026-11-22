# TruthTrace architecture

```text
Browser (localhost:8501)
    |
    v
Streamlit Frontend (frontend/app.py)
    |
    | POST http://127.0.0.1:8000/verify
    | JSON: claim + source passages ONLY (no API key)
    v
FastAPI Backend (backend/main.py)
    |
    | prompt selection and formatting (backend/prompts.py)
    | Pydantic input / output validation (backend/schemas.py)
    | reads Gemini key from local .env
    v
Google Gemini API (free-tier eligible models and quotas)
    |
    | JSON assessment
    v
Backend verbatim quote checker (backend/validation.py)
    |
    v
Streamlit verdict + evidence + confidence + limitations
```

The default browser client is served at port 8000 from frontend/web. It calls the same /verify endpoint as Streamlit. Example mode loads fixed fictional cases from /examples and prepared assessments from /examples/{id}/assessment. Both paths use the same exact-quotation checker. Each exported browser report includes the original inputs and the assessment.

## System limits

- Supplied excerpts are not verified independently for credibility or freshness.
- Exact quote matching is syntactic, not semantic verification.
- Uploaded claim / excerpts are sent to Gemini if you use the live model.
- No rate-limiting or authentication is provided. Keep the local service private.
- Do not publicly deploy this student prototype without appropriate security review.
- Demo/testing status: no live Gemini request performed when starter was generated.
