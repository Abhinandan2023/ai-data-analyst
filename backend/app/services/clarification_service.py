from backend.app.models.intent import ClarificationOption, IntentAnalysis


class ClarificationService:

    METRIC_OPTIONS = {
        "total_spending": "Highest total spending",
        "order_count": "Highest number of orders",
        "average_order_value": "Highest average order value",
        "lifetime_value": "Highest lifetime value",
    }

    def build_options(
        self,
        analysis: IntentAnalysis,
    ) -> list[ClarificationOption]:

        if not analysis.ambiguous:
            return []

        options = []

        for ambiguity in analysis.ambiguities:
            if ambiguity in self.METRIC_OPTIONS:
                options.append(
                    ClarificationOption(
                        value=ambiguity,
                        label=self.METRIC_OPTIONS[ambiguity],
                    )
                )

        return options