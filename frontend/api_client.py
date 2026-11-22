"""HTTP-only frontend-to-backend communication. No Gemini key lives here."""
import requests

BASE_URL = "http://127.0.0.1:8000"


def health():
    return requests.get(f"{BASE_URL}/health", timeout=5).json()


def verify_claim(payload):
    response = requests.post(f"{BASE_URL}/verify", json=payload, timeout=90)
    if not response.ok:
        try:
            detail = response.json().get("detail", f"HTTP {response.status_code}")
        except ValueError:
            detail = f"HTTP {response.status_code}"
        raise RuntimeError(str(detail))
    return response.json()
