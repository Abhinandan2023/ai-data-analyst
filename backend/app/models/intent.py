from typing import Optional

from pydantic import BaseModel, Field


class IntentAnalysis(BaseModel):
    intent: str = Field(
        description="The user's intended business operation."
    )

    ambiguous: bool = Field(
        description="Whether the user's request is ambiguous."
    )

    ambiguities: list[str] = Field(
        default_factory=list,
        description="Specific pieces of information that are missing or ambiguous."
    )

    clarification_question: Optional[str] = Field(
        default=None,
        description="A concise question to ask the user if clarification is needed."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the interpretation of the user's request."
    )

    metric: Optional[str] = Field(
        default=None,
        description="Metric specified by the user, if applicable."
    )