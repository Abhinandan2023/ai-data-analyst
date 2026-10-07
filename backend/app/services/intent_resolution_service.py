from backend.app.models.intent import (
    IntentAnalysis,
    ResolvedIntent,
)


class IntentResolutionService:

    def resolve(
        self,
        analysis: IntentAnalysis,
        selected_option: str,
    ) -> ResolvedIntent:

        if not analysis.ambiguous:
            return ResolvedIntent(
                intent=analysis.intent,
                metric=analysis.metric,
            )

        valid_options = {
            option.value
            for option in analysis.clarification_options
        }

        if selected_option not in valid_options:
            raise ValueError(
                f"Invalid clarification option: {selected_option}"
            )

        return ResolvedIntent(
            intent=analysis.intent,
            metric=selected_option,
        )