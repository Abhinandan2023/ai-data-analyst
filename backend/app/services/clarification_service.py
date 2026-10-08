from backend.app.models.intent import (
    ClarificationOption,
    IntentAnalysis,
)


class ClarificationService:

    def build_options(
        self,
        analysis: IntentAnalysis,
    ) -> list[ClarificationOption]:

        if not analysis.ambiguous:
            return []

        return analysis.clarification_options