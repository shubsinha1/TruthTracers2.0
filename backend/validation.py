"""Post-processing to prevent invented quotes from appearing as verified evidence."""
from .schemas import ModelResponse, VerifyRequest, VerifyResponse


def verify_evidence(model_result: ModelResponse, request: VerifyRequest, model_name: str) -> VerifyResponse:
    sources = {s.source_id: s for s in request.sources}
    valid = [
        item for item in model_result.evidence
        if item.source_id in sources and bool(item.quote.strip())
        and item.quote in sources[item.source_id].text
    ]
    dropped = len(model_result.evidence) - len(valid)
    limitations = list(model_result.limitations)
    verdict = model_result.verdict
    confidence = model_result.confidence
    explanation = model_result.explanation
    confidence_reason = model_result.confidence_reason
    if dropped:
        limitations.append(f"Removed {dropped} model quotation(s) not found exactly in supplied source passages.")
        if confidence == "High":
            confidence = "Medium"
    # Never present a decisive verdict without at least one validated quotation.
    if not valid and verdict != "Unverifiable":
        verdict = "Unverifiable"
        confidence = "Low"
        confidence_reason = "No supporting quotation passed exact-text validation."
        explanation = "The generated response did not provide a verifiable quotation supporting a decisive verdict."
        limitations.append("Provide source passages that directly address the claim and retry.")
    return VerifyResponse(
        verdict=verdict,
        explanation=explanation,
        evidence=valid,
        confidence=confidence,
        confidence_reason=confidence_reason,
        limitations=limitations,
        model_used=model_name,
    )
