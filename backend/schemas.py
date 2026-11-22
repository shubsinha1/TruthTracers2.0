"""Shared validation objects for the API and the AI response."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

Verdict = Literal["True", "False", "Misleading", "Unverifiable"]
Confidence = Literal["Low", "Medium", "High"]


class Source(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    source_id: str = Field(min_length=1, max_length=16)
    name: str = Field(min_length=1, max_length=150)
    url: str = Field(default="", max_length=500)
    text: str = Field(min_length=10, max_length=15000)

    @field_validator("source_id", "name", "text")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be blank")
        return value.strip()


class VerifyRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    claim: str = Field(min_length=5, max_length=1500)
    sources: list[Source] = Field(min_length=1, max_length=3)

    @field_validator("claim")
    @classmethod
    def valid_claim(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Claim cannot be blank")
        return value.strip()


    @field_validator("sources")
    @classmethod
    def unique_ids(cls, sources):
        if len({source.source_id for source in sources}) != len(sources):
            raise ValueError("Each source needs a distinct ID")
        return sources


class Evidence(BaseModel):
    source_id: str = Field(description="Identifier of the supplied passage, e.g. S1")
    quote: str = Field(description="Verbatim substring from the cited passage")
    how_it_relates: str = Field(description="How this quote relates to the claim")


class ModelResponse(BaseModel):
    verdict: Verdict
    explanation: str
    evidence: list[Evidence]
    confidence: Confidence
    confidence_reason: str
    limitations: list[str]


class VerifyResponse(ModelResponse):
    model_used: str
    evidence_checked: bool = True
