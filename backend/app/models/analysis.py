from typing import Optional

from pydantic import BaseModel, Field

from backend.app.models.intent import ClarificationOption


class AnalysisRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Natural language question from the user.",
    )

    selected_option: Optional[str] = Field(
        default=None,
        description="Selected clarification option, if clarification was requested.",
    )


class AnalysisResponse(BaseModel):
    status: str
    answer: Optional[str] = None
    clarification_question: Optional[str] = None
    clarification_options: list[ClarificationOption] = Field(
        default_factory=list
    )
    sql: Optional[str] = None