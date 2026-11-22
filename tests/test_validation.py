from backend.schemas import Evidence, ModelResponse, Source, VerifyRequest
from backend.validation import verify_evidence


def sample_request():
    return VerifyRequest(
        claim="Hot water cures a viral infection.",
        sources=[Source(source_id="S1", name="Example source", text="There is no evidence that hot water cures viral infections.")],
    )


def model_output(quote):
    return ModelResponse(
        verdict="False", explanation="Claim conflicts with the source.",
        evidence=[Evidence(source_id="S1", quote=quote, how_it_relates="The passage contradicts the cure claim")],
        confidence="High", confidence_reason="Direct evidence.", limitations=[]
    )


def test_exact_evidence_is_kept():
    result = verify_evidence(model_output("no evidence that hot water cures"), sample_request(), "test-model")
    assert result.verdict == "False"
    assert len(result.evidence) == 1


def test_invented_evidence_downgrades_to_unverifiable():
    result = verify_evidence(model_output("Hot water definitely cures diseases"), sample_request(), "test-model")
    assert result.verdict == "Unverifiable"
    assert result.confidence == "Low"
    assert not result.evidence
