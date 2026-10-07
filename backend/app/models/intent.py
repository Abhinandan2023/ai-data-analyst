from typing import Optional

from pydantic import BaseModel, Field


class ClarificationOption(BaseModel):
    value: str
    label: str


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

    clarification_options: list[ClarificationOption] = Field(
        default_factory=list,
        description="Possible options the user can choose from when clarification is needed."
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


class ResolvedIntent(BaseModel):
    intent: str = Field(
        description="The resolved business operation."
    )

    metric: Optional[str] = Field(
        default=None,
        description="The resolved metric, if applicable."
    )

    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Resolved filters that should be applied to the query."
    )

class SQLGenerationResult(BaseModel):
    sql: str = Field(
        description="The generated PostgreSQL SELECT query."
    )

    explanation: str = Field(
        description="A brief explanation of what the SQL query does."
    )